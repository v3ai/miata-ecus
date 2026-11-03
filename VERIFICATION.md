# Verification report

**Date:** 2026-10-30; full-firmware emulation, expanded circuit and board checks 2026-11-02; rev 0.7 and 0.8 fixes 2026-11-03.
**Boards:** daughterboard rev 0.8; motherboards 1989-93 and 1994-95 rev 0.8, 1996-97 / 1999-2000 / 2001-05 rev 0.6.
These revisions carry the fixes this review called for (see [Rev 0.5 changes](#rev-05-changes-and-re-verification),
[Rev 0.6](#rev-06-stm32f103-wideband-controller), [Rev 0.7](#rev-07-fixes-for-the-2026-11-02-findings) and
[Rev 0.8](#rev-08-driver-temperature-and-protected-outputs)).
The review itself was first run on daughterboard rev 0.4 and the previous motherboards.
**Firmware:** `firmware/` on rusEFI `1374bd07`.

Nothing here has been built yet, so this is a desk and simulation review. It covers:
- every pin and connection, checked against independent references;
- every chip checked against its datasheet;
- all five motherboard + daughterboard combinations, simulated with real engine signals running the board's own
  configuration code inside rusEFI's engine simulator (see [Limits of the simulation](#limits-of-the-simulation));
- flashing of both MCUs;
- a safety review.

## Summary
- **Wiring and pinouts: correct, with two cavities to check on a car.**
  - Every harness cavity on all five motherboards carries the function our references give it. Where the references
    disagree with each other (the 1989-95 tach cavity, see [Pinouts](#pinouts-findings)), check on a car.
  - The daughterboard stacks onto every motherboard pin-for-pin.
  - Every MCU peripheral sits on a pin that has that function.
  - The wideband MCU is wired exactly as the stock firmware expects.
- **Firmware: works in simulation for all five years**, with four fixes made during this review (see
  [Firmware](#firmware)). The most important: as first written, the engine would not have run at all on 1996-2002 cars
  (fuel and spark cut because an ignition-sense input that isn't wired read "key off"). Spark and fuel land at the right
  crank angles on the right harness pins, from cranking to the rev limiter.
- **Flashing: works in simulation.**
  - **Wideband MCU:** our flasher writes, verifies and boots the wideband firmware through a bootloader model that an
    independent tool (stm32flash) also drives successfully, and it handles every fault tried.
  - **Main MCU:** the image passes OpenBLT's checks.
- **Hardware: the four changes needed before building and the safety additions are made and re-checked.**
  - Daughterboard rev 0.5: 5 V drive for the low-side drivers, gated off until the firmware is running. Also: BOOT1
    pull-down, no relay back-feed, a fused and TVS-clamped logic supply, and clamped crank/cam inputs.
  - Motherboards: freewheel diodes on the valves, a fused AUX +12 V pin, and pull-up options for the switch inputs. The
    1989-93 board now uses two drivers per injector wire, with a clamp on each wire.
  - All boards were regenerated, routed and checked again; the simulations below cover every fix. The remaining open
    items are in [Open items](#open-items).
- **Full firmware, emulated (2026-11-02).** The real OpenBLT + rusEFI images run unmodified on an emulated STM32F407
  through every model year (boot, cranking on recorded captures, 6500 rpm, stall, key off): 0 failures, after fixing
  two firmware bugs that stopped rusEFI at boot (CAN on the wrong bus, two lambda inputs at once). The ECU flashes a
  blank emulated F103 through its ROM bootloader; the wideband then heats a modelled LSU 4.9 and rusEFI reads the
  lambda steps 1.00 / 0.85 / 1.20 over CAN. See
  [Full-firmware emulation](#full-firmware-emulation-expanded-circuit-and-board-checks-2026-11-02).
- **New hardware findings (2026-11-02), mostly fixed in rev 0.7:** the expanded circuit and fault checks found 13
  items (N1-N13), three of them high: the F103's supply order at power-up (VDDA ahead of VDD), unclamped analog inputs,
  and unprotected LSU signal wires (inherited from FOME). Rev 0.7 fixes N1, N2, N4, N5, N7 and N9 and most of N3 and
  N6. Still open: the LSU pump and virtual-ground wires shorted to battery (N3), a 24 V jump start while a crank, cam
  or temperature-sensor wire is shorted (N6), and the injector drivers' temperature at sustained high duty, which on
  the sequential years is worse than first reported (N8). See
  [Rev 0.7](#rev-07-fixes-for-the-2026-11-02-findings).
- **Rev 0.8 (2026-11-03): the rest of the hardware findings.** Larger daughterboard (125 × 76 mm) with DPAK injector
  drivers on drain copper and thermal vias (estimated 110 °C at 90 % duty and 85 °C ambient, was thermal shutdown),
  protected relay, lamp, tach and ignition outputs, a separate protected sensor 5 V for the harness, LSU drive clamps,
  a +3V3 shunt clamp and fault-tolerant CAN. Board fault checks: 4 FAILs left (from 215), all the LSU drive resistors
  taking a battery short so the ICs don't. See [Rev 0.8](#rev-08-driver-temperature-and-protected-outputs).
- **Review.** A second, independent pass checked this report against the sources. Its corrections are folded in below;
  it found the ignition-sense bug.

## How it was checked
| Check | Method | Result |
|---|---|---|
| Harness pinouts | Each motherboard's harness map compared cavity by cavity with rusEFI's Hellen NA6/NA96/NB1/NB2 boards (connector yaml and PCB nets), the rusEFI wiki 1990 and 1994 pinout tables, and `research/pinouts_9605.md` (2005 FSM) | All match |
| Header geometry | Our harness footprints compared pad-by-pad, by **position**, with the Hellen boards' footprints and nets (not just by name), so a mirrored or mislettered header would show up | All match |
| Daughter ↔ motherboard | All 80 J1/J2 pads of the daughterboard (headers on the bottom) against JD1/JD2 on each finished motherboard PCB: same position (pure translation, no mirroring) and same net | 5 × 80 OK |
| MCU pins | Power, VCAP, VDDA, BOOT0, crystal; alternate functions (USART3 PD8/PD9, CAN2 PB12/13, USB PA11/12, USART6 PC6/7, ADC channels, ADC3 on PA3) | OK (PB2 and PC13/14 fixed in rev 0.5) |
| Wideband MCU | Rev 0.6: STM32F103C8 pins (`scripts/wideband.py` U2_PADS) against our port of rusEFI's wideband firmware (`firmware/wideband/miata_f1`: ADC channels, heater/pump PWM timers and remap, LEDs, the three ESR drives, CAN, UART, ID straps, crystal, BOOT1) | Matches; floating ID straps give CAN index 0, as rusEFI expects |
| Datasheets | Every active part and sensor: supply, logic levels, current, thermal, pin functions (full notes: datasheet review, summarised below) | See findings |
| Engine simulation | `firmware/board/tests/test_miata_ecu.cpp`: the board's real configuration code inside rusEFI's unit-test engine, all five years (2001-02 and 2003-05 separately). Real NA CAS and NB2 crank+cam logic-analyser captures, plus running from cranking to 6500 rpm with realistic acceleration, then the rev limiter. Every output edge recorded and checked against crank angle | 18/18 tests pass (rev 0.5 pins) |
| End to end | `firmware/tools/sim_report.py`: for each year, the tune the firmware builds → STM32 pin → driver → J1/J2 → motherboard → harness cavity, compared with the cavity the references say carries that function. The expected cavities are a hand-written table of the functions the firmware drives or reads (not purge, pressure regulator, VICS or power pins). It follows the motherboards' fitted 0R links | 119/119 OK (6 configurations) |
| Circuits | `firmware/tools/circuit_sim.py` (ngspice), as built: hall inputs at 7200 rpm and shorted to battery, 12 V switch inputs with and without the pull-up option, CLT/IAT network −20…120 °C through the firmware's conversion, injector / idle / VVT turn-off, 1989-93 paired injectors with the TVS, relay-driver key-off back-feed, kick-back and a load dump on the relay feeds (each TVS at the bad end of its tolerance), logic supply under load dump, ISO pulse 2a, jump start and a sustained overvoltage, knock amplifier | 20 OK, 3 CHECK (switch inputs at 9 V cranking, knock clipping), 6 REF (rev 0.4 or no-fix references), 0 FAIL. Details in [Rev 0.5 changes](#rev-05-changes-and-re-verification) |
| Board layout | Every board regenerated from the design scripts, autorouted, schematic netlist compared pad by pad with the design, KiCad DRC | See [Rev 0.5 changes](#rev-05-changes-and-re-verification) |
| Wideband flashing | `firmware/tools/flash_sim/`: our `wideband_uart_flash.cpp`, unmodified, compiled for a PC against a model of the F103 ROM bootloader (AN3155, ID 0x410). The model was first validated with **stm32flash** (identified it as an STM32F10xxx medium-density part, wrote and verified the image with both erase variants) | 9/9 scenarios pass |
| Full firmware, emulated | `firmware/sim/run_ecu.py`: OpenBLT + rusEFI unmodified on an emulated STM32F407 (Renode), every model year, from boot through cranking on real captures to 6500 rpm, stall and key off. `run_system.py`: the ECU programs a blank emulated STM32F103 through its ROM bootloader, then both run together over CAN with an LSU 4.9 sensor model | 372 OK, 8 CHECK (default tune at 6500 rpm), 0 FAIL; two firmware bugs found and fixed. Two-chip run: see [Full-firmware emulation](#full-firmware-emulation-expanded-circuit-and-board-checks-2026-11-02) |
| Circuits, expanded | `firmware/tools/circuit_sim_full.py` (ngspice): every input and output stage, power-up order, ISO 16750-2 cranking, brown-out, key-off, shorts, the wideband front end and heater | Rev 0.6: 53 OK, 29 CHECK, 2 REF, 8 FAIL (findings N1-N13). Rev 0.7: 64 OK, 28 CHECK, 1 REF, 0 FAIL |
| Copper and faults | `firmware/tools/board_copper.py` / `board_checks.py`: netlist rebuilt from each routed board's copper and compared with the design; every harness cavity on every board shorted to ground, 14.4 V and 24 V | Copper = design on all six boards (0 opens, 0 shorts), rev 0.6 and rev 0.7. Faults: rev 0.6 1463 OK / 59 CHECK / 284 FAIL (feeding N2, N3, N6, N10); rev 0.7 1481 / 109 / 215 |
| Main-MCU image | `firmware/tools/check_image.py` on a fresh build: vector tables, OpenBLT's CRC-32 + size header (same algorithm as rusEFI's `FlashVerifyChecksum`), merged DFU layout, fit below the settings sectors | Pass; 77 KB spare |

## Pinouts: findings
Everything matched except these:
1. **1989-95 plug naming.** The NA ECU has plug 1 (22 pins) and a 26-pin plug.
   - The rusEFI 1990 page calls the 26-pin plug **3** (3A-3Z); the 1994 page calls it **2**.
   - Our boards say 2A-2Z.
   - The letters and functions are right, so this only matters when probing a harness with the 1990 page in hand.
2. **1994-95 is wired sequential:** four injector wires, 2U/2V/2Y/2Z. The motherboard docs said "batch"; corrected,
   and the firmware now runs 1994-95 sequential.
3. **1989-93 automatics: 3Z (our 2Z) is the A/T control unit.** On the rev 0.6 1989-93 motherboard, 2Y and 2Z
   are reached only through not-fitted links (R25/R26), so nothing drives them on a stock harness.
4. **1989-93 pin 1N.** We put the sensor 5 V on 1N (per the Hellen NA6 map).
   - The 1990 table shows 1N empty, and on 1994 cars 1N goes to the A/T unit; the 1994-95 board already leaves it open.
   - The 5 V supply is short-protected, so this is low risk. Check 1N on an automatic 1990-93 car before fitting.
5. **1994-95 air flow meter** is a vane AFM (the "MAF" label came from the rusEFI page's wording). Comment fixed; no
   wiring change.
6. **1989-95 tach cavity (our 2I; 3I on the 1990 page): input or output?** Both rusEFI wiki tables call it an input
   ("Tach Input", "tacho signal | Input"); the Hellen NA6 board drives it as an output, and so do we (2 pulses per
   revolution). If on your car this wire carries the igniter's tach signal, our ULN output would fight it. **Check 2I
   against the car's wiring diagram before driving.** If the igniter feeds it, set the tachometer output to none in
   TunerStudio.
7. **1989-93 1L and 1M:** the 1990 table lists these as unused; we put the fan relay and VSS there (per Hellen NA6). On
   a car without those wires nothing is connected, so this is harmless.

## Firmware
**What the simulation shows, every year:**
- RPM is within 2 % and full 720° phase sync is reached at 250, 900, 3000 and 6500 rpm.
- IGN1 (coil 1&4) and IGN2 (coil 2&3) fire twice per cycle, 180° apart, within 1.5° of TDC minus the commanded
  advance. IGN3/IGN4 stay idle.
- **1989-93:** INJ1/INJ2 open twice per cycle, 180° apart. INJ4 switches with INJ1 and INJ3 with INJ2, edge for
  edge (0 µs apart in the simulator), so each pair of drivers on one harness wire works as one.
- **Other years:** each injector opens once per cycle in 1-3-4-2 order, with pulse width equal to the computed
  duration.
- Fuel pump primes at key-on and stays on while running. Tach gives 2 pulses per revolution. The CEL lights at key-on.
- O2 heater on while running (1996-97, NB1). Alternator field PWM running (NB). Main relay held (2003-05).
- Ignition sense is configured exactly where the wire exists: 1C on 1989-95, 4S on 2003-05; nowhere else.
- Fuel is fully cut at 7600 rpm against the 7200 rpm limit (every year).
- On the real captures, NB1/NB2 read 875 rpm and 4.26° VVT, the same values rusEFI's own NB2 preset gets.

**Fixed during this review:**
- **No fuel or spark on 1996-97, 1999-2000 and 2001-02 (critical).**
  - The board configured rusEFI's ignition-sense input (PA2, VIGN_IN) on every year. That wire exists only on 1989-95
    (1C) and 2003-05 (4S). Elsewhere the input sits at 0 V, rusEFI decides the key is off, and it cuts fuel and spark
    (no CEL bulb check or fuel-pump prime either).
  - The first simulation didn't catch it, because rusEFI's unit-test build compiles that cut out (see
    [Limits](#limits-of-the-simulation)). The independent review found it in the code.
  - Now ignition sense is set only by the 1989-93, 1994-95 and 2003-05 presets. Other years use battery voltage, which
    is rusEFI's default.
  - 2001-02 and 2003-05 share a motherboard but not the wiring (2003-05 has an ECU-switched main relay and 4S; 2001-02
    has neither), so TunerStudio's Popular Vehicles now has separate **2001-02** and **2003-05** buttons. The tests
    check each year's setting directly.
- **1994-95 batch → sequential** (pinout finding 2).
- **1989-93 injector outputs:** first INJ3/INJ4 were unassigned (pinout finding 3). Now all four run in batch mode on
  the rev 0.6 motherboard's paired wiring.
- **Check engine light stuck on after every NB start.**
  - rusEFI only expires old warnings while TunerStudio, Lua or SD logging polls. NB cars always log "not firing until
    cam sync" during cranking, so with no laptop connected the CEL kept blinking after every start.
  - The simulation showed it still on after 16 s of idle; the board now expires warnings itself, and the CEL goes out.

**Behaviour to know about (rusEFI's own, not this board's):**
- **Hard acceleration.** At 1526 rpm/s and faster, rusEFI logs a trigger timing warning (the next tooth lands more
  than 10° from its prediction); at 763 rpm/s and slower it doesn't, on both NA and NB. The threshold is somewhere
  between. The engine keeps running; the warning lights the CEL until it expires.
- **Signal polarity.** An inverted NB crank/cam signal does not sync. Our hall inputs are non-inverting, so polarity
  should match the captures; if a car won't sync, try the invert settings.
- **Merge tool fills gaps with leftover data.** The tool that merges OpenBLT and the app into one DFU image fills
  address gaps with leftover buffer data instead of 0xFF. It only hits a few bytes of unused padding (8 in the CI
  build, just below 0x08008200), and each image's CRC covers its own fill, so it is harmless here; worth reporting upstream. (It also
  means the standalone and merged app images differ in those bytes, so CI compares them only where the firmware
  defines data.)

### Limits of the simulation
The engine tests run the board's own configuration code (`miata_board.cpp`) inside rusEFI's unit-test engine, not the
complete firmware as it runs on the STM32. That build differs from the real one in ways that matter:
- it compiles out the cut of fuel and spark when the ignition reads off (which is how the ignition-sense bug got
  through; the tests now check that setting directly);
- it doesn't start the analog sensors, so ADC readings and their conversions are checked separately
  (`circuit_sim.py`) rather than end to end;
- it defines the Hellen hardware flag, and doesn't run ChibiOS, the drivers or the boot sequence.

So the simulation shows the tune is right and the engine logic drives the right pins at the right angles. It does not
replace a bench test of the real board. The full-firmware emulation added on 2026-11-02 (see
[Full-firmware emulation](#full-firmware-emulation-expanded-circuit-and-board-checks-2026-11-02)) covers the parts this
build leaves out: boot, ChibiOS, the drivers, the ADC, CAN and the ignition-sense cut. It found two more firmware bugs.

## Wideband flashing (simulated)
- **Blank chip (both erase variants) and re-flash over old firmware:** all 31,744 bytes written and read back. The
  flasher leaves BOOT0 low and the chip boots its new firmware.
- **Faults:** no answer, read-protected, read-back mismatch, wrong chip ID and write refused each give a specific
  error and leave BOOT0 low.
- **Engine turning:** the flash is refused.
- **UART:** 115200 baud, 8 data bits + even parity, as AN3155 requires.
- **Duration:** about 59 kB cross the wire for the 26 KB F103 image (simulation: 31 kB out, 28 kB back), so expect roughly 6-8 s on the real 115200-baud link.
- **Failed flash:** a flash that fails after the erase leaves the F103 blank. It then stays in its bootloader, so
  re-run the flash or use the J102 SWD pads.

## Rev 0.5 changes and re-verification
Each change below was made in the design scripts. The boards were regenerated and re-routed, and each fix was
re-checked as listed. Refs are the new board's.

| # | Problem (rev 0.4) | Change | Re-check |
|---|---|---|---|
| H1 | AUIPS2041 inputs driven at 3.3 V (specified 4.0-5.5 V) | **Daughterboard:** SN74LVC4245A level shifter U11 (the part Hellen uses; LCSC C7859) drives Q1-Q8 at 5 V. Its output enable is pulled up (R71), so the eight drivers stay off through reset, boot, the bootloader and DFU. The firmware enables them on PA8 about 200 ms after start, once every output is configured, disables them for the whole of any configuration change, and never enables them during a fatal error. PA8 is driven open drain with inverted logic, so setting the pin up leaves the drivers off, and its writes are forced so they hold in hardware QC mode. R19-R26 hold the driver inputs low while the shifter is disabled. There was no room for MCU-side pull-downs, and rusEFI parks a released pin as input-with-pull-**up** (which would switch its driver on). So the board firmware parks every unused control pin with the MCU's pull-down: at start-up before enabling, after every configuration change, and on every slow tick | Driver input now about 5 V (circuit sim). Pin check passes with the enable pin; the production firmware compiles and links |
| H2 | No freewheel diodes on the idle and VVT valves: 3.4 W into the driver's clamp | **Motherboards:** SS34 D1 from the idle valve output to that valve's own +12 V feed: VBAT_IN, or IAC_12V through F2 on NB. D2 on the VVT output where it drives a coil: the purge solenoid on 1989-95, the VVT valve (OCV_12V through F3) on NB2. None on the alternator output (its field supply is unknown) or the O2 heater (resistive) | Idle valve at 200 Hz: **0 W** in the driver clamp (was 3.41 W); VVT valve at 300 Hz: 0 W |
| H3 | PB2 (BOOT1) floating: DFU entry unreliable | **Daughterboard:** R72 10 kΩ PB2 → GND | Netlist |
| H4 | 2003-05 key-off back-feed through the ULN2003 clamp diodes | **Daughterboard:** ULN2003 COM now goes to an SMAJ33A TVS (D11, 400 W, breakdown 36.7-40.6 V) instead of +12V. (A first draft used a 33 V zener; review found that a 35 V load dump on the battery-fed relay feeds would push current through it, and a failed-short zener would switch every relay on) | Key off: **0 mA** into the ECU (was 81 mA). Relay kick-back peaks at 42.6 V with the TVS at maximum breakdown (ULN limit 50 V). 35 V load dump on the relay feeds, TVS at minimum breakdown: **0 mA** into it |
| M1 | 1989-93: one driver carried two injectors (about 2 A, plus about 1 W of clamp energy at 7000 rpm) | **1989-93 motherboard:** two drivers per harness wire (R23: INJ1 + INJ4 on 2U; R24: INJ2 + INJ3 on 2V), plus an SMCJ40A clamp per wire (D3/D4, about 48 V, below the drivers' 63 V). **Firmware:** all four outputs in batch mode. rusEFI fires cylinder 1's output with cylinder 4's and 3's with 2's, so each pair switches together. 2Y/2Z (2Z = the A/T unit) only through not-fitted links R25/R26, for a sequential conversion | **0.99 A per driver** (was 1.96 A); **0 mW** in the drivers' clamps, 1.0 W in the SMC TVS at 7000 rpm, even with a 2 µs turn-off skew. Engine sim: the paired outputs switch edge for edge at 900-6500 rpm |
| M2 | Ignition-wake path unclamped; TVS clamp above the buck's 44 V maximum; C16 a 16 V part | **Daughterboard:** D7 and D8 now feed a 0.5 A PTC (F1; Hellen's power-module part), then an SMAJ33A (D12) on +12V. Its breakdown (36.7 V minimum) sits above the 35 V load-dump clamp, so the input TVS D6 takes that energy and D12 only catches fast spikes and the ignition-wake path. (A first draft used an SMAJ26A, which review found would conduct for the whole 400 ms load dump.) C16 is 10 µF / 50 V. D9 catch diode is a 60 V SS36 | +12V peaks with D12 at maximum breakdown: **34.2 V** (ISO 16750 suppressed load dump), **36.4 V** (ISO 7637 pulse 2a), 23.5 V (24 V jump start): all under the buck's 44 V. Energy into D12 at its minimum breakdown: **0 mJ** in all three. A sustained 39 V regulator failure puts 9 A through F1, which trips; below about 37 V nothing on +12V conducts |
| M3 | Fuel pump and main relay on the backup-domain pins PC14/PC13 | **No change, after checking the numbers.** ST limits these pins because their power switch can supply only 3 mA in total, and says not to drive LEDs from them. The two ULN2003 inputs draw at most about 0.72 mA each at 3.3 V ((3.3 V − 2 Vbe) / 2.7 kΩ), 1.45 mA together, and relays are DC, so the 2 MHz limit doesn't matter. (Moving them to PC0/PC1 was tried: the lines had to cross the crystal and the board would not route cleanly) | Calculation; end-to-end check (2T, 3H) |
| M4 | Switch inputs can't read ground-switching signals | **Motherboards:** R20-R22, 4.7 kΩ 0603 12 V pull-ups on VSS / A/C / clutch, **not fitted** by default (a switch that drives 12 V must not have one). Fit per car. (A first draft used 2.2 kΩ, 94 mW at 14.4 V against the 0603's 100 mW) | With a pull-up fitted, a ground-switching signal reads 3.02 V high / 0.04 V low at 14 V, 44 mW in the resistor. At 9 V (cranking) it reads 1.89 V, the same marginal case as a 12 V switch at 9 V |
| — | Crank/cam wire shorted to battery would destroy PE7/PE8 (no clamp on 5 V-tolerant pins) | **Daughterboard:** 1N4148WS from each hall input to +3V3 (D13/D14), after the 4.7 kΩ | Shorted to 14 V: pin at 3.9 V, 2.2 mA (was 14.4 V). At 24 V: 3.95 V, 4.3 mA. Normal signal still 0.28 / 3.81 V with 7.8 µs delay at 7200 rpm |
| — | AUX header J5-15 carried VBAT_IN off the board unfused | **Motherboards:** F4, 0.5 A PTC (Hellen's output-module part) | Netlist |
| — | Buck output capacitance about 20 µF (TI example 47 µF) | **Daughterboard:** third 10 µF (C59) | — |
| — | Buck inductor L2 (Sunlord MWSA0503S-100MT) saturates at 3.5 A, below the LMR14020's current limit (2.5 / 3.2 / 3.8 A min / typ / max) | **Daughterboard:** MWSA0603S-100MT (LCSC C132141): 10 µH, 5.5 A saturation, 4.5 A rated, 67 mΩ, 7 × 6.6 mm. Placed on end; D9 and the feedback divider moved 0.3 mm left to make room | No new courtyard overlaps; routes completely |
| — | Crystal load caps 22 pF for a 20 pF crystal | **Daughterboard:** C13/C14 33 pF C0G (C1663, basic part): C = 2 × (CL − about 4 pF of pin and stray capacitance), ST AN2867 | — |
| M5 | NB alternator control on by default with the field current unmeasured | **Firmware:** ships off; the pin, PID and target are set up, one switch in TunerStudio turns it on | Engine sim: field not driven on NB with the default tune |
| — | PB3/PB4 power-up states (SWO trace, JTAG pull-up) could pulse the idle valve or INJ4 | Covered by H1's output enable: nothing reaches the drivers until the firmware enables them | — |

**Layout:** each board's schematic netlist matches the design pad for pad, and each routes completely.
| Board | Netlist vs design | Routing | DRC errors | DRC warnings |
|---|---|---|---|---|
| Daughterboard rev 0.5 | 754 pads, 0 differences | complete | 0 (0 unconnected, 0 clearance) | silkscreen, library notes, 12 courtyard overlaps (all pre-existing) |
| 1989-93 rev 0.6 | 0 differences | complete | 4 hole-clearance items inside the USB-C footprint (as in every earlier release) | silkscreen, thermal spokes, library notes |
| 1994-95 rev 0.6 | 0 differences | complete | the same 4 USB-C items | as above |
| 1996-97 rev 0.4 | 0 differences | complete | the same 4 USB-C items | as above |
| 1999-2000 rev 0.4 | 0 differences | complete | the same 4 USB-C items | as above |
| 2001-05 rev 0.4 | 0 differences | complete (harness pin 3B tied to 3A on B.Cu: the bus lanes boxed it in) | the same 4 USB-C items | as above |

The level shifter sits on end with its MCU-side column facing the MCU, and the eight control lines into it are
pre-routed as a nested bundle, the same way the analog inputs are. The router fix this needed (its repair pass used
to drop nets that had already failed) is in `scripts/route.py`.

### Independent review of the fixes
A separate reviewer, who hadn't seen the work, checked the rev 0.5/0.6 changes. What it found and what was done:

| Finding | Done |
|---|---|
| D11 (first a 33 V zener) would conduct in a 35 V load dump on the relay feeds and could fail short | SMAJ33A TVS instead (H4) |
| D12 (first an SMAJ26A) would absorb the whole 400 ms load dump | SMAJ33A instead (M2) |
| Setting up the enable pin briefly enabled the shifter (OutputPin starts at logic 0, which was "enabled") | Inverted open drain: logic 0 now means released (off). Unused control pins are parked before the pin is set up |
| Hardware QC mode ignores normal writes | Enable writes are forced |
| During a configuration change rusEFI releases its pins with a pull-up for a moment, which could switch a driver on | The board's StopHardware hook disables the drivers first, and they stay off until the change has finished and the unused pins are parked again |
| R20-R22 at 2.2 kΩ were close to an 0603's rating | 4.7 kΩ (M4) |
| An older 1989-93 motherboard with the new firmware would pulse 2Z | Documented (1989-93 section, firmware README) |
| Reverse battery: new path through the driver body diode and D1/D2 | Quantified and documented (reverse battery, below) |
| VBATT reads about 0.3-0.4 V low (after D7 and F1) | Documented; the NB charging target is commented with it |
| The 1989-93 injector TVS slows injector closing; D3/D4 take about 1 W | Documented |
| rusEFI's default pin state pulls PA8 down until the firmware sets it up | No change: the MCU's pull-down (about 40 kΩ) against R71 (10 kΩ to 5 V) still leaves about 4 V on the enable (TTL input, 2 V threshold), so the drivers stay off. PA8 is 5 V tolerant |

**Sources for new parts:** SN74LVC4245A pinout and function table from the Nexperia 74LVC4245A datasheet (the TI part
has the same pinout); SN74LVC4245APWR (C7859), SMD1206P050TF/24 (C209741), 1N4148WS (C2128), SS34 (C8678) and
B5819W from rusEFI's Hellen BOMs; SMAJ33A (Bourns, C3720609), SMCJ40A (C224052), SS36 (C7428237, SMA) and the 0805 0 Ω
links (C17477) from LCSC listings. Check LCSC stock before ordering.

## Rev 0.5b: parts JLCPCB can actually assemble
JLCPCB's BOM check for the rev 0.5 daughterboard flagged ten lines short of stock and one footprint mismatch. Every
replacement below is in stock at JLCPCB (stock read from JLCPCB's parts library on 2026-10-31), fits the same
footprint. Replacing U9 added parts, so the board was re-routed (rev 0.5b).

| Ref | Was (out of stock) | Now | Why it's equivalent |
|---|---|---|---|
| Q1-Q8 | Infineon AUIPS2041LTR (C113610), also out at LCSC | **onsemi NCV8406ASTT3G (C459816)** | Same SOT-223 pinout (1 gate/input, 2 and tab drain, 3 source). Self-protected low side with current limit, thermal shutdown and a 60-70 V active clamp (AUIPS2041: 63-75 V), AEC-Q101. 210 mΩ at 5 V. Circuit sims rerun with its 60 V minimum clamp: the 1989-93 SMCJ40A still takes all the injector turn-off energy (0 mW in the drivers) |
| D11, D12 | Bourns SMAJ33A (C3720609) | Littelfuse SMAJ33A (C223988) | Same part number and ratings (36.7-40.6 V breakdown, 400 W) |
| F1 | SMD1206P050TF/24 (C209741) | TECHFUSE nSMD050-33V (C70077) | Same 1206, 0.5 A hold, 1 A trip, 100 A; rated 33 V instead of 24 V |
| L1 | Taiyo Yuden LBC3225T2R2MR (C223413) | FH CMI322513U2R2KT (C70960) | 2.2 µH 1210; 500 mA, 0.3 Ω. The buck draws about 0.15 A at 12 V |
| D1, D5 / D2 / D3 | Everlight 19-217 green / blue, 19-213 yellow | Hubei KENTO KT-0603G (C12624) / KT-0603B (C2288) / KT-0603Y (C2287) | Same 0603 status LEDs; the wideband already used the KENTO green and blue |
| C103 | FH 0402B333K100NT (C285077) | YAGEO CC0402KRX7R9BB333 (C106862) | 33 nF X7R 0402, rated 50 V instead of 10 V |
| R110 | 61.9 Ω 0603 1 % (C23092) | 62 Ω 0603 1 % (C23222) | Wideband pump-current sense resistor: 0.16 % higher, inside the 1 % tolerance |
| U9 | MAX9926UAEE+ (C1523548), also out at LCSC | **TI LM2903DR (C7549)**, plus D15-D18 BAT54SLT1G (C19726), R73-R80, C60 | The VR inputs are spares (no Miata year uses a VR sensor), but a single-source part was the wrong choice for them. The LM2903 is made by TI, onsemi (C57474), UMW (C668214), ST and others. See "VR input conditioner" below |
| F4 (all motherboards) | SMD1206P050TF/24 (C209741): out of stock at JLCPCB, delisted at LCSC | TECHFUSE nSMD050-33V (C70077) | The daughterboard's F1 part: same 1206, 0.5 A hold, 1 A trip, 33 V rating instead of 24 V |
| D6 | Brightking SMCJ30A (C310046), in stock but thin (about 3,000) | Littelfuse SMCJ30A (C224048) | Same part number and ratings, from a maker stocked at JLCPCB (18k) and at US distributors |
| D9 | "NH" SS36 (C7428237), unknown brand, no US distribution | Diodes Inc B360A-13-F (C94193) | Same SMA package, 60 V 3 A, 0.7 V at 3 A; JLC 128k, Mouser 150k |

The last three came from a review of every part's availability at JLCPCB and US distributors (October 2026). The
parts it flagged that need a design change rather than a swap (the MPX5700AP MAP sensor, now NRND at ST, and the
legacy TE harness headers) are listed under Open items.

Also fixed:
- **U105 footprint:** the AD8628ARTZ is the 5-lead SOT-23 package, and the board called its footprint TSOT-23-5
  (from the FOME module). KiCad's SOT-23-5 and TSOT-23-5 footprints have identical pads, so only the name changed.
  JLCPCB no longer reports a mismatch.
- **SW1/SW2** (same button) are one BOM line, so JLCPCB no longer warns that two lines match the same part.
- **Placement files (all boards).** The CPLs were written relative to the board's corner with KiCad's rotations, so
  JLCPCB's preview showed parts offset and several packages turned. They now use the gerbers' own coordinates (KiCad
  X, KiCad Y negated, no offset), and rotations get JLC's per-package corrections, read off JLC's placement preview
  of the rev 0.5 daughterboard: SOT-223, TO-252 and SOT-23 (3, 5 and 6 pin) +180°; SOIC, TSSOP and LQFP +270°;
  the 4-resistor arrays +90°; chip parts, SMA/SMC/SOD diodes, LEDs and the crystal unchanged (`scripts/order_bom.py`).
  The SOT-23-6 and USB4105 entries on the motherboards were not in that preview: check them in JLC's viewer.

### VR input conditioner (rev 0.5b)
Per channel: the harness legs go through 2 × 5.1k to the LM2903's inputs with 1 nF across them, as before. Each input
has a BAT54S to GND and +5V (holding it at -0.3 to 5.3 V; the LM2903's inputs take -0.3 to 36 V at any supply), and
100k to a 1.65 V bias (R79/R80 from +3V3, C60). 1M from the open-collector output back to IN+ gives about 30 mV of
hysteresis. Output polarity is the MAX9926's (high while harness − is above +), into PE13/PE12 with the existing 10k
pull-ups to +3V3, so the J2 wiring and firmware are unchanged.

`firmware/tools/circuit_sim.py` section H drives it with a 600 Ω / 100 mH sensor on a 36-1 wheel: 0.1 V peak at
150 rpm cranking (also with 40 mV of 47 kHz noise), 2 V at idle and 80 V at 7000 rpm all give one clean edge per
tooth, with one input always inside the common-mode range (0 to VCC − 2 V). With the sensor's − leg grounded at the
engine, the 80 V case still gives clean edges but both inputs briefly leave that range (CHECK): wire VR sensors with
both legs to the ECU.

Re-checked after the re-route: schematic netlist 778 pads, 0 differences; DRC 0 unconnected, 0 clearance (the
autorouter left HALL1 open and one AN_AUX3 track 0.05 mm from the new clamps; `scripts/daughter_patch.py` routes
HALL1 and moves that track, and the release is built from its output); circuit sims 25 OK / 4 CHECK / 6 REF / 0 FAIL.

## Rev 0.6: STM32F103 wideband controller
The wideband MCU (U102) is now an **STM32F103C8T6** instead of the STM32F042K6T6. rusEFI's developers have reported
F042 shortages for years ("the availability problem is with the f042 die"), and on 2026-11-01 JLCPCB had 167 and
LCSC about 70, against 200,215 F103C8T6 at JLCPCB. rusEFI's own newer wideband boards moved to the F103 for the same
reason.

**Hardware.** The FOME/rusEFI module's analog front end is unchanged. Only the MCU and its support parts changed:
- U102 LQFP-48, in the F042's spot. Its courtyard is the same 10.3 mm square.
- Pins were chosen so each group faces its parts (`scripts/wideband.py`, `U2_PADS`): ESR drives and LEDs left;
  heater PWM, battery sense, pump PWM and BOOT1 right; CAN, the programming UART and SWDIO up; analog inputs down.
- **Y101 8 MHz crystal** with 33 pF loads (C119/C120): the main MCU's part (C115962, JLC Basic). rusEFI's F1 boards
  run CAN from the internal oscillator, which drifts a few percent over temperature, more than CAN bit timing allows.
- **R135** holds BOOT1 (PB2) low, so BOOT0 high selects ST's ROM bootloader.
- **C121** decouples the third VDD pin.
- VDDA (REF3033, 3.300 V) against VDD (AMS1117, up to about 3.365 V): ST allows up to 300 mV between them during
  power-up and operation (STM32F103x8 datasheet, general operating conditions). This clears the F042 note that
  VDDA could sit below VDD.

**Firmware** (`firmware/wideband`): rusEFI's wideband controller sources (the pinned rusEFI's wideband submodule) with
our board port `miata_f1`. The port is rusEFI's F1 port with these changes:
- this board's pins;
- HSE 8 MHz × 6 = 48 MHz, so the bus clocks and CAN timing are the same as rusEFI's F1 boards;
- the FOME module's analog constants (Nernst gain 2.7, 10 Ω Vm resistor, Vm measured);
- the board's own battery sense (100k/10k), which the heater control now uses;
- the three ESR drive resistors (6.8k / 22k / 47k for LSU 4.2 / 4.9 / ADV);
- heater PWM on TIM2_CH3 with TIM2's partial remap, and the system tick on TIM4;
- settings in the last 8 KB of the 64 KB flash;
- no bootloader and no TunerStudio serial port.

Build result: 26,348 bytes of a 56 KB app area, and 6.8 KB of static RAM out of 20 KB. CI rebuilds it from source
and compares it with the committed image.

**Checks:**

| Check | Result |
|---|---|
| Pin map: `wideband.py` U2_PADS against `miata_f1/board.h` and `io/io_pins.h` (ADC channels 0/2/3/8, TIM3_CH1 on PA6, TIM2_CH3 remapped to PB10, CAN on PA11/12, USART1 on PA9/10, ESR on PB5/6/7, LEDs on PB8/9) | Match |
| Wideband firmware build (GCC 13.2), image check (fits flash and RAM, vector table) | Pass |
| Main firmware build with the new image and flasher (offline compile) | Compiles and links; carries the 26,348-byte image |
| Flasher against the AN3155 model, now an F103 medium-density bootloader (ID 0x410, 64 KB, erase 0x43 by default) | 9/9 scenarios pass |
| The model against **stm32flash** | Identified as "STM32F10xxx Medium-density"; wrote and verified the image with both erase commands |
| Schematic netlist against the design | 795 pads, 0 differences |
| DRC after re-route and `daughter_patch.py` | 0 unconnected, 0 clearance |

**Not verified on silicon:** the wideband firmware has not run on a real F103 yet. It has run unmodified on an
emulated F103 (see [Full-firmware emulation](#full-firmware-emulation-expanded-circuit-and-board-checks-2026-11-02)):
flashed by the ECU, started, heated a modelled LSU 4.9 and reported lambda over CAN. The analog scaling and control
loops are rusEFI's, unchanged; the clocks, pin setup and timer remap are ours. rusEFI's "Update wideband firmware" over CAN
carries the F042 module's image and does not apply. If pressed, the wideband acknowledges and resets, but with no
CAN bootloader on the F103 it just restarts its own firmware, and rusEFI's update times out without writing
anything. Use "Flash on-board wideband".

## Full-firmware emulation, expanded circuit and board checks (2026-11-02)
Three further checks, run on the rev 0.6 boards and the current firmware:
1. **Firmware-in-the-loop** (`firmware/sim/`): the real OpenBLT + rusEFI images and the wideband image run unmodified
   on emulated STM32F407 and STM32F103 chips (Renode 1.15.3), with the car, the board's input stage, the LSU sensor and
   the link between the two chips modelled.
2. **Expanded circuit simulation** (`firmware/tools/circuit_sim_full.py`, ngspice): every input and output stage,
   the power path through cranking and brown-outs, power-up order, faults and the wideband front end.
3. **Board-level checks** (`firmware/tools/board_checks.py`, `board_copper.py`): the copper of every routed board read
   back into a netlist, and every harness cavity shorted to ground, battery and 24 V on every board.

This is instruction-level emulation, not cycle-accurate: each instruction takes one clock, with no pipeline, flash
wait states or bus contention. Timers, ADC conversions, serial bytes and CAN frames run in virtual time at the real
clock rates, so firmware timing (pulse widths, dwell, spark angle, timeouts) is accurate to a few microseconds.

### Firmware-in-the-loop: ECU, every model year
`firmware/sim/run_ecu.py`. For each year the ECU runs through:
- boot through OpenBLT;
- key on, with sensor voltages through the board's input dividers;
- cranking on a **real recorded cranking capture** (rusEFI's NA and NB2 logic-analyser captures);
- idle at 900 rpm, cruise at 3000 rpm and 6500 rpm at full load;
- a stall and key off.

The output pins are recorded at every edge, and rusEFI's own state is read from emulated RAM 20 times a second.

| Year | Checks | Result |
|---|---|---|
| 1989-93 | 60 | 56 OK, 4 CHECK, 0 FAIL |
| 1994-95 | 61 | 57 OK, 4 CHECK, 0 FAIL |
| 1996-97 | 64 | 64 OK, 0 FAIL |
| 1999-2000 | 64 | 64 OK, 0 FAIL |
| 2001-02 | 64 | 64 OK, 0 FAIL |
| 2003-05 | 67 | 67 OK, 0 FAIL |

Passing, every year:
- the year preset is applied, with no critical or configuration error;
- battery, coolant, air temperature, MAP (barometric at key on) and key-sense readings match what was applied;
- the fuel pump primes at key on and stops after a stall;
- the engine syncs on the recorded capture;
- injectors: pulses per cycle and pulse width (within 0.18 ms of what the firmware commanded); firing order 1-3-4-2
  on the sequential years (1989-93 runs batch, two pulses per cycle);
- coils: 4.00 ms dwell, 180° between IGN1 and IGN2 at idle, cruise and 6500 rpm;
- injection and spark stop when the engine stops;
- 2003-05: the main relay is held at key on and released 1.03 s after key off.

CHECK, 1989-93 and 1994-95 only: at 6500 rpm and full load, rusEFI's default fuel table asks for more than 95 % of the
time between injections:
- 1989-93: 9.8 ms against a 9.2 ms window, because batch mode fires twice per cycle;
- 1994-95: 17.6 ms against 18.5 ms.

This is the default tune, not the board. Set the fuel table from the car's injector data before running at high load.

**Two firmware bugs found and fixed.** Both stopped rusEFI with a critical error at boot, which disables injection and
spark. Neither appears in rusEFI's unit-test build, which doesn't start the CAN or sensor drivers:
- **CAN on the wrong bus.** The board put the CAN transceiver (PB12/PB13, the STM32's CAN2 pins) on rusEFI's second
  bus. rusEFI's default CAN broadcast goes to the first bus, which had no pins, and raised "CAN1 device not
  configured". The transceiver is now rusEFI's first bus; rusEFI picks the CAN2 peripheral from the pins.
- **Two lambda inputs at once.** The board set both the analog AFR input (PC4) and the CAN wideband. rusEFI refuses
  that ("Please pick either analog AFR or CAN AFR input not both"). The on-board wideband over CAN is now the default.
  For an external 0-5 V wideband, set the AFR input to PC4 in TunerStudio and turn the CAN wideband off.

The unit tests, pin check and end-to-end harness check were rerun with both fixes: 18/18, pins OK, 119/119.

### Firmware-in-the-loop: ECU + wideband together
`firmware/sim/run_system.py` runs both chips as a new board starts life, with the F103 blank:
1. the ECU boots and the key goes on;
2. the ECU's wideband flasher (the TunerStudio button) takes the F103 into ST's ROM bootloader through BOOT0/NRST,
   erases it, writes and verifies the wideband image over USART3 and restarts it;
3. the engine runs, rusEFI allows the wideband to heat the sensor, and the wideband reports lambda over CAN;
4. the exhaust lambda in the sensor model steps from 1.00 to 0.85 to 1.20.

| Check | Result |
|---|---|
| ECU boots and stays free of critical errors with the wideband connected | OK |
| Flashing a blank F103 (status sequence starting → writing → verifying → done) | Done 3.6 s after the flash was started; the 26,348-byte image written and read back |
| F103 flash after flashing, against the image the ECU carries | CRC-32 b9c29a35 = b9c29a35 |
| F103 starts its new firmware and transmits | Standard (0x190) and diagnostic (0x191) frames at 100 Hz |
| CAN bit timing, read from both controllers | ECU 500 kbit/s, sample point 85.7 %; wideband 500 kbit/s, 87.5 % |
| Before the engine runs | Wideband reports "heating not allowed", then holds the preheat (about 2 % duty, condensation protection) |
| Heating once the engine runs | rusEFI allows heating; the wideband ramps the heater and reaches closed loop 12.5 s after engine start |
| Sensor in closed loop | 774 °C, ESR 330 Ω against the 300 Ω target; the wideband's own ESR reading tracks the sensor model's |
| Pump loop and lambda (rusEFI's reading: mean over each step's last second, and its range) | λ 1.00: pump −0.04 mA; rusEFI **1.007** (0.991-1.034). λ 0.85: pump −0.615 mA (Bosch table −0.652); rusEFI **0.849** (0.836-0.867). λ 1.20: pump 0.364 mA (Bosch 0.358); rusEFI **1.197** (1.156-1.234) |
| Overall | **0 FAIL** |

The ripple of a few percent comes from the pump loop working against the sensor model's cavity dynamics. A real
sensor's dynamics will differ, so treat the ripple as indicative only; rusEFI smooths the reading it uses.

Along the way this run caught gaps in the emulator and in the sensor model, all fixed in the models, not the firmware:
- Renode froze two machines that ran on separate threads.
- The wideband's system timer stopped at its first 16-bit wrap (Renode timer gaps, below).
- The first LSU model had no cavity dynamics: against the firmware's pump loop (kP 50) it oscillated rail to rail,
  which also corrupted the ESR reading. The LSU 4.9 measuring cavity is now an integrator with a 20 ms response, and
  the pump-current table is Bosch's.

Wall time is about 28 minutes for 40 s of virtual time.

### Renode gaps
Renode lacks parts of both chips, and several of its models behave differently from silicon in ways that stopped the
unmodified firmware. Each was modelled or worked around, and is listed in `firmware/sim/README.md`. The main ones:
- the NVIC never sets RETTOBASE, so ChibiOS never switched to a thread woken by an interrupt;
- the STM32F4 timers all ran at 10 MHz;
- there was no cycle counter, no STM32F4 ADC, and the DMA had no circular mode;
- the F103 had no clocks, flash controller, ADC, timers or CAN;
- the UART drops the 9-bit word-length bit that the ROM bootloader's 8E1 frame needs;
- there is no ST ROM bootloader. Ours models AN3155, including byte times, erase and programming times;
- a timer compare value of 0 never matches, and the counter wraps one count early. Together they stopped ChibiOS's
  system timer on the F103 at its first 16-bit wrap, 32.8 s after boot;
- the CAN model hides its bit-timing register outside init mode;
- two machines on separate host threads froze at random points. They now share one thread.

### Expanded circuit simulation
53 OK / 29 CHECK / 2 REF / 8 FAIL. The FAILs and the main CHECKs are hardware findings, listed in
[New hardware findings](#new-hardware-findings-2026-11-02). Things that pass:
- every sensor through its divider, filter and the firmware's conversion;
- crank and cam inputs at 150 and 7200 rpm, including during a crank dip;
- VSS at 200 km/h;
- the knock band;
- the wideband pump-current source over λ 0.65 to air (firmware lambda within 1.6 %);
- the virtual ground and Nernst sense;
- the heater driver's peak current and dissipation;
- the 24 V jump start on the switch inputs.

### Board-level checks
- **Copper = design, every board.** The netlist rebuilt from each routed board's copper geometry (tracks, vias, zones,
  pads; 4 layers on the daughterboard, 2 on the motherboards) matches the design scripts' netlist: 0 opens, 0 shorts.
- **Stacking:** all 80 J1/J2 pads land on JD1/JD2 on every motherboard, same net.
- **Every cavity, every year:** each harness pin traced to its MCU pin, driver or supply. Each MCU pin's electrical
  type was checked: FT or not, analog mode, the F103's IO pins.
- **Faults:** every harness cavity shorted to ground, 14.4 V and 24 V, on every board. 1463 OK / 59 CHECK / 284 FAIL.
  The FAILs are a short list of failure modes repeated across cavities and years. They are listed with the circuit
  findings below.

### New hardware findings (2026-11-02)
From the expanded circuit simulation and the board-level fault checks, as found on the rev 0.6 boards. What rev 0.7
changed for each, and what remains, is in [Rev 0.7](#rev-07-fixes-for-the-2026-11-02-findings).

| # | Severity | Finding | Proposed fix |
|---|---|---|---|
| N1 | High | **F103 supply order.** The wideband MCU's VDDA comes from the REF3033 (about 50 mV dropout) and its VDD from the AMS1117 (about 1 V dropout), both off +5V. While +5V rises from about 1.3 V to 4.3 V, at power-up, at every key-off and in a crank dip, VDDA sits up to 0.95 V above VDD for 1.5-4.6 ms. ST allows 300 mV. Repeated, this can latch up or degrade the F103 | Replace U4 (AMS1117-3.3) with a low-dropout regulator in the same SOT-223 footprint: simulated, the lead drops to about 200 mV. This also clears the AMS1117's 0 °C minimum rating (Minor list) |
| N2 | High | **Analog inputs unclamped.** A sensor wire (TPS, CLT, IAT, O2/AUX1-3, AFR) shorted to battery puts 9.2 V on its F407 pin; 15.4 V in a 24 V jump start. The pins are 5 V tolerant only as digital inputs; in analog mode the limit is about 3.6 V, and 7.3 V absolute. The hall inputs got clamps in rev 0.5; these didn't | A dual diode to +3V3 (BAT54S) or a 1N4148WS at each of the eight AN_ nodes, after the existing series resistor: about 1.9 mA into the clamp at 14.4 V, none into the MCU |
| N3 | High (inherited from FOME) | **LSU wires unprotected.** A cracked sensor or chafed harness that shorts an LSU signal wire to the heater's 12 V: LSU_VM puts about 2 A into F103 PA1/PA3 and the MCP6004 through R109 (10 Ω); LSU_UN goes straight to an MCP6004 input; LSU_IP and LSU_RT burn R110/R108. The wideband would be destroyed | Series resistance into F103 PA1 (LSU_VM is not sampled by the firmware: 10k, or no connection) and clamps to +3V3 on the sense nodes. The pump and Nernst paths can't take much series resistance without changing the analog design, so this needs care |
| N4 | Medium | **F407 brown-out window.** rusEFI sets BOR level 1 (about 2.1 V). In an ISO 16750-2 level II crank pulse with a worst-case AMS1117, or in a slow brown-out, the F407 runs for up to 93 ms with VDD between 2.1 and 2.7 V, below what its 5-wait-state flash setting at 168 MHz is specified for | Either set BOR level 3 (2.7 V) from the board code, so the ECU resets cleanly instead of running out of spec (a worst-case deep crank would then reset it), or the U4 change in N1, which keeps +3V3 above 2.7 V in a level II pulse |
| N5 | Medium | **Wideband heater warm-up vs the motherboard's F1 (2 A hold PTC).** At the start of the firmware's warm-up ramp, a cold heater draws 1.6-2.3 A rms (2.5-4 Ω cold resistance). The PTC's hold current derates to about 1.6 A at 60 °C, so it may trip during warm-up, and the controller then times out | A 3 A hold PTC in F1's footprint, or start the warm-up ramp lower in our wideband port (firmware only). Measure a real sensor's cold heater resistance either way |
| N6 | Medium | **Input resistors under-rated for shorts to battery.** Crank/cam: R62/R64 (1 kΩ 0603) take 88 mW at 14.4 V (62 mW rating) and 279 mW at 24 V; R61/R63 (4.7k pull-ups) 85 mW at 24 V. Analog inputs at 24 V: R27, R33, R36 66-134 mW | 0805 or 1206 parts in those positions (same values), or larger series values |
| N7 | Medium | **Knock input:** a knock wire shorted to battery couples a 14 V step through C44 into the LMV321's input diodes (about 1.2 A peak) | 1-10 kΩ in series with C44 |
| N8 | Medium | **Injector drivers at sustained high duty:** on 1989-93 each NCV8406A at 90 % duty reaches about 142 °C junction at 60 °C ambient and thermal shutdown at 85 °C ambient (about 20 mm² of tab copper). *Corrected in rev 0.7: the sequential years are worse, because each driver also absorbs its injector's turn-off energy (see Rev 0.7)* | More copper on the tabs (pour on both layers with vias), or convert to sequential |
| N9 | Low | **Switch inputs in a 35 V load dump** (battery-fed switch closed): 8.1 V on the FT pin, against 7.3 V abs max | 1N4148WS to +3V3, as on the hall inputs |
| N10 | Low | **AUX header J5:** UART TX/RX (PC6/PC7) and the AFR input (PC4) have no protection | Series resistors and clamps if the header is used with car wiring; fine for bench use |
| N11 | Low | **1989-93 2L** (manual-transmission idle switch, ground-switching) has no pull-up, so it can't be read. **1994-95 2L** (electrical-load signal), if it switches to battery, over-drives PC5 | Firmware reads TPS instead; fit a pull-up only if needed. Check the 1994-95 signal level on a car before wiring it |
| N12 | Low (inherited from FOME) | **ESR reads 27 % low** (C102 droops within each ESR half period), so the sensor runs at about 740 °C instead of 780 °C | A firmware calibration in our wideband port, or leave it as FOME and rusEFI do |
| N13 | Low | **+5V at 3.9 V in a level II crank pulse:** the TC4427 and the SN74LVC4245A port A are rated from 4.5 V. Both still switch, with less drive | None needed; noted |

## Rev 0.7: fixes for the 2026-11-02 findings
**Boards:** daughterboard rev 0.7; motherboards 1989-93 and 1994-95 rev 0.7, 1996-97 / 1999-2000 / 2001-05 rev 0.5
(the motherboards change only F1). Existing designators are unchanged; new parts have new numbers. Everything below
was simulated again on the rev 0.7 design and its routed board: `circuit_sim_full.py` **64 OK / 28 CHECK / 1 REF /
0 FAIL** (rev 0.6: 53 / 29 / 2 / 8), and the copper and fault checks.

| # | Status | Change | Re-check on rev 0.7 |
|---|---|---|---|
| N1 | **Fixed** | **U4: ST LDL1117S33R** (C435835, same SOT-223 pinout, 0.15 V typical / 0.3 V max dropout, rated −40 to 125 °C) instead of the AMS1117-3.3. The LDO alone still left VDDA about 0.8 V ahead of VDD at key-off and in a slow brown-out (the REF3033 holds up while +3V3 falls), so **D30** (BAT54WS, C124205) now runs from the F103's VDDA to +3V3 | VDDA − VDD, worst case: power-up 104 mV (253 mV with a max-dropout LDO), key-off 244 mV, slow brown-out 243 mV. ST's limit is 300 mV; rev 0.6 reached 953 mV |
| N2 | **Fixed** | **D19-D26** (BAT54WS Schottky) from each of the eight AN_ nodes to +3V3, after the 5.6k series resistor. The series resistors and the CLT/IAT bias resistors are now 0603 | Sensor wire shorted to 14.4 V: pin 3.55 V, 0.1 nA into the MCU, 1.9 mA into +3V3, 21 mW in the series resistor. 24 V jump start: 3.57 V (fault model 3.63 V, a CHECK: 0.33 V over VDDA against ST's 0.3 V), 3.7 mA, 75 mW. **New CHECK, clamp leakage:** a Schottky leaks into the node when the sensor is near 0 V; with BAT54WS figures (2 µA max at 25 V, 25 °C; temperature and voltage scaling assumed) that reads 5 mV high at the sensor at 60 °C typical, up to 46 mV with a max-leakage part, and 26 / 260 mV at 85 °C. Check a TPS and CLT reading against a meter on a hot day |
| N3 | **Partly fixed** | **R137** (10k) between the LSU_UN wire and the Nernst buffer input (U101 pin 10). F103 PA1 is no longer wired to LSU_VM (the firmware never sampled it). R114 moved down the LSU_UN line beside C102 to make room | UN wire shorted to the 12 V heater feed: 1.1 mA into the MCP6004 input (2 mA allowed); 2.0 mA in a 24 V jump start. IP and RT shorted: 1.1 mA into the AD8628 inputs through R112 / R111. **Still open:** the pump and virtual-ground drive paths (IP, RT, VM) carry the pump current and can't take series resistance, so a short of one of those wires to battery still damages U101 and R108-R110 (and VM reaches F103 PA3 through R109), as on the FOME module. Protecting them needs a different front end (a CJ125-class interface IC) |
| N4 | **Fixed by N1** | BOR stays at rusEFI's level 1 | ISO 16750-2 level II crank: +3V3 holds 3.30 V (also with a max-dropout LDO); rev 0.6 fell to 2.60 V. Level III still resets the ECU, cleanly |
| N5 | **Fixed** | Motherboard **F1: 3 A hold PTC** (LUTE 2920L300/30GR, C22446884: 3 A hold, 5 A trip, 30 V) instead of the 2 A part, on every motherboard. No 1812 part holds 3 A above 8 V, so the footprint is now 2920 | Cold heater warm-up: 2.25 A rms worst (2.5 Ω), against about 2.4 A hold at 60 °C. Heater reaches temperature in 13-14 s |
| N6 | **Fixed for a 14.4 V short; a 24 V jump start with a shorted wire still overloads some** | The hall 1k pull-ups R62/R64 are now 0603 (100 mW), standing beside their series resistors | Crank or cam wire shorted to 14.4 V: R62/R64 88 mW (CHECK, 88 % of rating; was over). **Still over in a 24 V jump start while a wire is shorted** (a double fault): R62/R64 279 mW, R61/R63 (4.7k, 0402) 85 mW, CLT/IAT bias R33/R36 134 mW. Thick-film parts take 2.5 × rated power for 5 s, so they survive a brief event, not a long one. 1206 parts would cover it; they don't fit the 2.54 mm column pitch |
| N7 | **Fixed** | **R138** (2.2k) ahead of the knock coupling cap C44 | Knock wire shorted to battery: 5.4 mA peak into the LMV321's input diode (was about 1.2 A). The 2.2k adds to the amplifier's input resistance: gain at 6.9 kHz now 4.52; 1 g gives 118 mV at the ADC, clipping above 14 g |
| N8 | **Improved, still a limit; wider than first reported** | OUT_INJ1-4 copper zones on both outer layers around Q1-Q4's tabs, stitched with 19-21 thermal vias each (`scripts/tab_copper.py`): 86-90 mm² per driver, about 65 mm² effective. The injectors are driven from the daughterboard on every year, so this applies to all five | Estimated RthJA 109 °C/W (was 130). **1989-93** (batch, two injectors per driver, TVS-clamped), 90 % duty: Tj 123 °C at 60 °C ambient (was 142 °C); thermal shutdown at 85 °C ambient. **Sequential years: the first report missed these.** Each driver absorbs its injector's turn-off energy in its own clamp (6 mJ per pulse, 0.36 W at 7200 rpm, with 8 mH injectors assumed). At 90 % duty and 7200 rpm a driver reaches thermal shutdown even at 60 °C ambient; at 80 % duty, typical Rds(on), 60 °C, it is still above 150 °C (128 °C if the injectors are 4 mH). Steady state; a short burst at full load is shorter than the board's thermal time constant. Proposed, not made: a TVS on each injector output on the sequential motherboards (as 1989-93 has), which takes the clamp energy off the drivers. Measure the injectors' inductance before deciding |
| N9 | **Fixed** | **D27-D29** (1N4148WS) from each switch input to +3V3, as on the hall inputs | Switch input at 35 V (load dump): 3.88 V at the FT pin (was 8.1 V; 7.3 V allowed); 24 V: 3.86 V |
| N10-N13 | Unchanged | As listed above: the AUX header is for bench use; 2L needs checking on a car; N12 is inherited from FOME; N13 needs nothing | — |

**Board checks on rev 0.7:**

| Check | Result |
|---|---|
| Schematic netlist against the design | 822 pads, 0 differences |
| DRC (`daughter_release.sh`) | 0 unconnected, 0 clearance errors. Courtyard overlaps 42 (rev 0.6: 11), all from the new clamps and the larger 0603 parts packed between existing ones. With every courtyard shrunk by 0.2 mm (about the part body) nothing overlaps |
| Copper rebuilt from geometry against the design (`board_copper.py`), all six boards | 0 opens, 0 shorts |
| Pin check (`check_pins.py`) | OK |
| Every harness cavity shorted to ground, 14.4 V and 24 V (`board_checks.py`) | 1481 OK / 109 CHECK / 215 FAIL (rev 0.6: 1463 / 59 / 284). The analog, switch and knock FAILs are gone. What remains: the sensor 5 V shorted to battery (it back-feeds every sensor), ignition and relay outputs shorted to battery (Minor list: unprotected outputs), the LSU drive wires (N3), the AUX header's UART (N10) and the 24 V double fault in N6 |
| Firmware-in-the-loop, two chips, in CI (`sim.yaml`) | Pass, after logging the sensor model every 50 ms (the per-step pump-current means were flaky) |

**How the board was re-routed.** Only the nets around the changed parts were routed again
(`scripts/route_eco.py` keeps the rev 0.6 copper everywhere else, then `route.py`'s finish passes route the rest), so
the proven layout elsewhere is unchanged. Two connections the router left open, the LED_ERR and LED_WARN lines from
the MCU to their status LEDs (ripped up by the finish passes), were routed by hand with `hand_route.py`; LED_WARN takes
several layer changes on its way.

**Not repeated:** the firmware-in-the-loop runs feed the MCU pins through models of the input stages, so the hardware
change doesn't alter them.

## Rev 0.8: driver temperature and protected outputs
**Boards:** daughterboard rev 0.8 (125 × 76 mm, was 125 × 60); motherboards 1989-93 and 1994-95 rev 0.8, 1996-97 /
1999-2000 / 2001-05 rev 0.6 (they carry the new protected sensor 5 V, V5_EXT, to the harness; 1989-93 also gets new
injector clamps). The parts and the reasons are in `daughterboard/README.md` (What changed in rev 0.8). Everything below
was run again on the released, routed boards: `circuit_sim_full.py` **84 OK / 12 CHECK / 1 REF / 0 FAIL** (rev 0.7:
64 / 28 / 1 / 0), and `board_checks.py` **1587 OK / 270 CHECK / 4 FAIL** (rev 0.7: 1481 / 109 / 215). The CHECK count
went up because faults that used to FAIL now end in a CHECK (a protected part working as designed, with a wrong reading
while the fault lasts).

| Finding | Status | Change | Re-check on rev 0.8 |
|---|---|---|---|
| N8, driver temperature | **Fixed** (estimate) | Q1-Q8: **VND7NV04** (DPAK, 60 mΩ, 200 mJ clamp) in a new 16 mm strip above J1, each tab on a drain copper column on F.Cu, In2.Cu and B.Cu (65-102 + 113-118 + 95-108 mm²) with 28-34 thermal vias, most in the tab pad | RthJA estimated **48 °C/W** (rev 0.7: 109), from 178 mm² effective copper. Sequential injectors, 90 % duty, 7200 rpm, worst-case Rds(on), 8 mH assumed: **Tj 84 °C at 60 °C ambient, 110 °C at 85 °C** (rev 0.7: thermal shutdown). 1989-93 paired drivers: 65 / 91 °C. Idle valve 62 / 87 °C. The model is a copper-area fit, not a thermal simulation: measure on the bench |
| 1989-93 injector clamps | **Changed; CHECK** | D3/D4 **SMCJ30A** (C224048) instead of SMCJ40A, on copper islands on both layers (about 115 mm² each side) | The new drivers clamp at 40 V minimum, so a 40 V TVS could have left the energy in a driver; the 30 V part always clamps first (0 mW in the drivers, peak 38 V). D3/D4 take 1.55 W each at 7200 rpm: **137 °C at 60 °C ambient, 162 °C at 85 °C**, over the 150 °C rating in that corner (sustained 7200 rpm, 8 mH injectors assumed). Measure the injectors' inductance; at 4 mH the energy halves |
| Unprotected relay, lamp and tach outputs | **Fixed** | Seven **ZXMS6004FF** protected low sides (Q9-Q15) instead of the ULN2003, behind a second SN74LVC4245A (U12) on the shared enable | Every output shorted to 14.4 and 24 V: current-limited, no FAIL. Hottest load (VICS solenoid, 402 mA): Tj 102 °C at 85 °C ambient |
| Unprotected ignition outputs | **Fixed** | B5819W Schottky (D31-D34) after each 100 Ω (now 1206); ZXMS6004FF pull-downs (Q16-Q19) from a 74HCT04 (U13); R144-R147 **3.3k** 1206 | Coil wire shorted to 14.4 / 24 V: the Schottky blocks it; R144-R147 within rating at 24 V (2.2k was over: found by `board_checks.py`). Output shorted to ground with the driver on: R18 180 mW, 72 % of rating (CHECK) |
| Sensor 5 V shorted to battery | **Fixed; CHECK** | Second TLS115 (U14): **V5_EXT** on J1 pin 13 to the harness sensors and J5-14. The first now feeds only the MAP sensor. Hall pull-ups from V5_EXT through D35 (BAT54A) | V5_EXT back-fed to 14.4 or 24 V: TLS115 protected (45 V rated), MAP sensor and the board's 5 V unaffected; the harness sensors read wrong while it lasts (CHECK) |
| N6, 24 V with a shorted wire | **Fixed** | V5_EXT and D35 (no back-feed into the pull-ups); 22k/10k switch dividers; R61/R63 0603 | No FAIL left in the crank/cam, CLT/IAT or switch cases |
| N3, LSU drive wires | **ICs protected; resistors sacrificial** | F2 (0.1 A PTC) in VM; Schottky clamps D40/D41 from the pump and virtual-ground drive nodes to +3V3; R108-R110 1206; R137 22k; +3V3 shunt clamp (below) | VM shorted: F2 trips in under 1 s, U101 and both MCUs protected. **Still 4 FAILs, all here:** RT or IP shorted to 14.4 / 24 V overloads R108 (2.3 W at 14.4 V; opens like a fuse) and R110 (0.57 W). U101, the F103 and the F407 survive; replace the resistors after such a fault. A PTC in those paths would change the pump loop: not done |
| Fault current into +3V3 | **New; CHECK** | U15 TL431 at 3.56 V + Q20 BCP53 shunt, C63 + C68 (2 × 100 µF) | 1 A pushed into +3V3: peak 3.93 V for microseconds, then 3.56 V (MCU absolute maximum 4.0 V: a 70 mV margin at the peak). In the worst board case (RT shorted to 24 V) Q20 sinks 341 mA, 1.22 W, above its 1 W rating until the fault clears |
| CAN at 24 V | **Fixed** (datasheet) | TCAN1042V-Q1 (U10, U106), ±58 V bus pins, −40 to 125 °C | A 24 V jump start is inside the bus pins' ±58 V rating (the SN65HVD230 allowed −4 to 16 V). The CAN wires go to the AUX header and the OBD/CAN wiring, not a harness cavity, so `board_checks.py` doesn't short them |
| N10, AUX UART | **Fixed** | R139/R140 **10k** and BAT54S clamps D36/D37 on PC6/PC7 | 4.7k was over its rating at 24 V (`board_checks.py`); 10k is inside it |
| Battery / ignition sense | **Fixed** | BAT54WS clamps D38/D39 | Ignition-sense cavity at 24 V: PA2 reads 3.60 V (clamped), OK on every year |
| Switch inputs at cranking | **Fixed** | 22k/10k dividers | 12 V signal at 9 V cranking: 2.81 V at the MCU, above ST's tested 2.31 V |

**Still CHECK in `circuit_sim_full.py`:** ISO 16750-2 level II/III cranks (level II: +5V 3.91 V, below the TC4427 and
shifter rating; level III resets the ECU cleanly), the NB alternator field (M5), the GM-type CLT/IAT option, the
analog clamps' leakage when hot (N2), the 1989-93 and 1994-95 harness inputs that need a car (2L), N12 (ESR, inherited
from FOME), the shunt clamp's 3.93 V peak, the LSU drive resistors above, and the 1989-93 TVS temperature above.

**Board checks on rev 0.8:**

| Check | Result |
|---|---|
| Schematic netlist against the design | 958 pads, 0 differences |
| DRC (`daughter_release.sh`) | 0 unconnected, 0 clearance errors. Courtyard overlaps 97 (rev 0.7: 42), from the new parts packed between existing ones; with every courtyard shrunk by 0.2 mm (about the part body) nothing overlaps |
| Copper rebuilt from geometry against the design (`board_copper.py`), all six boards | 0 opens, 0 shorts |
| Stacking | All 80 J1/J2 pads land on JD1/JD2 on every motherboard (the daughterboard's new strip overhangs free motherboard space) |
| Pin check (`check_pins.py`) | OK (LEDs now PD12 / PC8 / PC9 / PD15) |

**How the board was re-routed.** The rev 0.7 copper was moved down 16 mm and kept (`route_eco.py`), and only the nets
around the changed parts were routed again. Three connections (two LED lines and the wideband MCU's green LED and SWD
data) were left with no path. They were closed by hand: a few short wideband nets ripped up and rerouted in a better
order (`hand_route_all.py`), and the comms and warning LEDs moved from PD13/PD14 to the free PC8/PC9, which the
firmware follows. `hand_route.py` now keeps 0.2 mm from non-plated holes (the Tag-Connect's), and `clean_dangling.py`
removes the stubs and stacked vias the rip-ups leave.

## Open items
The 2026-11-02 findings N1-N13 are listed in [New hardware findings](#new-hardware-findings-2026-11-02); what rev 0.7
fixed is in [Rev 0.7](#rev-07-fixes-for-the-2026-11-02-findings) and what rev 0.8 fixed in
[Rev 0.8](#rev-08-driver-temperature-and-protected-outputs). Still open from that list: the LSU drive resistors in an
IP or RT short (N3, the ICs are protected), N11 (2L on a car), N12 (ESR, inherited) and N13 (noted).

| # | Issue | What to do |
|---|---|---|
| M5 | **NB alternator field drive unknown.** rusEFI's NB presets enable alternator PWM; **our firmware now ships it off** (pin and PID still set up). If the ECU drives the field coil directly (3-5 A, high inductance), a low-side driver (since rev 0.8 a VND7NV04 DPAK, current-limited with thermal shutdown; about 1.3 W allowed at 85 °C) is likely undersized for continuous field current and has no freewheel path | Measure the field current and its supply on a car (or check the FSM) before turning on "Alternator control" in TunerStudio. Until then the car may not charge: watch battery voltage. Add a freewheel diode only once the field's supply is known |
| M6 | ~~ULN2003 at full load~~ **Resolved in rev 0.8:** the relay, lamp and tach outputs are seven ZXMS6004FF protected low sides (hottest, the NB1 VICS solenoid: Tj 102 °C at 85 °C ambient) | — |
| Tach | 1989-95 tach cavity 2I: our board drives it as an output (as Hellen does); the wiki tables call it an input | Kept as an output. Check the wiring diagram; if the igniter feeds 2I, set the tach output to none |
| Switch inputs at cranking | ~~2.09 V at the MCU at 9 V~~ **Resolved in rev 0.8:** 22k/10k dividers give 2.81 V, above ST's tested 2.31 V | — |
| Supply | **MPX5700AP (MAP sensor, every motherboard) is NRND at ST**, which took over NXP's sensor line in 2026 (LCSC 191, Mouser 74 on 2026-10-31) | Kept for this revision: buy the sensors you need now. Next motherboard revision: add a connector for an external MAP sensor, fed from the protected 5 V sensor supply |
| Supply | **Harness headers:** TE lists all four as "not currently available"; 176122-6 (1999-2000) and 178780-1 (1996-97) are obsolete at Mouser. 174915-6 (76-pin, Mouser 263) and 353830-5 (72-pin, Mouser 252) are still stocked | Buy the headers ahead. Next revision: fit the 1996-97 board with 174915-6, and consider moving the 1989-95 and 1999-2000 boards to it as rusEFI's Hellen boards do (fit-check a real plug first) |

### Minor (not changed)
- **AMS1117:** rated 0 °C minimum (resolved in rev 0.7: U4 is now an LDL1117S33R, rated −40 °C).
- **Unprotected outputs** (resolved in rev 0.8): the ignition outputs have a Schottky and a protected pull-down per
  channel, the relay, lamp and tach outputs are protected low sides.
- **Knock amplifier:** clips above about 284 mV input (gain 5.7). Fine at light load; consider lower gain.
- **MPX5700AP:** the 15.6 kΩ divider loads it beyond its 0.1 mA typical source current above about 210 kPa. Only
  relevant with boost.
- **NB charge-warning lamp** (NB1 1Q, NB2 3U) is not driven.
- **CAN transceivers** (resolved in rev 0.8): TCAN1042V-Q1, −40 to 125 °C, bus pins ±58 V.
- **PTC voltage ratings:** F1-F4 on the motherboards are 24-30 V parts; the daughterboard's F1 is now a 33 V part
  (rev 0.5b). A PTC only sees the full voltage once tripped; the TVSs keep transients near 33-35 V.
- **O2 heater on OUT_VVT (1996-97, NB1)** is continuous DC. Its cold inrush (unverified) is likely within the
  driver's current limit (simulated: 4.6 A against the VND7NV04's 6 A minimum); if not, the driver limits it and the heater warms more slowly.
- **Floating MCU-side inputs:** while the MCU is in reset or a bootloader, the shifter's MCU-side inputs float. Its outputs are disabled then, so this only costs a little supply current. When a configuration change releases a control pin, rusEFI briefly sets it to pull-up before the board's hook parks it low again (well under a millisecond, far shorter than an injector's opening time).

## Safety review: current, faults and fuses
**Fuses on the boards:**
| Fuse | Board | Protects |
|---|---|---|
| F1, 0.5 A PTC (new) | daughterboard | logic supply: buck, sensor 5 V, relay-driver clamp |
| F1, 2 A PTC | every motherboard | LSU heater supply |
| F2, 2 A PTC | NB1, NB2 | idle valve +12 V feed |
| F3, 2 A PTC | NB2 | VVT valve +12 V feed |
| F4, 0.5 A PTC (new) | every motherboard | AUX +12 V pin J5-15 |

Injector, coil and relay currents come from the car's own fused feeds (the EGI/ECU fuse and main relay, the relay and
lamp circuits). The ECU only switches their ground side, through current-limited drivers.

**Normal current:**
| Load | Current |
|---|---|
| ECU logic | about 0.25 A at 13.8 V (F1 holds 0.5 A) |
| LSU heater | about 0.6 A average once warm, ramped by the wideband firmware; up to about 4 A briefly when cold |
| Injectors (through the ECU's grounds) | about 1 A each at peak, one per driver on every year (1989-93: two drivers per wire) |
| Idle valve, VVT valve | about 1 A each; turn-off energy goes into D1/D2 |
| Relays | about 0.18 A each through the ULN2003 |

None of these exceed their path's rating.

**Faults:**
| Fault | What happens | Verdict |
|---|---|---|
| Sensor 5 V shorted to ground | TLS115 is current-limited | OK |
| Sensor 5 V or a crank/cam wire shorted to battery | Since rev 0.8 the harness sensors have their own TLS115 (V5_EXT): it survives, the MAP sensor's supply is separate and unaffected. D13/D14 hold the MCU pins at 3.9 V (2-4 mA) | OK |
| Injector, idle, VVT, boost or alternator output shorted to battery | VND7NV04 (rev 0.8; NCV8406A before) current limit and thermal shutdown (cycles until the short is removed), driven at 5 V | OK |
| Relay, CEL or tach output shorted to battery | Rev 0.8: ZXMS6004FF current limit and thermal shutdown (the ULN2003 before had no limit) | OK |
| Ignition output shorted to battery | Rev 0.8: the B5819W in each channel blocks it; the ZXMS6004FF pull-down limits (before: R15-R18 burnt) | OK |
| Reverse battery | See below | Low risk; no change |
| Load dump, ISO pulse 2a, jump start | D6 on the input, then F1 and D12 after the series diodes: +12V peaks at 36.4 V (simulated, buck limit 44 V) | OK |
| Sustained overvoltage (failed regulator) | Up to about 37 V nothing on +12V conducts. Above that D12 conducts and F1 trips. While tripped F1 sees most of the overvoltage, within its 33 V rating up to the 36.7 V D12 clamp; it is the same part Hellen uses on its 12 V input, and a sustained 39 V on a car with a battery connected is unlikely | OK |
| Key-off drain on 2003-05 | COM TVS: no path | OK |
| Internal short on the daughterboard 12 V rail | F1 trips at 1 A | OK |
| Short on the AUX +12 V pin | F4 trips | OK |
| USB-only bench power | USB 5 V → D10 → +5V. The buck's high-side body diode may lift +12V to about 4 V. Harmless | OK |
| MCU reset, or a fatal error | On any reset the enable pin floats, the pull-up disables the shifter and the pull-downs switch all eight low sides off, with no firmware involved. After a fatal error the firmware releases the enable itself. (A hang that neither resets nor raises an error freezes the outputs, as on any ECU) | OK |

**Reverse battery (for example, jump leads crossed).** Risk: **low**; the consequence is a blown EGI/ECU fuse.
- The ECU's logic is blocked by D7/D8.
- The input TVS D6 conducts forward and short-circuits the reversed supply, so the car's 15-30 A ECU fuse blows within
  milliseconds. D6 (200 A surge rating) normally survives. If it fails, it fails short, which is the safe direction.
- Until the fuse blows, current also flows backwards through the drivers' body diodes and the loads: injectors,
  idle valve, relays and the LSU heater. Every ECU with low-side drivers does this, OEM ones included. For a few
  milliseconds it does no harm.
- **The new freewheel diodes add one low-resistance path:** ground → the idle (and VVT) driver's body diode → D1/D2 →
  the valve's +12 V feed. It runs in parallel with D6 and has no load in it. Simulated with 40 mΩ of harness and fuse,
  it shares about 45 A of the roughly 200 A fault current until the fuse blows (a few milliseconds). The SS34 is
  rated 80-100 A for 8.3 ms, so it is fine. The low-side driver's body diode has no pulse rating in its datasheet,
  so a hard reversal could damage the idle or VVT driver. On NB boards F2/F3
  (2 A resettable) sit in this path and limit it further.
  - If that matters to you, a 1 Ω resistor (2512, 1 W) in series with D1/D2 cuts it to about 3 A and costs about
    1 V of freewheel voltage and up to 0.4 W at the idle valve. It isn't on the boards.
- **Adding a reverse-polarity MOSFET would make this worse, not better.** It could only block the ECU's own supply,
  not the load path through its ground pins. And with the crowbar gone, the fuse would no longer blow, so the
  injectors and relays would stay energised for as long as the battery was reversed. The TVS crowbar is the right
  protection here; keep the original fuse rating in the car.

**1989-93 paired injectors.** Before rev 0.6 the risk was **moderate, at sustained high load**.
- Each driver carried about 2 A while open, against its 1.4 A continuous rating. On top of that went about 1 W of
  turn-off energy at 7000 rpm.
- At idle and cruise the duty cycle is low and the driver stays cool. At wide-open throttle and high rpm (80-90 % duty,
  for example on a track), the SOT-223 could reach its 165 °C thermal shutdown.
- The driver would then cut out and restart, and the engine would run lean exactly where lean does damage.
- Rev 0.6 halves the current per driver and moves the turn-off energy into a TVS rated for it. That removes the risk
  (simulated: 0.99 A per driver, no clamp energy in the drivers).
- The alternative is converting the harness to sequential, as on 1994-95 cars: new wires to 2Y/2Z, links moved, mode
  set to sequential.
- **Compatibility:** the firmware's 1989-93 preset now drives all four outputs. On a 1989-93 motherboard older than
  rev 0.6, INJ3/INJ4 go to 2Y/2Z, so 2Z (the A/T control unit's pin on automatics) would be pulsed. Use the rev 0.6
  board, or set injection pins 3 and 4 to none on an older one (firmware README).
- Costs of the fix: the 47 V TVS clamp closes the injectors a little more slowly than the drivers' own 65 V clamp, so
  check the injector dead time on the car. The two SMCJ40A take about 1 W each at 7000 rpm and high duty, well inside
  the SMC package.

## Not covered
- **Real hardware.** No board has been built. These need a bench and a car:
  - analog accuracy;
  - wideband heater and pump-loop behaviour (the circuit is FOME's, but the layout is new);
  - CAN signal integrity;
  - thermal behaviour in the case;
  - EMC.
- **Cycle-accurate timing.** The firmware-in-the-loop runs are instruction-level: each instruction takes one clock,
  with no pipeline, flash wait states or bus contention (see
  [Full-firmware emulation](#full-firmware-emulation-expanded-circuit-and-board-checks-2026-11-02)). Peripheral timing
  runs at the real clock rates.
- **Load models.** Injector, idle-valve and alternator inductance and current are typical published values, not
  measured on Miata parts.
- **Two wires the sources can't settle:** the 1989-95 tach cavity (pinout finding 6) and the NB alternator field supply
  (M5). Both need a look at a car.
- **The new level shifter's enable timing** runs only on the real firmware (it isn't in the unit-test build). Check
  on the bench that the injector and idle outputs stay off from power-up until about 200 ms after the firmware starts.
