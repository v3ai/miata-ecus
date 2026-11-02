# Firmware-in-the-loop simulation (Renode)

The real firmware images run unmodified on emulated microcontrollers, with the car and the board around them
modelled. This tests what the unit-test engine simulation (`firmware/board/tests`, `tools/sim_report.py`) cannot:
the bootloader handing over to the application, the ChibiOS kernel and HAL drivers on the actual peripherals,
interrupt timing, which pins really toggle and when, the ECU's wideband flasher against the F103's ROM bootloader
protocol, and the CAN link between the two MCUs.

It is instruction-level emulation, not cycle-accurate: Renode runs each instruction in one clock and does not model
pipeline, flash wait states or bus contention. Timers, ADC conversion times, serial byte times and CAN frames do
advance in virtual time at the real clock rates, so firmware timing (injector pulse widths, dwell, spark angle,
timeouts) is meaningful to a few microseconds.

## What runs

| Script | Machines | What it checks |
|---|---|---|
| `run_ecu.py` | ECU: STM32F407, OpenBLT + rusEFI | Per model year: boot, year preset, key-on sensor readings through the board's front end, fuel-pump prime, cranking on a **real recorded cranking capture**, idle/cruise/high rpm, injector count/width/order, coil count/dwell/180° spacing, stall shut-off, main-relay hold and release (2003-05) |
| `run_system.py` | ECU + wideband: STM32F407 and STM32F103 | Blank F103 programmed by the ECU over USART3 + BOOT0/NRST through the ROM bootloader protocol (erase, write, verify), F103 restart, CAN bit timing of both controllers, LSU 4.9 heater warm-up, ESR control, pump loop against the LSU curve, rusEFI's lambda reading |

`python3 run_ecu.py [--years 1989-93,2003-05]` (about 6-10 minutes per year), `python3 run_system.py` (about
30 minutes). The Renode log is written as the run goes; a run whose log stops growing for 10 minutes is stopped. Results (Renode log, pin
transitions, sampled firmware state, CAN frames, check table) go to `out/` (git-ignored); exit code 0 means every
check passed.

## Files

- `stm32f407_ecu.repl`: the ECU's STM32F407 (Renode's `stm32f4.repl` plus what it lacks for this firmware).
- `ecu_bench.repl`: ADC, crank/cam generator and the output-pin recorder wired to the ECU.
- `stm32f103_wbo.repl`, `wbo_bench.repl`: the wideband STM32F103 and its LSU sensor.
- `ecu_wbo_link.repl`: the F103 ROM bootloader on the ECU's programming pins, and a CAN sniffer.
- Platform files refer to their Python models as `@SIM@/models/...`; the run scripts write copies with the
  checkout's path into the output folder and load those.
- `models/`: peripheral and plant models (C#, compiled by Renode at load; Python for simple register files).
- `models/HostProbe.cs`: logs each machine's virtual time and PC every few seconds of host time, from a host
  thread, so a slow or stuck run shows where it is (`PROBE` lines in `renode.log`; map a PC with
  `arm-none-eabi-addr2line -f`).
- `tools/elf_probes.py`: reads addresses and types of firmware variables from the ELF's debug info, so the run
  can sample rusEFI's own state (RPM, sensors, timing, config) from emulated RAM. `tools/sampler.py` does the
  sampling from a hook in rusEFI's 20 Hz slow callback.

## Renode gaps found and how they are covered

Each of these made the unmodified firmware fail in emulation while it would work on silicon:

| Gap in Renode 1.15.3 | Effect on the firmware | Covered by |
|---|---|---|
| NVIC never sets ICSR.RETTOBASE | ChibiOS never switches to a thread woken by an interrupt (both MCUs) | `models/NvicRettobase.cs`: a bus front for the NVIC that sets RETTOBASE from the NVIC's own active-exception stack |
| STM32F4 timers all at 10 MHz | rusEFI's time base (TIM5) ran 8.4× slow; the watchdog reset the ECU after 1 s | real clocks in the platform file (APB1 timers 84 MHz, APB2 168 MHz) |
| No DWT cycle counter; a counter of executed instructions stops in WFI | wrong time measurement | `models/CortexMDwt.cs`: virtual time × core clock |
| No STM32F4 ADC | no battery, key, sensor or knock readings | `models/STM32F4ADC.cs` |
| STM32DMA: no circular mode, NDTR fixed, end-of-transfer interrupt late | ADCs free-run after each block | `models/STM32F4DMA.cs` for DMA2 |
| Flash-size word at 0x1FFF7A22 reads 0 | rusEFI stops: "expected at least 1024K of flash" | written by the run script |
| CCM, backup SRAM, GPIO G/H/I, DBGMCU IDCODE, TIM11 input capture (HSE detect), PWR ready bits | boot hangs or faults | `stm32f407_ecu.repl`, `models/pwr_f4.py`, `models/tim11_hse_capture.py` |
| F103 platform: no RCC, flash controller, ADC, timers, CAN, boot alias | wideband never starts | `stm32f103_wbo.repl`, `models/rcc_f1.py`, `models/STM32F1Flash.cs`, `models/STM32F1ADC.cs` |
| STM32_UART keeps no CR1.M (word length) bit | the 9-bit (8 data + even parity) frame the ROM bootloader needs is invisible on readback | the bootloader model takes the frame format from the CR1 write that enables the USART |
| No STM32F103 ROM bootloader (ST's code is not available) | nothing to flash | `models/F103RomBootloader.cs`: AN3155 v2.2 protocol, serial frame and baud checks, erase/program times |
| Two machines, one host thread each (the default): the time synchronisation between them races | the two-chip run froze at a random point (4.6-5.8 s) with neither CPU executing | `emulation SetGlobalSerialExecution true` in `run_system.py`: both machines on one thread, taking turns each quantum (also deterministic) |

## Limits

- The car side is modelled, not measured: sensors are resistances and voltages through the board's divider values;
  the crank/cam signals are rusEFI's recorded cranking captures (real cars) and rusEFI's trigger shapes for steady
  running; the LSU plant uses the firmware's own scale factors (the analog front end is covered by
  `tools/circuit_sim_full.py`).
- Pin levels are logic levels at the MCU. Whether a real CAS/CKP/CMP gives the polarity rusEFI expects at our
  input stage is a car fact the simulation assumes from the captures.
- No USB (TunerStudio) model: the flasher is started by a hook that does what the TunerStudio button does.
- Overrun, analog watchdog, injected ADC channels, DMA FIFO/burst and CAN bit-level errors are not modelled.
