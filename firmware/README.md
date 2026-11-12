# Firmware

This folder is the [rusEFI](https://github.com/rusefi/rusefi) board definition for the miata-ecus daughterboard
(STM32F407VGT6), plus a flasher that programs the on-board wideband MCU through the main one. One firmware serves
all five motherboards. You pick the model year in TunerStudio.

> **Status:** the board code compiles and links against rusEFI (commit `1374bd07`). It has **not run on hardware**,
> because no board has been built yet. Work through [First start](#first-start) before the engine is started.

## Files
| Path | What |
|---|---|
| `board/meta-info.env`, `board/board.mk` | Board name (`miata-ecu`), MCU, build flags. Also: OpenBLT bootloader, red error LED, knock ADC, the USART3 link, and where the wideband image comes from |
| `board/miata_board.cpp`, `board/miata_pins.h` | Pin map, board facts (dividers, pull-ups, CAN2, MAP sensor), the five year presets and warning expiry |
| `board/miata_nb_tune.cpp` | The 1999-2005 base tune: rusEFI's NB fuel, ignition, injector-lag and VVT target tables, copied unchanged (this one file is GPL-3.0) |
| `board/board_configuration.cpp` | Hooks the above into rusEFI and adds the hardware-only parts (LEDs, wideband flasher) |
| `board/mcuconf.h` | rusEFI's STM32F4 clock settings with the 32 kHz oscillator off (PC14 is the fuel pump; there is no 32 kHz crystal) |
| `board/tests/`, `board/board_unit_tests.mk` | Engine simulation of every year inside rusEFI's unit-test engine (see [Verification](#verification)) |
| `board/wideband_uart_flash.cpp` | Programs the wideband MCU over its ROM serial bootloader |
| `wideband/` | The wideband MCU's firmware: rusEFI's wideband controller sources with this board's STM32F103 port (`miata_f1/`), `build.sh`, and the built image the main firmware carries (`miata_wbo_f103.bin`) |
| `board/connectors/daughterboard.yaml` | Pin names TunerStudio shows (J1/J2 header signals) |
| `board/board_popular_vehicles.ini`, `board/board_commands.ini` | TunerStudio buttons: the five years and "Flash on-board wideband" |
| `board/prepend.txt`, `board/knock_config.h` | TunerStudio menu switches, knock input |
| `ext/rusefi` | rusEFI, as a git submodule pinned to the tested commit |
| `tools/check_pins.py` | Checks every pin here against the board design (`scripts/design.py`) |
| `tools/sim_report.py` | End-to-end check: firmware function → MCU pin → harness cavity, against independent pinouts |
| `tools/flash_sim/` | Wideband flasher run on a PC against a model of the F103's ROM bootloader |
| `tools/check_image.py`, `tools/circuit_sim.py` | Main-MCU image checks (OpenBLT header, layout); ngspice input/output circuit simulations |
| `tools/offline_compile_check.sh` | Compile check without rusEFI's Java code generation (see [Building](#building)) |

## Getting the firmware
The **Firmware** GitHub Actions workflow builds it on every push that touches `firmware/`. It uses rusEFI's own
custom-board build. Open the run on the repository's *Actions* tab and download its artifacts:
- `rusefi_bundle_miata-ecu.zip`: the rusEFI console, the firmware and the TunerStudio project file (`.ini`);
- `rusefi_miata-ecu.bin` / `.dfu` / `.hex`: OpenBLT bootloader + rusEFI in one image, starting at 0x08000000;
- `rusefi_miata-ecu.ini`: the TunerStudio `.ini` on its own.

## Flashing the main MCU (USB-C)
1. **First time:** put the STM32 in ST's DFU mode. Hold **BOOT** (SW1 on the daughterboard), tap **RESET** (SW2),
   then release BOOT. Flash the `.bin` at 0x08000000 with the rusEFI console from the bundle, STM32CubeProgrammer or
   `dfu-util -a 0 -s 0x08000000:leave -D rusefi_miata-ecu.bin`.
2. **Later updates:** use the rusEFI console's update button. The OpenBLT bootloader takes the new firmware over the
   same USB port, with no buttons to press.

## Choosing the year
Connect TunerStudio, open **Popular Vehicles** and press your year. That resets the tune to that year's defaults.
A blank board starts with the 1989–93 settings.

| Button | rusEFI engine type | Trigger | Injection | Ignition sense | Year-specific outputs |
|---|---|---|---|---|---|
| 1989-93 (NA6, 1.6) | `MAZDA_MIATA_NA6` | NA CAS: SGC on HALL2, SGT on HALL1 | batch, two drivers per wire | none (1C is the starter signal) | none (VVT driver = purge, not driven) |
| 1994-95 (NA8, 1.8) | `MAZDA_MIATA_NA94` | NA CAS | sequential | none (1C is the starter signal) | none (ALT driver = pressure regulator solenoid, not driven) |
| 1996-97 (NA8, OBD-II) | `MAZDA_MIATA_NA96` | NA CAS | sequential | none | O2 heater on the VVT driver |
| 1999-2000 (NB1) | `MAZDA_MIATA_NB1` | NB crank on HALL1, cam on HALL2 | sequential | none | O2 heater on VVT, alternator field on ALT (control off by default) |
| 2001-02 (NB2, VVT) | `MAZDA_MIATA_NB2` without main relay or ignition sense | NB crank + VVT cam | sequential | none | VVT valve, alternator field (control off by default) |
| 2003-05 (NB2, VVT) | `MAZDA_MIATA_NB2` | NB crank + VVT cam | sequential | 4S | VVT valve, alternator field (control off by default), main relay (3H) |

**Pick the right NB2 button.** 2001-02 and 2003-05 use the same motherboard but are wired differently. rusEFI cuts
fuel and spark while the ignition-sense input reads "off", so that input is only switched on for the years whose
harness carries an ignition-on wire (4S on 2003-05). Every other year uses battery voltage instead, rusEFI's default,
which comes from the key-switched main relay. 1989-95 pin 1C is not ignition-on: it is the starter (START) signal, live
only while cranking, so using it would cut fuel and spark the moment the key springs back. If an NB2
gets no fuel or spark with the key on, check that you didn't pick 2003-05 on a 2001-02 car.

- **NA years** use rusEFI's own Miata presets (`setMazdaMiataNA6`, `setMazdaMiataNA94`, `setMazdaMiata96`), which
  include base fuel and ignition tables.
- **1989-93:** the stock harness has two injectors on each of its two injector wires (2U, 2V). The 1989-93
  motherboard (rev 0.6) wires INJ1 + INJ4 to 2U and INJ2 + INJ3 to 2V, and the preset assigns all four in batch
  mode. rusEFI fires each cylinder's output together with the cylinder 360° away (1 with 4, 3 with 2), so the two
  drivers on a wire switch together and each carries one injector. 2Y and 2Z (2Z is the A/T control unit on
  automatics) are not connected. For a sequential conversion, move the motherboard links (R23/R24 out, R25/R26 in)
  and set the injection mode to sequential.
  - **Needs the rev 0.6 1989-93 motherboard.** On an older 1989-93 motherboard INJ3/INJ4 go to the unused 2Y/2Z
    pins, so with this preset 2Z (the A/T control unit's pin on automatics) would be pulsed. On an older board set
    injection pins 3 and 4 to "none" until it is replaced.
  - The 47 V injector clamps (D3/D4, SMCJ40A) close the injectors a little more slowly than the drivers' own 65 V
    clamp would. Check the injector dead time on the car. At high rpm and duty they dissipate about 1 W each,
    which the SMC package handles.
- **1994-95:** four injector wires (2U/2V/2Y/2Z), sequential, as in rusEFI's own 1994 preset.
- **NB years:** rusEFI builds its NB presets for its Hellen boards only, so the engine facts are repeated here
  (displacement, trigger, injector flow, idle and alternator PID, VVT PID), and rusEFI's NB fuel, ignition and VVT
  target tables are loaded from a copy in `board/miata_nb_tune.cpp`.

### Base tune
Every year button loads a complete starting tune: the engine runs on it without opening a table. None of it has run
on this board, and the tables were made on other people's cars, so treat it as a first start, not a finished tune.

| Year button | Fuel (VE) table | Ignition table | Stock injectors set |
|---|---|---|---|
| 1989-93 | rusEFI's 1.6 table, from a running MAP-based 1.6 (2020) | rusEFI's NA Miata table, with timing pulled above 100 kPa | 212 cc/min |
| 1994-95 | the same 1.6 table (rusEFI uses it for the 1.8 too) | the same NA table | 254 cc/min |
| 1996-97 | the same 1.6 table | the same NA table | 265 cc/min |
| 1999-2000 | rusEFI's NB table, from a running 2001-05 car (2017) | rusEFI's NB table | 256 cc/min |
| 2001-05 | the same NB table, plus rusEFI's VVT target table | rusEFI's NB table | 265 cc/min |

- **What else is set:** cranking fuel, warm-up and idle-speed curves, closed-loop idle, a 7200 rpm limit, fan
  temperatures, the coolant and air-temperature sensor curves for the stock sensors, and a target mixture that goes
  richer as load rises (rusEFI's default: lambda 1.0 in cruise, 0.90 at 100 kPa, 0.80 at 175 kPa).
- **Closed-loop fuel is on.** Once the engine is warm, the ECU trims fuel towards the target using the on-board
  wideband. It may move idle and cruise fuel 10 % either way; under load it may add 10 % but remove only 5 %. With no
  sensor fitted there is no correction. It only applies to a fresh tune: switch "Short term fuel trim" off in
  TunerStudio and it stays off.
- **Where it is weakest:**
  - The 1994-97 years run a fuel table made on a 1.6. Expect the wideband to do more correcting there.
  - Above about 100 kPa (boost) the NB fuel table is a flat 80 %, and the NA table stops at 128 kPa. Nobody has
    tuned these tables under boost: a turbo car needs a tuner before it sees full throttle.
  - Bigger injectors need their flow and dead time entered in the injector settings.
- **Always:** check base timing with a timing light before the first drive (step 11 below).

### Same on every year
- **Outputs:** fuel pump, A/C relay, radiator fan, second fan (LS7), check engine lamp, tach, idle valve, INJ1-4,
  IGN1 (coil 1&4) and IGN2 (coil 2&3) in wasted spark.
- **COP conversion:** IGN3/IGN4 are assigned too (cylinder 2 on IGN3, cylinder 4 on IGN4), ready for coil-on-plug.
- **Inputs:** SW1 = vehicle speed, SW2 = A/C switch, SW3 = clutch.
- **Sensors:** TPS, MAP (on-board MPX5700AP), CLT and IAT, MAF/AFM on AUX3. External 0-5 V wideband on AFR, used
  only if the CAN wideband is switched off.
  - **1989-93 manual cars have no TPS**, only a throttle switch: the TPS input reads 0 V and rusEFI reports the sensor
    failed (open-loop idle, no TPS acceleration fuel, no overrun cut). For a sensor on the stock plug, fit R28 and move
    R29 to R30 on the 1989-93 motherboard (rev 0.11; see `motherboards/1989-93/README.md`), then calibrate closed and
    wide-open throttle in TunerStudio. No firmware setting changes: the sensor arrives on the usual TPS input.
- **Wideband:** the on-board unit, over CAN.

### Board facts the firmware pins (TunerStudio can't change them)
- **Low-side enable (PA8):** the injector, idle, VVT, boost and alternator drivers sit behind a 5 V level shifter
  whose enable is pulled up on the board, so they stay off through reset, boot, the bootloader and DFU. The firmware
  releases them a few slow ticks (about 200 ms) after start, once every output is configured, and never while a
  fatal error is active. It also takes them off while rusEFI re-applies its pins after a configuration change (every
  Burn) and enables them again as soon as that's done, so a Burn with the engine running drops the outputs only for
  the re-configuration itself, not until the next slow tick (up to 50 ms). The pin is driven open drain with inverted logic, so it is
  released (drivers off) from the moment it is set up, and the writes are forced so they also hold in hardware QC
  mode. It shows up as "Low-side enable" in the pin list.
- **No 32 kHz crystal; PC14 is the fuel pump.** PC14 is also the 32 kHz oscillator's input, and the oscillator takes
  the pin over whenever it's switched on. rusEFI's F4 default switches it on at every boot (and waits about a second
  for a crystal this board doesn't have), so `board/mcuconf.h` turns it off for the firmware and the bootloader, and
  the board start-up clears it again in case an older image left it on. The real-time clock runs from the internal
  32 kHz RC oscillator instead.
- **Unused low-side control pins** (for example ALT on the NA years) are parked as inputs with pull-down by the board
  code: at start-up, after every configuration change and on every slow tick. rusEFI's own "unused" state is a
  pull-up, which would switch that driver on.
- **Analog dividers:** analog inputs ×1.56 (5.6k/10k). Battery and ignition sense ×5.85 (33k/6.8k). The ignition
  sense channel itself is part of the year defaults (table above).
- **CLT/IAT pull-up:** 2.7 kΩ to 5 V, and the ADC divider loads the same node. Together they behave like a
  4.26 V supply behind 2.30 kΩ, and the firmware uses exactly that. Only pick the sensor curve in TunerStudio (stock
  or the M12 sensor, as set by JP1).
- **MAP:** MPX5700AP, 0.2 V at 0 kPa to 4.70 V at 700 kPa (custom linear MAP type). This is set with the year
  defaults, so you can change it if you fit another sensor.
- **CAN:** the STM32's CAN2 peripheral on PB12/PB13 is the only bus, set up as rusEFI's first CAN bus (rusEFI picks
  the peripheral from the pins). The wideband and everything else rusEFI sends by default use that bus. Earlier
  firmware had it as rusEFI's second bus, which made rusEFI's default CAN broadcast raise a critical error.

## Flashing the on-board wideband
The wideband MCU (STM32F103C8, daughterboard rev 0.6) is programmed by the main MCU. Do it once on a new board, and
again whenever the wideband firmware changes, with the engine off:
- **In TunerStudio:** Popular Vehicles → **Flash on-board wideband**;
- **or in the rusEFI console:** `wbo_uart_flash`. `wbo_uart_status` reports progress and the result.

It takes about 15 seconds. These steps run in a background thread, so TunerStudio stays connected:
1. raise the F103's BOOT0 (PD10; its BOOT1 is held low on the board) and pulse its reset (PD11), which starts ST's
   ROM bootloader;
2. talk to it over USART3 (PD8/PD9, 115200 8E1, ST application note AN3155);
3. check the chip ID (0x410, STM32F103x8/xB), mass-erase, write the image and read it all back;
4. drop BOOT0 and reset the F103 into the new firmware.

**The image** is `wideband/miata_wbo_f103.bin`: rusEFI's wideband controller firmware (the wideband submodule of
the pinned rusEFI) built for this board by `wideband/build.sh`. The board port `wideband/miata_f1/` is rusEFI's F1
port with this board's pins, an 8 MHz crystal (Y101) and the FOME module's analog constants; it measures battery
voltage itself, drives the LSU 4.2 / 4.9 / ADV ESR resistors, and has no bootloader and no TunerStudio serial port,
so it fits the F103C8 with room to spare (about 26 KB of 56 KB). CI rebuilds it and compares it with the committed
image. The mass erase also resets the wideband's own settings to their defaults (LSU 4.9, CAN index 0).

rusEFI's **Update wideband firmware** button (over CAN) carries the F042 module's image and does not apply to this
board; use **Flash on-board wideband** instead.

**Fallback:** if the flash fails, the J102 Tag-Connect SWD pads on the daughterboard still reach the F103: flash
`miata_wbo_f103.bin` at 0x08000000 with any ST-Link.

## Pin map
| Signal | MCU | Header | rusEFI setting |
|---|---|---|---|
| IGN1 / IGN2 / IGN3 / IGN4 | PE1 / PE0 / PB9 / PB8 | J1-14..17 | ignition pins 1 / 3 / 2 / 4 |
| INJ1 / INJ2 / INJ3 / INJ4 | PB7 / PB6 / PB5 / PB4 | J1-19, 22, 25, 28 | injection pins 1-4 |
| IACV / VVT / BOOST / ALT | PB3 / PD7 / PD6 / PD5 | J1-31, 34, 37, 40 | idle solenoid / VVT or O2 heater / boost / alternator |
| Low-side enable | PA8 | on board | fixed: open drain, low = the eight low sides above are enabled |
| FP / MAINRLY / AC / FAN | PC14 / PC13 / PE6 / PE5 | J1-6..9 | fuel pump / main relay (2003-05) / A/C relay / fan |
| CEL / TACH / LS7 | PE4 / PE3 / PE2 | J1-10..12 | check engine / tach / fan 2 |
| HALL1 / HALL2 | PE7 / PE8 | J2-13, 14 | crank / cam (see the year table) |
| SW1 / SW2 / SW3 | PE9 / PE10 / PE11 | J2-15..17 | VSS / A/C switch / clutch |
| VR1 / VR2 (spare) | PE13 / PE12 | J2-21, 20 | not assigned (LM2903 comparator outputs, for VR sensors) |
| TPS / MAP / CLT / IAT | PA4 / PA5 / PA6 / PA7 | J2-4..7 | ADC 4 / 5 / 6 / 7 |
| AFR / AUX1 / AUX2 / AUX3 | PC4 / PC5 / PB0 / PB1 | J2-8..11 | AFR / spare / spare / MAF |
| KNOCK | PA3 (ADC3) | J2-3 | software knock (on for NB) |
| VBATT / VIGN | PA1 / PA2 | on board (VIGN from J1-3) | battery / ignition key sense (1989-95, 2003-05) |
| CAN2 RX / TX | PB12 / PB13 | J2-27, 28 (bus) | CAN2 |
| LEDs run / comms / warning / error | PD12 / PC8 / PC9 / PD15 (rev 0.8; PD12-PD15 before) | on board | fixed |
| Wideband link TX / RX / BOOT0 / NRST | PD8 / PD9 / PD10 / PD11 | on board | fixed |

Which harness pin each signal reaches is in each motherboard's README.

## First start
Read this before the engine runs for the first time.
1. **Year button and ignition.** Press your year in Popular Vehicles (2001-02 and 2003-05 are separate). With the key
   on, crank briefly with the injectors unplugged and check that the injector and spark outputs are active (trigger and
   output logs). If they stay silent, rusEFI thinks the ignition is off: check you picked the right NB2 button.
2. **Tach wire (1989-95).** Our board drives the tach cavity 2I as an output, as rusEFI's Hellen NA6 does, but the
   rusEFI wiki lists it as an input. Check your car's wiring diagram before the first start: if 2I is fed by the
   igniter rather than the ECU, set the tachometer output to none in TunerStudio.
3. **Wideband first.** Power the board on the bench, flash the wideband and check `wbo_uart_status`. Then check that
   TunerStudio shows the wideband on CAN before you fit the sensor in the exhaust.
4. **Trigger.** Crank with the injectors unplugged and look at the trigger log. If rusEFI won't sync, the hall
   input may need the opposite polarity: try the trigger "invert" settings.
5. **Switch inputs** are 12 V inputs through a 22k/10k divider, with no pull-up. Check that your car's VSS, A/C
   and clutch signals actually drive the line high. A signal that only pulls to ground needs the motherboard's
   pull-up for that input fitted (R20-R22, 4.7k 0603, not fitted by default). Don't fit one on a line the car
   drives to 12 V.
6. **Battery voltage reads low.** VBATT is measured after the board's reverse diode and fuse, so it reads about
   0.3-0.4 V below the battery. Compare it with a voltmeter on the first start; it shifts the NB charging voltage
   by the same amount.
7. **NB alternator: control ships off.** On NB cars the engine computer sets the charging voltage. Harness pin 1O
   (1999-2000) or 3M (2001-05) is a logic-level PWM input to the regulator inside the alternator (about 5 mA), not
   the field coil, so the ALT driver can run it. Check the wire once per car type before switching it on
   (VERIFICATION.md M5):
   1. ECU unplugged, key on: measure 1O / 3M to ground at the harness plug.
   2. **About 5 V or 12 V:** the alternator pulls it up. Turn on "Alternator control" in TunerStudio.
   3. **Near 0 V:** fit a 1k resistor in series with a 1N4148 from AUX J5-14 (5 V, anode) to J5-4 (OUT_ALT) first,
      then turn it on.
   4. First run: watch battery voltage. If it climbs past about 15 V, switch it off and invert the output.
   The pin, the PID, 250 Hz (as the stock ECU) and the 14.0 V target are already set up. Until it's on the car may
   not charge, so watch the battery.
8. **Base tune:** every year starts from Miata fuel and ignition tables (see [Base tune](#base-tune)). Watch the
   wideband on the first drives, and have a turbo car tuned before full throttle.
9. **Hard acceleration and the check engine light:** rusEFI logs a trigger timing warning when a tooth lands >10°
   from where it predicted it. In simulation that happened at 1526 rpm/s and not at 763 rpm/s (free revving). The engine keeps running; the light
   blinks the code for a few seconds, then the board's warning expiry clears it.
10. **Outputs left alone:** the NA purge solenoid (1989-93), the pressure-regulator solenoid (1994-95) and the NB1
   VICS solenoid have no rusEFI function. They stay off unless you set them up as general-purpose PWM outputs.
11. **Base timing.** Before the first drive, lock the timing (Ignition hardware: Timing Mode = fixed, Fixed Timing
   = 10), check it with a timing light on cylinder 1, and correct "Trigger Angle Advance" in the Trigger settings
   until the light reads 10 degrees. Then set Timing Mode back to dynamic.

## Building
**Normal build (needs Java and an ARM GCC; it's what CI runs):**
```sh
git submodule update --init firmware/ext/rusefi
cd firmware/ext/rusefi && misc/git_scripts/common_submodule_init.sh && cd firmware
bash bin/compile.sh ../../../board/meta-info.env
```
The output lands in `firmware/ext/rusefi/firmware/deliver/`, and the TunerStudio `.ini` in `tunerstudio/generated/`.

**Offline compile check:** rusEFI generates its configuration code with Gradle. Where Gradle can't download,
`tools/offline_compile_check.sh <rusefi checkout>` builds the board against the generated files rusEFI commits for
`f407-discovery` instead. This proves the board code compiles and links, for the firmware and for the OpenBLT
bootloader (which compiles the board sources too). It does not produce a firmware to flash.

**Checking pins:** `python3 firmware/tools/check_pins.py` (CI runs it too).

**Simulation tests** (rusEFI's unit-test engine plus this board's tests; no Java needed):
```sh
cd firmware/ext/rusefi/unit_tests
BOARD_DIR=../../../board make -j8 -o .tooljars-sentinel -o .config-sentinel -o .docsenums-sentinel -o .ramdisk-sentinel
build/rusefi_test --gtest_filter='Miata*' | tee /tmp/miata_sim.txt
python3 ../../../tools/sim_report.py /tmp/miata_sim.txt
bash ../../../tools/flash_sim/run_flash_sim.sh .. /tmp/flash_sim
```
CI runs all of these. What they cover and found is in [VERIFICATION.md](../VERIFICATION.md).

**Updating rusEFI:** move the submodule to a newer commit (`cd firmware/ext/rusefi && git checkout <commit>`), run
the build, commit the new submodule pointer.

## Verification
See [VERIFICATION.md](../VERIFICATION.md): pinout audit, datasheet review, engine and circuit simulations, flashing
simulation and the safety review, with the hardware changes they call for.

## Licences
- **This folder** is MIT, like the rest of the repository, except `board/miata_nb_tune.cpp`: its tables are copied
  from rusEFI's `mazda_miata_vvt.cpp`, so that file is GPL-3.0. A few NB engine values in `miata_board.cpp` come
  from the same rusEFI file.
- **The firmware you build includes rusEFI**, which is GPL-3.0, so the built firmware is GPL-3.0.
- **The wideband image** is from [rusefi/wideband](https://github.com/rusefi/wideband) (MIT).
