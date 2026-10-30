# Verification report

**Date:** 2026-10-30.
**Boards:** daughterboard rev 0.4; motherboards 1989-93 and 1994-95 rev 0.5, 1996-97 / 1999-2000 / 2001-05 rev 0.3.
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
- **Hardware: four changes are needed before building, and several more are recommended.** They are listed in
  [Hardware changes](#hardware-changes). The most important: the protected low-side drivers are driven below their
  specified input level, and the idle and VVT valves have no freewheel diodes.
- **Review.** A second, independent pass checked this report against the sources. Its corrections are folded in below;
  it found the ignition-sense bug.

## How it was checked
| Check | Method | Result |
|---|---|---|
| Harness pinouts | Each motherboard's harness map compared cavity by cavity with rusEFI's Hellen NA6/NA96/NB1/NB2 boards (connector yaml and PCB nets), the rusEFI wiki 1990 and 1994 pinout tables, and `research/pinouts_9605.md` (2005 FSM) | All match |
| Header geometry | Our harness footprints compared pad-by-pad, by **position**, with the Hellen boards' footprints and nets (not just by name), so a mirrored or mislettered header would show up | All match |
| Daughter ↔ motherboard | All 80 J1/J2 pads of the daughterboard (headers on the bottom) against JD1/JD2 on each finished motherboard PCB: same position (pure translation, no mirroring) and same net | 5 × 80 OK |
| MCU pins | Power, VCAP, VDDA, BOOT0, crystal; alternate functions (USART3 PD8/PD9, CAN2 PB12/13, USB PA11/12, USART6 PC6/7, ADC channels, ADC3 on PA3) | OK except PB2 and PC13/14, see below |
| Wideband MCU | F042 pins against the rusEFI wideband `f0_module` firmware we flash (ADC channels, heater/pump PWM, LEDs, ESR, CAN, UART, ID straps) | Matches; floating ID straps give CAN index 0, as rusEFI expects |
| Datasheets | Every active part and sensor: supply, logic levels, current, thermal, pin functions (full notes: datasheet review, summarised below) | See findings |
| Engine simulation | `firmware/board/tests/test_miata_ecu.cpp`: the board's real configuration code inside rusEFI's unit-test engine, all five years (2001-02 and 2003-05 separately). Real NA CAS and NB2 crank+cam logic-analyser captures, plus running from cranking to 6500 rpm with realistic acceleration, then the rev limiter. Every output edge recorded and checked against crank angle | 18/18 tests pass |
| End to end | `firmware/tools/sim_report.py`: for each year, the tune the firmware builds → STM32 pin → driver → J1/J2 → motherboard → harness cavity, compared with the cavity the references say carries that function. The expected cavities are a hand-written table of the functions the firmware drives or reads (not purge, pressure regulator, VICS or power pins) | 117/117 OK (6 configurations) |
| Circuits | `firmware/tools/circuit_sim.py` (ngspice): hall inputs at 7200 rpm, 12 V switch inputs, CLT/IAT network −20…120 °C through the firmware's conversion, injector / idle-valve turn-off, knock amplifier | See findings |
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
3. **1989-93 automatics: 3Z (our 2Z) is the A/T control unit.** The firmware now leaves INJ3/INJ4 unassigned on
   1989-93, so nothing drives 3Y/3Z on a stock harness.
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
- **1989-93:** INJ1/INJ2 open twice per cycle, 180° apart.
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
- **1989-93 INJ3/INJ4 unassigned** (pinout finding 3).
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
  address gaps with leftover buffer data instead of 0xFF. In this build it only hits 30 bytes of unused padding
  (0x080081E8-FF), and each image's CRC covers its own fill, so it is harmless here; worth reporting upstream. (It also
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

## Hardware changes
### Needed before building
| # | Issue | Evidence | Fix |
|---|---|---|---|
| H1 | **Q1-Q8 AUIPS2041L inputs are driven at 3.3 V.** Recommended input-high is **4.0-5.5 V**; the threshold is 1.1/2.0/2.7 V min/typ/max, and on-resistance and over-current shutdown are specified only at 5 V. These drive the injectors, idle valve, VVT, boost and alternator | Datasheet (recommended operating conditions), read directly | 5 V buffer with 3.3 V-compatible inputs (e.g. 74AHCT541 on +5V) in front of the eight inputs, or use 3.3 V-logic protected low sides |
| H2 | **No freewheel diodes on the idle and VVT valve outputs.** Each PWM turn-off dumps the coil's energy into the switch's 63-75 V clamp. (Hellen's boards fit diodes on the idle valve.) | ngspice: idle valve at 200 Hz puts **3.4 W** into the clamp without a diode, 0 W with one | A diode (e.g. SS34) from OUT_IACV and OUT_VVT to VBAT_IN: both valves are fed from VBAT_IN (F2/F3 on NB) or the main relay on every year. **Not** on OUT_ALT: if the alternator field is fed from the battery, that diode would back-feed the ECU with the key off (see M5). OUT_BOOST is on the AUX header only, so its diode goes across whatever valve is fitted |
| H3 | **PB2 (BOOT1) floating.** DFU entry needs BOOT0 = 1 *and* BOOT1 = 0, so first flashing over USB is unreliable | Netlist: pin 37 unconnected | 10 kΩ PB2 → GND |
| H4 | **2003-05 key-off back-feed.** ULN2003 COM is tied to +12V, and on 2003-05 the main-relay coil is battery-fed and switched by the ECU (3H). With the ECU off, battery → coil → ULN clamp diode → +12V can partly power the ECU: a brown-out/restart loop, relay clicking and battery drain | Netlist (U5 pin 9 = +12V); the coil feed is from the research notes, confirm on a car | Take COM off the supply: a ~33 V zener/TVS from COM to GND instead (still clamps relay kick-back), or a separately clamped driver for MAINRLY |

### Recommended
| # | Issue | Fix |
|---|---|---|
| M1 | **1989-93: two injectors per output** (stock batch wiring): about 2 A. Simulated clamp loss is about 1 W at 7000 rpm, plus about 0.7 W conduction, against a 1.4 A continuous rating at 85 °C | Higher-current driver on INJ1/INJ2 of the 1989-93 board, or convert the harness to sequential |
| M2 | **Input transients.** The ignition feed D8 joins +12V *after* the TVS, so that path is unclamped. SMCJ30A clamps at 40-48 V at high current, against the LMR14020's 44 V absolute maximum. C16 (on +12V) is a **16 V** capacitor | TVS on +12V after D7/D8; C16 → 50 V part; consider a 60 V buck |
| M3 | **Fuel pump and main relay on PC13/PC14.** ST says these backup-domain pins must not source current; the ULN inputs draw about 0.7 mA each | Move to free pins (e.g. PD0/PD1) |
| M4 | **Switch inputs (VSS, A/C, clutch) only read signals driven to 12 V.** An open-collector or ground-switching signal never goes high (simulated: 0 V), and the NB VSS comes from the cluster as a hall-style signal. At 9 V cranking a 12 V signal gives 2.09 V: above ST's design threshold, below its tested one | Fit-option pull-ups on the motherboards (5 V or 12 V via 0R/DNP) |
| M5 | **NB alternator field drive unknown, and it is on by default.** rusEFI's NB presets enable alternator PWM. If the ECU drives the field coil directly (3-5 A, high inductance), the AUIPS2041 is undersized (rated 1.4 A, 10 mH maximum load inductance) and there is no freewheel path. If the switch failed shorted, the field would run at full strength with nothing regulating it | Measure the field current and its supply on a car (or check the FSM) before relying on ALT. Until then, watch charging voltage on the first start; turning alternator control off in TunerStudio is the safe fallback |
| M6 | **ULN2003 at full load**: 4 relays + NB1 VICS is about 0.7-1.6 W against 0.73 W at 85 °C ambient. Fine at cabin temperatures (the ECU sits in the passenger footwell) | Move VICS or the fans to a protected driver if space allows |

### Minor
- **Buck (LMR14020):** about 20 µF effective output capacitance, against 47 µF in TI's example; add output capacitance.
  The part number for L2 couldn't be confirmed; check its saturation current is at least 3.8 A.
- **AMS1117:** rated 0 °C minimum and about 125 °C junction at 85 °C ambient; consider an automotive-temperature
  LDO.
- **Crystal:** 22 pF load caps for a 20 pF crystal; about 33 pF is closer.
- **Wideband STM32F042:** VDDA (REF3033, 3.300 V) can sit below VDD (up to 3.365 V). This is inherited from the FOME
  module.
- **Unprotected outputs:** the TC4427 ignition and ULN2003 relay outputs have no short-to-battery protection (the
  AUIPS2041 outputs do).
- **Knock amplifier:** clips above about 284 mV input (gain 5.7). Fine at light load; consider lower gain.
- **MPX5700AP:** the 15.6 kΩ divider loads it beyond its 0.1 mA typical source current above about 210 kPa. Only
  relevant with boost.
- **NB charge-warning lamp** (NB1 1Q, NB2 3U) is not driven.
- **CAN transceivers** are rated to 85 °C. Their bus pins are rated −4 to 16 V absolute maximum, which a 24 V jump
  start exceeds.
- **PB3 at power-up.** PB3 drives the idle valve, but rusEFI's default board setup makes it the SWO trace output until
  the idle pin is configured. What it outputs in that window can't be told from the sources; check on the bench that
  the idle valve doesn't twitch at power-up. (PB4/INJ4: the internal pull-up against R22 gives 0.55-0.83 V, below the
  AUIPS2041's 1.1 V threshold, so it stays off.)
- **Voltage ratings near the TVS clamp.** F1/F2/F3 are 30 V parts and the buck's catch diode D9 is 40 V, against a
  TVS clamp of 40-48 V under a large transient.
- **O2 heater on OUT_VVT (1996-97, NB1)** is continuous DC. Its cold inrush may exceed the AUIPS2041's 1.4 A rating
  (unverified); the over-current shutdown would trip and the heater would warm slower.
- `design.py` describes Q1-Q8 as having a "39V clamp"; the AUIPS2041 clamps at 63-75 V. Fix the text in the next hardware revision (it is repeated in the schematic and BOM).

## Safety review: current, faults and fuses
**Fuses already on the boards:**
| Fuse | Board | Protects |
|---|---|---|
| F1, 2 A PTC | every motherboard | LSU heater supply |
| F2, 2 A PTC | NB1, NB2 | idle valve +12 V feed |
| F3, 2 A PTC | NB2 | VVT valve +12 V feed |

Everything else relies on the car's fuses: the EGI/ECU fuse feeding the main relay, plus the relay and lamp
circuits' own fuses.

**Normal current:**
| Load | Current |
|---|---|
| ECU logic | about 0.25 A at 13.8 V |
| LSU heater | about 0.6 A average once warm, ramped by the wideband firmware; up to about 4 A briefly when cold |
| Injectors (through the ECU's grounds) | about 1 A each at peak (2 A per output on 1989-93) |
| Idle valve, VVT valve | about 1 A each |
| Relays | about 0.18 A each through the ULN2003 |

None of these exceed their path's rating, except the 1989-93 paired injectors (M1).

**Faults:**
| Fault | What happens | Verdict |
|---|---|---|
| Sensor 5 V shorted to ground | TLS115 is current-limited | OK |
| Sensor 5 V or a crank/cam wire shorted to battery | TLS115 survives. But the hall inputs (PE7/PE8) are 5 V-tolerant pins with no clamp diode to the supply (absolute maximum about 7.3 V), so with almost no current flowing they sit near 14 V and will **likely be damaged**. It would also damage the MPX5700AP | Add a clamp: e.g. a 3.3 V zener or BAT54S to +3V3 on each hall input after the series resistor |
| Injector, idle, VVT, boost or alternator output shorted to battery | AUIPS2041 over-current shutdown, specified at 5 V input (see H1) | OK after H1 |
| Relay, CEL or tach output shorted to battery | ULN2003 has no limit: the channel fails | Minor (rare fault) |
| Ignition output shorted to battery | The TC4427 outputs already have 100 Ω (R15-R18). A short with the output low puts about 2 W into the 0805 resistor, so the resistor fails, which protects the TC4427 | Minor (rare fault) |
| Reverse battery | D7 blocks the logic supply. The TVS D6 conducts forward and acts as a crowbar until the car's fuse blows; it may fail short. Also, the body diodes of the low-side drivers (AUIPS2041, VND14NV04, ULN2003) conduct from the ECU grounds back through every load: injectors, idle valve, relays, LSU heater, which all switch on | Brief connection: fuse blows. A reverse-battery MOSFET on the input is the real fix, but the loads path can't be blocked at the ECU |
| Load dump / ignition transients | See M2 | Needs M2 |
| Key-off drain on 2003-05 | See H4 | Needs H4 |
| Internal short on the daughterboard 12 V rail | Only the car's 15-30 A fuse limits it | Add a fuse |
| Short on the AUX header J5 pin 15 (VBAT_IN brought off-board) | Unfused; only the car's 15-30 A fuse limits it | Add a PTC on J5 pin 15 |
| USB-only bench power | USB 5 V → D10 → +5V. The buck's high-side body diode may lift +12V to about 4 V. Harmless | OK |

**Recommended additions:**
1. A small fuse or PTC (about 0.75-1 A hold) on the daughterboard's +12V input, ahead of the buck and TLS115, so an
   internal fault can't wait on the car's 15-30 A fuse. This doesn't cover VBAT_IN itself (the heater and valve feeds
   have F1-F3), so also:
2. A PTC (about 0.5-1 A hold, to suit the AUX use) on J5 pin 15, the unfused VBAT_IN on the AUX header.
3. The idle and VVT freewheel diodes from H2. These remove the biggest thermal risk.
4. Clamps on the hall inputs, so a crank/cam wire shorted to battery can't destroy the main MCU.

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
