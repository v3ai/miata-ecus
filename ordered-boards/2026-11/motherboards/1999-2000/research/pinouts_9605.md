# Mazda Miata ECU pinouts: 1996-97 NA8, 1999-00 NB1, 2001-05 NB2

Generated with the companion JSON (`/tmp/claude-0/pinouts_9605.json`). Terminal names are OEM (Mazda/wiki) names; the 'Hellen' column gives the Hellen board name for the same physical cavity.

## Resolved conflicts

- Conflict 1 (1996-97 crank/cam) resolved: OEM 4F (WHT) = CAS 4-pulse crank-angle signal (SGT, 'CKP') and OEM 4G = CAS 2-pulse cam signal (SGC, 'CMP'). Both come from the cam-driven CAS, Hall/open-collector, 12 V fed, so neither is a return of the other. This matches Hellen 3F = crank and 3G = cam, which are the same physical pins (Hellen 3x = OEM 4x). The wiki's 'Cam' label on 4F is wrong. OEM 4E (YEL/BLK) and 4H (YEL/WHT) are the two leads of the separate crank-pulley CKP sensor that 1996-97 added for OBD-II (TSB 006/98 confirms the pulley sensor; AMP calls it the 'OE crankshaft VR signal'). Hellen and DIY leave 4E/4H unconnected. Which of 4E/4H is VR+ is NOT resolved.
- Conflict 2 (sensor types): 1996-97: the CAS (4 wires: GND, +12 V switched, 4x, 2x per Haltech) is Hall/open-collector. The crank-pulley sensor is VR per AMP, but an aftermarket listing shows a 3-terminal connector, so it may be VR with shield or Hall (medium/low). 1999-2005: the CKP (BP4W-18-221, all NB years) and the CMP (one part for 1999-2005) are 3-wire Hall sensors fed +12 V from the main relay (2005 FSM: CKP A = main relay terminal D, B = signal, C = ground to PCM 4A; Haltech NB2: both Hall). There are no VR +/- pins on NB.
- Conflict 3 (power): 96-97: 4B = main-relay +12 V. 4I is possibly battery backup (Hellen +12V_PERM), unresolved. No ECU main-relay output. 99-00: 1B = main-relay +12 V, 1A = battery backup, no ECU main-relay output, no separate IG sense (Hellen uses 1B). 01-02: 4AF main-relay +12 V, 4AG backup, 4S unused, main relay switched by the key. 03-05: 4AF main-relay +12 V, 4AG backup, 4S = IG1 ignition-switch sense, 3H = PCM main-relay control (low side). PCM-sourced actuator supplies: NB1 3O (IAC+), NB2 2P (IAC+) and 4D (OCV+).
- Conflict 4 (grounds): 96-97: 4C, 4D ground (Hellen: power GND). 4A and 1O ground (Hellen: GNDA, role unconfirmed). 3O = sensor ground (BLK/BLU). 3L = ground (DIY only, low). 99-00: 3A/3B/3C power grounds, 3F sensor ground. 01-05: 3A injector power ground, 3B PCM ground, 4A device ground (CKP return), 4O analogue sensor ground.
- Conflict 5 (never drive): see do_not_drive=true rows. Summary: 96-97 1R/1T (A/T), 4E/4H (OE crank sensor), 4I (probable B+), plus every unidentified populated cavity. 99-00: 1A (B+), 1D/1L (DLC), 1K/1N (TCM), 1T (generator sense), 1H, 3K. 01-05: 3Q (K-line/DLC), 3S (immobilizer), 4E (DLC TEN), 4Z/4AC (TCM), 4AD (fuel gauge sender), 4AG (B+), plus inputs 4S/4T. Outputs to the cluster (MIL, charge lamp, tach, generator warning) are ECU low-side outputs; keep them open-collector and never source 12 V into them.

## Other notes

- Primary factory source reached as text: only the Mazda 2005 MX-5 workshop manual 'Engine Control System' PDF (mellens.net). The 1996/1997/1999-2001 factory wiring PDFs (mellens.net, neomiata.com Mitchell) are image-only and could not be read. The 1996-97 and 1999-2000 tables are therefore built from cross-checking independent secondary sources: rusEFI wiki, Hellen KiCad netlists, the Hellen NB1 'OEM ECU pin' sheet, DIY/AMP MSPNP Pro docs, Alex Engineering, Haltech and a Mazda TSB.
- Mazdaspeed (BP with TC, 2004-05) changes per the 2005 FSM: 4D = wastegate regulating valve, 4E = wastegate monitor, 4R = IAT No.2 INPUT (OCV- on non-turbo), 4X = MAP/MAF, 3D = BARO/MAP switching, 3T = VSS via cluster, 3O tach only, 4Y/4Z not used, 4AC = test mode via DLC TEN. A single NB2 board driving 4R as an OCV low side would fight the MSM IAT2 sensor.
- rusEFI/Hellen errata found: (a) wiki Mazda-Miata-1996 labels 4F 'Cam'; it is the CAS crank-angle (4x) signal. (b) wiki Mazda-Miata-1999 swaps 3M/3O (IAC drive is 3M, IAC +12 V is 3O). (c) wiki Mazda-Miata-2003-alt puts knock on 4K; the FSM says 4M (4K unused). (d) hellenMiataNA96 main.yaml info.title says 'Hellen Miata NB1' (copy-paste) and its ts_name for 2K says '2B - IAT'. (e) hellenMiataNB2 main.yaml lists '4Q', which has no cavity. (f) The Hellen NA96 yaml omits 2M (OEM 3M, front O2 heater), although the PCB routes it to OUT_O2H. (g) wiki Mazda-Miata-2002 writes 'VVT terminal 4S' where 4D is meant.
- Several Hellen pins are Hellen-only re-uses of OEM-empty cavities (CAN, MAP, AFR, IGN3-8, options ports). They are not OEM functions; the pin tables flag them in notes.
- Wire colours are sparse. 96-97 colours come only from the rusEFI wiki (some suspicious, e.g. GRN for both 4G and 4N) and allpinouts (unverified). No OEM colours were found as text for NB1 or NB2; the 'color' fields in the Hellen NB2 yaml are Hellen pigtail colours, not OEM.
- Beermoneymotorsports/Polygonus pinout pages copy the Hellen yaml. They were not counted as independent confirmation.

## 1996-1997 (NA8 OBD-II, BP-ZE 1.8)

### Header

- **oem section naming**: 1 (22-pin) | 2 (12-pin) | 3 (16-pin) | 4 (26-pin), left to right
- **section sizes physical order**: 22+12+16+26 = 76 positions
- **sections used by oem harness**: 1, 3, 4 (64 terminals). Section 2 (12-pin) has no harness plug.
- **header part number**: TE/AMP 178780-1 (76-pos 040/070 hybrid cap assy; used by Hellen NA8-96). Equivalents per rusEFI wiki: 178780-6 (obsolete), 174915-6, 3-178780-6. Rev-A Frankenso used the 64-pos TE 176122-6 (22+16+26), so the harness plugs also mate with that.
- **mating harness plugs**: 22p 174515-6, 16p 174514-6, 26p 174516-6, 12p 174913-1 (rusEFI wiki 76-pin entry)
- **hellen naming**: Hellen 1x = OEM 1x; Hellen 2x = OEM 3x (16-pin); Hellen 3x = OEM 4x (26-pin); Hellen 4A-4L = Hellen options/WBO port in the physical 12-pin section-2 slot (OEM 2x, unused).
- **naming confidence**: medium: OEM labels 1/3/4 from the rusEFI wiki, allpinouts (citing the factory supplement) and DIY MSPNP Pro. Geometry from the Hellen KiCad footprint (pads 1-22 | 65-76 | 23-38 | 39-64).
- **sources**: https://wiki.rusefi.com/Mazda-Miata-1996 (local: /home/claude/ref/rusefi.wiki/Mazda-Miata-1996.md); /home/claude/ref/miata/hellen-NA8-96/hellen64_NA8_96.kicad_pcb (pad->net trace); https://wiki.rusefi.com/OEM-connectors (local: /home/claude/ref/rusefi.wiki/OEM-connectors.md); https://www.heilind.com/amp178780-1.html; http://www.megasquirtpnp.com/docs/mspnp_gP_mm9697.php; https://allpinouts.org/pinouts/connectors/car/1996-1997-mazda-miata-ecu/; /home/claude/ref/rusefi-hardware/classic-designs/frankenso/known_issues.txt (item 50); /home/claude/ref/rusefi-hardware/classic-designs/frankenso/www_docs/frankenso_connector_miata_1996.png

### Pins

| Terminal | Hellen | Function | Dir | Wire | Sensor type | Conf | No-drive | Sources | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1A | 1A | Cooling (radiator) fan relay control | out | unknown |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697 | Low-side relay driver. |
| 1B | 1B | Fan No.2 / A/C condenser fan relay control | out | unknown |  | medium |  | wiki96, hellenNA96, kicadNA96 | wiki: 'Radiator Fan 2'; Hellen: 'AC Fan Relay'. DIY MSPNP Pro lists 1B as 'A/C Relay (Injector J Out)', duplicating 1G - probably a typo in that table. |
| 1C | 1C | Not used by OEM (no source assigns an OEM function) | none | unknown |  | low |  | mspnppro9697, hellenNA96 | Hellen puts its own CAN-H here; DIY lists N/C. |
| 1D | 1D | Unknown OEM function (possibly diagnostic link) | none | WHT/BLK (allpinouts, unverified) |  | low | YES | mspnppro9697, allpinouts96, kicadNA96 | DIY: N/C. Hellen: bare test pad. On 1994 the same position was the Data Link Connector (wiki94). Treat as possibly DLC; do not drive until probed. |
| 1E | 1E | MIL / check engine light control | out | unknown |  | high |  | hellenNA96, kicadNA96, mspnppro9697 | Low-side, lamp in instrument cluster. |
| 1F | 1F | Not used | none |  |  | high |  | wiki96, mspnppro9697 |  |
| 1G | 1G | A/C relay control | out | unknown |  | high |  | hellenNA96, kicadNA96, mspnppro9697 | Low-side. |
| 1H | 1H (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697, kicadNA96 | DIY N/C, Hellen test pad only. |
| 1I | 1I (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697, kicadNA96 | DIY N/C, Hellen test pad only. |
| 1J | 1J | Not used by OEM (no source assigns an OEM function) | none | unknown |  | low |  | mspnppro9697, hellenNA96 | Hellen puts its own CAN-L here. |
| 1K | 1K | A/C switch / refrigerant pressure switch input | in | unknown | switch | high |  | hellenNA96, kicadNA96, mspnppro9697 |  |
| 1L | 1L | Clutch switch input | in | unknown | switch | high |  | hellenNA96, kicadNA96, mspnppro9697 |  |
| 1M | 1M | Vehicle speed sensor input | in | unknown | VSS pulse | high |  | hellenNA96, kicadNA96, mspnppro9697, allpinouts96 |  |
| 1N | 1N | Not used | none |  |  | high |  | wiki96, mspnppro9697 |  |
| 1O | 1O | Ground | ground | unknown |  | medium |  | wiki96, mspnppro9697, allpinouts96, kicadNA96 | Hellen ties it to GNDA (sensor ground); allpinouts calls it power ground. Power-vs-signal role not confirmed by a factory source. |
| 1P | 1P (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697, kicadNA96 |  |
| 1Q | 1Q | Brake (stop light) switch input | in | unknown | switch | medium |  | hellenNA96, kicadNA96, allpinouts96 | DIY lists N/C. |
| 1R | 1R (test pad) | A/T only (PCM<->TCM / A/T signal) | comm | unknown |  | medium | YES | wiki96, kicadNA96 | Goes to the A/T system on automatic cars. Never drive. |
| 1S | 1S | Not used by OEM | none |  |  | medium |  | wiki96, mspnppro9697, hellenNA96 | Hellen re-uses this empty cavity for an add-on knock sensor input; wiki and DIY: not used. |
| 1T | 1T (test pad) | A/T only (PCM<->TCM / A/T signal) | comm | unknown |  | medium | YES | wiki96, kicadNA96 | Never drive. |
| 1U | 1U | Fuel pump relay control | out | LT GRN (allpinouts, unverified) |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697 | Low-side. |
| 1V | 1V | Not used | none |  |  | high |  | wiki96, mspnppro9697 |  |
| 2A | 4A (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2B | 4B (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2C | 4C (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2D | 4D (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2E | 4E (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2F | 4F (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2G | 4G (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2H | 4H (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2I | 4I (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2J | 4J (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2K | 4K (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 2L | 4L (Hellen options port) | 12-pin section: no mating plug in the OEM harness | none |  |  | medium |  | wiki96, mspnppro9697 | OEM harness does not populate section 2. DIY calls it 'optional wiring'; Hellen uses it as its options/WBO port (named 4A-4L). |
| 3A | 2A | Not used (OEM) | none |  |  | medium |  | wiki96, mspnppro9697 | Hellen uses it as a spare fuel-tank-pressure/aux input; wiki and DIY: not used. |
| 3B | 2B | MAF signal | in | RED/WHT |  | high |  | wiki96, hellenNA96, kicadNA96, allpinouts96 |  |
| 3C | 2C | Front HO2S signal | in | unknown | zirconia O2 | high |  | hellenNA96, kicadNA96, mspnppro9697, allpinouts96 |  |
| 3D | 2D | Rear HO2S signal | in | unknown | zirconia O2 | high |  | hellenNA96, kicadNA96, mspnppro9697, allpinouts96 |  |
| 3E | 2E (test pad) | Not used | none |  |  | high |  | wiki96, mspnppro9697 |  |
| 3F | 2F | Throttle position sensor | in | RED/BLK |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697, allpinouts96 |  |
| 3G | 2G | Engine coolant temperature sensor | in | BLU/WHT | thermistor | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697, allpinouts96 |  |
| 3H | 2H (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697, kicadNA96 |  |
| 3I | 2I | +5 V sensor reference (TPS, MAF) | power | unknown |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697 | ECU-sourced 5 V output. Never short to ground or 12 V. |
| 3J | 2J (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697, kicadNA96 |  |
| 3K | 2K | Intake air temperature sensor | in | unknown | thermistor | high |  | hellenNA96, kicadNA96, mspnppro9697, allpinouts96 |  |
| 3L | 2L (test pad) | Ground (probably MAF signal ground) | ground | unknown |  | low |  | mspnppro9697, kicadNA96 | Only DIY lists it, as 'Ground'. On 1994 a MAF signal ground existed (wiki94 2F BLK/RED). Hellen leaves it open. |
| 3M | 2M | Front HO2S heater control | out | unknown |  | high |  | mspnppro9697, hellenNA96, kicadNA96 | Low-side. Hellen yaml omits it, but the PCB jumper R26 routes 2M to OUT_O2H. |
| 3N | 2N (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697, kicadNA96 |  |
| 3O | 2O | Sensor (analogue) ground | ground | BLK/BLU |  | high |  | wiki96, mspnppro9697, hellenNA96, kicadNA96 | Return for TPS/CLT/IAT/MAF. Hellen: GNDA. |
| 3P | 2P (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697, kicadNA96 |  |
| 4A | 3A | Ground | ground | unknown |  | medium |  | wiki96, mspnppro9697, allpinouts96, kicadNA96 | Hellen ties 3A (OEM 4A) to GNDA. DIY and allpinouts: ground / power ground. |
| 4B | 3B | ECU +12 V from main relay | power | WHT/RED |  | high |  | wiki96, mspnppro9697, hellenNA96, kicadNA96 | Hellen fuses it and uses it as main supply and battery sense. The main relay is switched by the ignition switch (no ECU control found). |
| 4C | 3C | Ground | ground | unknown |  | high |  | mspnppro9697, kicadNA96 | Hellen: GND (power). |
| 4D | 3D | Ground | ground | unknown |  | high |  | mspnppro9697, kicadNA96 | Hellen: GND (power). |
| 4E | 3E (test pad) | Crank-pulley CKP sensor lead (OBD-II misfire sensor) | in | YEL/BLK | VR per AMP ('OE crankshaft VR signal'); polarity unknown | medium | YES | wiki96, amppro9697, tsb00698, mspnppro9697, kicadNA96 | This is the separate 1996-97 crank-pulley sensor. It is not the CAS signal used for fuel/spark by Hellen and DIY (both leave 4E open). Which of 4E/4H is + is UNRESOLVED. |
| 4F | 3F | CAS 4-pulse crank-angle signal (SGT/'CKP'), primary trigger | in | WHT | Hall/open-collector output of the cam-driven CAS (12 V fed); needs pull-up | high |  | mspnppro9697, hellenNA96, kicadNA96, haltechNA8, wiki94 | wiki96 labels it 'Cam Position Sensor', which is wrong: DIY says CKP and Hellen says CRANK (PULL_CRANK to 5 V). WHT is also the 4x SGT colour on 1994 (wiki94 2E). |
| 4G | 3G | CAS 2-pulse cam signal (SGC/CMP) | in | GRN (wiki, unverified) | Hall/open-collector output of the same CAS; needs pull-up | high |  | wiki96, mspnppro9697, hellenNA96, kicadNA96, haltechNA8 | Hellen fits a 4.7k pull-up to 5 V. |
| 4H | 3H (test pad) | Crank-pulley CKP sensor lead (OBD-II misfire sensor) | in | YEL/WHT | VR per AMP; polarity unknown | medium | YES | wiki96, amppro9697, tsb00698, mspnppro9697, kicadNA96 | Pair with 4E. Polarity UNRESOLVED. |
| 4I | 3I | CONFLICT: battery +12 V backup (Hellen) vs N/C (DIY Pro) vs optional tach output (MSPNP2 doc) | power | unknown |  | low | YES | kicadNA96, mspnppro9697, amp2_9697 | Hellen jumper R48 ties 3I to +12V_PERM (keep-alive). Probe with key off before use: if battery voltage, it is B+ backup. Never drive. |
| 4J | 3J (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697 |  |
| 4K | 3K (test pad) | CONFLICT: not used (wiki) vs condenser fan relay (DIY Pro) | none | unknown |  | low |  | wiki96, mspnppro9697, kicadNA96 |  |
| 4L | 3L | Tachometer output to instrument cluster | out | BLK/WHT (allpinouts, unverified) |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697, allpinouts96 | Drives the cluster tach input. Open-collector/pull-up style; do not back-drive 12 V. |
| 4M | 3M (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697 |  |
| 4N | 3N | Ignition IGT, cylinders 1 & 4 (igniter) | out | GRN (wiki, unverified) |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697 | Logic-level trigger to the coil pack with built-in igniter. |
| 4O | 3O (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697 |  |
| 4P | 3P (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697 |  |
| 4Q | 3Q | Idle air control valve (low side) | out | BLU/ORG |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697 | The IAC + is fed from the harness (no ECU pin). Needs a flyback diode. |
| 4R | 3R | Ignition IGT, cylinders 2 & 3 (igniter) | out | BRN |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697 |  |
| 4S | 3S | Not used (OEM) | none |  |  | medium |  | wiki96, mspnppro9697 | Hellen re-uses it for an 'EGR boost' aux input. |
| 4T | 3T (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697 |  |
| 4U | 3U | Injector No.1 | out | WHT (wiki, unverified) |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697 |  |
| 4V | 3V | Injector No.2 | out | YEL (wiki, unverified) |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697 |  |
| 4W | 3W | Injector No.3 | out | unknown |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697 |  |
| 4X | 3X | Injector No.4 | out | unknown |  | high |  | wiki96, hellenNA96, kicadNA96, mspnppro9697 |  |
| 4Y | 3Y (test pad) | Unknown | none | unknown |  | low | YES | mspnppro9697 |  |
| 4Z | 3Z | Rear HO2S heater control | out | unknown |  | medium |  | hellenNA96, kicadNA96 | DIY lists N/C. Hellen drives OUT_O2H2 here. |

## 1999-2000 (NB1, BP-4W 1.8)

### Header

- **oem section naming**: 1 (22-pin) | 2 (16-pin) | 3 (26-pin)
- **section sizes physical order**: 22+16+26 = 64 terminals used
- **sections used by oem harness**: all three (1, 2, 3)
- **header part number**: OEM: listed by rusEFI wiki as 64-pin TE 176122-6 / 4-174518-7 (22+16+26), medium confidence. Hellen NB1 instead uses 76-pos TE 178780-1 (22+12+16+26) and puts its own options port in the 12-pin slot between sections 1 and 2. Both fit the car, because the harness uses three separate plugs.
- **mating harness plugs**: 22p 174515-6 / 175110-6, 16p 174514-6 / 175109-6, 26p 174516-6 / 175111-6 (rusEFI wiki 64-pin entry)
- **hellen naming**: Hellen 1x/2x/3x = OEM 1x/2x/3x (same names). Hellen 4A-4L = Hellen options port (not OEM). The DIY MSPNP Pro MM9900 uses its own 1/2/3/4 names: DIY 3x = OEM 2x and DIY 4x = OEM 3x.
- **naming confidence**: medium-high: the same names appear in the rusEFI wiki, the Hellen 'OEM ECU pin' sheet and Alex Engineering. No Mazda FSM page was retrievable as text.
- **sources**: https://wiki.rusefi.com/Mazda-Miata-1999 (local: /home/claude/ref/rusefi.wiki/Mazda-Miata-1999.md); https://wiki.rusefi.com/OEM-connectors (local: /home/claude/ref/rusefi.wiki/OEM-connectors.md); https://docs.google.com/spreadsheets/d/19Mc_QA4MTJAY1hUR4UMexbdGiqNpH4JARKxWm1VD5KA (Hellen64_NB1 (99/00) pinout, 'OEM ECU pin' column); /home/claude/ref/miata/hellen-NB1/hellen64_NB1.kicad_pcb (pad->net trace); http://www.megasquirtpnp.com/docs/mspnp_gP_mm9900.php (DIY naming: their 3x = OEM 2x, their 4x = OEM 3x); https://alexengineering.pl/wp-content/uploads/2025/11/speeduino-pnp-nb-manual-eng-bt-upgrade-calibration-pinout-2.09.pdf

### Pins

| Terminal | Hellen | Function | Dir | Wire | Sensor type | Conf | No-drive | Sources | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1A | 1A | Battery +12 V backup (always hot) | power | BLU/RED |  | high | YES | wiki99, nb1sheet, kicadNB1 | Keep-alive input. Never drive. |
| 1B | 1B | ECU +12 V from main relay | power | WHT/RED |  | high |  | wiki99, nb1sheet, mspnppro9900, kicadNB1, alexeng | Hellen fuses it and uses it as main supply and VIGN/battery sense. The main relay is switched by the ignition switch (no ECU main-relay output is listed by any source). |
| 1C | 1C | N/C (OEM) | none |  |  | high |  | nb1sheet, mspnppro9900 | Hellen adds CAN-H here. |
| 1D | 1D (test pad) | Data Link Connector | comm | unknown |  | medium | YES | nb1sheet, kicadNB1 | Never drive. |
| 1E | 1E | MIL / check engine light | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng | Low-side, lamp in cluster. |
| 1F | 1F | Brake switch input | in | unknown | switch | high |  | nb1sheet, hellenNB1 |  |
| 1G | 1G | Power steering pressure switch input | in | unknown | switch | high |  | nb1sheet, hellenNB1, alexeng |  |
| 1H | 1H (test pad) | Unclear: '12 V battery (fuel inj 30A)' per Hellen sheet | power | unknown |  | low | YES | nb1sheet, kicadNB1 | Probe before use. Never drive. |
| 1I | 1I | A/C (condenser) fan relay | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng | Low-side. |
| 1J | 1J | N/C (OEM) | none |  |  | high |  | nb1sheet, mspnppro9900 | Hellen adds CAN-L here. |
| 1K | 1K (test pad) | TCM link (A/T) | comm | unknown |  | medium | YES | nb1sheet | Never drive. |
| 1L | 1L (test pad) | Data Link Connector | comm | unknown |  | medium | YES | nb1sheet | Never drive. |
| 1M | 1M (test pad) | N/C | none |  |  | medium |  | nb1sheet, mspnppro9900 |  |
| 1N | 1N (test pad) | TCM link (A/T) | comm | unknown |  | medium | YES | nb1sheet | Never drive. |
| 1O | 1O | Alternator field coil control (PWM) | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1 |  |
| 1P | 1P | A/C switch input | in | unknown | switch | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 1Q | 1Q | Charge (battery) warning lamp | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng | Low-side, lamp in instrument cluster. |
| 1R | 1R | Radiator cooling fan relay | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng | Low-side. |
| 1S | 1S | A/C compressor relay | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng | Low-side. |
| 1T | 1T (test pad) | Alternator sense (generator output voltage) | in | unknown |  | medium | YES | nb1sheet, mspnppro9900 | Input from the generator. Never drive. |
| 1U | 1U | Front HO2S heater control | out | unknown |  | high |  | nb1sheet, hellenNB1, alexeng | DIY MSPNP Pro grounds it permanently (labels it 'Ground'). Low-side. |
| 1V | 1V | Neutral switch input | in | unknown | switch | high |  | wiki99, nb1sheet, hellenNB1 |  |
| 2A | 2A | Fuel tank pressure sensor | in | unknown |  | high |  | wiki99, nb1sheet, hellenNB1 |  |
| 2B | 2B | Intake air temperature sensor | in | unknown | thermistor | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 2C | 2C | Front HO2S signal | in | unknown | zirconia O2 | high |  | nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 2D | 2D | Vehicle speed sensor | in | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 2E | 2E | Engine coolant temperature sensor | in | unknown | thermistor | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 2F | 2F | Knock sensor | in | unknown | piezo | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1 |  |
| 2G | 2G | N/C (OEM) | none |  |  | high |  | wiki99, nb1sheet, mspnppro9900 | Hellen adds an AFR input here. |
| 2H | 2H | Camshaft position sensor (CMP/SGC) signal | in | unknown | Hall, 3-wire, 12 V fed; open-collector-style (Hellen 4.7k pull-up to 5 V) | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, kicadNB1, alexeng, haltechNB2, walmartcmp | The CMP is sold as one part for 1999-2005; Haltech says the NB2 CMP is Hall-effect. Its ground return is not identified for NB1. |
| 2I | 2I | +5 V sensor reference | power | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1 | ECU-sourced 5 V output. |
| 2J | 2J | Crankshaft position sensor (CKP/NE) signal | in | unknown | Hall, 3-wire, 12 V fed from main relay | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, kicadNB1, alexeng, coxckp, fsm2005, haltechNB2 | Same part BP4W-18-221 fits 1999-2005; the NB2 FSM shows terminal A = main-relay power, B = signal, C = ground to PCM. |
| 2K | 2K | Tachometer output | out | unknown |  | medium |  | wiki99, nb1sheet, mspnppro9900, hellenNB1 | Alex Engineering calls 2K a 'stock unused pin'; three other sources say tach out. Verify on the harness. |
| 2L | 2L | MAF signal | in | unknown |  | high |  | nb1sheet, hellenNB1 |  |
| 2M | 2M (test pad) | EGR valve stepper coil | out | unknown | stepper coil | medium |  | nb1sheet, kicadNB1 | Hellen leaves these as test pads. |
| 2N | 2N (test pad) | EGR valve stepper coil | out | unknown | stepper coil | medium |  | nb1sheet, kicadNB1 | Hellen leaves these as test pads. |
| 2O | 2O (test pad) | EGR valve stepper coil | out | unknown | stepper coil | medium |  | nb1sheet, kicadNB1 | Hellen leaves these as test pads. |
| 2P | 2P (test pad) | EGR valve stepper coil | out | unknown | stepper coil | medium |  | nb1sheet, kicadNB1 | Hellen leaves these as test pads. |
| 3A | 3A | Power ground | ground | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, kicadNB1 |  |
| 3B | 3B | Power ground | ground | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, kicadNB1 |  |
| 3C | 3C | Power ground | ground | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, kicadNB1 |  |
| 3D | 3D | N/C (OEM) | none |  |  | high |  | nb1sheet, mspnppro9900 | Hellen adds an external MAP input here. |
| 3E | 3E | Throttle position sensor | in | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 3F | 3F | Sensor (analogue) ground | ground | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900 | Hellen PCB ties 3F to GND, not GNDA. |
| 3G | 3G | Ignition IGT, cylinders 1 & 4 | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 3H | 3H | Ignition IGT, cylinders 2 & 3 | out | BRN |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 3I | 3I | Clutch switch input | in | unknown | switch | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 3J | 3J | Rear HO2S signal | in | unknown | zirconia O2 | high |  | nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 3K | 3K (test pad) | N/C (Hellen sheet, DIY) vs 'fuel gauge' (wiki) | none | unknown |  | low | YES | nb1sheet, mspnppro9900, wiki99 | If it is the fuel gauge it belongs to the cluster. Never drive. |
| 3L | 3L (test pad) | Purge solenoid | out | unknown |  | high |  | nb1sheet, alexeng |  |
| 3M | 3M | Idle air control valve (negative / low side) | out | unknown |  | high |  | nb1sheet, mspnppro9900, hellenNB1, alexeng | The wiki 1999 page has 3M and 3O swapped (it calls 3M 'IAC power +12'). Hellen, DIY, Alex and the Hellen sheet all put the IAC drive on 3M. |
| 3N | 3N | Fuel pump relay (US cars) | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 3O | 3O | IAC +12 V supply (output from PCM) | power | ORG (wiki, attached to wrong pin there) |  | medium |  | nb1sheet, mspnppro9900, kicadNB1 | Hellen connects 3O to its +12V_RAW rail fed from 1B. DIY calls it '+12V Ignition'. Treat as power out to the IAC +; it must not be shorted. |
| 3P | 3P | Fuel pump relay (European cars with immobilizer) | out | unknown |  | medium |  | nb1sheet, mspnppro9900, amppro9900, alexeng | DIY jumper J2 selects 'Europe w/ immob.'. On US cars 3P is probably unpopulated. On EU cars the immobilizer path may sit on this circuit, so check before driving. |
| 3Q | 3Q | VICS solenoid | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 3R | 3R (test pad) | N/C | none |  |  | medium |  | nb1sheet, mspnppro9900 |  |
| 3S | 3S | EGR boost sensor | in | unknown |  | medium |  | nb1sheet, hellenNB1 |  |
| 3T | 3T | EGR boost sensor solenoid | out | unknown |  | medium |  | nb1sheet, hellenNB1 | Hellen re-uses it as a boost-control output. |
| 3U | 3U (test pad) | Canister drain cut valve (CDCV) | out | unknown |  | medium |  | nb1sheet |  |
| 3V | 3V | Rear HO2S heater control | out | unknown |  | high |  | nb1sheet, mspnppro9900, hellenNB1 |  |
| 3W | 3W | Injector No.1 | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 3X | 3X | Injector No.2 | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 3Y | 3Y | Injector No.3 | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |
| 3Z | 3Z | Injector No.4 | out | unknown |  | high |  | wiki99, nb1sheet, mspnppro9900, hellenNB1, alexeng |  |

## 2001-2005 (NB2, BP-Z3 1.8 S-VT (VVT); MSM turbo deltas in notes)

### Header

- **oem section naming**: 2 (17 terminals: 2A-2R without 2L) | 3 (24 terminals: 3A-3Z without 3G and 3R) | 4 (31 terminals: 4A-4AH without 4G, 4Q, 4Y)
- **section sizes physical order**: 17+24+31 = 72
- **sections used by oem harness**: all three (2, 3, 4). There is no OEM section '1'.
- **header part number**: OEM: 72-pos TE 353830-5 ('040III HD 72POS CAP ASSY', 3 rows, through-hole) per the rusEFI wiki and Heilind; alternate TE 1123038-2 per the rusEFI wiki. Hellen NB2 uses the 122-pos TE 8-5353015-1, which adds a 22-pos section '1' (mostly unconnected) and a 28-pos section '5' (Hellen options port) to the left of OEM 2/3/4: physical order 1(22) | 5(28) | 2(17) | 3(24) | 4(31).
- **hellen naming**: Hellen 2x/3x/4x = OEM 2x/3x/4x (same names). Hellen 1x and 5x are Hellen-only. The Hellen yaml '4Q' entry has no cavity in the footprint (phantom). The 2005 FSM lists 4G/4Q/4Y as '-'.
- **naming confidence**: high (2005 Mazda workshop manual terminal tables match the Hellen footprint cavities)
- **year split**: 2001-2002: main relay switched by the ignition switch; ECU power 4AF only; 4S not connected; 3H unused. 2003-2005: PCM drives the main relay via 3H; 4S = IG1 sense. (rusEFI wiki 2002/2003 pages; Hellen-NB2 jumper notes; 2005 FSM for 2005.) Whether 2001 matches 2002 exactly, and where 2004 falls, is inferred, not documented.
- **sources**: https://www.mellens.net/mazda/Mazda-Miata-2005/engine_control_system.pdf (Mazda 2005 MX-5 workshop manual, PCM terminal voltage tables BP and BP-with-TC); https://wiki.rusefi.com/OEM-connectors (local: /home/claude/ref/rusefi.wiki/OEM-connectors.md); https://www.heilind.com/amp353830-5.html; /home/claude/ref/miata/hellen-NB2/hellen72_NB2.kicad_pcb + connector-mapping.txt (pad->net trace); https://wiki.rusefi.com/Hellen-NB2 (local: /home/claude/ref/rusefi.wiki/Hellen-NB2.md); https://wiki.rusefi.com/Mazda-Miata-2002; https://wiki.rusefi.com/Mazda-Miata-2003

### Pins

| Terminal | Hellen | Function | Dir | Wire | Sensor type | Conf | No-drive | Sources | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2A | 2A | Injector No.1 | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 2B | 2B | Cooling fan relay (TC: fan relay No.1) | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 2C | 2C | Condenser fan relay (TC: fan relays No.2/3) | out | unknown |  | high |  | fsm2005, hellenNB2, wiki2003alt |  |
| 2D | 2D | Injector No.2 | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 2E | 2E (test pad) | EGR valve stepper coil #1 (EGR valve terminal E) | out | unknown | stepper coil | high |  | fsm2005, hellenNB2 |  |
| 2F | 2F (test pad) | EGR valve stepper coil #2 (EGR valve terminal A) | out | unknown | stepper coil | high |  | fsm2005, hellenNB2 |  |
| 2G | 2G | Injector No.3 | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 2H | 2H (test pad) | EGR valve stepper coil #3 (EGR valve terminal B) | out | unknown | stepper coil | high |  | fsm2005, hellenNB2 |  |
| 2I | 2I (test pad) | EGR valve stepper coil #4 (EGR valve terminal F) | out | unknown | stepper coil | high |  | fsm2005, hellenNB2 |  |
| 2J | 2J | Injector No.4 | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 2K | 2K | A/C relay | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 2M | 2M | Fuel pump relay | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 2N | 2N | VTCS solenoid valve | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 2O | 2O | Not used (OEM) | none |  |  | high |  | fsm2005 | Hellen re-uses it as IGN3 for a coil-on-plug option. |
| 2P | 2P | IAC valve positive (+12 V supply out) | power | unknown |  | high |  | fsm2005, hellenNB2, kicadNB2, wiki2003 | Hellen feeds it from 4AF (main relay). Fit a flyback diode 2P-2Q. |
| 2Q | 2Q | IAC valve negative (low side) | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 2R | 2R | MIL control (lamp in instrument cluster) | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 3A | 3A | Fuel injector ground (power ground) | ground | unknown |  | high |  | fsm2005, kicadNB2 |  |
| 3B | 3B | PCM ground | ground | unknown |  | high |  | fsm2005, kicadNB2 |  |
| 3C | 3C | Purge solenoid valve | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 3D | 3D | EGR boost sensor switching solenoid (TC: BARO/MAP switching) | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 3E | 3E | Not used in 2005 BP table; Hellen: CDCV (EVAP canister drain cut valve) | out | unknown |  | medium |  | fsm2005, hellenNB2 | Probably year-dependent: early NB2 EVAP used a CDCV, 2005 uses a leak-detection pump. |
| 3F | 3F | Ignition IGT, cylinders 1 & 4 | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 3H | 3H | Main relay control (2003-2005); not used (2001-2002) | out | unknown |  | high |  | fsm2005, wiki2002, wiki2003, hellenNB2 | 2005 FSM: B+ with ignition off, below 1 V with ignition on (low-side). The rusEFI wiki says the 2002 main relay is switched by the ignition switch, with nothing on 3H. |
| 3I | 3I | Ignition IGT, cylinders 2 & 3 | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 3J | 3J | Front HO2S heater control | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 3K | 3K | EVAP leak-detection pump motor (2005); Hellen: NC / SENS2 input | out | unknown |  | medium |  | fsm2005, hellenNB2 | Year-dependent. On 2005 it is a PCM output to the LDP. |
| 3L | 3L | Not used (OEM) | none |  |  | high |  | fsm2005 | Hellen re-uses it for AFR input / IGN7. |
| 3M | 3M | Generator field coil control (generator terminal D) | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 3N | 3N | Not used (OEM) | none |  |  | high |  | fsm2005 | Hellen re-uses it as IGN4. |
| 3O | 3O | Engine speed output: tachometer and DLC IG-TCM (A/T) | out | unknown |  | high |  | fsm2005, hellenNB2 | Shared with the A/T TCM. Must remain a tach-style open-collector output. |
| 3P | 3P | Rear HO2S heater control | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 3Q | 3Q | K-line serial communication (DLC-2 terminal KLN) | comm | unknown |  | high | YES | fsm2005, hellenNB2 | Never drive. |
| 3S | 3S | Immobilizer communication (immobilizer unit) | comm | unknown |  | high | YES | fsm2005, hellenNB2 | Never drive. |
| 3T | 3T | Vehicle speed (VSS; TC: from instrument cluster) | in | unknown | Haltech: reluctor VSS converted to Hall-style by the speedometer | high |  | fsm2005, hellenNB2, haltechNB2 |  |
| 3U | 3U | Generator warning light (in instrument cluster) | out | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 3V | 3V | CMP sensor signal (SGC) | in | unknown | Hall-effect, 3-wire, 12 V switched (Haltech); FSM measures SGC against PCM 4A | high |  | fsm2005, hellenNB2, kicadNB2, haltechNB2 | Hellen fits a 4.7k pull-up to 5 V. |
| 3W | 3W | Not used (OEM) | none |  |  | high |  | fsm2005 | Hellen re-uses it for CAN-H. |
| 3X | 3X | Not used (OEM) | none |  |  | high |  | fsm2005 | Hellen re-uses it for CAN-L. |
| 3Y | 3Y | CKP sensor signal (NE) | in | unknown | Hall-effect, 3-wire: A = +12 V from main relay terminal D, B = signal to 3Y, C = ground to PCM 4A | high |  | fsm2005, hellenNB2, kicadNB2, haltechNB2 |  |
| 3Z | 3Z | Not used (OEM) | none |  |  | high |  | fsm2005 | Hellen re-uses it as GNDA / IGN5 (jumper). |
| 4A | 4A | Device ground (also CKP sensor ground return) | ground | unknown |  | high |  | fsm2005, kicadNB2 | The CKP terminal C returns here. It is the reference for the SGC/NE waveform checks. |
| 4B | 4B | Brake switch | in | unknown | switch | high |  | fsm2005, hellenNB2 |  |
| 4C | 4C | Power steering pressure switch | in | unknown | switch | high |  | fsm2005, hellenNB2 |  |
| 4D | 4D | OCV positive (+12 V supply out) (TC: wastegate regulating valve) | power | unknown |  | high |  | fsm2005, hellenNB2, wiki2003 | Hellen feeds it from 4AF via fuse F6. Fit a flyback diode 4D-4R. |
| 4E | 4E | DTM switching, from DLC terminal TEN (TC: wastegate control monitor) | in | unknown |  | high | YES | fsm2005, hellenNB2 | Comes from the diagnostic connector. Never drive. |
| 4F | 4F | A/C refrigerant pressure switch | in | unknown | switch | high |  | fsm2005, hellenNB2 |  |
| 4H | 4H | Neutral switch (MT) | in | unknown | switch | high |  | fsm2005, hellenNB2 |  |
| 4I | 4I | Clutch switch (MT) | in | unknown | switch | high |  | fsm2005, hellenNB2 |  |
| 4J | 4J | VTCS vacuum switch | in | unknown | switch | high |  | fsm2005, hellenNB2 |  |
| 4K | 4K | Not used (OEM) | none |  |  | high |  | fsm2005 | Hellen re-uses it as +5 V for MAP or IGN6. The wiki 2003-alt page wrongly lists knock on 4K. |
| 4L | 4L | VREF +5 V (TP, EGR boost / BARO-MAP sensors) | power | unknown |  | high |  | fsm2005, hellenNB2 | ECU-sourced 5 V. |
| 4M | 4M | Knock sensor | in | unknown | piezo | high |  | fsm2005, hellenNB2 |  |
| 4N | 4N | IAT sensor (TC: IAT No.1) | in | unknown | thermistor | high |  | fsm2005, hellenNB2 |  |
| 4O | 4O | Analogue sensor ground (EGR boost, TP, ECT, IAT, HO2S) | ground | unknown |  | high |  | fsm2005, hellenNB2, kicadNB2 |  |
| 4P | 4P | ECT sensor | in | unknown | thermistor | high |  | fsm2005, hellenNB2 |  |
| 4R | 4R | OCV negative (low side) (TC: IAT No.2 input!) | out | unknown |  | high |  | fsm2005, hellenNB2 | On the Mazdaspeed (BP with TC) 4R is an INPUT (IAT No.2). Do not drive it on MSM. |
| 4S | 4S | IG1 ignition-switch sense (2003-2005); not connected (2001-2002) | in | unknown |  | high |  | fsm2005, wiki2002, wiki2003, wikiHellenNB2 | Fed from the 15A ENGINE fuse in start/run (wiki 2003). |
| 4T | 4T | Generator output voltage (generator terminal P) | in | unknown |  | high |  | fsm2005, wikiHellenNB2 | Hellen measures battery voltage here on 2002 cars. Input only. |
| 4U | 4U | Not used (OEM) | none |  |  | high |  | fsm2005, hellenNB2 | Hellen re-uses it for MAP2/IGN8. |
| 4V | 4V | TP sensor | in | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 4W | 4W | Front HO2S signal | in | unknown | zirconia O2 | high |  | fsm2005, kicadNB2 |  |
| 4X | 4X | MAF sensor (TC: MAP/MAF) | in | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 4Z | 4Z | PCM-to-TCM communication (A/T) | comm | unknown |  | high | YES | fsm2005, hellenNB2 | Goes to TCM terminal O. Never drive. |
| 4AA | 4AA | Rear HO2S signal | in | unknown | zirconia O2 | high |  | fsm2005, hellenNB2 |  |
| 4AB | 4AB | Not used in 2005 BP table; Hellen: fuel tank pressure sensor | in | unknown |  | medium |  | fsm2005, hellenNB2 | Probably year-dependent (EVAP). |
| 4AC | 4AC | TCM-to-PCM communication (A/T) (TC: test mode via DLC TEN) | comm | unknown |  | high | YES | fsm2005, hellenNB2 | Goes to TCM terminal AL. Never drive. |
| 4AD | 4AD | Fuel tank level (fuel gauge sender) | in | unknown |  | high | YES | fsm2005, hellenNB2 | Shared with the fuel gauge. Never drive. |
| 4AE | 4AE | EGR boost / BARO sensor | in | unknown |  | high |  | fsm2005, hellenNB2 |  |
| 4AF | 4AF | ECU +12 V from main relay | power | unknown |  | high |  | fsm2005, hellenNB2, wiki2002, wiki2003 | Main power input. On Hellen it also feeds IAC+ (2P) and OCV+ (4D). |
| 4AG | 4AG | Battery back-up power (always hot) | power | unknown |  | high | YES | fsm2005, hellenNB2 | Keep-alive. Never drive. |
| 4AH | 4AH | EVAP leak-detection pump solenoid | out | unknown |  | medium |  | fsm2005, hellenNB2 | Year-dependent EVAP hardware. |

## Source key

- `wiki96`: https://wiki.rusefi.com/Mazda-Miata-1996 (local: /home/claude/ref/rusefi.wiki/Mazda-Miata-1996.md)
- `wiki94`: https://wiki.rusefi.com/Mazda-Miata-1994
- `hellenNA96`: /home/claude/ref/rusefi/firmware/config/boards/hellen/hellenMiataNA96/connectors/main.yaml ; https://rusefi.com/docs/pinouts/hellen/hellenNA8_96/
- `kicadNA96`: /home/claude/ref/miata/hellen-NA8-96/hellen64_NA8_96.kicad_pcb (pad->net trace)
- `mspnppro9697`: http://www.megasquirtpnp.com/docs/mspnp_gP_mm9697.php
- `amppro9697`: https://ampenginemanagement.com/blogs/mspnp-pro-documentation/pro-mm9697-installation
- `amp2_9697`: https://ampenginemanagement.com/blogs/mspnp2-documentation/mspnp2-mm9697-v2-installation
- `haltechNA8`: https://support.haltech.com/portal/en/kb/articles/93-na8-1-6l-b6-ze
- `tsb00698`: https://www.miata.net/garage/tsb/006-98-1.pdf
- `allpinouts96`: https://allpinouts.org/pinouts/connectors/car/1996-1997-mazda-miata-ecu/
- `ebay96ckp`: https://www.ebay.com/itm/256963168515
- `frankenso`: /home/claude/ref/rusefi-hardware/classic-designs/frankenso/known_issues.txt (item 50); /home/claude/ref/rusefi-hardware/classic-designs/frankenso/www_docs/frankenso_connector_miata_1996.png
- `oemconn`: https://wiki.rusefi.com/OEM-connectors (local: /home/claude/ref/rusefi.wiki/OEM-connectors.md)
- `heilind178780`: https://www.heilind.com/amp178780-1.html
- `wiki99`: https://wiki.rusefi.com/Mazda-Miata-1999 (local: /home/claude/ref/rusefi.wiki/Mazda-Miata-1999.md)
- `nb1sheet`: https://docs.google.com/spreadsheets/d/19Mc_QA4MTJAY1hUR4UMexbdGiqNpH4JARKxWm1VD5KA (Hellen64_NB1 (99/00) pinout, 'OEM ECU pin' column)
- `hellenNB1`: /home/claude/ref/rusefi/firmware/config/boards/hellen/hellenMiataNB1/connectors/main.yaml ; https://rusefi.com/docs/pinouts/hellen/hellen-nb1/
- `kicadNB1`: /home/claude/ref/miata/hellen-NB1/hellen64_NB1.kicad_pcb (pad->net trace)
- `mspnppro9900`: http://www.megasquirtpnp.com/docs/mspnp_gP_mm9900.php (DIY naming: their 3x = OEM 2x, their 4x = OEM 3x)
- `amppro9900`: https://ampenginemanagement.com/blogs/mspnp-pro-documentation/pro-mm9900-installation
- `alexeng`: https://alexengineering.pl/wp-content/uploads/2025/11/speeduino-pnp-nb-manual-eng-bt-upgrade-calibration-pinout-2.09.pdf
- `coxckp`: https://www.coxmazdaparts.com/oem-parts/mazda-crankshaft-position-sensor-bp4w18221b
- `walmartcmp`: https://www.walmart.com/ip/1189340422
- `fsm2005`: https://www.mellens.net/mazda/Mazda-Miata-2005/engine_control_system.pdf (Mazda 2005 MX-5 workshop manual, PCM terminal voltage tables BP and BP-with-TC)
- `wiki2002`: https://wiki.rusefi.com/Mazda-Miata-2002
- `wiki2003`: https://wiki.rusefi.com/Mazda-Miata-2003
- `wiki2003alt`: https://wiki.rusefi.com/Mazda-Miata-2003-alt
- `wikiHellenNB2`: https://wiki.rusefi.com/Hellen-NB2 (local: /home/claude/ref/rusefi.wiki/Hellen-NB2.md)
- `hellenNB2`: /home/claude/ref/rusefi/firmware/config/boards/hellen/hellenMiataNB2/connectors/main.yaml ; https://rusefi.com/docs/pinouts/hellen/hellen72/
- `kicadNB2`: /home/claude/ref/miata/hellen-NB2/hellen72_NB2.kicad_pcb + connector-mapping.txt (pad->net trace)
- `haltechNB2`: https://support.haltech.com/portal/en/kb/articles/01-05-nb2-1-8l-w-vvt-bp-z3-bp-ve
- `heilind353830`: https://www.heilind.com/amp353830-5.html
- `beermoney`: https://www.beermoneymotorsports.com/pages/nb2-pinout-wiring (derived from Hellen yaml, not independent)
