# R20 - Electrical interface data of stock Miata sensors and actuators, 1989-2005

Date of reading: 2026-11-16. Tags: VERIFIED = read today in a primary source (workshop manual page), INFERRED = reasoning shown, UNVERIFIED = memory/forum/search snippet.
Coverage is PARTIAL (see "Not checked"): the sources that were reachable give resistances, terminal voltages, pulse counts and sensor wiring; they do NOT give drive frequencies, inductances, opening times, flow rates or the cluster tach threshold. Those gaps are stated as gaps, not guessed.

## Summary
1. 1989-93 (1.6): crank/cam angle sensor is "Optical pickup" (1990 manual spec table); ECU Ne on 2E and G on 2G, 0/5 V levels (R16 terminal table; rusEFI shape file gives the NA 4/2-slit pattern). Pull-up is in the ECU (rusEFI wiki NA48: 2.7k pull-up to 5 V on the crank angle inputs, per the Hellen/MRE board; UNVERIFIED for the stock ECU value).
2. 1994-95 and 1996-97 CAS: ECU pins SGT (2E / 4F) "approx. 5.0 V, 4 pulses per revolution" and SGC (2G / 4G) "approx. 5.0 V, 2 pulses per revolution" (CHARM 1994, 1995, 1996 spec pages, VERIFIED). Sensor supply voltage and output transistor type not stated by any page read (the repo says "hall/open collector, 12 V fed"; UNVERIFIED).
3. 1996-97 additionally has a separate crank-pulley sensor NE on 4H/4E with resistance 500-600 ohm at 20 C (CHARM 1996, VERIFIED) = a two-wire magnetic (VR) sensor by the resistance (INFERRED). The repo leaves it unconnected (mb_na96.py:30, VERIFIED) - consistent with it being used only for OBD-II misfire/crank-pulley monitoring (UNVERIFIED purpose).
3b. 2001-05 (2004-05 Mitchell manual "BP"/"BP with TC"): CKP, CMP and MAF are 3-wire sensors: terminal A = power from MAIN RELAY terminal D (switched battery), B = signal to PCM, C = PCM ground (4A). CKP air gap 0.5-1.5 mm to a 4-projection plate (VERIFIED, Mitchell 2005 pp.76-82 and CHARM 2002 CKP page; text at kb/research/files/R20/mitchell2005_engine_control_system.txt lines 2986-2990, 3181-3184, 2710-2714). So the sensors are fed ~12 V, not 5 V; the signal is a PCM-pulled-up open-collector style output swinging ~0 to ~5 V (scope image, INFERRED).
4. Temperature sensors (ECT and IAT) 1994-2005: 2.21-2.69 kohm at 20 C; ECT 0.287-0.349 kohm at 80 C (1994/1996 CHARM, 2005 Mitchell p.73 "2.27-2.74 / 0.29-0.34"). 1990: -20 C 13.6-18.4 kohm (IAT), 60 C 493-667 ohm (VERIFIED, 1990 manual OCR).
5. Injectors: 12-16 ohm at 20 C in every year 1990-1996 (1990 manual, Mitchell 1994, CHARM 1994/95/96) = high-impedance, voltage drive. No 1999-2005 value was obtained (CHARM 2002 spec page returned an error). Flow, inductance, opening time: NOT found in any primary source.
6. IAC solenoid: 11-13 ohm (1990 manual spec table), 10.7-12.3 ohm (CHARM 1994, 1996). Purge solenoid 23-27 ohm (1990, 1994, 1996). Fuel pressure control solenoid (1994) 23-27 ohm. Ignition coil primary 0.78-0.94 ohm (Mitchell 1994 specs, VERIFIED) - igniter inputs are bases at ~659 ohm per R16.
7. 2004-05 PCM has more actuators than the repo documents: EGR valve as four coil drives 2E/2F/2H/2I (a stepper, "EGR valve coil control #1-#4"), EVAP leak-detection pump 3K and its solenoid 4AH, EGR boost-sensor solenoid 3D, VTCS solenoid 2N, VTCS vacuum switch input 4J, fuel gauge sender input 4AD, immobilizer serial 3S, K-line 3Q. (VERIFIED, Mitchell 2005 BP table lines 1190-1640.) 2001-05 differences between model years are R19's.
8. Alternator 1999-2005: PCM 3M "generator field coil control" duty 0-100 % (PID ALTF) and 4T "generator output voltage (terminal P)" read ~14 V at idle per the PID table (ALTT V) but "3-8 V at idle, no load" per the terminal table - the manual disagrees with itself; do not design from the terminal table alone. 3U drives the charge lamp low.
9. Switch polarity (2005): brake 4B 0 V released / B+ pressed; PSP 4C B+ straight / <1 V turned; neutral 4H <1 V in neutral; clutch 4I B+ pedal depressed; A/C request 4F <1 V when A/C and fan on (low = on); outputs fan 2B/2C, A/C relay 2K, fuel pump relay 2M, main relay 3H are low-side (<1 V = on), main relay 3H B+ when ignition off.
10. Tach: the 1989-95 NA6/NA8 tach is driven by the igniter, the ECU only provides a pull-up (rusEFI wiki NA48 section 2.4; consistent with R16 finding, VERIFIED page read). 1996+ tach signal comes from PCM (3O in 2001-05, pulse train about 2 pulses/rev at idle, see below). Cluster threshold voltage: NOT found.

## 1. Reference table by year group
Legend: V = volts at the ECU terminal. "Key" = key on engine off.

### 1.1 Crank / cam sensors
| Group | Sensor | ECU pins | Signal | Pattern / pulses | Source |
|---|---|---|---|---|---|
| 1989-93 | Crank angle sensor in distributor, "Optical pickup" | 2E Ne, 2G G | 0/5 V; idle ~2 V (Ne), ~1.5 V (G) on a DMM (R16) | rusEFI NA shape: cam-speed, 4 + 2 slit windows over 720 deg (edges listed in trigger_mazda.cpp lines 27-55) | wm1990 spec OCR kb/research/files/R20/wm1990_F92_spec_ocr_excerpt.txt ("Crank angle sensor / Optical pickup", VERIFIED); R16 terminal table (VERIFIED from its sources); repo/firmware/ext/rusefi/firmware/controllers/trigger/decoders/trigger_mazda.cpp (VERIFIED) |
| 1994-95 | CAS on intake cam end | 2E SGT, 2G SGC | approx 5.0 V | SGT 4 pulses/rev of sensor shaft, SGC 2 pulses/rev | CHARM 1994 "Crankshaft Position Sensor", 1995 "Camshaft Position Sensor" (files charm_1994/1995_electrical_specs.txt) VERIFIED |
| 1996-97 | CAS | 4F SGT, 4G SGC | approx 5 V | 4 and 2 pulses/rev | CHARM 1996 "Camshaft Position Sensor" VERIFIED |
| 1996-97 | crank-pulley NE sensor | 4H, 4E | coil 500-600 ohm at 20 C | (unknown; tooth count not read) | CHARM 1996 "Crankshaft Position Sensor" VERIFIED; type "VR" INFERRED from resistance |
| 1999-2000 | crank + cam | 1999-2000 ECU pins not read here (R18 note is a stub) | Haltech page lists crank as Hall, 3-wire | - | Haltech BP-4W page, search snippet only, UNVERIFIED |
| 2001-05 | CKP (4 projections on plate behind pulley), CMP (VVT cam) | 3Y NE, 3V SGC | 3-wire: A = main-relay terminal D (switched battery), B = signal, C = GND 4A; air gap 0.5-1.5 mm | Scope (Mitchell 2005 Fig. 24/25, image kb/research/files/R20/mitchell2005_scope_SGC_NE.png): NE idles high ~5 V with 4 narrow negative pulses per 2 crank revs displayed; SGC high ~4-5 V with low pulses in groups 2-1-2 | Mitchell 2005 manual pp.56-57, 76-82, VERIFIED (levels read from a downscaled image: INFERRED, medium) |

Pull-up location: no manual states it. The PCM table shows a stable ~5 V high at 3V/3Y with the sensor disconnected from nothing; the open-collector character with supply 12 V implies the PCM (or sensor) pulls up to 5 V. INFERRED only.
rusEFI forum evidence (Haltech/rusEFI search summaries, UNVERIFIED): a 2003 test car's CKP looked like VR to rusEFI developers at first, then they reported an inverted Hall-type signal. Treat NB CKP type as "Hall, polarity/edge to be checked on a real car".

### 1.2 Temperature, throttle, airflow
| Item | Years | Interface | Values | Source |
|---|---|---|---|---|
| ECT thermosensor | 1990 | 2Q: 2.5 V at 20 C, 0.4 V warm | 20 C 2.2-2.7 kohm; -20 C 14.6-17.8 kohm | wm1990 OCR; R16 |
| | 1994-96 | | 20 C 2.21-2.69 kohm; 80 C 0.287-0.349 kohm | CHARM 1994 and 1996 VERIFIED |
| | 2005 | 4P, sensor A = PCM supply side, B = GND 4O | 20 C 2.27-2.74; 80 C 0.29-0.34 kohm; PCM sees ~3.0 V at 20 C, ~0.9 V at 80 C | Mitchell 2005 pp.72-73 and table VERIFIED. Implied internal pull-up to 5 V: about 1.4-1.7 kohm (INFERRED from 3.0 V @ ~2.5 kohm and 0.9 V @ 0.31 kohm; the two points disagree, so ~1.5 kohm is only approximate) |
| IAT | 1990 (inside vane meter, THAA) | 2P: 2.5 V at 20 C | -20 C 13.6-18.4 kohm; 20 C 2.21-2.69 kohm; 60 C 0.493-0.667 kohm | wm1990 OCR VERIFIED |
| | 1994-96 | | 20 C 2.21-2.69 kohm | CHARM VERIFIED |
| | 2005 (4N, A=GND 4O, B=signal) | 20 C 2.3-2.4 V, 30 C 1.9 V; sensor 2.21-2.69 kohm at 20 C | | Mitchell 2005 VERIFIED. Implied pull-up about 2.7 kohm (INFERRED) |
| IAT No.2 (turbo only) | 2004-05 BP with TC | 33 kohm at 25 C, 3.5 kohm at 85 C, -20 C 357 kohm: a different, high-resistance sensor; do NOT use its curve for the standard IAT | Mitchell 2005 p.64 VERIFIED |
| Throttle | 1989-93 MT | idle contact 1N (0 V released / 12 V depressed per R16), power contact 2L 5 V / 0 V | | R16; wm1990 OCR |
| | 1994 | TPS variable resistor to 2M: closed 0.1-1.1 V, WOT 2.8-4.5 V; idle switch to 1N | | CHARM 1994 VERIFIED |
| | 1996 | closed 0.1-1.1 V, WOT 3.1-4.5 V; full-close switch continuity A-B | | CHARM 1996 VERIFIED |
| | 2005 | TP sensor A = Vref (4L, 5.0 V), B = GND 4O, C = signal 4V: closed 0.1-1.1 V, WOT 3.0-4.6 V | | Mitchell 2005 VERIFIED |
| Vane airflow meter (VAF) | 1990 | 5 V reference (2K 4.5-5.5 V), signal 2O: 3.8 V key on, 3.3 V idle (manual); fuel-pump switch contact inside; IAT inside | | wm1990 OCR component description "Use Vref (5 volt) as power source" VERIFIED; R16 voltages |
| | 1994 | signal 2O: below 1.0 V key on, 1.0-2.0 V idling; 2F below 1 V | | CHARM 1994 VERIFIED |
| | 1996-97 | ECM 3B: below 1.0 V key on, 1.0-2.0 V idle | | CHARM 1996 VERIFIED |
| | Conflict 1990 vs 1994-96 | 3.8/3.3 V (1990 manual via R16) vs <1/1-2 V (1994-96) - either the meter output polarity changed or one transcription is wrong. Lakey's measured values (4-5 V closed, 0-0.5 V open) agree with the 1990 manual direction. NOT RESOLVED; measure on the car before designing the VAF input for 1994-97. | | |
| MAF (hot film) | 2001-05 | 3-wire: A GND (4A), B signal 4X, C = main-relay D (12 V). Signal key on 0.9-2.0 V, idle 1.7-2.4 V; idle flow 2.6-3.3 g/s (MT) | | Mitchell 2005 VERIFIED. Output type (analog, not frequency) from "voltage" listing - INFERRED. rusEFI Proteus wiki says the MAF input "needs pulldown" (UNVERIFIED) |
| Barometric/EGR boost | 1996-97, 2001-05 | 1996: 3H baro approx 4.0 V at 101.3 kPa; 2005: 4AE 4.1-4.3 V; EGR boost 3N / 3.0-3.4 V at -26.6 kPa | | CHARM 1996, Mitchell 2005 VERIFIED |

### 1.3 Oxygen sensors
| Years | Heater | Signal | Source |
|---|---|---|---|
| 1994-96 | 13 ohm at 20 C (approx), 1994/95/96 | decel <0.4 V, accel >0.5 V; at idle below 1 V | CHARM 1994, 1995, 1996 VERIFIED |
| 2005 front | 2-20 ohm (cold, spec range) heater on 3J low-side; signal 4W 0-1 V | rear heater 2-50 ohm, 3P (the table lists B+ with key on / <1 V at idle heating) | Mitchell 2005 p.91-92 VERIFIED |
Heater current estimate (INFERRED): 13.5 V / 13 ohm = about 1 A cold (inrush) at 1994-96; 13.5 V / 2-20 ohm = 0.7-6.7 A is the allowed spread for the NB front sensor; typical value ~6 ohm -> 2 A (UNVERIFIED typical).

### 1.4 Knock sensor
2001-05: PCM 4M, shows approx 2.4 V key-on (digital meter), resistance between KS terminal A and the body approx 560 kohm at 20 C (Mitchell 2005 p.87-91 VERIFIED): this is a piezo sensor with an internal bleed resistor (INFERRED). Centre frequency for this bore: NOT FOUND in any source (rusEFI default for a 4-cyl 1.8 is a project/firmware matter; repo already documents knock amp clipping). 1989-97: no knock sensor in any terminal table (R17, R16).

### 1.5 Actuators
| Actuator | Years | Resistance / levels | Drive | Source |
|---|---|---|---|---|
| Injectors | 1990-96 | 12-16 ohm at 20 C | voltage drive, 12 V at key on (injector pins), low-side pulses; 1989-93 paired (2U Nos.1,3; 2V Nos.2,4), 1994-97 four separate pins | wm1990, Mitchell 1994, CHARM 1994/95/96 VERIFIED |
| | 2001-05 | four pins 2A/2D/2G/2J, common GND 3A | no resistance, flow, inductance found | Mitchell 2005 VERIFIED (pins only) |
| IAC / ISC valve | 1990 | 11-13 ohm; ECU 2W 7 V key on, 9 V idle (duty) | single low-side duty output | wm1990 OCR VERIFIED |
| | 1994-96 | 10.7-12.3 ohm | | CHARM 1994, 1996 VERIFIED |
| | 2001-05 | PCM 2P "IAC positive", 2Q "IAC negative", scope between them at 2 V/div, 25 ms/div; PID idle duty ~30 % (BP) | the repo/R19 treat 2P as 12 V fed and 2Q as low-side drive; the manual calls both PCM terminals: a drive-both-ends (H-bridge/two-driver) valve cannot be excluded. NOT RESOLVED. Coil resistance, frequency: NOT FOUND | Mitchell 2005 lines 1254-1263, 2259-2263, 2005 text; scope image of Fig. 18 not read |
| Purge solenoid | 1990, 1994, 1996 | 23-27 ohm | 12 V; 2005 duty-controlled 3C (scope 2 V/div) | wm1990, CHARM VERIFIED |
| Fuel pressure control solenoid | 1994 | 23-27 ohm | 2R (R17) | CHARM 1994 VERIFIED |
| Circuit-opening relay (1989-93) | | coil B-Fc 109-226 ohm, STA-E1 21-43 ohm (OCR; the "21-43" reading is from a noisy OCR) | not ECU-driven; fed from AFM switch/start | wm1990 OCR VERIFIED/low-quality |
| Fuel pump relay | 2001-05 | 2M low-side, <1 V cranking and idle (= on), B+ otherwise | | Mitchell 2005 VERIFIED |
| Main relay | 2001-05 | 3H: B+ ignition off, <1 V ignition on (low-side relay control); 4AF power supply, 4AG backup B+ | | Mitchell 2005 VERIFIED |
| Fan relays | 1994 1L/1B; 2005 2B (fan) 2C (condenser) | low-side: <1 V when ECT >97 C (2B) or >108 C with A/C (2C) | | Mitchell 2005, R17 |
| A/C relay and request | 2005 2K relay low = on; 4F request <1 V = on (A/C and fan switches on) | | Mitchell 2005 VERIFIED; 1994: 1J relay, 1Q request low = on (R17) |
| VVT oil control valve | 2001-05 | PCM 4D positive, 4R negative; scope between them 2 V/div, 0.5 ms/div -> fast PWM (about 2 kHz scale, INFERRED from time base only); resistance NOT found | Mitchell 2005 VERIFIED (terminals); frequency INFERRED low confidence |
| VTCS solenoid / vacuum switch | 2001-05 | 2N solenoid low-side, B+ when ECT>60 C at idle; 4J vacuum switch input B+ / <1 V | | Mitchell 2005 VERIFIED |
| EGR | 1994-97 | solenoid vent 1R, vacuum 1T (1994-95); position sensor 2.7 kohm, 3J 0.8 V at 0 kPa to 4.9 V at 17 kPa | | CHARM 1996 VERIFIED |
| EGR | 2004-05 | four coils 2E,2F,2H,2I (stepper-style, "coil control #1-4"); not in repo | | Mitchell 2005 VERIFIED |
| Alternator | 1994-96 | rotor 3.5-4.5 ohm, regulated 14.3-14.9 V | | CHARM VERIFIED |
| | 1999-2005 | 3M field control, ALTF 0-100 %; 4T output voltage (terminal P); 3U charge lamp low | | Mitchell 2005 VERIFIED |
| Igniter / coil | 1989-95 | igniter base inputs ~659 ohm (R16), 1G/1H 0.2 V idle; 1994 coil primary 0.78-0.94 ohm | | R16; Mitchell 1994 VERIFIED |
| | 1996-97 | IGT1 4N, IGT2 4R | | R17 |
| | 2001-05 | IGT 3F (1,4), 3I (2,3) | 2 coils, wasted spark | Mitchell 2005 VERIFIED |

### 1.6 Vehicle speed, switches, lamps, diagnostics, tach, immobiliser
| Item | Value | Source |
|---|---|---|
| VSS 1994 | 4 pulses per shaft revolution (transaxle speed sensor); ECU 1M "2-5 V driving, 1 or 7 V stopped" (R17) | CHARM 1994 "Vehicle Speed Sensor" VERIFIED |
| VSS 2005 | 3T; scope 1 V/div, 10 ms/div at 50 km/h shows a square wave about 3.5 divisions high (about 3.5 V peak, image-read, LOW confidence), period about 15 ms (about 65 Hz at 50 km/h) | Mitchell 2005 Fig. 23, image kb/research/files/R20/mitchell2005_scope_vss_p55.png; INFERRED low |
| Tach 2005 | PCM 3O (also DLC IG-TCM terminal); scope 2 V/div, 20 ms/div at idle: square wave about 8 V high (grid-read, LOW confidence), period about 38 ms = about 2 pulses per rev at 750-800 rpm | Mitchell 2005 Fig. 22, image kb/research/files/R20/mitchell2005_scope_tach_p54.png; INFERRED low |
| Tach 1989-95 | igniter generates the tach signal; ECU only pull-up to 5 V (rusEFI wiki) ; stock cluster expectation 12 V square wave per one forum (UNVERIFIED, forums disagree: another says pulled to ground; rusEFI wiki says use pull-up) | rusEFI wiki NA48 2.4 VERIFIED page read; forums UNVERIFIED |
| Cluster tach threshold per year | NOT FOUND | - |
| Brake / PSP / clutch / neutral 2005 | see Summary 9; clutch input is HIGH when pedal depressed, neutral LOW in neutral: do not copy one polarity to the other | Mitchell 2005 VERIFIED |
| 1994 switches | 1N idle 0 V / B+ depressed; 1O brake; 1P PSP B+/0 V when loaded; 1V neutral/clutch 0 V in neutral or clutch in | R17 |
| Check-engine lamp | 2005 2R: <1 V = lit, B+ = off (low-side lamp driver); 1994: 1E <2.5 V lit | Mitchell 2005; R17 |
| Diagnosis | 2005: K-line 3Q to DLC-2 KLN (serial, no voltage test), TEN on 4E (open = B+, grounded = <1 V), immobilizer serial 3S ("serial communication: voltage judgment not possible") ; ALSO 2004-05 TCM serial 4Z/4AC for AT | Mitchell 2005 VERIFIED |
| Immobiliser line | 3S serial; no level/baud documented; stock behaviour with standalone: see R19 | Mitchell 2005 VERIFIED (existence only) |

## 2. Disagreements recorded
- VAF signal level direction/size 1990 vs 1994-97 (section 1.2). Trusted: each year's own manual; unresolved for design.
- 2005 generator terminal 4T: 3-8 V (terminal table) vs ~14 V (PID table).
- IAC 2P/2Q: manual naming "positive/negative" vs R19/repo "2P 12 V supply, 2Q low side".
- 1990 injector OCR read "12-160" is OCR noise; the same manual lists 12-16 (type "High-ohmic", "Voltage" drive) and Mitchell/CHARM confirm 12-16.

## 3. Implications for this project (tie to the six goals)
1. (goal 1 errors; confidence medium) The repo's NB mb treats CKP/CMP as Hall inputs with a 1k pull-up to the daughterboard's sensor 5 V (mb_nb2.py comment, design.py around line 433). The manual shows these sensors are powered from the main relay (about 12 V), signal on B, ground on 4A. The board must NOT feed 5 V/12 V onto 3Y/3V and the sensor supply is not the ECU's: check that the main relay terminal D feeds the sensors in the stock harness and that the board does not need to supply it. The design's choice (pull-up, no supply) matches this reading; confirm there is no case where the pull-up source collapses when the 5 V rail is off (cranking dips). Evidence: Mitchell 2005 lines 2986-2990, 3181-3184.
2. (goal 1; medium) A 4-wire reading: 2004-05 has actuators not handled by the repo: stepper-type EGR (2E/2F/2H/2I), EVAP leak pump 3K and valve 4AH, EGR-boost solenoid 3D, fuel gauge input 4AD. The repo documents "no EGR/purge", but leaving 2004-05 EGR coils unconnected will set a DTC and may not matter for a race ECU; for customers with a tach/fuel gauge the 4AD fuel-level input is passed through the PCM (the gauge may read the PCM, UNVERIFIED) - the board should check whether 4AD is wired to the cluster (cost: documentation).
3. (goal 4 UX; medium) Switch polarities: clutch input 4I is active-high while neutral 4H is active-low in 2005; brake 4B active-high; PSP 4C active-low; A/C request 4F active-low. Firmware defaults must have a per-input polarity table per year (rusEFI configs exist per vehicle). Documentation item.
4. (goal 1; medium) 1996-97 NE (4H/4E) is a 500-600 ohm sensor, probably VR, left unconnected by the repo (mb_na96.py:30). Acceptable if the CAS signals give crank sync (rusEFI NA8-96 does), but crank speed resolution is limited to 4 pulses per cam rev (about 2 per crank rev); misfire/low-speed accuracy is lower than a 36-1 setup. This documents a known trade-off, no board change.
5. (goal 1; low-medium) VAF output direction conflict between years (1990 vs 1994-97): the VAF input scaling (divider/clamp) should be checked on a real 1989-93 and a 1994-97 meter before ordering again; the hand measurement costs nothing.
6. (goal 1/4; medium) Fuel-pump relay: R16 says 1989-93 has no ECU fuel pump output (COR is fed by the airflow meter switch/start), but 2001-05 does (2M, low-side on = <1 V). Do not expect one output behaviour across years.
7. (goal 5; low) 2004-05 IAT No.2 is a 33 kohm @25 C sensor on turbo cars only; ignore.
8. (goal 3; low) Nothing in this task changes cost; no alternate part findings.
9. Not resolved items listed below are design risks: IAC 2P/2Q topology, drive frequencies, OCV frequency, injector inductance/flow, knock frequency, cluster tach threshold per year.

## Sources actually read
- Mitchell 2005 MX-5 manual PDF copy: kb/research/files/R09/mellens/Mazda-Miata-2005_engine_control_system.pdf (text copy kb/research/files/R20/mitchell2005_engine_control_system.txt; PCM tables lines 1100-1640, circuit checks 2480-3290, scope pages 53-58 viewed as images).
- Mitchell 1994 specs PDF: kb/research/files/R09/mellens/Mazda-Miata-1994_specs.pdf (coil primary, injector 12-16, TPS continuity).
- Operation CHARM electrical specification pages 1994, 1995, 1996 (fetched today via scripts fetch2.py, fetch4.py; text in kb/research/files/R20/charm_199x_electrical_specs.txt) base https://charm.li/Mazda/<year>/MX-5%20Miata%20L4-1.8L%20DOHC/Repair%20and%20Diagnosis/Specifications/Electrical%20Specifications/ ; CHARM 2002 CKP page "Component Tests and General Diagnostics".
- 1990 MX-5 workshop manual OCR text (archive.org, via R16): work/R16-stock-ecu-1989-93/dl/wm1990_djvu.txt lines 10190-10250 (excerpt saved) and 18900-18960, 20066-20095, 20245-20270; page images F-90/F-91/F-92 viewed.
- rusEFI wiki NA 48-pin page, NB2 Proteus HOWTO and Mazda Miata 2002 page (saved texts), rusEFI trigger_mazda.cpp, repo/scripts/mb_na96.py and mb_nb2.py.
- Search summaries only (UNVERIFIED): Haltech BP-4W/BP-Z3 knowledge-base articles (JS pages, not retrievable by curl), rusEFI forum NB2 threads, grassroots tach threads, injector-flow forum listings (205 cc / 13.9 ohm for a 1.6 Denso; 230-238 cc quoted for 1.8: UNVERIFIED).

## Not checked
- Drive frequencies and duty ranges of IAC, purge, OCV, alternator field; injector flow, inductance, opening time; knock sensor centre frequency; cluster tach input threshold per year; VSS levels for 1989-93 and 1996-2000; 1999-2000 ECU pin tables (R18 stub); ECU-side pull-up resistor values; sensor supply voltage of the 1989-97 optical CAS; hot-wire MAF output type (analog vs frequency) beyond the voltage table; 1996-2000 immobiliser; DLC terminal details beyond TEN/KLN; electrical-load switch (headlight/blower) 1994-97 voltages beyond R17; 2001-05 EGR stepper coil resistance; IAC scope Fig. 18 and OCV scope Fig. 26 images were not examined.
