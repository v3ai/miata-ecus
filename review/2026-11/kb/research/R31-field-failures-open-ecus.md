# R31 - Field failures and support history of comparable open ECU products

Status: complete for the scope reached (2026-11-16). Limits are in "Not checked".

## Summary (10 lines)

1. The public record is dominated by *installation errors* and *assembly/BOM problems*, not by silicon dying in normal use (Speeduino forum: "hundreds out there, issues are generally user error"; rusEFI Hellen trackers: shorted sensor 5 V, wrong firmware, wrong chips).
2. The single most damaging Miata-specific class: **unprotected 5 V sensor outputs** (stock TPS left connected, sensor 5 V shorted) killed a Hellen NA6; fix = tracker regulator. The project has a protected harness 5 V (U14, README rev 0.8).
3. **Ignition / EMI class**: rusEFI hardware faulted ("red FATAL", USB descriptor failure) next to a 3-phase fan VFD, "smoke" incidents (M73 board, IGBT set on fire), long dwell (460 ms) at sync loss on uaEFI. Maintainers' mitigations: HW watchdog/CSS ideas, USB isolators, dedicated ignition IC. No board-level cure was found in the threads (open issues).
4. **Output drivers**: ULN2003-class low sides do not survive a short to +12 V (hellen-one #360); injector-driver second sources are not pin-compatible (NB2 #34); alternator push-pull output fed back into MCU pins (NB2 #23).
5. **Power input**: H72 crowbar MOSFETs short at about 22 V on the bench (hellen-one #47): load-dump circuits fail short, taking the fuse/supply with them.
6. **JLCPCB assembly**: poor joint + flux blob (NA6 #29), diode-polarity queries (NA6 #23), substituted op-amp LMV324 for MCP6004 (NB2 #4). No "rotated parts" case found for rusEFI Miata boards: the class exists generally but I did not find a public case (not found != absent).
7. **Bootloader/USB**: F407 DFU failure from slow 8 MHz crystal start (fix 20 MHz crystal); boards from different batches differ on auto-reboot after DFU (rusefi #4847). The project's crystal choice should be checked by the owner (not read by me).
8. **Wideband**: uaEFI WBO blue-blink was a poorly pinned cable; WBO stuck in underheat when ECU powered from USB only (wideband #71, still open); LSU sensor life complaints are generic, not board-specific.
9. Frequency data are not available: trackers hold tens of issues per board, not unit counts; I rank classes by number of independent reports only.
10. Support plan implications are at the end (production test list, bring-up checklist, spare/replacement policy).

## Method

- Sources mined: GitHub issues of rusEFI / FOME / Speeduino hardware and firmware repositories (unauthenticated
  REST API + the public issue pages), rusEFI wiki and forum, Speeduino forum, Miata owner forums, vendor pages.
  Local clones under `ext/` for board changelogs.
- Tags: VERIFIED (read today in the primary source: the issue thread / wiki page / design file itself),
  INFERRED (reasoning shown), UNVERIFIED (memory / single post / hearsay).
  Note: "VERIFIED" for a field-failure case means *the report exists and says this*; the root cause is only as good
  as the diagnosis in the thread (stated per case).
- Raw downloads: `work/R31-field-failures-open-ecus/dl/`; documents worth re-checking: `kb/research/files/R31/`.

## Case log (preliminary, first pass over the rusEFI Miata board trackers)

| # | Product | What failed | Root cause (per thread) | Fix | Source | Tag |
|---|---|---|---|---|---|---|
| C1 | Hellen NA6 (H64 rev B) | Board "bricked" during install; 5 V rail part lifted, MCU module damaged | Customer left the stock (non-variable) TPS connected: sensor 5 V pin 1N shorted to ground; "no circuit protection on any of the +5v outputs" | rev C added protection (TLS115 tracker on sensor 5 V) | https://github.com/rusefi/hellenNA6_issues/issues/22 ; https://github.com/andreika-git/hellen-one/issues/119 | VERIFIED |
| C2 | Hellen NB2 (H72) | "Pin error while driving"; STM32 runs hot, pins to TC4427 measure 2-20 ohm to 3V3/GND | Alternator field output (TC4427 push-pull) fed energy back into the MCU pins; bad alternator PID suspected as contributor | 1k series MCU->TC4427 input, 100R + 100n on output ("output-0.3" module); later the extra 1k on the output had to be removed because the alternator stopped charging (NB1 #29) | https://github.com/rusefi/hellen-NB2-issues/issues/23 ; https://github.com/andreika-git/hellen-one/issues/118 ; https://github.com/rusefi/hellen-NB1-issues/issues/29 | VERIFIED |
| C3 | Hellen (all F407 boards) | Would not enter DFU (software and sometimes button) | F407 ROM bootloader waits ~800 us for HSE; the 8 MHz crystal locked in ~900 us -> bootloader resets | 20 MHz crystal (starts in ~250 us) | https://github.com/andreika-git/hellen-one/issues/79 ; https://github.com/rusefi/hellen-NB2-issues/issues/5 | VERIFIED |
| C4 | Hellen NA6 rev B | Wideband analog input reads 0 V | JLC assembly defect: poor joint on a resistor + dried flux blob on the MCU pin | hand rework; no process change recorded | https://github.com/rusefi/hellenNA6_issues/issues/29 | VERIFIED |
| C5 | Hellen NA6 / NA8-96 | BOOT button dead | Poor solder joint, pad too small for the SMD button | larger pads | https://github.com/rusefi/hellenNA6_issues/issues/25 | VERIFIED |
| C6 | Hellen NA6 (JLC order) | JLC queried diode polarity (D418/D420) "a few different errors reported by JLC during production" | Placement/polarity data ambiguity | none recorded | https://github.com/rusefi/hellenNA6_issues/issues/23 | VERIFIED |
| C7 | Hellen NB2 rev D | Built with LMV324 instead of MCP6004 (cannot reach the rails; TPS reads wrong) | Chip shortage substitution + ordering error | chips replaced by hand; BOM pinned | https://github.com/rusefi/hellen-NB2-issues/issues/4 ; https://github.com/andreika-git/hellen-one/issues/63 | VERIFIED |
| C8 | Hellen NB2 rev E | Substitute injector driver ZXMS6005 not pin-compatible with AUIPS2041 when the tab is used | Second-source part with a different tab function | footprint changed in rev F | https://github.com/rusefi/hellen-NB2-issues/issues/34 ; https://github.com/andreika-git/hellen-one/issues/147 | VERIFIED |
| C9 | Hellen NB2 / NA6 | SD card not seen | Board revision moved the card from SPI3 to SPI2; firmware could not tell revisions apart | board-ID resistor read by firmware | https://github.com/rusefi/hellen-NB2-issues/issues/36 | VERIFIED |
| C10 | Hellen NB2 rev C | Red LEDs lit with key in a "weird" position | Board back-powered through an output's diode from a wire that is live before the ECU supply (A/C) | diodes moved in series with LEDs; "consider any LS output as a potential external power source" | https://github.com/rusefi/hellen-NB2-issues/issues/20 | VERIFIED |
| C11 | Hellen NA6 rev D | Critical error at boot after MCU package change (176 -> 144 pin) | LED pins differ between MCU variants, firmware pin validation trips | firmware change | https://github.com/rusefi/hellenNA6_issues/issues/35 | VERIFIED |
| C12 | Hellen NB1 used with NB2 firmware | "HARDWARE VALIDATION FAILED" | Customer flashed the wrong board's firmware | support: use the right bundle | https://github.com/rusefi/hellen-NB2-issues/issues/44 | VERIFIED |
| C13 | Hellen NB2 | "Trigger sync" loss at 6500 rpm after a firmware update | Coincidence: failing cam sensor on the car | sensor replaced | https://github.com/rusefi/hellen-NB2-issues/issues/42 | VERIFIED |
| C14 | Hellen NB1 rev B | Alternator stops charging then overshoots to 17-18 V | 1k + 100R in series on the alternator output (added by the C2 fix) | 1k removed | https://github.com/rusefi/hellen-NB1-issues/issues/29 | VERIFIED |
| C15 | Hellen NA6 | Flex fuel reading drops to 0 until power cycle | Firmware regression (fixed by newer firmware) | firmware | https://github.com/rusefi/hellenNA6_issues/issues/27 | VERIFIED |

## Case log (preliminary, first pass over the rusEFI Miata board trackers)

| # | Product | What failed | Root cause (per thread) | Fix | Source | Tag |
|---|---|---|---|---|---|---|
| C1 | Hellen NA6 (H64 rev B) | Board "bricked" during install; 5 V rail part lifted, MCU module damaged | Customer left the stock (non-variable) TPS connected: sensor 5 V pin 1N shorted to ground; "no circuit protection on any of the +5v outputs" | rev C added protection (TLS115 tracker on sensor 5 V) | https://github.com/rusefi/hellenNA6_issues/issues/22 ; https://github.com/andreika-git/hellen-one/issues/119 | VERIFIED |
| C2 | Hellen NB2 (H72) | "Pin error while driving"; STM32 runs hot, pins to TC4427 measure 2-20 ohm to 3V3/GND | Alternator field output (TC4427 push-pull) fed energy back into the MCU pins; bad alternator PID suspected as contributor | 1k series MCU->TC4427 input, 100R + 100n on output ("output-0.3" module); later the extra 1k on the output had to be removed because the alternator stopped charging (NB1 #29) | https://github.com/rusefi/hellen-NB2-issues/issues/23 ; https://github.com/andreika-git/hellen-one/issues/118 ; https://github.com/rusefi/hellen-NB1-issues/issues/29 | VERIFIED |
| C3 | Hellen (all F407 boards) | Would not enter DFU (software and sometimes button) | F407 ROM bootloader waits ~800 us for HSE; the 8 MHz crystal locked in ~900 us -> bootloader resets | 20 MHz crystal (starts in ~250 us) | https://github.com/andreika-git/hellen-one/issues/79 ; https://github.com/rusefi/hellen-NB2-issues/issues/5 | VERIFIED |
| C4 | Hellen NA6 rev B | Wideband analog input reads 0 V | JLC assembly defect: poor joint on a resistor + dried flux blob on the MCU pin | hand rework; no process change recorded | https://github.com/rusefi/hellenNA6_issues/issues/29 | VERIFIED |
| C5 | Hellen NA6 / NA8-96 | BOOT button dead | Poor solder joint, pad too small for the SMD button | larger pads | https://github.com/rusefi/hellenNA6_issues/issues/25 | VERIFIED |
| C6 | Hellen NA6 (JLC order) | JLC queried diode polarity (D418/D420) "a few different errors reported by JLC during production" | Placement/polarity data ambiguity | none recorded | https://github.com/rusefi/hellenNA6_issues/issues/23 | VERIFIED |
| C7 | Hellen NB2 rev D | Built with LMV324 instead of MCP6004 (cannot reach the rails; TPS reads wrong) | Chip shortage substitution + ordering error | chips replaced by hand; BOM pinned | https://github.com/rusefi/hellen-NB2-issues/issues/4 ; https://github.com/andreika-git/hellen-one/issues/63 | VERIFIED |
| C8 | Hellen NB2 rev E | Substitute injector driver ZXMS6005 not pin-compatible with AUIPS2041 when the tab is used | Second-source part with a different tab function | footprint changed in rev F | https://github.com/rusefi/hellen-NB2-issues/issues/34 ; https://github.com/andreika-git/hellen-one/issues/147 | VERIFIED |
| C9 | Hellen NB2 / NA6 | SD card not seen | Board revision moved the card from SPI3 to SPI2; firmware could not tell revisions apart | board-ID resistor read by firmware | https://github.com/rusefi/hellen-NB2-issues/issues/36 | VERIFIED |
| C10 | Hellen NB2 rev C | Red LEDs lit with key in a "weird" position | Board back-powered through an output's diode from a wire that is live before the ECU supply (A/C) | diodes moved in series with LEDs; "consider any LS output as a potential external power source" | https://github.com/rusefi/hellen-NB2-issues/issues/20 | VERIFIED |
| C11 | Hellen NA6 rev D | Critical error at boot after MCU package change (176 -> 144 pin) | LED pins differ between MCU variants, firmware pin validation trips | firmware change | https://github.com/rusefi/hellenNA6_issues/issues/35 | VERIFIED |
| C12 | Hellen NB1 used with NB2 firmware | "HARDWARE VALIDATION FAILED" | Customer flashed the wrong board's firmware | support: use the right bundle | https://github.com/rusefi/hellen-NB2-issues/issues/44 | VERIFIED |
| C13 | Hellen NB2 | "Trigger sync" loss at 6500 rpm after a firmware update | Coincidence: failing cam sensor on the car | sensor replaced | https://github.com/rusefi/hellen-NB2-issues/issues/42 | VERIFIED |
| C14 | Hellen NB1 rev B | Alternator stops charging then overshoots to 17-18 V | 1k + 100R in series on the alternator output (added by the C2 fix) | 1k removed | https://github.com/rusefi/hellen-NB1-issues/issues/29 | VERIFIED |
| C15 | Hellen NA6 | Flex fuel reading drops to 0 until power cycle | Firmware regression (fixed by newer firmware) | firmware | https://github.com/rusefi/hellenNA6_issues/issues/27 | VERIFIED |
| C16 | H72b (power12 module) | Pop and dead short at ~22 V on a bench supply; 0.5-0.7 ohm fault | Crowbar MOSFET(s) failed short (TVS tested fine); maintainer: problem is in power12 module, same on B and C; ISO test B 35 V expectation questioned | none recorded in thread; h72c uses a supply "much closer to proteus" | https://github.com/andreika-git/hellen-one/issues/47 | VERIFIED (report), cause per reporter |
| C17 | hellen-one output module | Weak low sides have no current limit; ULN2003 would not survive a short to +12 V | design | module marked deprecated | https://github.com/andreika-git/hellen-one/issues/360 | VERIFIED |
| C18 | hellen-one power12 | Documentation lists limits: >24 V may damage module, >30 V blows ext. fuse, reverse polarity blows fuse, V12/VBAT have no short protection | design | documentation | https://github.com/andreika-git/hellen-one/issues/121 | VERIFIED |
| C19 | hellen-one modules | Solder can bridge IC pad to opened (unmasked) module pad | mask openings for debug | open | https://github.com/andreika-git/hellen-one/issues/66 | VERIFIED |
| C20 | hellen88bmw (4-layer) | Red FATAL / USB descriptor failure with laptop on top of 3-phase VFD fan box, ECU 6 ft away; reproduced with a single USB-C cable and with USB extension | EMI via USB; maintainer "never seen on a Proteus" | none; open question how to reproduce | https://github.com/rusefi/rusefi/issues/4310 ; forum https://www.rusefi.com/forum/viewtopic.php?p=48645 | VERIFIED (report) |
| C21 | Proteus (Jeep 4.0) | TunerStudio link lost, USB "unknown device" as soon as engine runs; 3 cables, laptop charger on/off | ground loop / charger; owner and a forum user cured with a cheap ADuM3160 USB isolator | USB isolator | https://www.rusefi.com/forum/viewtopic.php?p=47554 | VERIFIED (report); fix single post |
| C22 | rusEFI smoke incidents (M73 board; Proteus + harness patch cord, IGBT set on fire) | Hardware damage / PCB fire | not established. Patch-cord case: all 23 wires twisted together made VR input pick up ETB motor pulses | firmware test showed ignition pins go low on error/hard fault; HW watchdog planned; later issue #6349 | https://github.com/rusefi/rusefi/issues/5728 ; /5729 ; /5723 ; forum p=48645 | VERIFIED (reports), cause UNVERIFIED |
| C23 | uaEFI | Dwell 150-460 ms at sync loss while cranking ("could damage components") | firmware | issue open at read time | https://github.com/rusefi/rusefi/issues/6349 | VERIFIED |
| C24 | all F4 boards | Oscillator short halts CPU; CSS (clock security system) switches to HSI; stuck-active ignition outputs possible with PLL/clock failure; "use special IC (MC33810)" | MCU clock failure | tests/issues | https://github.com/rusefi/rusefi/issues/5730 ; forum p=48645 | VERIFIED (discussion) |
| C25 | rusEFI hellen boards | Auto-reboot after DFU upload differs between two assembly batches with the same MCU part number | unknown | open | https://github.com/rusefi/rusefi/issues/4847 | VERIFIED |
| C26 | Frankenso NB1 | Startup pin-state error on tach pin PE8 | firmware self-test not performed for "open collector"; not hardware (discovery removed) | firmware | https://github.com/rusefi/rusefi/issues/3558 | VERIFIED |
| C27 | uaEFI WBO | Green on, blue blinks once, heater red then silence | poorly pinned cable | re-pin | https://github.com/rusefi/wideband/issues/65 | VERIFIED |
| C28 | rusEFI wideband F042 | Falls into SensorUnderheat with no way out when ECU powered from USB (heater supply 0 V) and "force heating" is set | firmware logic | fix merged then re-opened in 2026 series (#71 open, #83 closed, #84 open) | https://github.com/rusefi/wideband/issues/71 | VERIFIED |
| C29 | rusEFI wideband single units | Single units transmit as dual (IDs 190-193) | firmware image | user-built firmware | https://github.com/rusefi/wideband/issues/67 | VERIFIED |
| C30 | microRusEFI R0.5.3 | Battery-sense wire to +12 V -> FATAL, link drops; main-relay low side stops working | not diagnosed (damage suspected, firmware suspected) | none in thread | https://www.rusefi.com/forum/viewtopic.php?p=50032 | VERIFIED (report), UNVERIFIED cause |
| C31 | microRusEFI | USB device not recognised (code 43) via ECU pigtail USB wires; worked on micro-USB direct | wiring of USB through harness, driver | direct USB | https://rusefi.com/forum/viewtopic.php?p=41108 | VERIFIED (report) |
| C32 | Speeduino 0.4.4c | Ignition channels dead, LEDs lit solid, intermittent first, after long trouble-free use | not found; Mega swapped, coil swapped | new board suggested | https://speeduino.com/forum/viewtopic.php?t=4426 | VERIFIED (report), cause UNKNOWN |
| C33 | Speeduino UA4C / SpeedyEFI Miata PNP | Fuel pump driver killed because installer left the fuse in; IAC needs flyback diode; forum consensus "user error" | installation | IC replaced | https://speeduino.com/forum/viewtopic.php?t=4583 | VERIFIED (report) |


## Failure classes: frequency, root cause, fix, and mapping onto this project

Frequency = number of independent public reports found (small samples; not unit rates).

| Class | Reports found | Root causes seen | Hardware/process fix upstream | Project status (README claims, not verified by me) | Prevent by |
|---|---|---|---|---|---|
| Sensor 5 V shorted/overloaded | C1 (1 destroyed board, NA6) | stock TPS left connected, no protection | tracker regulator on sensor 5 V (NA6 rev C) | README rev 0.8: second TLS115 U14 protected harness 5 V, MAP on separate regulator (INFERRED covered) | production test: short sensor 5 V to GND and confirm board survives; install guide: remove/identify stock TPS wiring |
| Output drivers | C2, C8, C10, C17 | alternator push-pull output backfeed; second-source driver pin mismatch; backfeed via output diode; ULN2003 not short-proof | series R, protected drivers, diode placement | README: VND7NV04 injectors, ZXMS6004FF protected low sides, ignition Schottky (D31-D34), alternator ships off; rev 0.9 ordered boards lack 220 ohm (documented). Alternator output risk: C14 shows adding 1k on output broke charging. | do not add series R on an alternator field line without testing; do not accept substituted driver parts from JLC |
| Ignition outputs stuck/long dwell, coil/igniter damage | C22-C24, C32 | clock/PLL failure, sync loss dwell, EMI | HW watchdog, dwell limit, dedicated ignition IC (proposed) | design has per-channel ZXMS pull-down and series Schottky, but no hardware dwell limiter was found in README (INFERRED, not searched) | bench test: stop the MCU clock (short the oscillator) and see ignition pins; firmware max-dwell check; first start with a spare coil/igniter |
| Power supply / load dump | C16-C18 | crowbar MOSFET fails short at ~22 V; no short protection on rails | process: bench-test the over-voltage behaviour | README: 150 C TVS, PTC fuses rated 24-33 V (documented open item) | production sample test of 24 V jump-start case with current limit; fuse before first power-up |
| USB drop / reset from noise | C20, C21, C30, C31 | USB cable, laptop charger ground loop, VFD, harness wiring of USB | USB isolator (user side) ; 4-layer; HSE issues | none known; ordered db is 4-layer, current 6-layer. USB-C on motherboard (review brief) | support doc: "use a battery-powered laptop or an isolator"; ship a short shielded cable; test with a coil running on the bench |
| Trigger noise / sync loss | C13, C22 (twisted wires) | failing sensor; wiring of VR next to actuator wires | wiring practice | stock harness reuse reduces this | INSTALL: leave stock routing; log sync errors in support template |
| Wideband faults | C4, C27-C29 | flux/solder joint, cable pinning, firmware states, ID | firmware | wideband is on-board; FOME circuit copied; new layout | production test with an LSU simulator/real sensor: heater, pump, CAN or analog out; verify behaviour on USB power only |
| Connector/solder | C4, C5, C19, C27 | JLC joints, small pads, unmasked pads, poorly pinned cable | larger pads | hand-fitted TH parts by seller: continuity test of every harness pin | 100% continuity test of every connector pin to net, using kb/interconnect.md |
| SD/logging | C9 | board revisions on different SPI | board-ID resistor | project has microSD on SPI2 | firmware on correct board ID; test SD on every unit |
| Processor lockup / bootloader | C3, C24, C25 | HSE start time vs ROM bootloader; clock failure | 20 MHz crystal; CSS | crystal not checked by me | DFU test on every unit before shipping |
| Firmware update bricking | C12 | wrong board firmware | firmware board validation | project builds its own firmware | one firmware per board, version string on label |
| JLCPCB assembly errors | C4, C6, C7 | polarity data, substitutions, flux | manual rework; pinned BOM | not seen: rotated-part case for rusEFI; | review JLC preview of every placement, X-ray/inspect first article, forbid substitutions |
| ESD on arrival | none found | | | | ESD bag + test on receipt |
| User wiring errors | C1, C33, C22 | | | | install checklist, first-power with current-limited supply |

## Implications for this project

1. (info/risk, medium confidence) The class with the most hardware destruction in rusEFI Miata history is a short on sensor 5 V; the project's README says it has protected harness 5 V. Test it on every unit as a production step. Evidence C1.
2. (risk, medium) Ignition stuck-on after MCU clock/PLL failure is an open topic upstream; add a bring-up test (stop clock, check ignition outputs low) on the first article and a firmware dwell cap. Evidence C23-C24.
3. (ux, high) Prepare a support note on USB drops: laptop charger/ground loop, use of ADuM3160-type isolator or battery operation, cable length. Evidence C20-C21.
4. (risk, medium) A load-dump/crowbar that shorts at 22 V happened on H72; confirm the project's transient parts at 24 V jump start with a current-limited bench (README already lists PTC fuse rating as open).
5. (process, high) JLCPCB: pin the BOM (no substitutions), inspect first article for flux/joints; rotated-part problems are documented only as polarity queries upstream.
6. (ux, medium) Put per-unit test list in the shipping flow: continuity of hand-fitted connectors, sensor-5 V short test, DFU entry, SD card, wideband heater test, USB power-only behaviour (wideband #71).
7. (risk, low) Do not add series resistance to alternator field output (C14).

## Sources actually read

GitHub pages (saved in work/R31-field-failures-open-ecus/dl/): the URLs in the case table; rusEFI forum p=41108, 47554, 48645, 50032; Speeduino forum t=4583, t=4426. Earlier pass: hellen NA6/NB1/NB2 issue trackers (JSON in dl/).

## Not checked

- GitHub search API was rate-limited, so issue sweeps for uaEFI/Proteus/wideband hardware repos were partial.
- No Miata forum (miata.net, 3si) owner threads read; no Hellen vendor errata/wiki hardware revision pages read; Speeduino GitHub issues not read (search returned none).
- Failure frequencies per unit are not available publicly.
- Not verified whether the project's crystal, USB filtering or watchdog features exist; mapping statements marked INFERRED rely on README.
- Only the first 3500 chars of the Speeduino threads were read; no case of ESD on arrival or JLC rotated parts for rusEFI boards was found.
