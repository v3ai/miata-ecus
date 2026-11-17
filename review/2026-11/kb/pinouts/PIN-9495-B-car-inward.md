# PIN-9495-B car inward: 1994-95 NA8 (1.8 L BP-ZE, 48-pin ECU) pinout chain audit

STATUS: STEPS 1-3 complete (see end). Verification tags: FSM/VERIFIED = read today in Mazda 1994 FSM images.

## STEP 1: factory pinout from external sources only

Sources (independent):
- S1 Mazda 1994 MX-5 FSM, "Engine Performance / Self-Diagnostics" chart pages (Mitchell reprint, mellens.net/mazda/Mazda-Miata-1994/tests_with_codes.pdf; images extracted to work/PIN-9495-B-car-inward/img/). PRIMARY. Gives, per ECU terminal, wire colour of component terminals and continuity tables (component terminal -> "PCME terminal"). The FSM calls the ECU "PCME" (Powertrain Control Module-Engine). The 1994 wiring-diagram PDF on the same site (wiring.pdf Fig. 8/9 "1.8L Engine Performance Circuits") has BLANK figure pages (checked: no image objects, pages render empty), so the 1994 ECU wiring diagram was NOT readable. The FSM "PIN VOLTAGE CHARTS" article is not in the downloaded set (UNREAD).
- S2 rusEFI wiki "1994 Mazda Miata" (wiki.rusefi.com/Mazda-Miata-1994/): full 1A..1V / 2A..2Z colour+function table (HTML saved dl/r94.html). "1995 Mazda Miata" page has no table (only "48 pin case" and a link to 1994).
- S3 Haltech support KB "BP-ZE Engine 94-97 NA8" (support.haltech.com/portal/en/kb/articles/93-na8-1-6l-b6-ze; despite the URL it describes the 1.8 BP-ZE): sensor/igniter/MAF-connector level.
- S4 AMP EFI "AMP-PNP-MM9495" installation page + Rear Options pinout image (ampenginemanagement.com): which functions the PnP keeps (MAF analog input optional via jumper JP7, VSS, clutch switch, IAT, fan/injector jumpers JP2 INJC/TC, JP3 INJD/INJB, JP4 VTPS, JP5 TOUT, JP6 GND/AGND, JP8 FAN 1.6 only).
- S5 rusEFI MRE "Miata NA 48 pin board" wiki (rusefi_mre.txt from the 8993-B notes: 94+ jumper table JP1 AC fan 94+, JP4 TPS 94+, JP56 1M VSS pull-up, JP53/57 INJ3/4 sequential, JP54/55 2I tach out / pull-up, "TachOUT on 95.5").
- S6 DIYAutoTune MSPNP2 MM9093 manual (J5 variable TPS "should be installed on 94-95 Miatas", J6 "Tach Out on 4I (1995.5+ Miata only)", J8 fan 1.6 only) and AMP/MSPNP table for 4U/4V/4Y/4Z.
- hellen64_NA6_94 board files (ext/, one source, not yet read here; see STEP 2).
Cavity naming: Mazda "CONN #1" = 1A..1V (22), "CONN #2" = 2A..2Z (26).

### Table 1: cavities with at least one hard fact (colour/function) 
Tag: FSM = S1 primary (VERIFIED by image read today), R = S2 rusEFI, H = Haltech, A = AMP, other tags are UNVERIFIED general knowledge for the electrical column.

| Cav | Colour (R) | Function | Dir | Electrical character | Evidence / variants / disagreements |
|---|---|---|---|---|---|
| 1A | BLU/RED | Room fuse, permanent +B | in | battery, keep-alive memory | R |
| 1B | WHT/RED | Main relay output, ECU + sensor + solenoid supply | in | switched 12 V. FSM: every solenoid (PRC, purge, EGR vac/vent) and ISC valve terminal A / W/R wire is battery voltage with IG on, from the "main relay terminal D" | FSM + R |
| 1C | VIO | rusEFI: ignition ON; Link/1991 diagram (ST SIGN fuse): START signal, 12 V only while cranking | in | 12 V sense | R vs 1991 diagram + repo firmware comment (Link): disagree |
| 1D | WHT/GRN | Data link connector | ? | diag | R; 2H LT GRN/YEL also data link (TEN/FEN pair UNRESOLVED). FSM igniter drawing shows the data link connector on igniter terminal D |
| 1E | YEL/BLK | Check engine lamp | out | low-side, lamp fed 12 V | R |
| 1F | (R: "extra analog input") | not used on car | | | R |
| 1G | BRN/YEL | Igniter IB1 (coil 1&4) | out | logic drive into igniter; FSM Code 01 step 6 "PCME terminals 1G and 1H voltages" | FSM |
| 1H | BRN | Igniter IB2 (coil 2&3) | out | as 1G | FSM |
| 1I | BLU/WHT | A/T: PCM(transmission) | ? | | R only |
| 1J | BLU/BLK | A/C compressor relay | out | low-side | R |
| 1K | BLK | "J/C? (M/T only)" | ? | | R only, questionable |
| 1L | BLK/GRN | Cooling fan relay (A/C-extra/main) | out | low-side | R lists 1L; 1991 car used 1R for this (see 8993-B). In 94 FSM EGR vent solenoid is 1R |
| 1M | GRN/RED | Vehicle speed sensor | in | the VSS reluctor feeds the speedometer which outputs a hall-type signal; ECU needs pull-up (Haltech: "Hall effect, falling edge, pull-up disabled", about 2780 pulses/km). 1M was N/C on 90-93 | R, H, S5 (JP56 "pullup VSS 94+ untested") |
| 1N | RED | A/T PCM | ? | | R |
| 1O | GRN/BLK | Stop light switch | in | 12 V when braking | R |
| 1P | BLU/YEL | Power steering pressure switch (per 1991, UNVERIFIED for 94) | in | | R blank |
| 1Q | LT GRN/BLK | A/C pressure/thermo switch | in | | R |
| 1R | YEL/BLK | EGR vent solenoid B terminal (YEL/BLK) | out | low-side, solenoid fed WHT/RED | FSM code 29: "EGR solenoid valve (vent) terminal B - PCME terminal 1R" |
| 1S | BLU/ORG | Heater control unit | in | | R |
| 1T | YEL/RED | EGR vacuum solenoid B terminal (YEL/RED) | out | low-side | FSM code 28: "PCME terminal 1T" |
| 1U | RED/BLK | not identified (tail fuse in 1991) | | | R |
| 1V | BRN/WHT | A/T PCM and clutch switch | in | | R |
| 2A, 2B | BLK | Power ground | | high current | R |
| 2C | BLK/LT GRN | Logic ground | | | R |
| 2D | BLK/BLU | Sensor ground: FSM: TPS A, EGR function sensor A, CTS B (B/LG), IAT C (BLK/BLU) all return to 2D | | | FSM + R |
| 2E | WHT | Crank angle (SGT/NE, 4x) | in | Hall sensor, W/R supply from main relay; FSM: "approx 5 V at ECU terminal 2E with sensor disconnected" => ECU pulls the line up to about 5 V | FSM |
| 2F | BLK/RED | Mass airflow sensor ground (FSM: MAF terminal E "BLK/LT GRN" -> PCME 2F) | | | FSM and R disagree on the colour (BLK/LT GRN vs BLK/RED) |
| 2G | YEL/BLU | Crank angle (SGC/G, 2x) | in | as 2E; FSM: "5 V at 2E (sic) with connector disconnected" | FSM |
| 2H | LT GRN/YEL | Data link connector | ? | | R |
| 2I | BLK/WHT | Tach / IGf from igniter | in (igniter -> ECU) | FSM Code 01: "Does tachometer operate? No: check for open circuit from ignition coil to PCME terminal 2I". Igniter terminals in FSM drawing: C, D, B, E, F, A with 1G, 2I, 1H going to the PCME. Pull-up in ECU (S5 JP55 pull-up to 5 V, "stock coils"); "1995.5+ tach out on 2I" (S5, S6) | FSM, R, S5, S6 |
| 2J | LT GRN/RED | EGR function (boost/position) sensor signal | in | 4.5-5.5 V at terminal C; pot 2.7 k total, C wiper 0.1-2.4 k | FSM Fig. code 16 |
| 2K | LT GRN/WHT | +5 V sensor reference (TPS D terminal "LT GRN/WHT" -> 2K; EGR sensor B -> 2K) | out | ~5 V regulated; changed from 1991 where 2K was LT GRN/RED | FSM + R agree; MSPNP 9093 "1N" = old TPS note |
| 2L | BLU/RED | Rear window defroster SWITCH input (FSM vacuum schematic 94D45305 lists 'rear window defroster switch' among PCME inputs; R wrongly calls it a relay). Not TPS in 94 (TPS = 2K/2M/2D). In 1990-93 2L was the M/T throttle-switch input | in | 12 V (or switch) level UNVERIFIED | FSM schematic + R; Haltech: 3-pin M/T TPS is a switch only (for B6) |
| 2M | RED/BLK | Throttle position sensor signal (variable, all cars) | in | analog 0.5-4.5 V (UNVERIFIED value) | FSM Code 12 ("TPS C RED/BLK -> PCME 2M"; D LT GRN/WHT -> 2K; A BLK/BLU -> 2D) |
| 2N | RED/BLU | Oxygen sensor (heated 4-wire) | in | 0.1-0.9 V; heater fed WHT/RED, probably switched by ECU? (UNVERIFIED) | FSM code 15 "ECU terminal 2N", R |
| 2O | RED | Mass airflow (hot-wire) signal | in | analog | FSM code 08: MAF B (RED) -> PCME 2O, E -> 2F. H: MAF connector 5 pins: 1 BLK/LT GRN chassis ground, 2 BLK/BLU signal ground, 3 RED/BLK IAT, 4 RED/WHT MAF signal, 5 WHT/RED 12 V switched (hot wire needs 12 V + ground) |
| 2P | RED/BLK | Intake air temp (in MAF) | in | NTC 2.21-2.69 kOhm at 20 C, ECU pull-up (AMP bias 2490 ohm for GM sensor) | FSM code 10 (terminals C BLK/BLU -> 2D, D RED/BLK -> 2P) |
| 2Q | BLU/WHT | Coolant temp | in | NTC: -20 C 14.6-17.8 k, 20 C 2.2-2.7 k, 80 C 290-350 ohm; FSM wire "L/W" -> 2Q, "B/LG" -> 2D | FSM code 9 |
| 2R | YEL/GRN | PRC (pressure regulator control) solenoid B terminal | out | low-side; terminal A WHT/RED battery voltage with IG ON; "continuity between PRC solenoid B and PCME 2R" | FSM code 25 |
| 2S | BLU/WHT | Condenser fan relay | out | low-side | R only |
| 2T | LT GRN | Fuel pump relay (circuit-opening relay control) | out | low-side to relay coil | R only (FSM text only mentions "fuel pump relay" behind dash, Mitchell engine text) |
| 2U | YEL | Injector #1 | out | low-side; injectors fed WHT/RED | R; S6 table (MSPNP 4U); individual wires 94+ |
| 2V | YEL/BLK | Injector #2 | out | | R |
| 2W | BLU/ORG | Idle speed control (ISC) valve B terminal "B (L/O)" | out | low-side duty; valve resistance 12 +/- 1 ohm; A terminal W/R from main relay | FSM code 34 |
| 2X | YEL/RED | Purge control solenoid valve B "(Y/R)" | out | low-side; 25 +/- 2 ohm; W/R feed | FSM code 26 (colour Y/R agrees with R; rusEFI 1990 page says WHT/BLU, wrong for 94) |
| 2Y | GRN/WHT | Injector #3 | out | | R |
| 2Z | GRN | Injector #4 | out | | R |
| 2F/2D..| | internal barometric (atmospheric pressure) sensor inside the ECU: FSM code 14 "Atmospheric pressure sensor: replace ECU" (no external pin) | | | FSM |

Not in the table (no source): 1I..1K, 1P, 1U details, 2L; variants below.

### Variants (what the sources say)
- 1990-93 vs 1994-95: new 5 V ref cavity (2K LT GRN/WHT vs 2K LT GRN/RED / 3K), TPS signal moved from 2L (M/T switch) / 2M (A/T) to 2M for all (FSM), hot-wire MAF (2O + 2F ground, 12 V supply) replaces vane AFM (VS/VC), 1M VSS input, 2T fuel pump relay and 2R PRC solenoid added, 2R/2T/2S/1L/1T/1R new, 2J EGR function sensor. Paired injector wires 2U/2V in 1991; 1994 has four injector cavities 2U/2V/2Y/2Z (R; individually driven, sequential on 1.8 in 94 UNVERIFIED how Mazda drives them: MSPNP jumpers INJ3/INJ4 "sequ"/"parallel" with 94+ default sequ).
- Manual vs automatic: A/T lines 1I, 1N, 1V, 2Z? to the transmission PCM (R); M/T: clutch switch on 1V (R). Haltech: B6 Auto 4-pin TPS vs M/T 3-pin (that is for the B6 1.6 L/90-93; for 94 FSM shows a variable TPS).
- Federal vs California: EGR present on 94-95 US cars (EGR vac 1T, vent 1R, function sensor 2J; FSM codes 16, 28, 29). California-only differences in 94-95 not found in any source (UNVERIFIED).
- 1995.5 (late 95): MSPNP J6 and MRE JP54 note "tach out 2I on 95.5": the late-95 car's ECU sends the tach itself (different igniter arrangement) per both sources, but how not documented. UNVERIFIED.

Disagreements: (a) 2F colour (FSM BLK/LT GRN, R BLK/RED); (b) 2K colour history; (c) 2L (FSM silent, R "rear defroster relay"); (d) rusEFI 94 table duplicates colours (2M and 2P both RED/BLK, 1E and 1R both YEL/BLK, 2Q/2S both BLU/WHT; FSM confirms 2P RED/BLK, 2M RED/BLK as separate terminals of different sensors, and 1R as YEL/BLK EGR vent) so the R table is not reliable for colour on its own; (e) 2I direction ("input" vs igniter confirm) - consistent with FSM: igniter -> ECU.

### Extra primary facts from the 1994 FSM vacuum schematic (94D45305, image read)
PCME inputs drawn: starter, steering pressure sensor, A/C sensor, rear window defroster switch, combination switch, blower switch, stoplight switch (MT), clutch switch (MT), neutral switch (MT), TEN terminal, park/neutral switch (AT), vehicle speed sensor, plus MAF, IAT, CTS, O2, TPS, EGR function sensor, crank sensor. Outputs drawn: A/C relay, coolant fan relay, condenser fan relay, purge solenoid, PRC solenoid, EGR vacuum and vent solenoids, ISC (BAC) valve, injectors, igniter, fuel pump relay (text). The "combination switch" and "starter" inputs have no cavity identified in any source (candidate 1U/1P/1C). The atmospheric (baro) sensor is inside the ECU (code 14).

## STEP 2: comparison with the board (cur_mb8995 jumpers per motherboards/1989-95/README.md 94-95 column; ord_mb9495 from kb/interconnect.md; firmware repo/firmware/board/miata_board.cpp)
Daughterboard conditioning read from evidence/cur_db/pcb_footprints.csv, design.py comments (lines 433-445, 298-330, 478).
Legend: OK = matches car; OK* = matches with unverified assumption; GAP = stock function not provided; RISK.

| Cav | Board (cur_mb8995 94-95 / ord_mb9495) | MCU function | Verdict |
|---|---|---|---|
| 1A,1D,1F,1I,1K,1O,1P,1S,1T,1U, 2H,2J | no net (both) | none | GAP only for functions: 1O stop light, 1S heater, 1P PS, 1T EGR vac, 2J EGR sensor, 2H/1D diag; nothing harmful: unconnected inputs on the car side are just open |
| 1B | VBAT_IN (also fuses, daughterboard supply) | power | OK |
| 1C | VIGN_IN (JD1.3, divider R13) | key sense | OK: firmware does not use it for 1989-95 (miata_board.cpp:129-140 comment) |
| 1E | OUT_CEL ZXMS6004 low-side | CEL | OK (low-side, lamp fed 12 V) |
| 1G,1H | OUT_IGN1/2: ZXMS6004 pulled low 3.3k, 5 V logic into igniter IB1/IB2 | ign | OK*: FSM names 1G/1H as igniter drive; 5 V logic (UNVERIFIED igniter input threshold; repo documents) |
| 1J | OUT_AC low-side | A/C relay | OK |
| 1L | OUT_FAN low-side | coolant fan relay | OK: FSM schematic has coolant fan relay output; R says 1L |
| 1M | IN_SW1 -> R65 22k / R66 10k divider; R20 pull-up NOT fitted (README) | VSS (vehicleSpeedSensorInputPin) | OK* : Haltech says the signal is a driven hall-type level with pull-up disabled; if the cluster output is actually open-collector the input never rises (RISK low: only speed features) |
| 1Q | IN_SW2 divider | A/C switch | OK* (level 12 V assumed) |
| 1V | IN_SW3 divider | clutch | OK on M/T; on A/T 1V is also a PCM(transmission) line |
| 1R, 1T | cur: 1R -> JP3 pos1 (fan2 on 1990-91 only), ord: no net; 1T no net | none | GAP: EGR vent / EGR vacuum solenoids (FSM codes 28/29) never driven. Note: README says 1R is "A/C fan relay on 1990-91" and puts it on JP3; on 94-95 1R is the EGR VENT solenoid (FSM). Correct only if JP3 is set to 94-95 (pos 2-3); if the shunt is left on 90-93 on a 94-95 car OUT_LS7 would pulse the EGR vent solenoid (harmless 12 V solenoid, 25-ohm class) instead of the condenser fan |
| 1N | cur: HARN_1N via R28 0R (not fitted) / ord: none | none | OK: on 94-95 1N is a PCM(transmission) line (R); R28 must stay unfitted on A/T cars (5 V onto a TCM line) |
| 2A-2D, 2F | GND | | OK: 2D carries all sensor returns (FSM). Sensor ground and power ground are one net on the board (MAF hot-wire return current through 2F, <1 A UNVERIFIED, negligible drop) |
| 2E, 2G | IN_HALL1/2: 1k pull-up to V5_EXT through D35 BAT54A, 4.7k series, 1n, clamp to 3V3 | triggers | OK: FSM says "about 5 V at 2E with sensor disconnected", so a ~5 V pull-up is what the car expects; board gives 5 V minus Schottky (about 4.7 V). Hall sink 4.7 mA |
| 2I | cur: HARN_2I -> JP5 (open) = floating, no pull-up, no input; ord_mb9495: net OUT_TACH straight to Q14 (ZXMS6004 low side), no pull-up (R37 not on ord board); firmware miataNoTachOutput -> Q14 never driven | none | UNRESOLVED (documented open item): the board neither reads the igniter signal nor pulls it up. FSM code 01 ties tach operation to the wire to PCME 2I ("tachometer does not operate: check open circuit ... to PCME terminal 2I"); rusEFI MRE fits a 2I pull-up by default on 94+ with stock coils (JP55 Y, JP54 tach-out N); both MSPNP and MRE say 2I becomes a tach OUTPUT on 1995.5+. If the cluster tach needs the ECU pull-up the needle reads zero; if the igniter drives the tach directly (1991 diagram) all is fine. Needs a measurement on a stock car |
| 2K | V5_EXT (TLS115 tracker, short-to-battery proof) | 5 V ref | OK: out, FSM TPS D and EGR B terminals on 2K; load TPS plus pull-ups |
| 2L | cur: HARN_2L -> R29 0R (fitted) -> IN_AUX1 (R39 5.6k), R30 not fitted; ord: IN_AUX1 direct | spare analog | OK, no harm: defroster switch is read as an analog; GAP: stock uses it for idle-up (no firmware use) |
| 2M | IN_TPS via R27 5.6k, ADC | TPS | OK: FSM TPS signal on 2M with 2K/2D; 0.5-4.5 V class (UNVERIFIED) fits a 3.3 V ADC only if the input divider exists: R27 5.6k + (check) design: see not_done |
| 2N | IN_AUX2 (5.6k, ADC) | spare analog (stock NB O2) | OK*: heated NB O2 sensor 0.1-0.9 V read but not used for control (wideband replaces); heater (4-wire) supply stays on car side, ECU does not switch it here (UNVERIFIED) |
| 2O | cur: JP6 pos AFM -> IN_AUX3; ord: IN_AUX3 direct (5.6k) | mafAdcChannel | OK: hot-wire MAF analog out RED to 2O (FSM code 08); MAF powered on the car harness from WHT/RED (Haltech pin 5). Note the MAF gets power independent of the ECU, so it still burns off at key-off/on as before |
| 2P | cur: IN_IAT (stock) or ext J3 via JP1; pull-up R36 2.7k to V5_EXT | IAT | OK: FSM IAT 2.21-2.69 k at 20 C; the 2.7 k bias suits it |
| 2Q | IN_CLT, R33 2.7k pull-up | CLT | OK: FSM 14.6-17.8 k (-20 C) / 2.2-2.7 k (20 C) / 290-350 ohm (80 C); 2.7 k bias gives mid-range sensitivity |
| 2R | cur: JP4 (fit on 94-95) -> OUT_ALT (Q8 VND7NV04 low-side, internal clamp, no external freewheel diode); ord: 2R direct to OUT_ALT/J5.4 | alternatorControlPin (off by default) | OK electrically (low-side, solenoid fed WHT/RED); GAP functionally: stock PRC solenoid is ECU-driven (FSM code 25), the firmware never drives it (isAlternatorControlEnabled=false, no PRC logic); and if the user turns on alternator control on a 94-95 car, the alternator PWM (250 Hz) would chatter the PRC solenoid |
| 2S | ord: OUT_LS7 direct; cur: JP3 pos 94-95 | fan2 | OK: condenser fan relay output (FSM schematic) |
| 2T | OUT_FP low-side | fuelPumpPin | OK: ECU controls the pump relay on this year (R); 12 V coil from the car |
| 2U,2V,2Y,2Z | cur: 2U/2V direct with D3/D4 SMCJ30A TVS; 2Y/2Z via JP1/JP2 SEQ; ord: all four direct (no TVS); VND7NV04 low-side with 40 V clamp | injectors 1-4 | OK: individual wires (R, MSPNP), preset IM_SEQUENTIAL (rusEFI setMazdaMiataNA94). Note rusEFI preset sets the Mazda NA trigger, injector 254 cc/min. Cur: JP1/JP2 must be on SEQ for 94-95; if left open (1989-93 default) injectors 3 and 4 are never driven = two cylinders dead. |
| 2W | OUT_IACV + SS34 to VBAT | idle valve | OK: FSM ISC valve B (BLU/ORG) on 2W, 12 +/- 1 ohm (about 1 A at 12 V) driven low-side with flyback diode |
| 2X | OUT_VVT + SS34 | purge (no firmware default) | OK electrically: FSM purge 25 +/- 2 ohm, YEL/RED on 2X; GAP: vvtPins unassigned for NA, purge never driven (check firmware) |

## STEP 3: stock functions this year that the board does not do / does differently
| Stock function (1994-95) | Board | What the driver notices / what is harmed | Evidence |
|---|---|---|---|
| Hot-wire MAF (2O, 2F; supplied 12 V by car harness) | Supported as analog input only; default tune is speed-density (MAP on MPX5700AP) and 2O is read on AUX3; no MAF transfer table verified | MAF stays in the intake as an unused sensor; driver notices nothing if speed-density tune is right; if user selects MAF, needs a calibration | FSM code 08; Haltech; AMP (MAF only via JP7, default speed density) |
| Sequential injection on 2U/2V/2Y/2Z | Supported (needs JP1/JP2 on SEQ on cur board; direct on ordered 9495 board) | none if jumpers set; two cylinders dead if cur-board JP1/JP2 left open | R + README |
| PRC solenoid on 2R | Not driven (output exists, off). Mazda uses it to raise fuel pressure for hot restarts (UNVERIFIED from memory) | possible long cranking after a hot soak (vapor); not harmful to engine | FSM code 25; vacuum schematic shows PRC on the regulator line |
| TPS 2M, 5 V ref 2K, ground 2D | Supported. The 2L "throttle idle switch" of 1990-93 is gone on 94-95 so no idle contact to emulate | none | FSM code 12 |
| Fan relays 1L, 2S, A/C relay 1J, A/C sensor 1Q | Supported through firmware fan/A/C logic; stock fan thresholds not copied (fan on 100 C, rusEFI preset) | fan may start later/earlier than stock | schematic 94D45305 |
| Fuel pump relay 2T | Supported (rusEFI prime + run) | pump runs only if firmware sees RPM; no AFM-switch backup because MAF has none | R |
| Igniter / tach 1G, 1H, 2I | 1G/1H OK; 2I floated (see above) | tach may read 0 or not depending on the 2I arrangement; also ECU never sees IGf | FSM code 01 |
| EGR (1T vent? 1R, 2J function sensor, 1994-95 US) | none (cavities open) | no EGR on the car: slightly higher NOx and lower knock margin; no CEL on the stock side; the EGR control valve stays closed | FSM codes 16, 28, 29 |
| Purge 2X (25 ohm solenoid) | output exists (OUT_VVT) but no firmware purge logic | canister never purges: fuel smell/evap pressure, charcoal saturates; no engine harm | FSM code 26 |
| Baro sensor (inside ECU, code 14) | MAP read at key-on is the only baro estimate (UNVERIFIED in firmware) | altitude correction less accurate | FSM code 14 |
| Automatic: 1I, 1N, 1V(, 2Z on 1990-93), park/neutral switch | 1I/1N not connected; 1V read as clutch | TCM gets no ECU signals: shift quality/limp mode risk; documented "automatics untested" | R, schematic |
| VSS 1M | supported, no pull-up (R20 DNP) | speedometer unaffected; rusEFI speed features may read 0 | Haltech, README |
| Rear defroster 2L, blower 1S, combination switch, starter: idle-up inputs | not read except 2L analog | idle does not rise with defroster/blower load; minor stumble | schematic |
| 1994 vs 1995 / Federal vs California | no source distinguishes 94 from 95 pin-for-pin except "1995.5: tach out on 2I" (MSPNP J6, MRE JP54); California-specific cavities for 94-95 not found | 1995.5+ cars may expect the ECU to output the tach: then the needle stays at zero | S5, S6 (UNVERIFIED) |
| Check engine lamp / self-diagnosis (1D, 1K, 2H TEN/FEN) | CEL output only, no diag connector, no TEN | no Mazda code reading | |

## Sources actually read
work/PIN-9495-B-car-inward/dl: tests94.pdf images (codes 1,2,3,8,9,10,12,14,15,16,25,26,28,29,34), vacuum_diagrams.pdf, wir94.pdf (blank figures), r94.html/r95.html (rusEFI), hal94.html, amp9495.html + jumper/rear connector images, plus 8993-B notes dl files (rusefi_mre, msg2). Repo side: kb/interconnect.md lines 95-284, 1168-1343; evidence/cur_db/pcb_footprints.csv; repo/scripts/design.py comments; repo/motherboards/1989-95/README.md; firmware/board/miata_board.cpp, rusEFI mazda_miata_1_6.cpp setMazdaMiataNA94; ext/hellen-miata-NA6 netlist (3I -> R48).

## Not checked
1994 wiring-diagram figure pages (blank in the available scan); FSM PIN VOLTAGE CHARTS (absent); 1995 FSM; real igniter/cluster tach wiring for 1994-95; AMP rear-options connector B and full 48-pin table (image only partly read); daughterboard input divider values for TPS/MAF to the 3.3 V ADC (only the 5.6 k series seen); firmware purge/PRC logic existence (grep only).
