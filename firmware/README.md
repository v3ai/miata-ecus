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
| `board/board_configuration.cpp` | Hooks the above into rusEFI and adds the hardware-only parts (LEDs, wideband flasher) |
| `board/tests/`, `board/board_unit_tests.mk` | Engine simulation of every year inside rusEFI's unit-test engine (see [Verification](#verification)) |
| `board/wideband_uart_flash.cpp` | Programs the wideband MCU over its ROM serial bootloader |
| `board/connectors/daughterboard.yaml` | Pin names TunerStudio shows (J1/J2 header signals) |
| `board/board_popular_vehicles.ini`, `board/board_commands.ini` | TunerStudio buttons: the five years and "Flash on-board wideband" |
| `board/prepend.txt`, `board/knock_config.h` | TunerStudio menu switches, knock input |
| `ext/rusefi` | rusEFI, as a git submodule pinned to the tested commit |
| `tools/check_pins.py` | Checks every pin here against the board design (`scripts/design.py`) |
| `tools/sim_report.py` | End-to-end check: firmware function → MCU pin → harness cavity, against independent pinouts |
| `tools/flash_sim/` | Wideband flasher run on a PC against a model of the F042's ROM bootloader |
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
| 1989-93 (NA6, 1.6) | `MAZDA_MIATA_NA6` | NA CAS: SGC on HALL2, SGT on HALL1 | batch, two drivers per wire | 1C | none (VVT driver = purge, not driven) |
| 1994-95 (NA8, 1.8) | `MAZDA_MIATA_NA94` | NA CAS | sequential | 1C | none (ALT driver = pressure regulator solenoid, not driven) |
| 1996-97 (NA8, OBD-II) | `MAZDA_MIATA_NA96` | NA CAS | sequential | none | O2 heater on the VVT driver |
| 1999-2000 (NB1) | `MAZDA_MIATA_NB1` | NB crank on HALL1, cam on HALL2 | sequential | none | O2 heater on VVT, alternator field on ALT (control off by default) |
| 2001-02 (NB2, VVT) | `MAZDA_MIATA_NB2` without main relay or ignition sense | NB crank + VVT cam | sequential | none | VVT valve, alternator field (control off by default) |
| 2003-05 (NB2, VVT) | `MAZDA_MIATA_NB2` | NB crank + VVT cam | sequential | 4S | VVT valve, alternator field (control off by default), main relay (3H) |

**Pick the right NB2 button.** 2001-02 and 2003-05 use the same motherboard but are wired differently. rusEFI cuts
fuel and spark while the ignition-sense input reads "off", so that input is only switched on for the years whose
harness carries the wire (1C, 4S). A car without the wire uses battery voltage instead, rusEFI's default. If an NB2
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
  (displacement, trigger, injector flow, idle and alternator PID, VVT PID). The VE, ignition and VVT target tables
  stay at rusEFI's generic defaults. Load a base map for your car before driving.

### Same on every year
- **Outputs:** fuel pump, A/C relay, radiator fan, second fan (LS7), check engine lamp, tach, idle valve, INJ1-4,
  IGN1 (coil 1&4) and IGN2 (coil 2&3) in wasted spark.
- **COP conversion:** IGN3/IGN4 are assigned too (cylinder 2 on IGN3, cylinder 4 on IGN4), ready for coil-on-plug.
- **Inputs:** SW1 = vehicle speed, SW2 = A/C switch, SW3 = clutch.
- **Sensors:** TPS, MAP (on-board MPX5700AP), CLT and IAT, MAF/AFM on AUX3. External 0-5 V wideband on AFR, used
  only if the CAN wideband is switched off.
- **Wideband:** the on-board unit, over CAN.

### Board facts the firmware pins (TunerStudio can't change them)
- **Low-side enable (PA8):** the injector, idle, VVT, boost and alternator drivers sit behind a 5 V level shifter
  whose enable is pulled up on the board, so they stay off through reset, boot, the bootloader and DFU. The firmware
  releases them a few slow ticks (about 200 ms) after start, once every output is configured, and never while a
  fatal error is active. It also takes them off for the whole of a configuration change (when rusEFI releases and
  re-starts its pins) and enables them again afterwards. The pin is driven open drain with inverted logic, so it is
  released (drivers off) from the moment it is set up, and the writes are forced so they also hold in hardware QC
  mode. It shows up as "Low-side enable" in the pin list.
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
- **CAN:** CAN2 on PB12/PB13 is the only bus. The wideband is set to "CAN2".

## Flashing the on-board wideband
The wideband MCU (STM32F042) is programmed by the main MCU. Do it once on a new board, with the engine off:
- **In TunerStudio:** Popular Vehicles → **Flash on-board wideband**;
- **or in the rusEFI console:** `wbo_uart_flash`. `wbo_uart_status` reports progress and the result.

It takes about 15 seconds. These steps run in a background thread, so TunerStudio stays connected:
1. raise the F042's BOOT0 (PD10) and pulse its reset (PD11), which starts ST's ROM bootloader;
2. talk to it over USART3 (PD8/PD9, 115200 8E1, ST application note AN3155);
3. check the chip ID, mass-erase, write the image and read it all back;
4. drop BOOT0 and reset the F042 into the new firmware.

**The image** is rusEFI's `wideband_image_with_bl.bin`, from the wideband submodule of the rusEFI being built (CAN
bootloader + FOME/rusEFI wideband firmware for the F042 module). Once it is on the chip, rusEFI's normal
**Update wideband firmware** (over CAN) works too.

**Fallback:** if the flash fails, the J102 Tag-Connect SWD pads on the daughterboard still reach the F042.

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
| VR1 / VR2 (spare) | PE13 / PE12 | J2-21, 20 | not assigned |
| TPS / MAP / CLT / IAT | PA4 / PA5 / PA6 / PA7 | J2-4..7 | ADC 4 / 5 / 6 / 7 |
| AFR / AUX1 / AUX2 / AUX3 | PC4 / PC5 / PB0 / PB1 | J2-8..11 | AFR / spare / spare / MAF |
| KNOCK | PA3 (ADC3) | J2-3 | software knock (on for NB) |
| VBATT / VIGN | PA1 / PA2 | on board (VIGN from J1-3) | battery / ignition key sense (1989-95, 2003-05) |
| CAN2 RX / TX | PB12 / PB13 | J2-27, 28 (bus) | CAN2 |
| LEDs run / comms / warning / error | PD12 / PD13 / PD14 / PD15 | on board | fixed |
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
5. **Switch inputs** are 12 V inputs through a 33k/10k divider, with no pull-up. Check that your car's VSS, A/C
   and clutch signals actually drive the line high. A signal that only pulls to ground needs the motherboard's
   pull-up for that input fitted (R20-R22, 4.7k 0603, not fitted by default). Don't fit one on a line the car
   drives to 12 V.
6. **Battery voltage reads low.** VBATT is measured after the board's reverse diode and fuse, so it reads about
   0.3-0.4 V below the battery. Compare it with a voltmeter on the first start; it shifts the NB charging voltage
   by the same amount.
7. **NB alternator: control ships off.** On NB cars the engine computer regulates the charging voltage through the
   alternator field (ALT output), but the field current hasn't been measured (VERIFICATION.md M5) and the driver is
   rated 1.4 A. Until it's switched on the car may not charge, so watch battery voltage. Measure the field current
   (or check the FSM); if it's within the driver's rating, turn on "Alternator control" in TunerStudio. The pin, PID
   and 14.0 V target are already set up.
8. **NB tables:** set VE, ignition and (NB2) the VVT target before driving. The defaults are generic.
9. **Hard acceleration and the check engine light:** rusEFI logs a trigger timing warning when a tooth lands >10°
   from where it predicted it. In simulation that happened at 1526 rpm/s and not at 763 rpm/s (free revving). The engine keeps running; the light
   blinks the code for a few seconds, then the board's warning expiry clears it.
10. **Outputs left alone:** the NA purge solenoid (1989-93), the pressure-regulator solenoid (1994-95) and the NB1
   VICS solenoid have no rusEFI function. They stay off unless you set them up as general-purpose PWM outputs.

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
`f407-discovery` instead. This proves the board code compiles and links. It does not produce a firmware to flash.

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
- **This folder** is MIT, like the rest of the repository. A few NB engine values are taken from rusEFI's
  `mazda_miata_vvt.cpp`.
- **The firmware you build includes rusEFI**, which is GPL-3.0, so the built firmware is GPL-3.0.
- **The wideband image** is from [rusefi/wideband](https://github.com/rusefi/wideband) (MIT).
