# PIN-0105-B car inward: 2001-05 NB2 (1.8 L BP-Z3 VVT, 72-pin PCM) pinout chain audit

STATUS: COMPLETE (STEP 1, 2, 3 written).

SUMMARY (10 lines)
1. Primary source: Mazda FSM "PCM Terminal Voltage Table" for 2001, 2002, 2003 (2004 = same images as 2003; 2005 pages 3,5 read, same), via charm.li; images read today. Cross-sources: rusEFI wiki 2001/2002/2003/2003-alt/Proteus-NB2, Haltech BP-Z3 KB, AMP MM0105 page, MiataTurbo/mx5oc threads, hellen NB2 (ext, one source).
2. 72 cavities: connector No.2 17 pin, No.3 24 pin, No.4 31 pin. The repo harness list equals the FSM drawing exactly (72 = 72, no extra, none missing) VERIFIED by script.
3. 2001 = 2002 (CDCV 3E, FTP 4AB, 3H/4S unused, relay key-driven). 2003-05: 3H main-relay control, 4S IG1, EVAP leak pump 3K/4AH replace CDCV/FTP. The repo nb2Early/2003-05 split matches this.
4. FSM 2003 table prints TP on 4Y; 4Y is not a physical cavity in the FSM drawing, so it is an FSM typo for 4V (repo, rusEFI, Proteus all 4V). Checked, repo correct.
5. Signal chain verdicts: injectors, fans, A/C, FP, MIL, IGT, CKP/CMP, TP, CLT, IAT, knock, A/C and clutch switches, main relay, power: consistent with the car. No outright wiring error found in cur_mb0105.
6. VVT OCV coil is 6.9-7.9 ohm at 20 C (FSM image): 1.8-2.1 A at 14 V, so the 2 A hold PTC F3 is at/over its rating at high duty (risk).
7. Open electrical questions (need a car): tach 3O level (stock swings 0 to about 12 V, rusEFI maps it high-side), alternator 3M level (stock about 1 V swing, Haltech says high-side drive).
8. Not driven and driver-visible: charge lamp, EGR, purge, VTCS, EVAP pump, HO2S heaters, immobiliser comms, PSP idle-up, K-line.
9. Immobiliser (3S) is in the 2001, 2002, 2003 FSM tables; aftermarket ECUs (AMP, Adaptronic) run the car, light flashes.
10. Wire colours NOT obtained (FSM wiring diagram pages not fetched): see Not checked.


## STEP 1: factory pinout from external sources only

Sources (all external; no repo/research, README tables or kb/interconnect.md opened before this step):
- S1 PRIMARY: Mazda 2002 MX-5 Miata L4-1.8L FSM, "Pinout Values and Diagnostic Parameters" = "PCM Terminal Voltage Table (Reference)", via charm.li (Operation CHARM), page https://charm.li/Mazda/2002/MX-5%20Miata%20L4-1.8L%20DOHC/Repair%20and%20Diagnosis/Powertrain%20Management/Computers%20and%20Control%20Systems/Testing%20and%20Inspection/Pinout%20Values%20and%20Diagnostic%20Parameters/ . Six table images downloaded to work/PIN-0105-B-car-inward/img/pv02_*.png and READ by image today (VERIFIED). Same page for 2003: pv03_*.png.
  Connector layout from the FSM: PCM connector No.2 = 17 pin (2A..2R, no 2L? cavities drawn), No.3 = 24 pin (3A..3Z), No.4 = 31 pin (4A..4AH) => 72 cavities total. The FSM table has no wire colours (colours are in the wiring diagrams, not obtained; see Not checked).
- S2 rusEFI wiki "Mazda Miata 2002" and "2003 Mazda Miata Alt" (saved in work/R19-stock-ecu-2001-05/dl/, re-read today).
- S3 hellen-miata-NB2 (ext/, counts as one source): connector-mapping.txt, README.
- Further sources: see below as they are read.

### 2002 PCM terminal table (S1, VERIFIED unless noted). B+ = battery voltage; "<1.0" = below 1.0 V.
Direction is from the ECU's point of view; electrical character INFERRED from the test condition where marked.

| Cav | FSM signal | Connected to | FSM test condition -> voltage | Dir / inferred electrical character |
|---|---|---|---|---|
| 2A | Fuel injector control #1 | injector 1 | scope waveform | out, low-side |
| 2B | Cooling fan control | cooling fan relay | idle, ECT>97C, A/C on, TEN grounded: <1.0; others B+ | out, low-side (relay fed B+, ECU pulls to ground to energise) |
| 2C | Condenser fan control | condenser fan relay | ECT>108C etc.: <1.0; others B+ | out low-side |
| 2D | Fuel injector #2 | inj 2 | scope | out low-side |
| 2E | EGR valve #1 coil control | EGR valve term E | IG on / idle <1.0 | out, 4-coil stepper EGR (2002 has stepper EGR) |
| 2F | EGR valve #2 coil | EGR term A | IG on / idle B+ | out |
| 2G | Fuel injector #3 | inj 3 | scope | out |
| 2H | EGR valve #3 coil | EGR term B | B+ | out |
| 2I | EGR valve #4 coil | EGR term F | <1.0 | out |
| 2J | Fuel injector #4 | inj 4 | scope | out |
| 2K | A/C control | A/C relay | idle, A/C and fan sw on <1.0; others B+ | out low-side |
| 2L | not used | | | |
| 2M | FP control | fuel pump relay | IG on B+; cranking <1.0; idle <1.0 | out low-side (note: B+ with IG on, i.e. relay off then pulled low) |
| 2N | VTCS control | VTCS solenoid valve | ECT>60C idle B+; ECT<60C and 3500 rpm <1.0 | out low-side (shutter valve solenoid; ON (low) at 3500 rpm per this wording) |
| 2O | not used | | | |
| 2P | IAC (positive) | IAC valve | scope | out, IAC solenoid driven by 2P/2Q pair: wiki says 2P is +12 supply and 2Q the control (S2 vs FSM "positive/negative") |
| 2Q | IAC (negative) | IAC valve | scope | out low-side PWM |
| 2R | MIL control | MIL in cluster | IG ON <1.0; idle (MIL off) B+ | out low-side (lamp lit when ECU grounds) |
| 3A | Fuel injector GND | GND | <1.0 | power ground |
| 3B | PCM GND | GND | <1.0 | ground |
| 3C | Purge control | purge solenoid | scope | out low-side PWM (duty) |
| 3D | EGR boost sensor switching control | EGR boost sensor solenoid valve | IG on / idle B+ | out low-side (B+ = off) |
| 3E | CDCV control | CDCV (canister drain cut valve) | IG on B+; diagnosis exceeded <1.0 | out low-side |
| 3F | IGT control No.1/No.4 | ignition coil | scope | out, logic level to coil pack driver (coil-on-plug-pair w/ internal igniter; waveform not seen) |
| 3G, 3H | not used (2002) | | | 3H = main relay control on 2003 (S2) |
| 3I | IGT control No.2/No.3 | ignition coil | scope | out |
| 3J | HO2S heater (front) control | front HO2S | IG on <1.0; idle <1.0 | out low-side (heater on at both) |
| 3K, 3L | not used | | | |
| 3M | Generator field coil control | generator term D | scope; voltage raised when load on | out, field-coil PWM (low-side) |
| 3N | not used | | | |
| 3O | Engine speed | DLC IG- terminal, TCM (AT), tachometer | scope | out, tach signal |
| 3P | HO2S heater (rear) control | rear HO2S | IG on B+; idle heater operating <1.0 | out low-side |
| 3Q | K-LINE | DLC KLN (DLC 2) | serial | bidirectional K-line |
| 3R | not used | | | |
| 3S | Immobilizer communication | immobilizer unit | serial, no voltage judgement | bidirectional serial; fitted on this car (2002 FSM) |
| 3T | Vehicle speed | VSS | scope | in, pulses (circuit/pull-up not stated) |
| 3U | Generator warning light control | cluster lamp | IG on <1.0; idle B+ (no DTC P0111/P0112/P1631/P1633/P1634) | out low-side |
| 3V | SGC | CMP sensor | scope | in |
| 3W | not used | | | |
| 3X | not used | | | |
| 3Y | NE | CKP sensor | scope | in |
| 3Z | not used | | | |
| 4A | Device GND | GND | <1.0 | ground |
| 4B | Brake | brake switch | released <1.0; depressed B+ | in, 12 V active |
| 4C | PSP | power steering pressure switch | idle: straight B+; fully turned <1.0 | in, B+ = normal, low = loaded (active low) |
| 4D | OCV control (positive) | oil control valve (VVT) | scope | out: positive side of OCV (supply from main relay per S2 wiki; 4R is the low-side control) |
| 4E | DTM switching | DLC TEN | IG on: TEN open B+; TEN grounded below | in, pulled up inside ECU |
| 4F | A/C | refrigerant pressure switch | IG on: A/C & fan sw on <1.0; others B+ | in, active low |
| 4G | not used | | | |
| 4H | Load/no-load | neutral switch (MT) | IG on, in neutral <1.0; others B+ | in, active low, MT only |
| 4I | Load/no-load | clutch switch (MT) | released B+; depressed <1.0 | in, MT only |
| 4J | VTCS vacuum switch | VTCS vacuum switch | IG on B+; ECT>60C idle B+; ECT<60C & 3500 rpm <1.0 | in, 12 V level |
| 4K | not used | | | rusEFI wiki says knock on 4K (conflict, see 4M) |
| 4L | Constant voltage (Vref) | TP sensor, EGR boost sensor, FTP sensor | IG on approx 5.0 V | out, 5 V reference |
| 4M | Knocking | KS | IG on approx 2.4 V (DC bias) | in, analog, 2.4 V bias |
| 4N | IAT | IAT sensor | 20C 2.3-2.4 V; 30C 1.9 V | in analog NTC, internal pull-up (INFERRED: 2.35 V at 20C) |
| 4O | Analogue sensor GND | GND | <1.0 | ground |
| 4P | ECT | ECT sensor | 20C approx 3.0 V; 80C approx 0.9 V | in analog NTC |
| 4Q | not used | | | |
| 4R | OCV control (negative) | oil control valve | scope | out low-side PWM (VVT) |
| 4S | not used (2002) | | | 2003: ECU power (S2) |
| 4T | Generator output voltage | generator term P | IG on <1.0; idle 3-8 V | in, PWM-like (duty) charge-state signal |
| 4U | not used | | | |
| 4V | TP | TP sensor | closed 0.1-1.1 V; WOT 3.0-4.6 V | in analog |
| 4W | HO2S (front) | front HO2S | scope | in, narrowband 0-1 V |
| 4X | MAF | MAF sensor | IG on 0.9-2.0; idle warm 1.7-2.4 | in analog |
| 4Y | not used | | | |
| 4Z | PCM-TCM comm (PCM to TCM) | TCM term O | serial | out, AT only; DTC P1601 if wrong |
| 4AA | HO2S (rear) | rear HO2S | IG on 0-1.0; idle cold 0-0.5; warm 0-1.0; accel 0.5-1.0; decel 0-0.5 | in, narrowband |
| 4AB | FTP | fuel tank pressure sensor | IG on 0 kPa approx 2.5 V | in analog (US evap) |
| 4AC | PCM-TCM comm (TCM to PCM) | TCM term AL | serial | in, AT only |
| 4AD | Fuel tank level | fuel gauge sender | full 0.2-0.5; half 1.8-2.8; empty 3.4-4.4 V | in analog |
| 4AE | BARO/EGR boost | EGR boost sensor | idle at <400 m 4.1-4.3 V; -26.6 kPa 3.0-3.4 V | in analog (switched via 3D valve between baro and manifold) |
| 4AF | Power supply | main relay | IG on B+; IG off <1.0 | in, switched +12 |
| 4AG | Back-up power | battery | B+ always | in, KAM |
| 4AH | not used | | | |

(Counts: 17+24+31 = 72 drawn positions; not every position populated.)

### NOTES 2002 vs rusEFI/hellen (S2/S3 pending detailed comparison)
- Key lines from S2 (2002 page): main relay controlled by ignition switch, nothing on 4S, ECU powered through 4AF; flyback diode needed between VVT 4S and 4R (wiki typo: FSM says OCV positive is 4D, the 2003 page says 4D) and between IAC 2P and 2Q.

## STEP 1b: 2003 FSM (S1, 2003 MX-5 Miata L4-1.8L, same page, images pv03_*.png, READ today = VERIFIED) differences from 2002

| Cav | 2002 FSM | 2003 FSM |
|---|---|---|
| 3E | CDCV control (IG on B+, diagnosis exceeded <1.0) | not used |
| 3H | not used | Main relay control: IG off B+, IG on <1.0 (ECU low-side drives the main relay coil; relay coil fed from battery) |
| 3K | not used | EVAP system leak detection pump (pump): IG on B+ / idle B+ (out low-side, ELD pump motor) |
| 4AH | not used | EVAP leak detection pump solenoid valve: B+ / B+ (out low-side) |
| 4S | not used | Ignition switch IG1 input: off <1.0, on B+ |
| 4AB | FTP sensor (approx 2.5 V at 0 kPa) | not used |
| 4L | Vref for TP, EGR boost, FTP | Vref for TP, EGR boost only (page lists "TP sensor, EGR boost sensor") |
| 4V / 4Y | TP sensor on 4V; 4Y not used | 4V NOT USED; TP sensor on 4Y (0.1-1.1 V closed, 3.0-4.6 V WOT) |
| 4O | Analogue sensor GND | Analogue sensor GND lists EGR boost, TP, ECT, IAT, HO2S front, HO2S rear |
| 4AF | main relay power: IG on B+, off <1.0 | same |
| 3J, 3P, 3U, 3M, 4D, 4R, 4T, 4N, 4P, 4W, 4AA, 4X, 4AD, 4AE, 2x, 3F, 3I, 3O, 3Q, 3S, 3T, 3V, 3Y | as listed above | identical |

So the FSM says three real differences 2002 -> 2003: (a) 2003 has ECU-controlled main relay 3H and IG1 sense on 4S (2002: relay driven by the ignition switch directly, 4S unused), (b) US-style EVAP leak detection (3K, 4AH) replaces FTP/CDCV, (c) TP moved 4V -> 4Y (see conflict below).
2001 and 2004-05 FSM pages were NOT read (charm.li 2001 page index only). 2001 equals 2002 hardware per rusEFI wiki (it has own page); not independently verified.

CONFLICT to chase: rusEFI "2003 Mazda Miata Alt" lists TPS on 72-pin 4V; the 2003 FSM table lists 4V unused and TP on 4Y.
## STEP 2: cavity-by-cavity comparison with cur_mb0105 / ord_mb0105 (kb/interconnect.md lines 779-856, 1824-1900; firmware repo/firmware/board/)
Circuit facts used (VERIFIED from interconnect.md / design.py): low-side outputs = MCU -> SN74LVC4245 -> VND7NV04 (inj, IACV, VVT, BOOST, ALT) or ZXMS6004FF (FP, MAINRLY, AC, FAN, CEL, TACH, LS7) active high; ignition = TC4427 5 V push-pull; switch inputs IN_SW1/2/3 = 4.7k pull-up to VBAT_IN + divider; D8 B5819W wakes the 12 V rail from VIGN_IN (4S); F2/F3 2 A PTC feed IAC_12V (2P) and OCV_12V (4D), SS34 flyback D1 (2Q->2P) / D2 (4R->4D). I compared the ord_mb0105 list too: same nets for every cavity (ordered rev 0.7 vs current differ elsewhere, not on the harness nets).

| Cav | Car (FSM) | Board | Verdict |
|---|---|---|---|
| 2A 2D 2G 2J | injectors 1-4 low side | OUT_INJ1-4 (VND7NV04) | OK (order matches firmware INJ1..4; cyl numbering is firmware) |
| 2B | cooling fan relay, low = on | OUT_FAN ZXMS6004 | OK |
| 2C | condenser fan relay | OUT_LS7 (fan2Pin) | OK |
| 2E 2F 2H 2I | EGR stepper 4 coils (both years) | no net | not implemented (documented) |
| 2K | A/C relay low = on | OUT_AC | OK |
| 2L 2O 3G 3R 4G 4Q 4Y | not cavities / unused | not present / no net | OK |
| 2M | FP relay low = on (B+ at key-on) | OUT_FP | OK (relay off at power-up since driver enable high-Z) |
| 2N | VTCS solenoid low side | no net | not implemented (documented) |
| 2P / 2Q | IAC valve; scope on 2P is a 0-12 V pulse train | IAC_12V via F2 2 A + D1; OUT_IACV low side | OK electrically (solenoid is non-polar); see note A |
| 2R | MIL, low = lit | OUT_CEL | OK |
| 3A 3B 4A 4O | injector GND / PCM GND / device GND / analogue sensor GND | all one GND net | OK, but sensor-return shares injector-return plane (risk low, note F) |
| 3C | purge, PWM | none | not implemented (documented) |
| 3D | EGR boost-sensor switching valve | none | not implemented |
| 3E (2001-02) | CDCV | none | not implemented |
| 3F / 3I | IGT cyl 1&4 / 2&3, about 4-5 V pulses, falling-edge fire (scope amplitude read from image, Haltech: constant charge, falling edge) | OUT_IGN1 / OUT_IGN2, TC4427 5 V | OK |
| 3H (2003-05) | main relay coil, ECU pulls low | OUT_MAINRLY, mainRelayPin set for 2003-05 only | OK |
| 3J / 3P | HO2S heater front/rear low side | none | not driven (documented), see STEP 3 |
| 3K, 4AH (2003-05) | EVAP leak pump / solenoid | none | not implemented |
| 3M | generator field control, scope amplitude only about 1 V | OUT_ALT VND7NV04 low side, control ships OFF | unresolved, see finding on 3M |
| 3O | engine speed, swings 0 to about 12 V, 2 pulses/rev | OUT_TACH ZXMS6004 low side, no pull-up on mb | unresolved, see finding on 3O |
| 3Q, 3S, 4E | K-line, immobiliser serial, DLC TEN | none | not implemented (documented) |
| 3T | VSS: about 5 V swing, rounded rising edge (pull-up RC), 2780 pulse/km (Haltech) | IN_SW1 R20 4.7k to VBAT_IN, 22k/10k divider | plausible: high = 3.75 V at the pin; low if open-collector; UNVERIFIED whether the cluster output is open collector or push-pull (push-pull 5 V would give only 1.56 V = below STM32 VIH). Low risk |
| 3U | charge lamp low = lit | none | not driven (documented VERIFICATION 1122) |
| 3V / 3Y | CMP SGC / CKP NE Hall | IN_HALL2 / IN_HALL1 | OK |
| 4B 4C 4H | brake / PSP / neutral switches | none | not connected, see STEP 3 |
| 4D / 4R | OCV, 6.9-7.9 ohm; scope on 4D is 0-12 V pulses | OCV_12V via F3 2 A PTC + D2; OUT_VVT low side | OK topology (matches Hellen/Proteus); PTC margin finding |
| 4F, 4I | A/C pressure switch, clutch (low = active) | IN_SW2, IN_SW3 with pull-ups | OK |
| 4J | VTCS vacuum switch | none | not implemented |
| 4L | 5 V Vref (TP, EGR boost, [FTP 2001-02]) | V5_EXT, J5.14, R35 | OK |
| 4M | knock, ECU bias about 2.4 V | IN_KNOCK -> 2.2k -> 100 nF AC coupling, own bias | OK (DC bias irrelevant) |
| 4N / 4P | IAT 2.3-2.4 V at 20 C / ECT 3.0 V at 20 C, 0.9 V at 80 C | IN_IAT, IN_CLT 2.7k pull-up to V5_EXT | OK; stock pull-up INFERRED about 1.5-1.6 k (CLT) vs 2.7 k on board: only the firmware calibration table matters, not hardware |
| 4S (2003-05) | IG1 sense | VIGN_IN -> D8 -> rail wake, ADC divider | OK: board powers from 4S via D8 until it pulls 3H low, then 4AF |
| 4T | generator output, 3-8 V at idle | none | not connected |
| 4V | TP 0.1-1.1 V closed, 3.0-4.6 V WOT (FSM 2003 says 4Y, typo) | IN_TPS | OK |
| 4W / 4AA | HO2S front/rear signal | IN_AUX2 / IN_AUX1 analog | OK for a narrowband 0-1 V (unused: wideband is on board) |
| 4X | MAF 0.9-2.0 V key-on | IN_AUX3 | OK (MAF not used by speed-density tune) |
| 4Z / 4AC | PCM-TCM serial (AT) | none | automatic not supported (documented) |
| 4AB (2001-02) | FTP | none | not implemented |
| 4AD | fuel level | none | not connected (the gauge uses its own sender; the ECU copy is for diagnostics) UNVERIFIED |
| 4AE | BARO/EGR boost | none | baro comes from on-board MAP |
| 4AF | main relay power | VBAT_IN | OK |
| 4AG | permanent battery (KAM) | none | OK, rusEFI keeps data in flash |

Notes
A. Stock scope probes for IAC (2P) and OCV (4D) show 0-12 V rectangular pulses, so in the stock PCM those pins are switched, not plain relay-fed pins. The board's solution (feed +12 through a PTC, switch the other terminal low side, flyback across the coil) is the same as rusEFI Hellen NB2 and the Proteus adapter. The FSM itself says the OCV terminals are interchangeable. Pixel estimates from the scope images (INFERRED, grid read by eye): IAC about 40 % high, period about 50 ms (about 20 Hz); OCV about 40 % high, period about 2 ms (about 500 Hz). The repo uses rusEFI defaults (VVT 300 Hz).
F. Ground: stock separates injector GND 3A, PCM GND 3B, device GND 4A and analogue GND 4O. Board ties all to one plane (net GND in interconnect.md). 4O carries TP/ECT/IAT/EGR/HO2S returns. Injector pulses of several amps on a shared plane may shift the analogue reference; INFERRED, depends on layout (other audit's scope).

## STEP 3: what the stock ECU does that this board does not (2001-05)
| Function | Stock | This board | What the driver notices / what can be harmed |
|---|---|---|---|
| VVT OCV (4D/4R) | PCM drives OCV (6.9-7.9 ohm at 20 C, about 400-500 Hz) | implemented, PTC 2 A | see finding: PTC may trip when duty is high in a hot cabin; spool returns to full retard without power (FSM OCV inspection), so a trip costs top-end power, no damage |
| VTCS shutter valve (2N, 4J) | solenoid low side; FSM: B+ (off) warm idle, <1 V cold at 3500 rpm | none | with solenoid never energised the shutters stay in the unpowered position (UNVERIFIED which). Cold-start/idle tumble effect lost: slightly rougher cold idle and higher HC; Haltech says plates close below 60 C and idle. Nothing harmed |
| Main relay (3H) | 2003-05 ECU holds relay; 2002: key does | firmware, 2003-05 only | if firmware locks up, relay drops: engine stops. 2001-02 preset must be selected on 2001-02 cars; the "3H" wire does not exist there so a mis-selected preset only wastes a driver |
| Presets differ because | 2001-02: key-switched relay feeds 4AF, 4S unused; 2003-05: 4S = IG1, ECU controls 3H | firmware nb2Early | if a 2003 car were run on the early preset: board is woken by 4S/D8 but never closes the relay: 4AF stays dead, injectors, IAC, OCV, LSU supply drop: car will not run. If early car on 2003 preset: relay output unused, ignition sense channel assigned but 4S floating reads key off: rusEFI cuts fuel/spark (firmware comment says exactly this) |
| Alternator (3M, 4T, 3U) | ECU sets field duty, reads load on P, lights charge lamp | off by default | alternator regulates itself (UNVERIFIED default behaviour); no charge lamp at all, not even the key-on bulb check; undetected alternator failure drains battery |
| HO2S heaters (3J, 3P) | ECU low-side switches, FSM: front on from key-on | not driven | heaters never run: narrowbands only work once exhaust is hot (about 350 C), nothing is damaged; closed-loop uses the wideband. Rear sensor/cat monitor gone (documented) |
| Immobiliser (3S) | serial to immobiliser unit; FSM lists 3S in 2001, 2002, 2003 tables; PCM + unit + key transponder are a set | none | security light flashes (AMP MM0105 page: "fault indicator ... will illuminate and/or flash"; MiataTurbo thread: standalone Adaptronic in an MSM, light flashes). Car still runs on these standalones (UNVERIFIED on this board; no firsthand). US model-year coverage: FSM 2001-2005 all list it; Mazda service text covers 2001-02; presence on every US car not proven |
| EGR (2E,2F,2H,2I,3D,4AE) | stepper EGR | none | no EGR: slightly more NOx, no driveability change; valve left unpowered (UNVERIFIED closed) |
| Purge (3C), CDCV (3E), EVAP pump (3K, 4AH), FTP (4AB) | canister purge, leak test | none | canister never purged: possible fuel odour, fails emissions test; no harm |
| Fans, A/C | 2B/2C/2K | implemented | OK. Stock thresholds: cooling fan on above about 97 C with A/C etc., condenser above 108 C (FSM test condition text); firmware thresholds are rusEFI defaults |
| Cruise | no ECU cavity in the 2001-05 FSM table | n/a | A/T Aisin connector lists a cruise-control module pin (rusEFI), not ECU |
| PSP (4C), brake (4B), neutral (4H) | idle-up on steering load, load/no-load | not wired | idle dips when the wheel is turned fully at parking speed (INFERRED); no harm |
| K-line, DLC TEN | OBD-II/diagnostics | none | no scan tool, no emission test (documented) |
| 72 cavity naming | 2A-2R (17), 3A-3Z (24), 4A-4AH (31) | identical set | OK |

## Disagreements between sources
- TP: FSM 2003 "4Y" vs FSM 2002/2001, rusEFI 2003-alt, Proteus page "4V". 4Y is not drawn in either FSM connector figure: resolved as FSM typo (INFERRED).
- Knock: rusEFI 2003-alt table says 4K; FSM says 4M (4K unused). Repo uses 4M (matches FSM). rusEFI alt table is a Hellen-121-pin map and looks wrong/obsolete.
- OCV 4D/IAC 2P: FSM "positive" = scope-probed switched terminal; rusEFI calls them +12 supply. Electrically irrelevant for a coil.
- rusEFI 2002 page text says "VVT 4S" in flyback line; its own 2003 page says 4D. FSM: OCV positive is 4D. Typo on the 2002 page.
- Alternator: Haltech "high side duty from ECU" vs repo "low side with 1k pull-up"; FSM scope amplitude about 1 V.

## Sources actually read
- Mazda FSM via charm.li (images in work/PIN-0105-B-car-inward/img/): 2002 pinout pv02_1..6; 2003 pv03_1..6 (2004 uses identical image ids); 2001 pv01_3, pv01_5 (others not read); 2005 pv05_3, pv05_5; 2002 oscilloscope waveforms osc_*.png (OCV, IAC, gen, tach, VSS, IGT read); 2002 OCV inspection image ocv_b.png (6.9-7.9 ohm); 2002 Antitheft service precaution text.
- rusEFI wiki: Mazda-Miata-2001, 2002, 2003, 2003-alt (pages saved in work/R19-stock-ecu-2001-05/dl/ and work/PIN-0105-B-car-inward/dl/), HOWTO Miata NB2 on Proteus (pin table 2A..4AF).
- Haltech support KB "BP-Z3 (BP-VE) Engine 01-05 NB2" (dl/haltech.html).
- AMP MM0105 installation page (immobiliser warning text, jumpers); page fetch of AMP-PNP-MM0105 page.
- MiataTurbo thread (R19 dl/mt1) and mx5oc immobiliser-emulator thread.
- ext/hellen-miata-NB2 (README, connector-mapping, releaseNotes): the P2 connector is the module-to-board connector with Hellen-internal names, not Mazda cavities, so it gave no pin data.
- Repo, STEP 2 only: kb/interconnect.md cur/ord_mb0105 harness tables; scripts/design.py (D8, knock stage); firmware/board/miata_pins.h, miata_board.cpp; README/INSTALL/VERIFICATION greps.

## Not checked
- Wire colours for the 72 cavities (FSM wiring diagrams not fetched); Link/ECUMaster/AEM/ME442 NB2 pin PDFs (Link PDF URL returned an HTML shop page; not retrieved). So only 3 independent sources (FSM, rusEFI, Haltech/AMP) per table.
- Load resistances other than OCV (IAC, VTCS, purge, relays, EGR, heaters), HO2S heater current: values not in the pages read.
- 2001 FSM pages 1, 2, 4, 6, 7 and 2005 pages 1, 2, 4, 6, 7 not viewed (only pages carrying 2K-3H, 3I-3U, 4F-4R differences); 2004 relied on identical image ids.
- Exact pixel-derived frequencies are rough (grid read by eye).
- Which US VINs carry the immobiliser; what the immobiliser does at crank with a foreign ECU on this board (no car).
- IAC valve exact resistance and PWM frequency; VSS output stage type; whether the tach/alt wires have pull-ups in the cluster/alternator (needs a car: key on, ECU unplugged, measure 3O and 3M).
