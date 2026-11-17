# PIN-9697-B car inward: 1996-97 NA8 (1.8 L OBD-II, 76-position ECU) pinout chain audit

STATUS: COMPLETE (steps 1, 2, 3 all done; no in-progress placeholders).

## STEP 1: factory pinout from external sources only (done before opening repo tables)

### Sources
- S1 PRIMARY: Mazda 1996 MX-5 1.8 L "Engine Control Module (ECM)" wiring diagram, 2 sheets (images 81753 / 81754, Mazda-style factory diagram), as hosted by the rusEFI wiki page "1996 Mazda Miata" (https://wiki.rusefi.com/Images/diagrams/1996_miata_1.8_1.png and _2.png; local dl/ in work dir). Read by eye, zoomed crops (work/PIN-9697-B-car-inward/c1a-c, c2a-c.png). Colours and destinations VERIFIED-by-scan; the function of each wire is INFERRED from the component at the far end (the diagram has no terminal-function table). US 1.8 OBD-II ECM, one diagram for M/T and A/T (A/T lines marked "A/T ONLY").
- S2 rusEFI wiki "1996 Mazda Miata" table (https://wiki.rusefi.com/Mazda-Miata-1996/): partial; uses its own plug naming (Plug1 22 pin; Plug2 12 pin "not used on OEM ECU"; Plug3 16 pin; Plug4 26 pin).
- S3 hellen-miata-NA8 board netlist (github rusEFI/hellen-miata-NA8, hellen64_NA8_96.xml, downloaded; counts as ONE source with S2's maintainers): J=P2 178780-1 76-pin, gives which cavities the rusEFI board reads as which function. It names the four plugs 1 (22) / 2 (16) / 3 (26) / 4 (12 aux), i.e. its "2x" = Mazda "3x", its "3x" = Mazda "4x" (VERIFIED by comparing: MAF/TPS/CLT/IAT/+5 V/ground colour-matched 2B/2F/2G/2K/2I/2O vs Mazda 3B/3F/3G/3K/3I/3O).
- S4 AMP/DIYAutoTune MSPNP2 MM9697 install doc (ampenginemanagement.com .../mspnp2-mm9697-v2-installation; in dl/amp2.txt): only jumper text (J4 "Connector J3 pin 4S" A/C fan / VICS, J6 "tach out on J3 pin 4I" for 95.5+) - those text are copied from the 94-95 doc: they do not match the 96-97 factory diagram (4S, 4I are NC / +B-backup there). Used only as a warning.
- S5 search snippet (not opened, page unreachable ECONNREFUSED): autorepairshq 1996 MX-5 FSM "Electrical Specifications / Camshaft Position Sensor" lists ECM signal "4F 4 pulses/rev, 4G 2 pulses/rev" (UNVERIFIED, search-engine snippet only). Haltech NA8 / Link / ECUMaster / AEM pinout PDFs were not retrievable (Haltech page = images; others no 96-97 plug-in). So there are two real factory-derived sources (S1, S2/S3) plus snippets; the electrical character column is therefore mostly INFERRED from sensor types/general Mazda knowledge. I state UNVERIFIED where so.

Cavity naming used here = Mazda's (S1): connector 1 = 22 cavities 1A-1V; connector 3 = 16 cavities 3A-3P; connector 4 = 26 cavities 4A-4Z; connector 2 (12 cavities) is NOT used on the car's ECM (S1 shows no 2x; S2 agrees). 22+12+16+26 = 76.
Used on car per S1: conn1 19 (all but 1F, 1N, 1S), conn3 14 (all but 3A, 3E), conn4 22 (all but 4K, 4M, 4S, 4Z) = 55 wired cavities (the "72 used" count in the task is the header's, not the car's).

### CONN 1 (22)
| Cav | Colour | Function (far end) | Dir | Electrical character | Variant |
|---|---|---|---|---|---|
| 1A | BLK/GRN | Cooling fans system (fan relay(s) coil) | out | low-side sink to relay coil, coil fed 12 V (INFERRED) | S2 says "Radiator fan 1" |
| 1B | BLU/WHT | A/C system | ? | INFERRED A/C related (relay control or amplifier) | S2 "Radiator fan 2"- disagrees |
| 1C | VIO | Starting/charging system (ignition/start-switch related 12 V sense) | in | 12 V level sense (INFERRED) | |
| 1D | WHT/BLK | Data-link: goes to Data Link Connector WHT/BLK (FEN) and DLC-2 WHT/BLK (OBD-II diag pin) | out | K-line / FEN monitor: open collector/ISO 9141 (UNVERIFIED), 12 V pull-up in tester | OBD-II addition |
| 1E | YEL/BLK | Check-engine lamp (cluster 1C) | out | low-side sink, lamp fed 12 V | |
| 1F | - | not used | | | |
| 1G | BLU/BLK | A/C system | ? | | |
| 1H | RED/BLK | Headlights system | in | 12 V sense (load-on input, INFERRED) | |
| 1I | LT GRN/YEL | Data Link Connector (TEN) | in | pulled up in ECU, grounded by tool | |
| 1J | RED/WHT | Defogger system | in | 12 V sense (INFERRED) | |
| 1K | LT GRN/BLK | A/C system (A/C switch / request) | in | 12 V sense (INFERRED) | S3 reads 1K as IN_AC_SW |
| 1L | BRN/WHT | M/T: starting/charging system (clutch/neutral switch); A/T: transmission system | in | switch to ground or 12 V (UNVERIFIED) | variant |
| 1M | GRN/RED | Instrument cluster 2F "VSS INPUT" (vehicle speed) | in | pulses (cluster-buffered speed signal; level UNVERIFIED) | |
| 1N | - | not used | | | |
| 1O | BLK/LT GRN | Sensor ground (to junction/G119, MAF, cam sensor) | - | analog reference return | |
| 1P | BLU/ORG | A/C system | ? | INFERRED A/C compressor relay/clutch control | |
| 1Q | GRN/BLK | Brake switch (stop-lamp feed, brake switch GRN) | in | 12 V when braking | |
| 1R | GRN | Transmission system (A/T only) | ? | | A/T |
| 1S | - | not used | | | |
| 1T | GRN/BLU | Transmission system (A/T only) | ? | | A/T |
| 1U | LT GRN | Fuel pump relay coil + DLC FP terminal | out | low-side sink to relay coil (relay coil other end WHT/RED = +B) | |
| 1V | - | no colour on the 1V row; a WHT/GRN wire (fuel-inj fuse, hot at all times, from main relay) runs past it to "starting/charging system": re-checked, that wire is NOT an ECM pin (INFERRED); treat as not used (S2 agrees) | | | |

### CONN 3 (16): sensor connector
| Cav | Colour | Function | Dir | Electrical | Variant |
|---|---|---|---|---|---|
| 3A | - | not used | | | |
| 3B | RED/WHT | Mass air flow sensor signal (MAF, RED/WHT at sensor) | in | analog 0-5 V (UNVERIFIED) | S2/S3 agree (MAF) |
| 3C | RED/GRN | Front HO2S (left rear of engine) signal | in | 0-1 V narrowband, ref at sensor ground | OBD-II: heated, S3 IN_AFR |
| 3D | RED/BLU | Rear HO2S (below left of vehicle) signal | in | 0-1 V | OBD-II addition, S3 IN_O2S2 |
| 3E | - | not used | | | |
| 3F | RED/BLK | TPS signal | in | analog 0.5-4.5 V (UNVERIFIED) | S2 agrees; S3 IN_TPS |
| 3G | BLU/WHT | Engine coolant temp sensor (top of engine) | in | NTC, ECU pull-up | S2 agrees |
| 3H | BRN/BLK | EGR boost sensor terminal | in | analog (signal), role INFERRED | OBD-II addition |
| 3I | LT GRN/WHT | +5 V sensor reference (TPS, EGR boost, EGR valve position, A/T) | out | 5 V regulated | |
| 3J | LT GRN/RED | EGR valve position sensor signal | in | analog | OBD-II addition |
| 3K | RED/BLK | MAF-sensor connector 2nd signal = intake air temp (INFERRED: MAF has IAT) | in | NTC divider | S3 IN_IAT |
| 3L | RED | TPS idle-switch (TPS 4th terminal), also to A/T | in | switch to ground | |
| 3M | RED/WHT | Front HO2S heater control (the remaining front-HO2S terminal; INFERRED) | out | low-side sink; heater fed from BLK/YEL (meter-fuse ignition 12 V) | OBD-II addition. Alternative reading from the symbol: heater between BLK/BLU and RED/GRN: UNRESOLVED |
| 3N | BLK/YEL | EGR boost sensor 2nd terminal (role unclear) | ? | | |
| 3O | BLK/BLU | Sensor ground (TPS, ECT, EGR pos, EGR boost, HO2S refs) | - | | S2 3O ground |
| 3P | BLU/YEL | Power-steering pressure switch | in | switch to ground (INFERRED) | |
Rear HO2S: terminals BLK/BLU, RED/BLU (3D), BLK/YEL (+12 V), BLK (chassis G407): so the rear heater seems NOT driven by the ECM (always on with ignition) - INFERRED.

### CONN 4 (26)
| Cav | Colour | Function | Dir | Electrical | Variant |
|---|---|---|---|---|---|
| 4A | BLK/LT GRN | ECM signal ground (G119) | - | | |
| 4B | WHT/RED | +B from main relay (powers ECM, injectors, solenoids, MAF, cam sensor, fuel pump relay contacts) | in | 12 V switched, high current (4 injectors + 3 solenoids + sensors) | S2: 4B Power |
| 4C | BLK | Power ground (G119) | - | high-current return | |
| 4D | BLK | Power ground (G117) | - | high-current return | |
| 4E | YEL/BLK | Crankshaft position sensor | in | see crank note | S2 agrees |
| 4F | WHT | Camshaft position sensor + A/T transmission system | in | see cam note | |
| 4G | YEL/BLU | Camshaft position sensor | in | see cam note | |
| 4H | YEL/WHT | Crankshaft position sensor | in | | |
| 4I | BLU/RED | Room fuse: permanent +B (keep-alive memory) | in | 12 V always hot, low current | |
| 4J | YEL/GRN | PRC solenoid valve (pressure regulator control, front right of engine) | out | low-side; solenoid fed WHT/RED | OBD-II-era part |
| 4K | - | not used | | | |
| 4L | BLK/WHT | Instrument cluster system (tach signal) | out | open-collector pulse (UNVERIFIED) | |
| 4M | - | not used | | | |
| 4N | BRN/YEL | Ignition coil #1 (cyl 1&4) input (coil pack with igniter: coil has BLK, BLU +12 ign, BRN/YEL) | out | logic-level drive of built-in igniter (UNVERIFIED level) | S2 colour GRN: disagrees |
| 4O | YEL | EGR solenoid valve (vent) | out | low-side | OBD-II addition |
| 4P | YEL/WHT | EGR solenoid valve (vacuum) | out | low-side | OBD-II addition |
| 4Q | BLU/ORG | Idle air control valve | out | low-side PWM/duty | S2 agrees |
| 4R | BRN | Ignition coil #2 (cyl 2&3) input | out | as 4N | S2 agrees |
| 4S | - | not used | | | |
| 4T | YEL/RED | Purge solenoid valve | out | low-side | OBD-II addition |
| 4U | YEL | Injector #1 | out | low-side; injector fed WHT/RED | S2 colour WHT, disagrees |
| 4V | YEL/BLK | Injector #2 | out | low-side | S2 YEL |
| 4W | GRN/WHT | Injector #3 | out | low-side | |
| 4X | GRN | Injector #4 | out | low-side | |
| 4Y | BLU/YEL | Transmission system (A/T only) | ? | | A/T |
| 4Z | - | not used | | | |

Notes: (a) crank: S1 sensor box has coil symbol, 3 terminals YEL/WHT, YEL/BLK, BLK/LT GRN with shield (GRY): reads as 2-wire variable reluctance pair + shield, with no sensor 12 V: INFERRED; the cam sensor has 4 terminals (WHT/RED +12 from main relay, YEL/BLU, WHT, BLK/LT GRN): two signal outputs (S5 snippet: 4F 4 pulses/rev, 4G 2 pulses/rev, UNVERIFIED) so a Hall type with +12 V supply. S3 treats the 3F/3G (Mazda 4F/4G) as the inputs and gives 3G a 4.7 k pull-up. Disagreement S1/S3: S3 names 4F "IN_CRANK", S1 shows 4F WHT on the cam sensor; the crank pair per S1 is 4E/4H. RESOLUTION PENDING for Step 2.
(b) +5 V: 3I only. (c) no immobiliser line in S1 (US car: none). (d) no cruise, no alternator-field, no VSS output other than 1M.

Main relay: S1 shows the main-relay coil fed from the ignition-switch ENGINE fuse (BLK/WHT) and grounded, no ECM pin on it: the relay is ignition-switched, ECM does not control it (INFERRED from tracing; repo research says the same). Coil packs (2): each has 3 wires only: BLK ground, BLU +12 V ignition, and the ECM input (BRN/YEL, BRN). No ignition-confirm (IGf) line exists in 1996-97 (unlike 1989-95 2I).

## STEP 2: cavity-by-cavity comparison with cur_mb9697 / ord_mb9697 (kb/interconnect.md lines 374-452 and 1433-1511) and firmware

Both boards have identical harness netlists except 3K (ordered: HARN_IAT -> JP1 pin 1; current: IN_IAT direct). Board circuit facts: R20-R22 (4.7 k to VBAT_IN) are NOT FITTED options (scripts/mb_common.py:111, mb_readme.py:123); D1 SS34 freewheel from 4Q to VBAT_IN; all four ground cavities 1O/3O/4A/4C/4D are one GND net; 3I = V5_EXT (J5.14, JD1.13, R35).
Firmware: miata_board.cpp:329-333 (NA96 preset), :93-95 pin assignments, :330 comment "VVT driver runs the front O2 heater (3M)"; trigger: primary 2-pulse HALL2, secondary 4-pulse HALL1 (setInputs, miata_board.cpp ~108).

Legend: OK = matches factory; NOTE = works, remark; GAP = factory function absent; RISK = could be wrong/harmful.
| Cav | Board net -> daughter pin -> MCU function | Factory character (S1) | Verdict |
|---|---|---|---|
| 1A | OUT_FAN JD1.9 -> MIATA_FAN PE5 protected low side | BLK/GRN fan relay coil low-side | OK |
| 1B | OUT_LS7 JD1.12 -> PE2 low side, firmware fan2Pin | colour BLU/WHT, S1 says only "A/C system"; S2 "radiator fan 2"; Hellen "AC fan relay" | RISK (low): function unconfirmed; if it is an A/C-compressor-related control, hot-coolant fan2 logic would also engage it (UNVERIFIED) |
| 1C | none | VIO start/IG-switch related sense | GAP (low): no cranking/start signal; rusEFI uses RPM |
| 1D | none | FEN/K-line diag out to DLC + DLC2 | GAP: no OBD-II scan tool communication |
| 1E | OUT_CEL JD1.10 -> PE4 low side | check-engine lamp low-side | OK |
| 1G | OUT_AC JD1.8 -> PE6 low side, acRelayPin | BLU/BLK "A/C system"; direction unconfirmed | NOTE: relies on Hellen/DIY; S1 cannot confirm direction |
| 1H | none | RED/BLK headlight load sense | GAP (low): no idle-up on headlights |
| 1I | none | LT GRN/YEL DLC TEN (test-enable) | GAP: harmless open; stock self-test mode unavailable. Repo research calls 1I "unknown, never drive": S1 resolves it as TEN |
| 1J | none | RED/WHT defogger load sense | GAP (low): no idle-up |
| 1K | IN_SW2 -> A/C switch input, PE10 via 22k/10k; R21 pull-up not fitted | LT GRN/BLK A/C system, sense (12 V-driven) | OK (no pull-up needed for 12 V-driven signal; level/polarity UNVERIFIED) |
| 1L | IN_SW3 -> clutch switch | BRN/WHT clutch switch (M/T) or A/T trans | OK on M/T; A/T: line carries A/T signal, rusEFI reads it as clutch: NOTE |
| 1M | IN_SW1 -> VSS PE9 via 22k/10k | GRN/RED to cluster 2F "VSS input" | OK (level UNVERIFIED) |
| 1O | GND | BLK/LT GRN sensor/signal ground (to G119 splice) | NOTE: S1 shows it is the signal ground; board merges it with power ground (all 5 ground cavities one net) - few mV ground shift, low |
| 1P | none | BLU/ORG "A/C system" | GAP (unknown): untouched; if it is an ECM-driven A/C control the A/C may not engage; test needed |
| 1Q | none (repo has brake switch unconnected on 96-97) | GRN/BLK brake switch (12 V when braking) | GAP (low): brake input not wired; repo research lists 1Q "brake switch input (medium)" but board has no net: rusEFI brake use (idle/cruise) unavailable |
| 1R, 1T, 4Y | none | A/T only (GRN, GRN/BLU, BLU/YEL) to transmission system | GAP on automatics (see step 3) |
| 1U | OUT_FP -> PC14 (backup domain pin) | LT GRN fuel pump relay coil low-side (+ DLC FP) | OK; low side |
| 3B | IN_AUX3 -> PB1 ADC via 5.6k/10k (x1.56) | RED/WHT MAF signal, MAF sensor powered 12 V | OK for 0-5 V signal (UNVERIFIED range) ; unused by speed-density preset |
| 3C | IN_AUX2 -> PB0 front O2 | RED/GRN front HO2S signal 0-1 V, ref BLK/BLU | OK (narrowband read only; 15.6 k load on a cold ceramic sensor irrelevant) |
| 3D | IN_AUX1 -> PC5 rear O2 | RED/BLU rear HO2S | OK |
| 3F | IN_TPS -> PA4 | RED/BLK TPS 0.5-4.5 V, Vref 3I | OK |
| 3G | IN_CLT -> PA6 with 2.7 k to V5_EXT | BLU/WHT NTC | OK |
| 3H, 3J, 3N | none | EGR boost / EGR valve position sensor wires | GAP (EGR absent; no harm, no OBD-II) |
| 3I | V5_EXT 5 V out | LT GRN/WHT 5 V ref (TPS, EGR x2, TCM) | OK; A/T TCM also loads it |
| 3K | IN_IAT (cur) / HARN_IAT->JP1.1 (ord) | RED/BLK IAT NTC in MAF connector | OK: ordered board: IAT only reaches ADC with shunt on JP1 1-2 (documented, default EXT) |
| 3L | none | RED TPS idle switch + TCM | GAP (low); repo research mislabels 3L "ground, probably MAF signal ground": S1 shows RED to TPS idle switch terminal |
| 3M | OUT_VVT JD1.34 -> PD7 low side; firmware o2heaterPin=PD7 | RED/WHT front HO2S heater control, heater fed from ignition-switched BLK/YEL | OK; matches repo (confirmed independently). Heater current UNVERIFIED (typ. 1-2 A) |
| 3O | GND | BLK/BLU sensor ground | NOTE as 1O |
| 3P | none | BLU/YEL power-steering pressure switch | GAP: no PS idle-up; repo has it unconnected on 96-97 |
| 4A, 4C, 4D | GND | signal ground, 2 x power ground | OK |
| 4B | VBAT_IN: SS34 D1, F1 3A, F4 1.1 A, R20-22 (n/f) | +B from main relay; injectors, IAC, solenoids fed from the same rail in the car | OK; NOTE the board now also draws wideband-heater (F1 3 A) through this single cavity: current UNVERIFIED vs cavity rating |
| 4E, 4H | none | crank-pulley VR pair (OBD-II misfire sensor, shielded) | GAP by design: not needed; matches repo and Hellen. Independent check: S1 shows the pulley sensor as a separate 3-terminal part from the cam-driven sensor |
| 4F | IN_HALL1 -> PE7, pull-up 1 k to harness 5 V via Schottky | WHT: 4-pulse signal of the 4-terminal sensor (WHT/RED +12 V, YEL/BLU, WHT, ground); S1 also routes WHT to the A/T unit | OK: open-collector Hall on 12 V-supplied sensor, 5 V pull-up fine (UNVERIFIED output type); repo's resolution 4F = 4-pulse crank-angle (SGT) matches S5 snippet 4F = 4/rev, 4G = 2/rev. rusEFI wiki 'Cam' label for 4F disagrees (wiki is wrong per this) |
| 4G | IN_HALL2 -> PE8 | YEL/BLU: 2-pulse signal | OK |
| 4I | none | BLU/RED room fuse, permanently hot (S1: wire 29 joins the room-fuse BLU/RED at the fuse block) | RESOLVED: repo research row 4I says "CONFLICT, low, never drive": S1 shows it is permanent +B (keep-alive). Open on board is correct; GAP: no keep-alive supply (rusEFI does not need it) |
| 4J | none | YEL/GRN PRC solenoid (fuel-pressure regulator control, UNVERIFIED role) | GAP: see step 3 |
| 4L | OUT_TACH JD1.11 -> PE3 low side | BLK/WHT to instrument cluster (tach) | OK if the cluster tach input is open-collector style (UNVERIFIED; no electrical spec found; ECU output is the only driver) |
| 4N | OUT_IGN1 JD1.14 -> PE1 TC4427 5 V push-pull via 100 R + Schottky, protected pull-down | BRN/YEL input of coil-pack igniter | OK: coil packs with igniters built in (3 wires). Drive 5 V logic UNVERIFIED vs igniter threshold; matches Hellen |
| 4O, 4P, 4T | none | EGR vent (YEL), EGR vacuum (YEL/WHT), purge (YEL/RED) solenoids, fed WHT/RED | GAP (OBD-II emission items); solenoids stay de-energised = EGR closed, purge closed |
| 4Q | OUT_IACV + SS34 D1 | BLU/ORG idle air control valve low side, WHT/RED feed | OK |
| 4R | OUT_IGN2 -> PE0 | BRN coil 2&3 | OK; S2 colour for 4N (GRN) wrong vs S1 (BRN/YEL) |
| 4U-4X | OUT_INJ1..4 JD1.19/22/25/28 | one wire per injector, low side, fed WHT/RED; S1 colours 4U YEL, 4V YEL/BLK, 4W GRN/WHT, 4X GRN | OK (S2's colours WHT/YEL for 4U/4V disagree with S1; function identical) |
| 4Z | none | not used | OK (research table claims "rear HO2S heater control": not in S1, only Hellen) |

## STEP 3: what the stock ECU does that this board does not (and consequences)
1. Two heated O2 sensors: the board reads front (3C) and drives the front heater (3M), reads rear (3D). Rear heater is not ECM-driven in S1 (BLK/YEL + chassis BLK). No catalyst/O2 monitors: nothing for the driver to notice; no MIL for a dead sensor (rusEFI shows none). Front narrowband is only informational because the on-board wideband is the AFR source.
2. EGR system (vent 4O, vacuum 4P solenoids, boost sensor 3H/3N, position sensor 3J): not driven or read. Driver notices: nothing; NOx higher and no EGR-related drivability change; inspection fails anyway.
3. Purge (4T): not driven: canister is never purged (fuel vapour stays in the canister, may saturate; possible fuel smell, no driveability). PRC solenoid (4J): never energised: if it is the fuel-pressure boost for hot restart (UNVERIFIED role) a long hot restart is possible.
4. K-line / DLC: 1D (FEN, to DLC-2) and 1I (TEN) unconnected: no scan tool, no readiness monitors, cannot pass OBD-II smog test (already documented "no OBD-II"). Not harmful to the car. The DLC "FP" terminal (LT GRN) is on the 1U net, so the fuel-pump jumper works as stock.
5. Crank/cam: factory has a cam-driven 4-terminal Hall sensor (12 V from main relay WHT/RED, 4-pulse 4F and 2-pulse 4G) and a separate crank-pulley VR sensor (4E/4H) for OBD-II misfire detection. Board uses the cam-driven pair (right) and ignores the pulley sensor: engine runs; no misfire detection. The cam sensor's 12 V supply is the car's own, so the board does not supply it.
6. Ignition: coil packs with built-in igniters, two inputs 4N/4R; board drives them 5 V logic. No IGf feedback line in the car. If the igniter input threshold differs (UNVERIFIED) misfire/no-spark would result; the same as Hellen's approach.
7. Fuel pump relay 1U and fan relay 1A: driven; main relay: ignition-switched in the car, so the ECU cannot hold power after key-off (no after-run), same as stock. No ECU-controlled pump priming safety beyond firmware.
8. Immobiliser: none shown in the 1996-97 diagram (no connector 2, no transponder line) -> none to emulate. (Matches the repo's statement that the US car has no immobiliser; UNVERIFIED for other markets.)
9. Idle-up loads: headlights 1H, defogger 1J, power steering 3P, brake 1Q, start 1C not read: on the stock car the ECU raises idle when headlight/defroster/power-steering load appears; here only closed-loop idle PID reacts: small idle dip/hunting when loads switch on (inferred).
10. Automatic transmission: 1R, 1T, 4Y (GRN, GRN/BLU, BLU/YEL) plus 4F/3I/TPS runs to the TCM; board does not connect 1R/1T/4Y: the TCM-ECM communication (probably torque-reduction/ load/ fault lines, UNVERIFIED content) is lost: possible harsh shifts/ limp mode and A/T MIL; repo: automatics untested/unsupported.
11. Sensors: MAF remains powered by the car (12 V WHT/RED) but unused by speed-density; stock IAT in the MAF only used if JP1 on STOCK.
12. Keep-alive memory 4I and start signal 1C: no learned-adaptation memory kept (rusEFI stores tune in flash): nothing for driver.

## Disagreements between sources (S1 factory diagram is the reference)
- 4N colour: S1 BRN/YEL vs S2 GRN; 4U/4V colours S1 YEL / YEL/BLK vs S2 WHT / YEL; 4F: S1 WHT shown on the cam-drive sensor with 4-pulse (S5) vs S2 "cam" and hellen "crank": function 4-pulse signal (reconciled).
- Plug naming: S3 (Hellen) numbers the plugs 1 / 2(16) / 3(26) / 4(12 option); S2 and S1 call them 1 / 3(16) / 4(26) / 2(12 unused). The repo follows S1/S2 numbering (4B = power). Repo research text claims "Hellen 2x/3x/4x = OEM 2x/3x/4x (same names)" in pinouts_9605.md:206 for the 2001-05 only; for 96-97 line 7 says Hellen 3x = OEM 4x: consistent.
- 1B function: S1 "A/C system", S2/S3 fan: unresolved.
- Pinouts of other manufacturers (Haltech/Link/ECUMaster/AEM): not retrievable (images or none for 96-97); MSPNP2 doc text copied from the 94-95 doc (references 4S, 4I as tach/J4) is wrong for 96-97 and must not be used.

## Sources actually read
- https://wiki.rusefi.com/Mazda-Miata-1996/ and https://wiki.rusefi.com/Images/diagrams/1996_miata_1.8_1.png, _2.png (dl/), https://wiki.rusefi.com/Miata
- github rusEFI/hellen-miata-NA8 hellen64_NA8_96.xml, bom_replace_64_NA8_96-a.csv (work dir dl/na8)
- https://ampenginemanagement.com/blogs/mspnp2-documentation/mspnp2-mm9697-v2-installation (text)
- web search snippets only: diyautotune 96-97 page, autorepairshq FSM snippet (UNVERIFIED)
- Repo (step 2 only): kb/interconnect.md 374-486, 1433-1544; repo/firmware/board/miata_board.cpp, miata_pins.h; rusefi mazda_miata_na8.cpp; repo/research/pinouts_9605.md 39-114; scripts/mb_common.py; evidence/ord_mb9697 BOM; motherboards/1996-97/README.md.

## Not checked
- Electrical levels (igniter threshold, tach input, VSS, A/C, brake) have no primary electrical spec: not found (FSM terminal-voltage tables not reachable; autorepairshq ECONNREFUSED).
- Haltech/Link/ECUMaster/AEM ECU pinouts for 96-97: not obtained. M/T vs A/T, Federal vs California differences, 1997 vs 1996 changes: the diagram covers one version only (UNVERIFIED for others).
- Daughterboard schematic-level circuits behind each JD pin (current limits, clamps): not re-derived (other audits).
- Heater current and cavity current rating, HO2S pin roles (BLK/BLU vs RED/GRN heater/sensor terminal ordering) resolved by inference only.
