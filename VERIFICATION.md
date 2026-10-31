# Verification report

**Date:** 2026-10-30.
**Boards:** daughterboard rev 0.5; motherboards 1989-93 and 1994-95 rev 0.6, 1996-97 / 1999-2000 / 2001-05 rev 0.4.
These revisions carry the fixes this review called for (see [Rev 0.5 changes](#rev-05-changes-and-re-verification)).
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
- **Review.** A second, independent pass checked this report against the sources. Its corrections are folded in below;
  it found the ignition-sense bug.

## How it was checked
| Check | Method | Result |
|---|---|---|
| Harness pinouts | Each motherboard's harness map compared cavity by cavity with rusEFI's Hellen NA6/NA96/NB1/NB2 boards (connector yaml and PCB nets), the rusEFI wiki 1990 and 1994 pinout tables, and `research/pinouts_9605.md` (2005 FSM) | All match |
| Header geometry | Our harness footprints compared pad-by-pad, by **position**, with the Hellen boards' footprints and nets (not just by name), so a mirrored or mislettered header would show up | All match |
| Daughter ↔ motherboard | All 80 J1/J2 pads of the daughterboard (headers on the bottom) against JD1/JD2 on each finished motherboard PCB: same position (pure translation, no mirroring) and same net | 5 × 80 OK |
| MCU pins | Power, VCAP, VDDA, BOOT0, crystal; alternate functions (USART3 PD8/PD9, CAN2 PB12/13, USB PA11/12, USART6 PC6/7, ADC channels, ADC3 on PA3) | OK (PB2 and PC13/14 fixed in rev 0.5) |
| Wideband MCU | F042 pins against the rusEFI wideband `f0_module` firmware we flash (ADC channels, heater/pump PWM, LEDs, ESR, CAN, UART, ID straps) | Matches; floating ID straps give CAN index 0, as rusEFI expects |
| Datasheets | Every active part and sensor: supply, logic levels, current, thermal, pin functions (full notes: datasheet review, summarised below) | See findings |
| Engine simulation | `firmware/board/tests/test_miata_ecu.cpp`: the board's real configuration code inside rusEFI's unit-test engine, all five years (2001-02 and 2003-05 separately). Real NA CAS and NB2 crank+cam logic-analyser captures, plus running from cranking to 6500 rpm with realistic acceleration, then the rev limiter. Every output edge recorded and checked against crank angle | 18/18 tests pass (rev 0.5 pins) |
| End to end | `firmware/tools/sim_report.py`: for each year, the tune the firmware builds → STM32 pin → driver → J1/J2 → motherboard → harness cavity, compared with the cavity the references say carries that function. The expected cavities are a hand-written table of the functions the firmware drives or reads (not purge, pressure regulator, VICS or power pins). It follows the motherboards' fitted 0R links | 119/119 OK (6 configurations) |
| Circuits | `firmware/tools/circuit_sim.py` (ngspice), as built: hall inputs at 7200 rpm and shorted to battery, 12 V switch inputs with and without the pull-up option, CLT/IAT network −20…120 °C through the firmware's conversion, injector / idle / VVT turn-off, 1989-93 paired injectors with the TVS, relay-driver key-off back-feed, kick-back and a load dump on the relay feeds (each TVS at the bad end of its tolerance), logic supply under load dump, ISO pulse 2a, jump start and a sustained overvoltage, knock amplifier | 20 OK, 3 CHECK (switch inputs at 9 V cranking, knock clipping), 6 REF (rev 0.4 or no-fix references), 0 FAIL. Details in [Rev 0.5 changes](#rev-05-changes-and-re-verification) |
| Board layout | Every board regenerated from the design scripts, autorouted, schematic netlist compared pad by pad with the design, KiCad DRC | See [Rev 0.5 changes](#rev-05-changes-and-re-verification) |
| Wideband flashing | `firmware/tools/flash_sim/`: our `wideband_uart_flash.cpp`, unmodified, compiled for a PC against a model of the F042 ROM bootloader (AN3155). The model was first validated with **stm32flash** (wrote and verified the image, both erase variants) | 9/9 scenarios pass |
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
replace a bench test of the real board.

## Wideband flashing (simulated)
- **Blank chip (both erase variants) and re-flash over old firmware:** all 31,744 bytes written and read back. The
  flasher leaves BOOT0 low and the chip boots its new firmware.
- **Faults:** no answer, read-protected, read-back mismatch, wrong chip ID and write refused each give a specific
  error and leave BOOT0 low.
- **Engine turning:** the flash is refused.
- **UART:** 115200 baud, 8 data bits + even parity, as AN3155 requires.
- **Duration:** about 71 kB cross the wire, so expect roughly 8-10 s on the real 115200-baud link.
- **Failed flash:** a flash that fails after the erase leaves the F042 blank. It then stays in its bootloader, so
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
footprint, and the board was not re-routed.

| Ref | Was (out of stock) | Now | Why it's equivalent |
|---|---|---|---|
| Q1-Q8 | Infineon AUIPS2041LTR (C113610), also out at LCSC | **onsemi NCV8406ASTT3G (C459816)** | Same SOT-223 pinout (1 gate/input, 2 and tab drain, 3 source). Self-protected low side with current limit, thermal shutdown and a 60-70 V active clamp (AUIPS2041: 63-75 V), AEC-Q101. 210 mΩ at 5 V. Circuit sims rerun with its 60 V minimum clamp: the 1989-93 SMCJ40A still takes all the injector turn-off energy (0 mW in the drivers) |
| D11, D12 | Bourns SMAJ33A (C3720609) | Littelfuse SMAJ33A (C223988) | Same part number and ratings (36.7-40.6 V breakdown, 400 W) |
| F1 | SMD1206P050TF/24 (C209741) | TECHFUSE nSMD050-33V (C70077) | Same 1206, 0.5 A hold, 1 A trip, 100 A; rated 33 V instead of 24 V |
| L1 | Taiyo Yuden LBC3225T2R2MR (C223413) | FH CMI322513U2R2KT (C70960) | 2.2 µH 1210; 500 mA, 0.3 Ω. The buck draws about 0.15 A at 12 V |
| D1, D5 / D2 / D3 | Everlight 19-217 green / blue, 19-213 yellow | Hubei KENTO KT-0603G (C12624) / KT-0603B (C2288) / KT-0603Y (C2287) | Same 0603 status LEDs; the wideband already used the KENTO green and blue |
| C103 | FH 0402B333K100NT (C285077) | YAGEO CC0402KRX7R9BB333 (C106862) | 33 nF X7R 0402, rated 50 V instead of 10 V |
| R110 | 61.9 Ω 0603 1 % (C23092) | 62 Ω 0603 1 % (C23222) | Wideband pump-current sense resistor: 0.16 % higher, inside the 1 % tolerance |
| U9 | MAX9926UAEE+ (C1523548), also out at LCSC | **Not fitted** | The VR inputs are spares: no Miata year uses a VR sensor. The footprint stays; it's in the self-order BOM as optional |

Also fixed:
- **U105 footprint:** the AD8628ARTZ is the 5-lead SOT-23 package, and the board called its footprint TSOT-23-5
  (from the FOME module). KiCad's SOT-23-5 and TSOT-23-5 footprints have identical pads, so only the name changed.
  JLCPCB no longer reports a mismatch.
- **SW1/SW2** (same button) are one BOM line, so JLCPCB no longer warns that two lines match the same part.

Re-checked: schematic netlist 754 pads, 0 differences; DRC 0 unconnected, 0 clearance; circuit sims 20 OK / 3 CHECK /
6 REF / 0 FAIL.

## Open items
| # | Issue | What to do |
|---|---|---|
| M5 | **NB alternator field drive unknown.** rusEFI's NB presets enable alternator PWM; **our firmware now ships it off** (pin and PID still set up). If the ECU drives the field coil directly (3-5 A, high inductance), a SOT-223 low-side driver (now the NCV8406A, current-limited with thermal shutdown) is likely undersized for continuous field current and has no freewheel path | Measure the field current and its supply on a car (or check the FSM) before turning on "Alternator control" in TunerStudio. Until then the car may not charge: watch battery voltage. Add a freewheel diode only once the field's supply is known |
| M6 | **ULN2003 at full load:** 4 relays + NB1 VICS is about 0.7-1.6 W, against 0.73 W at 85 °C ambient. Fine at cabin temperature (the ECU sits in the passenger footwell) | Move VICS or the fans to a protected driver in a later revision if needed |
| Tach | 1989-95 tach cavity 2I: our board drives it as an output (as Hellen does); the wiki tables call it an input | Kept as an output. Check the wiring diagram; if the igniter feeds 2I, set the tach output to none |
| Switch inputs at cranking | A 12 V switch signal at 9 V gives 2.09 V at the MCU: above ST's by-design threshold (1.79 V), below its tested one (2.31 V) | Only matters while cranking; no change |

### Minor (not changed)
- **AMS1117:** rated 0 °C minimum and about 125 °C junction at 85 °C ambient; consider an automotive-temperature
  LDO.
- **Wideband STM32F042:** VDDA (REF3033, 3.300 V) can sit below VDD (up to 3.365 V). This is inherited from the FOME
  module.
- **Unprotected outputs:** the TC4427 ignition and ULN2003 relay outputs have no short-to-battery protection (the
  NCV8406A outputs do).
- **Knock amplifier:** clips above about 284 mV input (gain 5.7). Fine at light load; consider lower gain.
- **MPX5700AP:** the 15.6 kΩ divider loads it beyond its 0.1 mA typical source current above about 210 kPa. Only
  relevant with boost.
- **NB charge-warning lamp** (NB1 1Q, NB2 3U) is not driven.
- **CAN transceivers** are rated to 85 °C. Their bus pins are rated −4 to 16 V absolute maximum, which a 24 V jump
  start exceeds.
- **PTC voltage ratings:** F1-F4 on the motherboards are 24-30 V parts; the daughterboard's F1 is now a 33 V part
  (rev 0.5b). A PTC only sees the full voltage once tripped; the TVSs keep transients near 33-35 V.
- **O2 heater on OUT_VVT (1996-97, NB1)** is continuous DC. Its cold inrush (unverified) is likely within the
  NCV8406A's current limit; if not, the driver limits it and the heater warms more slowly.
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
| Sensor 5 V or a crank/cam wire shorted to battery | TLS115 survives; D13/D14 hold the MCU pins at 3.9 V (2-4 mA). The MPX5700AP would still be damaged by 14 V on its supply | OK (MAP sensor at risk) |
| Injector, idle, VVT, boost or alternator output shorted to battery | NCV8406A current limit and thermal shutdown (cycles until the short is removed), driven at 5 V | OK |
| Relay, CEL or tach output shorted to battery | ULN2003 has no limit: the channel fails | Minor (rare fault) |
| Ignition output shorted to battery | R15-R18 (100 Ω) take about 2 W and fail, which protects the TC4427 | Minor (rare fault) |
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
- **The main MCU's boot.** It wasn't run in an instruction-level emulator. QEMU's STM32F4 model lacks the clock and
  peripheral models rusEFI waits on at start-up, so the image was checked structurally instead.
- **Load models.** Injector, idle-valve and alternator inductance and current are typical published values, not
  measured on Miata parts.
- **Two wires the sources can't settle:** the 1989-95 tach cavity (pinout finding 6) and the NB alternator field supply
  (M5). Both need a look at a car.
- **The new level shifter's enable timing** runs only on the real firmware (it isn't in the unit-test build). Check
  on the bench that the injector and idle outputs stay off from power-up until about 200 ms after the firmware starts.
