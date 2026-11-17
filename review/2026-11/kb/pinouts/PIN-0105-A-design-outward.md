# PIN-0105-A: pinout chain audit 2001-05 (NB2, BP-Z3 VVT), method A (design outward)

Boards: cur_mb0105 (motherboard rev 0.9 + daughterboard rev 0.10) and ord_mb0105 (rev 0.7 + daughterboard rev 0.9). Mazdaspeed excluded.
Scratch: work/PIN-0105-A-design-outward/ (Haltech/pinouts.ru/rusEFI wiki dumps, CHARM 2001 voltage-table PNGs c2001_*.png).

## Summary
1. Chain wiring is correct for all 36 connected cavities: harness pad -> net -> JD pin -> daughterboard net -> MCU pin -> firmware all agree (interconnect.md cur/ord; design.py `mcu` dict vs LQFP100 numbering; miata_pins.h). The 72 harness pads equal exactly the physical cavity set of the Mazda connector drawing (17 + 24 + 31; no 2L, 3G, 3R, 4G, 4Q, 4Y). VERIFIED.
2. Every connected cavity's stock function was confirmed against at least two independent sources: Mazda 2001/2002/2003 CHARM PCM voltage tables (read as images), Mazda 2005 FSM (via repo pinouts file, claim), rusEFI Hellen NB2 yaml and wiki 2002/2003 pages, Haltech NB2 page. No pin error found.
3. 2001 = 2002 (verified from the 2001 CHARM table: 3H "-", 4S "-", 3E CDCV, 4V TP). 2003-05: 3H main relay (B+ key off, <1 V key on) and 4S IG1. The two presets differ only in mainRelayPin and ignKeyAdcChannel. The 2003-05 wake-up path exists in hardware: 4S -> D8 -> F1 -> +12V (design.py:204), so the ECU can boot before the relay it must close. VERIFIED (design), INFERRED (that the stock relay coil is fed from battery and only grounded by 3H, from the 3H voltage table).
4. Functional gaps with customer-visible effect (new): A/C request 4F and clutch 4I are active-low with ECU-side pull-up (CHARM + Hellen firmware), but the board ships R21/R22 not fitted and firmware does not set the pin mode: A/C never engages; condenser fan 2C is not tied to A/C; charge lamp 3U never driven.
5. Everything else not done by this board (VTCS, EGR, purge, CDCV/LDP, heaters, K-line, immobiliser, A/T serial, battery backup) is harmless to the engine; consequences below.
6. Wire colours at the PCM connector could not be found in any text source (see Not checked). Sensor-side colours from Haltech only.

## Sources used (independent set)
- CHARM2001/2002/2003: Mazda workshop manual PCM Terminal Voltage Tables (charm.li, pages read as images; 2003 PNGs in kb/research/files/R19, 2001 in work dir). Primary factory source for electrical character.
- FSM2005: via repo/research/pinouts_9605.md (claim, not re-read).
- HELLEN: repo/firmware/ext/rusefi/.../hellenMiataNB2/connectors/main.yaml and board_configuration.cpp (rusEFI's own plug-in board), ext/hellen-miata-NB2/connector-mapping.txt.
- WIKI: wiki.rusefi.com Mazda-Miata-2001/2002/2003/2003-alt (read today).
- HALTECH: support.haltech.com 01-05 NB2 BP-Z3 page (read today): sensor wire colours, IAC, alternator, VTCS, VSS.
- AMP: MSPNP-Pro MM0105 page (immobiliser statement), MiataTurbo thread (R19).

## Chain table (cur_mb0105 unless marked; ord differs where noted)
Conditioning on the daughterboard (rev 0.10 / ordered rev 0.9): low-side outputs go MCU -> SN74LVC4245 (3.3->5 V, OE = DRV_EN) -> [220 R in rev 0.10 only] -> ST VND7NV04 (inj, IACV, VVT, BOOST, ALT) or ZXMS6004FF (FP, MAINRLY, AC, FAN, CEL, TACH, LS7), active high. Inputs: analog 5.6k/10k divider + 10n + BAT54WS clamp to 3V3; Hall 1k (via D35 Schottky) to V5_EXT + 4.7k + 1n + 1N4148 clamp; switch inputs 22k/10k + 10n + clamp; knock 2.2k + 100n AC coupling + LMV321 gain 5.7 + 330R; IGN TC4427 5 V push-pull.

| Cavity | Stock function, electrical (source) | MB net, parts | JD pin | MCU pin / firmware (year preset) | Verdict |
|---|---|---|---|---|---|
| 2A,2D,2G,2J | Injector 1-4 low side, wave profile (CHARM, Hellen, FSM) | OUT_INJ1..4 | JD1.19/22/25/28 | PB7/PB6/PB5/PB4, injectionPins, sequential (NB common) | correct |
| 2B | Cooling (radiator) fan relay, low = on, B+ off (CHARM 2003 p1) | OUT_FAN | JD1.9 | PE5, fanPin, fan1AcMode=Relay, on 92 C default | correct pin; see F-A/C |
| 2C | Condenser fan relay, low = on (CHARM) | OUT_LS7 | JD1.12 | PE2, fan2Pin, fan2AcMode unset (Disabled), on 95 C | correct pin; condenser fan not tied to A/C |
| 2E,2F,2H,2I | EGR stepper coils 1-4 (CHARM: 2E/2I <1 V, 2F/2H B+ held) | none | - | none | unconnected by design: EGR stays at its last position (see below) |
| 2K | A/C relay, <1 V when A/C+fan switches on, else B+ (CHARM) | OUT_AC | JD1.8 | PE6, acRelayPin | correct |
| 2M | Fuel pump relay: B+ key on, <1 V cranking and idle (CHARM) | OUT_FP | JD1.6 | PC14 (backup domain pin), fuelPumpPin; rusEFI primes on key-on | correct; stock has no long prime either |
| 2N | VTCS solenoid: B+ ECT>60 idling, <1 V ECT<60 at 3500 rpm (CHARM) | none | - | none | unconnected by design (VTCS) |
| 2P | IAC +: +12 V supply out of PCM (Hellen "via 4AF", wiki) | IAC_12V = VBAT_IN via F2 (2 A PTC); D1 SS34 2P->2Q | - | - | correct |
| 2Q | IAC low side, 2-wire duty valve (Haltech: pin1 signal, pin2 12 V) | OUT_IACV, D1 | JD1.31 | PB3, idle.solenoidPin, 300 Hz rusEFI default (stock frequency not found) | correct, polarity ok (low side, flyback to supply) |
| 2R | MIL, low = on key on, B+ off (CHARM) | OUT_CEL | JD1.10 | PE4, malfunctionIndicatorPin | correct |
| 2O,2L(absent) | not used | - | - | - | correct (nothing) |
| 3A | injector ground | GND | JD1 grounds | - | correct |
| 3B | PCM ground | GND | | - | correct |
| 3C | Purge solenoid, wave | none | - | none | unconnected (purge) |
| 3D | EGR boost-sensor switching solenoid, B+ always | none | - | none | unconnected (EGR) |
| 3E | 2001-02: CDCV, B+ key on; 2003+: "-" (CHARM 2001/2002 vs 2003) | none | - | none | unconnected (CDCV) |
| 3F / 3I | IGT cyl 1&4 / 2&3 | OUT_IGN1 / OUT_IGN2 | JD1.14 / 15 | PE1 / PE0, ignitionPins[0]/[2] | correct (coil igniter input 5 V logic) |
| 3H | 2003-05 main relay: B+ key off, <1 V key on; 2001-02 "-" | OUT_MAINRLY, J5.5 | JD1.7 | PC13; mainRelayPin only if !nb2Early | correct |
| 3J | Front HO2S heater, <1 V (on) from key-on (CHARM) | none | - | o2heaterPin unassigned | unconnected: heater never powered |
| 3K | 2003: EVAP leak detection pump (B+) | none | - | none | unconnected |
| 3M | Generator field control (generator D), PWM | OUT_ALT, J5.4 | JD1.40 | PD5 alternatorControlPin, 250 Hz, control disabled by default | correct pin; documented risk |
| 3O | Engine speed to tach and DLC IG-TCM (A/T) | OUT_TACH | JD1.11 | PE3, tachOutputPin, 2 pulses/rev | correct |
| 3P | Rear HO2S heater: B+ key on, <1 V when heating | none | - | none | unconnected |
| 3Q / 3S | K-line / immobiliser serial | none | - | none | unconnected, never drive |
| 3T | VSS pulse (reluctor converted by speedometer to Hall-style, Haltech; waveform in CHARM) | IN_SW1, R20 (DNP 4.7k to VBAT) | JD2.15 | PE9 vehicleSpeedSensorInputPin; 4 pulses x 1.117 per wheel turn | correct pin; drive type/pull-up cannot verify |
| 3U | Generator warning lamp, <1 V key on, B+ running (CHARM) | none | - | none | unconnected: lamp never lights |
| 3V | CMP (SGC), 3-wire Hall, +12 V from main relay | IN_HALL2 | JD2.14 | PE8, camInputs[0], VVT_MIATA_NB | correct |
| 3Y | CKP (NE), 3-wire Hall | IN_HALL1 | JD2.13 | PE7, trigger TT_MIATA_VVT | correct |
| 3W,3X,3Z,3N,3L | not used | - | - | - | correct |
| 4A | device ground, CKP return | GND | | | correct |
| 4B / 4C | brake switch (B+ pressed) / power-steering pressure switch (<1 V turned) | none | - | none | unconnected: no PS idle-up |
| 4D | OCV +12 V supply out of PCM (Hellen "via 4AF", wiki) | OCV_12V via F3 (2 A PTC); D2 SS34 4D->4R | - | - | correct |
| 4R | OCV low side (negative) | OUT_VVT, D2 | JD1.34 | PD7, vvtPins[0] (NB2 only), auxPid, 300 Hz default | correct |
| 4E | DTM / DLC TEN | none | | | unconnected, never drive |
| 4F | A/C: <1 V when A/C and fan switches on, else B+ (CHARM); Hellen: PI_PULLUP input | IN_SW2, R21 (DNP) | JD2.16 | PE10 acSwitch, mode default | wrong default: see F1 |
| 4H | neutral switch (MT) <1 V in neutral | none | - | none | unconnected |
| 4I | clutch (MT): B+ released, <1 V depressed (CHARM); Hellen PI_INVERTED_DEFAULT | IN_SW3, R22 (DNP) | JD2.17 | PE11 clutchDownPin, mode default | wrong default: see F1 |
| 4J | VTCS vacuum switch input | none | - | none | unconnected |
| 4L | Vref 5 V to TP and EGR boost sensors | V5_EXT (JD1.13, J5.14, R35) | JD1.13 | protected tracker U14 | correct |
| 4M | knock sensor (piezo, ~2.4 V DC at PCM) | IN_KNOCK, J5.6 | JD2.3 | PA3 ADC3, AC coupled, software knock | correct |
| 4N | IAT thermistor 2.3-2.4 V at 20 C | IN_IAT (cur); HARN_IAT -> JP1 -> IN_IAT (ord, shunt STOCK) | JD2.7 | PA7, 2.7k to V5_EXT | correct |
| 4O | analogue sensor ground | GND | | | correct |
| 4P | ECT thermistor ~3.0 V at 20 C, 0.9 V at 80 C | IN_CLT | JD2.6 | PA6 | correct pin (curve not checked) |
| 4S | 2003-05 IG1 sense <1 V off, B+ on (CHARM 2003); 2001-02 "-" | VIGN_IN | JD1.3 | D8 wake path; PA2 divider; ignKeyAdcChannel only 2003-05 | correct |
| 4T | generator P output voltage input (3-8 V idle) | none | - | none | unconnected, harmless |
| 4V | TP: 0.1-1.1 V closed, 3.0-4.6 V WOT (CHARM 2001/2002, FSM05, Hellen, wiki) | IN_TPS | JD2.4 | PA4 | correct. (2003 CHARM lists TP on 4Y: the 2003 connector figure has no 4Y; typo) |
| 4W | Front HO2S, zirconia narrowband 0-1 V | IN_AUX2 | JD2.10 | PB0, not used by default | correct |
| 4X | MAF, 0.9-2.0 V key on, 1.7-2.4 V idle (12 V powered sensor, Haltech colours B/L gnd, pink sig, W/R 12 V) | IN_AUX3 | JD2.11 | PB1 mafAdcChannel | correct |
| 4AA | Rear HO2S signal | IN_AUX1 | JD2.9 | PC5 | correct |
| 4AB | 2001-02 FTP sensor; later "-" | none | | | unconnected |
| 4AC / 4Z | A/T serial | none | | | unconnected, never drive (A/T untested) |
| 4AD | fuel level sender 0.2-4.4 V (shared) | none | | | unconnected |
| 4AE | BARO/EGR boost sensor 4.1-4.3 V | none | | | unconnected |
| 4AF | ECU power from main relay: B+ key on, <1 V off | VBAT_IN (F1..F4, D7 path) | JD1.1,2 | - | correct |
| 4AG | battery backup, B+ always | none | | | unconnected (no keep-alive; rusEFI uses flash) |
| 4AH | EVAP LDP solenoid | none | | | unconnected |
| 4K,4U,4Q(absent) | not used | | | | correct |

## Findings in detail

### F1. A/C request (4F) and clutch (4I) are ground-switched with a PCM-side pull-up; board ships without the pull-up and firmware does not set polarity (inferred, medium)
- CHARM 2003 p4: 4F "<1 V when A/C and fan switches on, otherwise B+"; 4I "B+ clutch released, <1 V depressed". A switch to ground read as B+ at the PCM terminal means the pull-up lives in the PCM. Hellen NB2 firmware (board_configuration.cpp:88-93): acSwitchMode = PI_PULLUP, clutchDownPinMode = PI_INVERTED_DEFAULT, i.e. rusEFI's own NB2 board treats both as active-low with a pull-up. rusEFI debounce.cpp:112 inverts only for PI_PULLUP.
- Board: R21/R22 (4.7k to VBAT_IN) are not fitted; INSTALL.md does not tell the NB2 owner to fit them; the divider 22k/10k to ground pulls a floating line to 0 V. miata_board.cpp:112-113 sets acSwitch/clutchDownPin but no pin modes. Result with shipped hardware: both lines read 0 V always (switch closed = 0 V too) so the A/C request is never seen: compressor relay 2K never energised, no idle-up, no fan-for-A/C. If R21 is fitted, the line is high when off and low when on, but rusEFI default polarity is active-high, so the request would read inverted (A/C asked for when the switch is OFF) unless acSwitchMode is set to inverted in TunerStudio. M4 in VERIFICATION already says "fit per car"; what is new is that NB2 is determinable (active-low), so default should be R21+R22 fitted and the preset should set the modes. Not read: whether 4F might be driven (not open) by the A/C amplifier when off; Hellen's pull-up choice and CHARM both say pull-up at the PCM.
- Same open question for 3T VSS: Haltech says the cluster converts the reluctor to a Hall-style signal and "pull-up disabled" on their input, so R20 may not be needed. Cannot verify.

### F2. Condenser fan 2C not tied to A/C
miata_board.cpp:228 sets fan1AcMode only; fan2AcMode stays Disabled (rusEFI fan_control.cpp:289). Hellen NB2 sets fan2AcMode = Relay on 2C ("AC Fan"). Here fan1 = 2B (radiator fan) comes on with A/C, the condenser fan comes on at 95 C. Whether the stock ECU also runs the condenser fan with A/C: not shown by the CHARM tables (their fan conditions are diagnostic modes). INFERRED, low-medium; moot until F1 is fixed. Same as sibling PIN-9900 finding (b).

### F3. Generator warning lamp 3U never driven
Stock: lamp low-side by the PCM, <1 V key on (lamp lit = bulb check), B+ when charging OK, and lit on DTC P0111/P0112/P1631/P1633/P1634 (CHARM 2003). Here 3U open: lamp never lights, no bulb check, no warning of a charging fault. Hellen NB2 drives 3U (AWARN). Alternator control also ships off (documented). VERIFIED stock behaviour; consequence INFERRED. Medium (safety-relevant warning missing; belt/alternator failure goes unnoticed except battery gauge/voltage). Fix: a spare low-side exists on AUX header J5 (OUT_BOOST/IN?) only via ribbon; or wire LS7 jumper; simplest: document, and use OUT_LS7/BOOST via J5 ribbon to 3U.

### F4. VVT OCV: pin, coil, current, PTC derating (inferred, low-medium)
- Pins: 4D +12 V out of PCM (= main relay via 4AF), 4R low side (CHARM 2003 p4 "control (positive)/(negative)", Hellen yaml, wiki 2002/2003). Board: D2 SS34 freewheel 4R->4D, F3 SMD1812-200-30 in the 4D feed. Matches wiki "flyback diode, stripe to +12 V". Note wiki 2002 page prints "VVT 4S" for 4D (typo).
- Coil resistance: Mazda OCV spec in the 2.0 L/MZR manuals is 6.9-7.9 ohm at 20 C (web search summary of workshop-manuals.com/mazda neocities pages, UNVERIFIED for BP-Z3); a 2001 Miata P0012 diagnosis reports 7.5 ohm (diag.net, search summary). The 2002 CHARM page has the spec in an image I could not get. So full-on current = 14.4/7.5 = 1.9 A, repo says "about 1 A".
- PTC F3: datasheet SMD1812-200 hold current derates 2.00 A (25 C) -> 1.45 (60 C) -> 1.09 (70 C) -> 0.80 A (85 C) (datasheet C46641168 thermal derating table). Average current at 50 % duty and 14.4 V about 0.96 A, pulses higher. In a hot cabin the PTC can trip at moderate duty; result is the VVT valve de-energised (cam retarded, power loss at mid revs), self-resetting, no damage. Duty actually used by rusEFI NB2 table not computed. INFERRED, low confidence. Fix: 2.6 A/3 A part or short link (the VND7NV04 limits current anyway).
- PWM frequency: stock not found; rusEFI default 300 Hz (rusefi_generated DEFAULT_SOLENOID_FREQUENCY).

### F5. 4AF is the only B+ cavity and carries everything
4AG (always-hot backup) is unconnected, 4AF (main relay) feeds ECU logic 0.25 A, LSU heater (about 2.3 A rms cold, 4 A peak per VERIFICATION.md), IAC and OCV valves (about 1 A each up to 1.9 A), AUX header 1.1 A: up to roughly 6-7 A through one PCM terminal and wire. Stock: logic + IAC + OCV (Hellen: 4D/2P fed from 4AF), injectors/heater of the stock O2 sensors are fed outside the PCM. Terminal and wire rating (040III HD, gauge) not found. UNVERIFIED, low. Check with P19c / P06 owners.

### F6. Year split and power chain (verified)
- 2001 CHARM (read today): 3H "-", 4S "-", 3E CDCV control, 4V TP, 4T generator voltage. 2002 per R19 same. So 2001-02 preset = no main relay, no IG sense; relay is switched by the ignition switch; ECU power from 4AF only. 2003 CHARM: 4S IG1, 3H main relay control; wiki 2003: "ECU powered from ENGINE fuse 15 A via 4S in start or run".
- How the ECU wakes (2003-05): key on -> 4S 12 V -> D8 -> F1 0.5 A PTC -> +12V -> buck -> MCU boots (hundreds of ms, drivers disabled by DRV_EN) -> firmware pulls 3H low through ZXMS6004 -> main relay closes -> 4AF live -> D7 path. Key off: 4S falls, ECU holds the relay about 1.03 s (VERIFICATION.md:406) then releases, power gone. 2001-02: relay closes with the key, 4AF live, VIGN floats (not used).
- Wrong preset consequences: 2001-02 car on the 2003-05 preset: 4S is not wired, the key reads off, no fuel or spark (INSTALL.md:170). 2003-05 car on the 2001-02 preset: 3H is never driven, so (INFERRED from the 3H table) the relay is never closed, 4AF stays dead and the ECU only runs from the 4S wake diode; no reliable start. Either way: pick the right year button.
- Fuel pump: 2M low at cranking/idle (running), B+ at key on (CHARM). rusEFI primes on key-on by its own timer.

### F7. Immobiliser
US cars have an immobiliser unit (CHARM 2002 manual has the system; R19: forum says 2001-05, UNVERIFIED for 2001 specifically; PCM pin 3S exists in 2001-05 tables). PCM and unit are paired to the keys; PCM is the enforcer. Without the PCM answering: AMP MSPNP page (read): dash fault indicator illuminates and/or flashes; MiataTurbo thread: engine runs, light flashes, owners pull the bulb. No source found of a fuel cut caused by the unit itself. INSTALL.md:177 says "may flash": evidence says it will. Doc only; low.

### F8. Items not driven and consequences
| Item | Stock | Consequence here |
|---|---|---|
| HO2S heaters 3J (front, on from key-on) / 3P (rear) | PCM low-side | Heater elements never powered, no damage; stock narrowband takes minutes to read, is not used (lambda from the on-board LSU). Rear sensor idle. No readiness monitors anyway |
| EGR stepper 2E/2F/2H/2I, 3D, 4AE | PCM holds coil pattern | Valve stays where it was left; stock PCM's rest position not verified: if left partly open it is a vacuum leak at idle. Cannot verify |
| Purge 3C | PWM | Canister never purged; vapour smell/fuel vapour only; no harm to engine |
| CDCV 3E (2001-02), LDP 3K/4AH (2003+) | | no evaporative leak test; harmless |
| VTCS 2N + 4J | solenoid closes shutter at cold idle | shutters stay in solenoid-off state (default not verified); cold-idle combustion slightly worse |
| Brake 4B, PS 4C, neutral 4H | inputs | no PS idle-up (idle dips at parking), nothing else |
| K-line 3Q, TEN 4E | OBD-II | no scan tool, no inspection readiness |
| A/T 4Z/4AC | PCM<->TCM serial | automatics: TCM sees no PCM (DTC P1601); untested/unsupported |
| Fuel gauge 4AD, 4T, 4AG | | none |
| Cruise | separate module + servo (CHARM tree) | unaffected; it takes VSS from its own wiring (not checked) |
| Alternator 3M | PCM PWM | Haltech: ECU drives D (grey/red) high-side duty; repo ships off with open-collector; documented (review brief s6) |

### F9. Cavity naming (72 positions)
Connector plug 2: 2A-2R without 2L (17); plug 3: 3A-3Z without 3G, 3R (24); plug 4: 4A-4AH without 4G, 4Q, 4Y (31); no plug 1. The CHARM 2003 connector drawing (page 1) lists exactly these cavities (counted 17 + 24 + 31). Script check: the 72 harness pads of cur_mb0105 equal the expected set. VERIFIED. The 2003 CHARM table's "4Y TP" (4V "-") contradicts its own figure (no 4Y); 2001/2002 tables, FSM05, Hellen and wiki all put TP on 4V. Hellen yaml "4Q" is a phantom.

### Other checks that held up
- MCU pin map vs LQFP100 numbering (PE2..PE6 pins 1-5, PC13/14 pins 7/8, PB7..PB4 pins 93..90, PB3 89, PD7..PD5 88..86, PE1/PE0 98/97, PB9/8 96/95, PE7..PE11 38..42, PA1..PA7 24..32, PC4/PC5/PB0/PB1 33..36, PA8 67) agrees with design.py and miata_pins.h (INFERRED from my memory of the ST pin table; repo has check_pins.py).
- Idle valve: 2-wire, +12 V on 2P, low-side PWM on 2Q (Haltech "pin 1 open signal, pin 2 power 12 V"); correct polarity; flyback D1 to its own feed.
- Tach on 3O must stay open-collector (also feeds A/T DLC IG-TCM): board is a low side. correct.
- Ordered board differences on this chain: 4N via JP1 (shunt must be on STOCK, documented INSTALL.md:76); no 220 R (documented); R35 etc absent. No chain errors specific to ord.

## Sensor-side wire colours found (Haltech)
TP: LG/W 5 V (4L), B/R ground (4O), G/B signal (4V). MAF: B/L ground, pink signal (4X), W/R 12 V. Alternator: P grey (feedback), D grey/red (duty). CMP/CKP: 3-wire Hall A +12 V, B signal, C ground. No PCM-side colour table found.

## Sources actually read
CHARM 2001 (all 6 pages ordered, pages 2 and part of 5 viewed), 2003 pages 1-6 (1,2,3,4,5,6 viewed), 2002 via R19 notes; repo/research/pinouts_9605.md NB2 section; motherboards/2001-05/README.md; kb/interconnect.md cur/ord 0105; scripts/design.py 85-500; firmware/board/miata_board.cpp, miata_pins.h, daughterboard.yaml; rusEFI Hellen NB2 main.yaml/board_configuration.cpp, fan_control.cpp, debounce.cpp; Haltech NB2 page; wiki.rusefi.com 2002/2003/2003-alt; datasheet C46641168 derating table; kb/research/R19; sibling PIN-9697/9900 notes.

## Not checked
- Wire colours at the PCM connector (no text source; wiring diagram images not reachable); 2004-05 voltage table; FSM2005 not re-read.
- Stock IAC/OCV PWM frequencies and OCV coil resistance for BP-Z3 (spec image not retrieved; 7.5 ohm from forum/search summaries).
- Whether stock EGR rests closed; VTCS solenoid default state; condenser-fan-with-A/C logic; whether 4F/4I are pulled up externally.
- ECT/IAT curves vs stock sensors (P12 scope); VSS pulses/km (Haltech 2780/km vs firmware 4.47 pulses per wheel turn: about 2470/km with 195/50R15, 11 % different, not resolved).
- Terminal/wire current rating of cavity 4AF.
