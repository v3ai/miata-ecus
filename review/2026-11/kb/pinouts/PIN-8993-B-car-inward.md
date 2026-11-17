# PIN-8993-B car inward: 1989-93 NA6 (1.6 L, 48-pin ECU) pinout chain audit

STATUS: complete (steps 1-3). Steps 2 and 3 follow step 1.

## STEP 1: factory pinout from external sources only

Sources (independent):
- S1 Mazda 1991 MX-5 wiring diagram "Fig. 2 Computer Engine Control (Grid 4-7)" (scan, mellens.net/mazda/Mazda-Miata-1991-1993/1991_wiring.pdf, page 4, file work/.../dl/wir91.pdf, crop pg/c1.png c2.png). PRIMARY. Read by eye plus pixel-column tracing (every wire line was matched to its connector box by x position: 22 boxes of conn #1 A..V, 26 boxes of conn #2 A..Z). Only 1991 shown (1989-90 and 92-93 not checked: UNVERIFIED for those years).
- S2 rusEFI wiki "1990 Mazda Miata" (wiki.rusefi.com/Mazda-Miata-1990/): plug tables; calls the 26-pin plug "Plug 3" with letters 3A..3Z that map to Mazda's 2A..2Z (colours match S1 for 3K..3Q, 3U..3W). Partial, has "?" entries.
- S3 allpinouts.org "1990-1995 Mazda Miata ECU": only 8 pins (1O, 2B, 2I, 2M, 2N, 2O, 2P, 2Q), derived from the factory diagram.
- S4 AMP/DIYAutoTune MSPNP2 MM9093 docs (megasquirtpnp.com mspnp_g2_mm9093): TPS wiring (2L signal, 2C ground, 1N 5 V), injector table, 1993 California note.
- S5 Haltech support article B6-ZE 89-93 (sensor/igniter/AFM/TPS/BAC connector level; its ECU pinout is an image, not read).
- S6 rusEFI MRE "Miata NA 48 pin board" wiki (jumper table JP54/JP55 2I tach pull-up; 1M VSS; 94+/93- jumpers) and hellen64_NA6_94 board files in ext/ (count as one source; they are 94-95 oriented: uses 3x naming, "For 1990-1993 M/T / A/T" resistor options on TPS cavities).
- Mazda FSM text of 1991 engine volume is scanned (no ECU terminal table found in 37 pages; not used).

Cavity naming: Mazda "CONN #1" = 22 cavities 1A..1V, "CONN #2" = 26 cavities 2A..2Z (22+26=48).
Electrical-character column is mostly UNVERIFIED (general knowledge of the Mazda EGI ECU; no primary electrical spec found) unless tagged.

### CONN #1 (colour per S1 VERIFIED-by-scan)
| Cav | Colour | Function | Dir | Electrical character | Variant notes |
|---|---|---|---|---|---|
| 1A | BLU-RED | Room fuse, permanent +B (memory/ keep-alive) | in | battery, always hot | S2 agrees (hot all times) |
| 1B | WHT-RED | Main relay output +12 V (injector, ECU power) | in | switched by main relay, supply for ECU + injector common | S2 agrees |
| 1C | VIO | Ignition-switch ON (IG1 / ST sign fuse line) | in | 12 V sense | S2 agrees; S1 shows VIO from fuse block "ST SIGN FUSE" |
| 1D | WHT-GRN | Diagnosis connector terminal (one of TEN/FEN group) | ? | open to diag connector | which of D/F/K is TEN vs FEN: S2 says 1K = TEN; S1 shows D, F, K all go to diag connector (LT GRN-YEL, WHT-GRN, WHT-YEL). UNRESOLVED which is FEN/monitor |
| 1E | YEL-BLK | Check-engine lamp (instrument cluster) | out | low-side sink, lamp fed 12 V | S2 agrees |
| 1F | WHT-YEL | Diagnosis connector terminal | ? | as 1D | |
| 1G | BRN-YEL | Igniter input IB1 (cyl 1&4 coil) | out | ECU drives igniter input; level 0-5 V logic (S2: "+5 V") | igniter pin B per S1 |
| 1H | BRN | Igniter input IB2 (cyl 2&3 coil) | out | as 1G | igniter pin G |
| 1J | BLU-BLK | A/C relay (compressor clutch relay) | out | low-side to relay coil | S2 lists 1J A/C relay (BLUE/BLACK) |
| 1K | LT GRN-YEL | Diagnosis connector TEN (per S2) | in | pulled up internally, grounded by test tool | |
| 1N | RED | Throttle switch contact (the RED wire on both the M/T 3-wire switch and the A/T 4-wire TPS in S1); S4 re-uses it as 5 V for an add-on TPS | in | contact to sensor ground (INFERRED: S1 shows common = BLK-LT GRN) | which contact (idle vs full) is not decidable from S1; S4/S2 disagree on role |
| 1O | GRN | Stop (brake) light switch | in | 12 V when braking | S2, S3 agree |
| 1P | BLU-YEL | Power-steering pressure switch | in | switch to ground | S2 agrees |
| 1Q | LT GRN-BLK | A/C thermo switch (A/C request) | in | 12 V sense | S2 agrees |
| 1R | BLK-GRN | Cooling fan relay (single relay, "COOLING FAN RELAY") | out | low-side | S2 "A/C extra cooling fan relay" BLK/GRN |
| 1S | BLU-ORG | Heater control unit (blower/defrost) | in | switch | S2 agrees |
| 1U | RED-BLK | not traced (carried to bottom of sheet) | | | UNRESOLVED |
| 1V | BRN-WHT (or BLK-BLU) | M/T: clutch + neutral switches (via cruise control); A/T: ignition-switch BLK-BLU | in | switch to ground | S1 bottom of sheet; "tail fuse" label sits near this pair: UNRESOLVED which of 1U/1V is tail fuse (S2: 1U) |
| 1I,1L,1M,1T | none | unused on 1991 | | | S2 lists 1L,1M as N/C. S6 uses 1M as VSS only for 94+ |

### CONN #2
| Cav | Colour | Function | Dir | Electrical character | Variant notes |
|---|---|---|---|---|---|
| 2A, 2B | BLK | Power ground | - | high-current return | S3 2B |
| 2C, 2D | BLK-LT GRN | Sensor ground (AFM, TPS, CTS, CAS) | - | | S4 2C ground |
| 2E | WHT | Crank angle sensor, 4x (SGT) | in | Hall effect (open collector, sensor powered from main relay 12 V); needs pull-up in ECU | S5: 4x white |
| 2F | none | unused | | | |
| 2G | YEL-BLU | Crank angle sensor, 2x (SGC / home) | in | as 2E | S5 yellow/blue |
| 2H | RED-WHT | California-only short connector (diagram "(CALIFORNIA ONLY) -> SHORT CONN") | ? | | traced by eye; low confidence |
| 2I | BLK-WHT | Igniter pin E (Haltech names igniter pin 5 "IGf" ignition-fail/confirm) | in (igniter -> ECU) | open-collector confirm pulse; ECU pull-up needed (S6 JP55 "2I tach pullup, used with stock coils") | tach to cluster is YEL-BLU from igniter pin D (TAC) direct, NOT via ECU in S1 |
| 2K | LT GRN-RED | +5 V sensor reference (AFM VC, TPS) | out | ~5 V regulated, sensors | S2 3K |
| 2L | LT GRN-WHT | Throttle switch / TPS signal, M/T (3-pin idle-switch type) | in | contact to ground, pull-up in ECU | S4 2L; Haltech: 3-pin M/T TPS is a switch only |
| 2M | RED-BLK | TPS signal A/T (4-pin, VTA analog 0.5-4.5 V) | in | analog | S3 2M |
| 2N | RED-BLU | Narrow-band O2 sensor | in | 0.1-0.9 V, own ground via sensor body | S3, S2 |
| 2O | RED | Vane airflow meter (VAF) signal | in | analog 0-~5 V with AFM VC 5 V | S3, S2 |
| 2P | RED-GRN | Intake air temp (in AFM) | in | NTC to sensor ground, ECU pull-up | S2 pull-up 2.7 k (UNVERIFIED) |
| 2Q | BLU-WHT | Coolant temp sensor (rear of head) | in | NTC + ECU pull-up | S2 |
| 2R,2S,2T | none | unused | | | |
| 2U | YEL | Injectors cyl 1 & 3 (paired, one wire) | out | low-side; both injector coils from WHT-RED main relay | S1 injectors 1 and 3 on YEL; 2 and 4 on YEL-BLK |
| 2V | YEL-BLK | Injectors cyl 2 & 4 (paired) | out | low-side | |
| 2W | BLU-ORG | Idle speed control (ISC) solenoid | out | low-side duty, solenoid fed WHT-RED | S2 |
| 2X | YEL-RED | Purge solenoid (S1); S2 says WHT/BLUE | out | low-side | S1 vs S2 colour disagreement |
| 2Y | none | unused on 1991 | | | per S4, 93 California ECU uses 2Y = cyl 3 injector |
| 2Z | LT GRN | A/T control unit (A/T only) | ? | | S1 and S2 agree |

Disagreements between sources: (a) 2X purge colour (YEL-RED S1 vs WHT/BLUE S2); (b) which diag cavity is TEN (S2: 1K) / FEN; (c) S2 labels tach on "3I" input; S1 says that cavity (2I) is BLK-WHT = igniter pin E, and the cluster tach wire (YEL-BLU) comes from igniter D; (d) S4 puts 5 V ref for an add-on TPS on 1N, S1/S2 put the stock +5 V on 2K; (e) S4: 93 California injectors 2U/2V/2Y/2Z (individual), S1 (1991) paired only.
Years: S1 is 1991. 1989-90 and 1992-93 variants only from S2/S4 text. Other: 1993 California individual injector wires and sequential (S4, UNVERIFIED).

Component-level facts (S1/S5): AFM connector: VC 5 V (LT GRN-RED), VS (RED), THA (RED-GRN), E2 (BLK-LT GRN), fuel-pump switch FC (LT GRN) / E1 (BLK) - FC is a contact in the AFM that makes the fuel pump relay (circuit opening relay) run when air flows, wired on the car harness side to the circuit opening relay LT GRN, not to an ECU cavity. The ECU controls no fuel pump relay directly on this year. Circuit-opening relay pin (VIO) shows the ST signal (starter) also energises the pump during cranking.


Extra S1 facts: S1 injector coils: both injectors of a pair get WHT-RED (main relay) on one side; AFM connector wires: LT GRN-RED (VC 5 V), RED (VS), RED-GRN (THA), BLK-LT GRN x2 (E2 -> 2C/2D), LT GRN (FC pump switch, to circuit-opening relay), BLK (E1). Fan: the only ECU fan wire is 1R BLK-GRN (1L has no wire in S1); S2 adds that the thermostat-housing water thermoswitch switches the fan itself at 97 C.

## STEP 2: board vs car, cavity by cavity (ordered rev 0.11 = ord_mb8993 + ord_db rev 0.9; current rev 0.13 jumpers where different)
Sources: kb/interconnect.md ord_mb8993 harness table + parts, fab BOM (JLC places only R23, R24, R29; R20-22, R25-R28, R30 hand-fit options), repo/motherboards/1989-95/README.md (after step 1), repo/firmware/board/miata_board.cpp, miata_pins.h.

| Cav | Car (S1) | Board (ordered 0.11) | Verdict |
|---|---|---|---|
| 1A permanent +B | BLU-RED | no net | OK for rusEFI (no keep-alive RAM need); loses ECU "memory" only. Info |
| 1B | main-relay +12 | VBAT_IN, F1 3 A, D1/D2, JD1.1/2 | OK |
| 1C | VIO ignition/ST | VIGN_IN (JD1.3) | OK as wire; firmware correctly does not use it as key-on (it is START only on 89-95 per repo comment; S1 labels it ST SIGN FUSE, consistent) |
| 1D, 1F, 1K | diag connector (TEN etc.) | no net | Function lost (see step 3). Not an error |
| 1E | CEL YEL-BLK | OUT_CEL, ZXMS6004 low side | OK |
| 1G / 1H | igniter IB1 / IB2, 0-5 V logic from ECU | OUT_IGN1/2: TC4427 5 V push-pull via 100R + Schottky, pull-down FET | OK, level and polarity match S2 "+5 V"; stock igniter input is active-high (rusEFI also) |
| 1J | A/C relay BLU-BLK | OUT_AC low side | OK |
| 1L | no wire in S1 | OUT_FAN (fanPin) | Harmless. Radiator-fan logic (fanPin) therefore not used; README hedges "early cars 1R, later 1L" (1L is the 94+ position per hellen). |
| 1R | fan relay BLK-GRN (the only ECU fan wire) | OUT_LS7 = fan2Pin (ordered: fixed, no JP3) | OK electrically; relies on fan2 thresholds: rusEFI NA6 preset sets fan2 on 95 C / off 91 C (mazda_miata_1_6.cpp:284) vs fan1 100 C. Fan also runs from the stock thermoswitch, so no overheating hazard |
| 1M | no wire (VSS only 94+) | IN_SW1 VSS | harmless, spare |
| 1N | RED throttle-switch contact | HARN_1N, R28 (to 5 V) not fitted | Checked, correct: R28 would short V5_EXT to ground through the closed switch. Never fit with stock switch (README says so) |
| 1O stop light, 1P PS pressure sw, 1S heater control | inputs | no net | Functions lost (step 3) |
| 1Q | A/C thermo sw (LT GRN-BLK) | IN_SW2 22k/10k divider, R21 pull-up not fitted | Polarity of the car signal not verifiable here (UNVERIFIED); with R21 absent it works only if the car drives 12 V |
| 1V | M/T: BRN-WHT clutch + neutral switches to ground; A/T: BLK-BLU = ignition switch 12 V | IN_SW3, R22 pull-up not fitted | M/T: the switch-to-ground never produces a level change without R22 (input sits low). A/T: input is 12 V with key on -> "clutch down" permanently if firmware polarity is active high. Low impact (INFERRED) |
| 1U | RED-BLK (not traced) | no net | unknown (UNVERIFIED) |
| 2A-2D | power GND (2A,2B), sensor GND (2C,2D) | all GND, one plane | OK electrically; sensor ground not separated (low risk, INFERRED) |
| 2E / 2G | CAS WHT (4x, SGT) / YEL-BLU (2x, SGC) Hall open collector | IN_HALL1 / IN_HALL2, 1k pull-up to 5 V through Schottky, clamp 3.3 V (miata_pins.h) | OK. Firmware: primary = HALL2 (2x), secondary = HALL1 (4x); matches S5 colour assignment |
| 2F | no wire | GND | harmless (README calls it AFM ground; S1 AFM grounds are 2C/2D) |
| 2H | RED-WHT California short connector | no net | harmless |
| 2I | BLK-WHT = igniter pin E, igniter -> ECU (S1, Haltech igniter table "IGf"); tach goes igniter pin D YEL-BLU -> cluster directly | ordered 0.11: OUT_TACH hard-wired to 2I (ZXMS6004 drain to 2I, no JP5, no pull-up); firmware NA6 preset sets tachOutputPin = Unassigned | The review brief open item (direction unresolved) is RESOLVED by S1: input from igniter. Ordered board is harmless only because firmware never drives it: FET off = high-Z. If the tach output is enabled (wrong preset/TunerStudio) the FET pulls the igniter confirm line low. Current 0.13 has JP5 (open) fixing that |
| 2K | +5 V ref out (AFM VC + A/T TPS) | V5_EXT protected 5 V | OK |
| 2L | M/T throttle switch contact LT GRN-WHT (S4 uses it as TPS signal) | HARN_2L; R29 (fitted) to IN_AUX1; R27 pull-up not fitted | OK for no-TPS manual car; the switch is not read without R27 |
| 2M | A/T TPS RED-BLK analog | IN_TPS | OK |
| 2N | narrowband O2 RED-BLU | IN_AUX2 | Input only, firmware does not use it (wideband on board). Stock sensor stays connected, harmless |
| 2O | AFM VS (RED), ~0-5 V | HARN_2O -> IN_AUX3 (ordered: direct net IN_AUX3, no JP6), mafAdcChannel = AUX3, 5.6k/10k divider x1.56 | OK |
| 2P | AFM IAT RED-GRN, NTC | JP1 select (ordered) -> IN_IAT, 2.7k pull-up to 5 V | OK; S2 also 2.7k (UNVERIFIED value) |
| 2Q | CLT BLU-WHT NTC | IN_CLT, 2.7k pull-up | OK |
| 2T | no wire | OUT_FP | documented (INSTALL.md:170) |
| 2U | YEL inj 1&3 (about 1.8 A per wire per repo) | OUT_INJ1 + R23 -> OUT_INJ4 (both drivers on one wire), D3 SMCJ30A | OK. Batch mode, both drivers switch together. Matches S1 pairing |
| 2V | YEL-BLK inj 2&4 | OUT_INJ2 + R24 -> OUT_INJ3, D4 | OK |
| 2W | ISC BLU-ORG, solenoid fed WHT-RED | OUT_IACV low side + SS34 flyback to VBAT_IN | OK (same supply as the valve) |
| 2X | purge YEL-RED (S2: WHT/BLU) | OUT_VVT + SS34 flyback; no firmware function on NA6 | valve stays closed; documented no purge |
| 2Y | none on 1991; 93 CA cyl 3 (S4, UNVERIFIED) | HARN_2Y via R25 (not fitted) | OK |
| 2Z | A/T control unit LT GRN | HARN_2Z via R26 (not fitted) | OK; R26 must stay off on automatics (README says so) |

No wiring error found in the ordered 1989-93 harness table against S1. Where the repo text and S1 disagree: fan cavity statement (README "1L radiator fan" vs S1 only 1R), "2F = AFM ground" (S1: 2C/2D), 1D/1F/1K diag.

## STEP 3: what the stock ECU did that this board does not (89-93)
1. Diagnosis connector (1D, 1F, 1K; TEN/FEN/monitor): no flash-code self diagnosis, no TEN-grounded base-timing/idle-check mode; a shop or owner cannot set base timing the Mazda way with a timing light: use rusEFI's fixed-timing test mode instead. Driver notices nothing while driving. (function of TEN: UNVERIFIED from memory)
2. Fuel pump: still controlled by the AFM contact via the circuit-opening relay (S1); ECU has no pump wire. Works only while the vane AFM stays; if removed the pump does not run (documented INSTALL.md:170).
3. Vane AFM: read on 2O (AUX3) with the on-board divider; 5 V from 2K; IAT on 2P. Fine.
4. Throttle: M/T has only idle/full switch contacts (2L, 1N); the board does not read them in the default build (R27/R22-style pull-ups unfitted): the stock ECU used them for idle/decel/enrichment. Effect: no throttle-closed decel fuel cut or idle-switch idle logic until a TPS is fitted (documented). A/T: 2M TPS is read; 1N idle contact ignored.
5. Igniter/tach: stock ECU received the igniter confirm (IGf) on 2I and, per Mazda logic, may use its absence for fault handling (UNVERIFIED). Board ignores it. Tach itself is untouched (igniter -> cluster). No risk of tach loss.
6. Injectors 2U/2V paired: reproduced with two drivers (0.11) or one (0.13). 93 California separate wires: R25/R26 options.
7. A/C: request 1Q and relay 1J present; the stock ECU also idled-up and cut the compressor at full throttle/hot; board has the relay only with rusEFI logic. Polarity of the 1Q signal needs checking (R21).
8. Single fan relay on 1R: driven by fan2 logic; stock thermoswitch still works.
9. ISC 2W: closed-loop duty drive present (IM_AUTO preset). Frequency not verified vs the Mazda valve.
10. Purge 2X (California and also US 1990 per S2) and EGR: valve closed, no purge (documented; evaporative canister fills, may hiss/ pressure; no CEL).
11. Stop light 1O, power steering 1P, heater control 1S: no idle-up; driver notices RPM dip when turning at standstill / blower+defrost load; closed-loop idle recovers after a sag. 1M (VSS) is a spare input on 89-93 and could take 1P with a jumper.
12. Automatic (2Z, 1V ignition feed, 1N): A/T control unit signal not handled; automatics untested (documented).
13. 1A constant +12 V: no memory backup.

## Sources actually read
Mazda 1991 wiring PDF (page 4, Fig. 2) via mellens.net; wiki.rusefi.com/Mazda-Miata-1990 and the MRE NA 48-pin page; allpinouts.org 1990-1995 Mazda Miata ECU; megasquirtpnp.com MM9093 docs (g2 and gP); support.haltech.com NA6 89-93 article; ext/hellen-miata-NA6 schematic text; kb/interconnect.md ord_mb8993; evidence/ord_mb8993 and cur_mb8995 pcb_footprints.csv and fab BOMs; repo/firmware/board/miata_board.cpp, miata_pins.h; repo/motherboards/1989-95/README.md; repo/INSTALL.md grep; ext rusefi mazda_miata_1_6.cpp.

## Not checked
miata.net pinout PDF (Cloudflare blocked); Link, ME221/442, ECUMaster, AEM pinouts (no text found); 1989, 1990, 1992, 1993 factory diagrams (only 1991); AMP and Haltech pinout images (images only); electrical specs (pull-up values, igniter IGf output stage, ISC coil resistance/frequency, diag connector TEN/FEN function) not from primary sources; 1N/1U/2H traced only by line position; daughterboard schematic circuits beyond net names.
