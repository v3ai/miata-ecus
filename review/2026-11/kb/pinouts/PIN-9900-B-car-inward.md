# PIN-9900-B car inward: 1999-2000 NB1 (1.8 L BP-4W, 64-position PCM) pinout chain audit

STATUS: complete (steps 1-3).

## STEP 1: factory pinout from external sources only
Sources (independent):
- S1 PRIMARY, Mazda 2000 MX-5 Wiring Diagram (Form 5455-1U-99G, scan, neomiata.com PDF, work/PIN-9900-B-car-inward/dl/w2000.pdf), pdf p.21/23/25 = sections B-1a/b/c "Engine control system" incl. connector box "B1-01 PCM" (colours of every cavity, read from 300 dpi crop pg/c1.png c2.png), p.19 charging system. VERIFIED (read by eye).
  Harness symbols (F) (E) (EM) (INJ) are harness names, NOT variants. Variants shown: "<> AT" and "*1 California / *2 except California" (rear HO2S wiring only).
- S2 rusEFI wiki "Mazda Miata 1999" (wiki.rusefi.com/Mazda-Miata-1999): partial (many blanks), 3 plugs 22/16/26 pins. Contains some errors (3M/3O swap, see below).
- S3 Bartune Engineering, "Australian MX-5 NB8A (1999-2000) ECU Pinout" (bartuneengineering.wordpress.com): complete function list in Mazda lettering (Australian car, no OBD2, so MIL missing, 1H/1D/1L etc.).
- S4 rusEFI Hellen NB1 board (ext + repo/firmware/ext/.../hellenMiataNB1/connectors/main.yaml, board_configuration.cpp) = one source; AMP/DIYAutoTune MM9900 docs (ampenginemanagement.com mm9900 installation: JP2 "fuel pump: USA / Europe w/ immobilizer" jumper, rear options connector). Mazda tech tip Oct 1998: 2I = VREF about 5 V, LG/R wire.
Connector: Mazda 3 plugs: CONN 1 = 22 cavities (1A..1V), CONN 2 = 16 cavities (2A..2P), CONN 3 = 26 cavities (3A..3Z), total 64 (VERIFIED from S1 connector box and S2).
Letters: plug 1 A..V (22, includes I), plug 2 A..P (16), plug 3 A..Z (26).
Electrical-character column: UNVERIFIED general knowledge of Mazda PCM unless tagged; dir = relative to PCM.

### CONN 1 (22)
| Cav | Colour (S1) | Function | Dir | Electrical character | Variants / source notes |
|---|---|---|---|---|---|
| 1A | L/R | Constant +B, room fuse 10A (memory) | in | battery, always hot | S2,S3 agree |
| 1B | W/R | Main relay output +B (PCM power, switched) | in | 9-16 V; relay coil is switched by IG "ENGINE" 15A fuse directly (no PCM main-relay control on 1999-2000 US; S3 lists main-relay control only for 2001+ OBD2) | S2,S3 agree |
| 1C | * (n/c) | unused | | | S3 "-" |
| 1D | G/W | Data link connector-2 (DLC) | bidir | diag line | S3 DLC |
| 1E | W/L | Check engine (MIL) lamp, to instrument cluster | out | low side sink, lamp fed from IG | S2 low-side output; S3 "-" (Aus car without OBD2 MIL) |
| 1F | G | to instrument cluster (circle 31) / not named | ? | | S1 only; function not labelled, UNRESOLVED |
| 1G | BR | Power steering pressure switch (B1-05 PSP; B/(EM) ground side) | in | switch to ground, PCM pull-up | S3 agrees (1G PS switch); S4 hellen 1G steering switch |
| 1H | G/R | +B from FUEL INJ 30A fuse (injector/IAC supply tap?) | in | battery constant | S3 "constant 12V injector fuse" (S2 blank) |
| 1I | L/W | Condenser (A/C) fan relay | out | low side | S2,S3,S4 agree |
| 1J | * | unused | | | |
| 1K | * (MT) / V/G (AT) | Transmission control module (AT only) | | | S1 <>AT note; S3 "trans system (auto only)" |
| 1L | BR/Y | Data link connector-2 (circle 21) | ? | | S3 DLC |
| 1M | * | unused | | | |
| 1N | * (MT) / P/B (AT) | TCM (AT only) | | | S1 |
| 1O | GY/R | Generator (alternator) field / regulator control | out | PCM drives regulator field command (duty); regulator input through a resistor inside generator (A-03) | S2,S3,S4 agree: "alternator field". UNVERIFIED electrical (open collector / PWM freq not documented) |
| 1P | LG/B | A/C request line: node joining A/C amplifier output (R/W via refrigerant pressure switch G-09), condenser fan motor and condenser-fan-relay contact (S1 p.49 Z-46) | in | INFERRED active-high 12 V when A/C requested / condenser fan relay on; otherwise pulled to ground through the fan motor winding | S3 "A/C switch (ground input)"; S2 "A/C system"; S4 "A/C pressure in" |
| 1Q | BR/R | Charge warning lamp: cluster lamp (1.4 W, fed from IG, diode) to BR/R to PCM 1Q (S1 p.33 Z-30, VERIFIED) | out | low side sink, ~0.1 A | S2 "low battery light", S3, S4 agree |
| 1R | R/G | Cooling fan relay | out | low side to relay coil | all agree |
| 1S | L/B | A/C relay (compressor) | out | low side | S3,S4 agree; S2 "A/C system" |
| 1T | GY | Generator feedback (regulator transistor collector, field monitor) | in | from generator A-03 GY | S3 "alternator feedback" (S3 numbers it 1T; S2 blank) |
| 1U | V/Y | Front heated O2 sensor heater, ground side | out | low side, heater B1-06 (V/Y), 1U | S3,S4 agree |
| 1V | V (MT only; AT *) | Neutral switch (B1-22) | in | switch to ground | S2,S3 agree |

### CONN 2 (16)
| Cav | Colour | Function | Dir | Electrical character | Notes |
|---|---|---|---|---|---|
| 2A | R/G | FTP (fuel tank pressure) sensor signal | in | analog 0.5-4.5 V ratiometric (US EVAP; present also California/federal) | S2,S3(S3: 2A "-" for Aus; Aus 2001+ has FTP OBDII only) |
| 2B | P/L | Intake air temp (in MAF) | in | NTC to sensor ground, PCM pull-up | all agree |
| 2C | L | Front heated O2 sensor signal (B1-06 "L") | in | 0.1-0.9 V narrowband | S3 "lambda signal", S4 "O2S" ; S2 blank |
| 2D | W/B | Vehicle speed signal (from cluster) | in | pulses (cluster output) | all agree |
| 2E | R/L | Coolant temp sensor | in | NTC, pull-up | all agree |
| 2F | W (+ shield, B/L) | Knock sensor | in | piezo, shielded, ground via 3C B/L | all agree |
| 2G | * | unused | | | |
| 2H | GY/L | Camshaft position sensor (3-pin B1-16: W/R supply, B/L ground) | in | Hall/open collector, sensor powered from main relay 12 V, PCM pull-up | S2,S3 agree |
| 2I | LG/R | +5 V reference (Vref) | out | regulated ~5 V (Mazda TSB: 2I should read about 5 V) | S2,S3,S4 agree |
| 2J | GY/R | Crankshaft position sensor (3-pin B1-25: W/R supply, B/L ground) | in | Hall, 12 V supplied from main relay, PCM pull-up | all agree |
| 2K | G/O | Tachometer output to cluster (and DLC) | out | pulse train to cluster | all agree |
| 2L | LG/B | Mass air flow sensor signal (B1-17: W/R supply, ground, signal) | in | analog 0-5 V; MAF (hot-wire) is a *powered* sensor, 12 V from main relay | S3 agree (S2 blank) |
| 2M | V | EGR valve solenoid (stepper-type, 4 coils) | out | low side | S1, S3 (2M..2P EGR) |
| 2N | W/G | EGR valve coil | out | low side | |
| 2O | P/B | EGR valve coil | out | low side | |
| 2P | P | EGR valve coil | out | low side | |
S2 lists 2M..2P blank; S2 says 5 V (2I) matches.

### CONN 3 (26)
| Cav | Colour | Function | Dir | Electrical character | Notes |
|---|---|---|---|---|---|
| 3A | B/Y | Power ground | | high current return | all |
| 3B | B/Y | Power ground | | | |
| 3C | B/L | Sensor ground (knock sensor shield etc.) | | | S3 "3C sensor ground" |
| 3D | * | unused | | | S2 "*" |
| 3E | G/B | Throttle position sensor signal | in | analog 0.5-4.5 V (B1-20 TPS: LG/R 5 V, B/R gnd) | all |
| 3F | B/R | Sensor ground | | | all |
| 3G | BR/Y | Ignition coil no.1 (cyl 1&4) driver input (coil pack with integral igniter, B1-03 C? connector A..D; coil gets B+ from IG) | out | logic level 5 V (hellen: "logic level for smart coil") | all |
| 3H | BR | Ignition coil no.2 (cyl 2&3) | out | logic level | all |
| 3I | BR/W | Clutch switch (B1-21), MT; also cruise | in | switch to ground | S2 agrees |
| 3J | R | Rear heated O2 sensor signal (shielded, California *1; F: R/Y etc.) | in | 0.1-0.9 V | S4 "3J O2S2" ; present all US OBD2 cars |
| 3K | BR/B | Fuel gauge / fuel level signal from cluster (circle 15) | in | analog from sender via cluster | S2 "fuel gauge" |
| 3L | BR/R | Purge solenoid valve (B1-09) | out | low side, valve fed W/R from main relay | S3 agrees 3L |
| 3M | O | IAC solenoid valve control (B1-24 O) | out | low side PWM (duty) | S3, S4 agree; S2 wrongly says "3M IAC power" (S1 refutes) |
| 3N | LG | Fuel pump relay control (circle 27) | out | low side to relay coil | S2,S4 agree; S3 (Australian) puts it on 3P: disagreement (market difference, not US) |
| 3O | V/R | +B supply for IAC solenoid (passes through PCM) | out | 12 V supply, current of the IAC coil | S3,S4 agree (+12 V); S2 says "IAC control" (wrong) |
| 3P | * | unused (S3: fuel pump relay Aus) | | | |
| 3Q | W/L | VICS solenoid valve (B1-10) | out | low side, valve fed W/R from main relay | all |
| 3R | * | unused | | | |
| 3S | GY | EGR boost sensor signal (B1-07) | in | analog | S3 agree |
| 3T | GY/B | EGR boost sensor solenoid valve (B1-11) | out | low side | S3 agree (3T) |
| 3U | L/O | CDCV (canister drain cut valve, B1-18) | out | low side, 1999-2000 US EVAP | S1; S3 "-" |
| 3V | R/Y | Rear heated O2 sensor heater (ground) | out | low side | S4 "3V O2H2" |
| 3W | Y/B | Injector 1 | out | low side, injectors fed W/L from main relay, ~12-16 ohm high-impedance | all |
| 3X | V/G | Injector 2 | out | low side | S1 diagram: no.1 Y/B (3W), no.2 V/G (3X), no.3 Y/R (3Y), no.4 Y/G (3Z) |
| 3Y | Y/R | Injector 3 | out | low side | S3 agrees |
| 3Z | Y/G | Injector 4 | out | | |

### Disagreements between sources
- 3M/3O: S1 (primary) says 3M = IAC control (O), 3O = +12 V (V/R). S3, S4 agree. S2 (rusEFI wiki) swaps them (wiki error).
- Fuel pump relay: 3N (S1 LG, S2, S4) vs 3P (S3 Australian). US car: 3N.
- 1E MIL: present in US (S1, S2); absent on the Australian list.
- Immobiliser: not on the US PCM plug; S3 2001+ Australian list has an immobiliser module line (pin 31) and AMP documents a "Europe w/ immob" fuel-pump jumper: on immobilised markets the fuel pump relay (3N / EU 2P?) is controlled via the immobiliser. UNVERIFIED for 1999-2000 (Hellen yaml: "3N: 2M US / 2P EUROPE - FPUMP": in Europe the fuel pump cavity differs: 2M US / 2P EUROPE hints the immobiliser-market uses a different cavity; the Mazda 2000 US diagram shows 2P = EGR in US).

Variants (S1 "<>AT"): AT adds 1K V/G and 1N P/B to the TCM and drops 1V neutral; MT has 1V neutral and 3I clutch. S1 marks rear HO2S wiring (3J/3V) differently for California (*1) and federal (*2). No other federal/California differences visible in the PCM box (EVAP FTP 2A, CDCV 3U, EGR 2M-2P, EGR boost 3S/3T present in the diagram without a variant tag). 2000 vs 1999: S1 is the 2000 book; S2/S3 (1999 and 1999-2000) agree on every cavity both list, so no year change seen (not independently verified for 1999 colours).
Generator wiring (S1 p.19 Z-16): generator connector A-03 carries GY/R (to PCM 1O, through a resistor inside the generator) and GY (from the regulator transistor to PCM 1T); B+ terminal separate. Arrow heads on the Mazda page references give no signal direction (checked on 1P/1S/1R/1E: not consistent), so direction rests on S2/S3/S4 ("alternator field output", "feedback").
Not on the PCM plug: immobiliser (US cars), ignition-switch sense (1C unused), main relay control (key switches the relay via ENGINE 15A fuse). 1H G/R is +B from FUEL INJ 30A fuse (S1 p.21; S3).

## STEP 2: cavity-by-cavity comparison with cur_mb9900 / ord_mb9900
Source: kb/interconnect.md lines 576-656 (cur) and 1634-1702 (ord); evidence/*/pcb_footprints.csv; firmware/board/miata_pins.h, miata_board.cpp. The ordered board's harness net map is identical to the current one (only 2B -> HARN_IAT via JP1 differs, and F4 0.5 A). Daughterboard side was not re-audited here (scope: cavity chain).
Verdicts: OK = matches factory function/polarity; OK(n/c) = left open, no harm beyond Step 3; ISSUE = see findings.
| Cav | Board net -> MCU | Verdict |
|---|---|---|
| 1A | none | OK(n/c): keep-alive +B not used (rusEFI keeps tune in flash) |
| 1B | VBAT_IN | OK: main relay output is the ECU supply |
| 1C,1J,1M,2G,3D,3P,3R | none | OK: unused in factory |
| 1D,1L | none | OK(n/c): diagnostic link; no OBD tool works |
| 1E | OUT_CEL low side (E4) | OK: matches W/L MIL low side |
| 1F,1H,1K,1N | none | OK(n/c) (1K/1N AT only; 1H +B pre-relay) |
| 1G | none | OK(n/c): power-steering pressure switch ignored, no idle-up on PS load |
| 1I | OUT_LS7 (E2) low side | OK: condenser fan relay L/W low side |
| 1O | OUT_ALT (D5) low side, no pull-up, control OFF in firmware | documented (alternator may need pull-up); S1 shows regulator input with internal resistor, consistent with repo note |
| 1P | IN_SW2 (E10), R21 not fitted | OK: A/C request is a 12 V line (INFERRED) and R21 correctly not fitted. Note the same node is the condenser-fan motor feed (R/W line), so any pull-up or the 22k/10k divider loads a low-impedance winding path: harmless |
| 1Q | none | ISSUE (documented, consequence not stated): charge lamp never lit |
| 1R | OUT_FAN (E5) | OK |
| 1S | OUT_AC (E6) | OK: A/C relay L/B low side |
| 1T | none | OK(n/c): alternator feedback unread; consistent with control off |
| 1U | OUT_VVT (D7) low side, o2heaterPin | OK: front HO2S heater ground side, low side; resistive heater needs no flyback |
| 1V | none | OK(n/c): neutral switch ignored |
| 2A | none | OK(n/c): FTP sensor unread |
| 2B | IN_IAT (A7) | OK |
| 2C | IN_AUX2 (B0) front narrowband | OK |
| 2D | IN_SW1 (E9), R20 not fitted | UNRESOLVED: cluster VSS output type (open collector vs 12 V drive) not shown in the diagram pages read; repo asks owner to fit R20 if open collector |
| 2E | IN_CLT (A6) | OK |
| 2F | IN_KNOCK (A3) | OK (clip documented) |
| 2H,2J | IN_HALL2/1 (E8,E7), 1k pull-up to V5_EXT | OK: sensors are 3-wire, supplied 12 V from main relay (S1 B1-16/B1-25 W/R), output open collector; 5 V pull-up clamped to 3.3 V is a valid design (not simulated here) |
| 2I | V5_EXT out | OK: Vref LG/R feeds TPS, EGR boost, FTP; board supplies it from protected 5 V |
| 2K | OUT_TACH (E3) | OK (UNVERIFIED cluster input threshold; cluster has its own pull-up in practice) |
| 2L | IN_AUX3 (B1) MAF | OK: signal only; MAF 12 V supply W/R from main relay is car side |
| 2M-2P | none | OK(n/c): EGR stepper valve never driven, stays closed |
| 3A,3B,3C,3F | GND | OK: 3C B/L (sensor gnd) and 3F B/R (sensor ground) tied to power ground on the board: loses sensor-ground separation (TPS/CLT/IAT/knock return currents share the injector return ground). See finding |
| 3E | IN_TPS (A4) | OK |
| 3G,3H | OUT_IGN1/2 5 V logic | OK |
| 3I | IN_SW3 (E11), R22 not fitted | ISSUE: S1 shows clutch switch BR/W grounded (B) when closed, so by factory design R22 should be fitted; repo says signal is 12 V driven |
| 3J | IN_AUX1 (C5) | OK rear O2 signal |
| 3K | none | OK(n/c): fuel level signal from cluster unused |
| 3L | none | OK(n/c): purge never opens |
| 3M | OUT_IACV (B3) + D1 flyback to 3O | OK: IAC low side on 3M (matches S1; rusEFI wiki error) |
| 3N | OUT_FP (C14) | OK: LG fuel pump relay |
| 3O | IAC_12V = VBAT_IN via F2 2A | OK: +B to IAC coil (S1: V/R) |
| 3Q | OUT_MAINRLY (C13) low side, unassigned in NB1 firmware | ISSUE: VICS never energised (see Step 3) |
| 3S,3T,3U,3V | none | OK(n/c): EGR boost sensor/solenoid, CDCV, rear HO2S heater not used |
| 3W..3Z | OUT_INJ1..4 | OK: order 1,2,3,4 on W,X,Y,Z agrees with S1/S3 |
| XA..XL (12 header positions) | none | OK: no harness plug in that bay (consistent with S1: 22+16+26=64) |
Connector: car has 64 positions in three plugs (22/16/26); current board header TE 178780-1 has 76 (64 + 12-position bay between plug 1 (x 116-147) and plug 2 (x 173-194), where 152-168 mm hold XA..XL). Ordered board uses 176122-6 (64P). Geometry gap of 12 positions at 3 mm pitch; can not verify the car's ECU shroud has that bay (Hellen NB1 uses the same 76P part per its kicad symbol, supporting it). Checked, consistent.

## STEP 3: what the stock ECU did that this board does not
| Function (pin) | Stock behaviour | This board | Driver notices / harm |
|---|---|---|---|
| Alternator control (1O out, 1T feedback, 1Q lamp) | PCM sets regulator target via 1O (250 Hz per repo note), reads 1T, lights lamp via 1Q | 1O driver exists, control off; 1T, 1Q open | Regulator runs on its own default (documented unknown pull-up). Charge lamp never lights: neither bulb-check at key-on nor on charging failure; car can run the battery flat with no warning. VERIFIED wiring (S1 p.33: lamp fed from IG, sink is PCM 1Q) |
| VICS solenoid (3Q) | Forum report (UNVERIFIED): solenoid energised below about 5200 rpm (vacuum closes VICS valves), de-energised above so a spring opens them | firmware leaves 3Q off (mainRelayPin unassigned for NB1, README: wired but not set up) | Valves would sit in the high-rpm (open) state at all rpm if that polarity is right: lost low/mid torque, no damage. Polarity and rpm need checking on the car; repo does not say which state results |
| EGR (2M-2P, 3S, 3T) | stepper EGR valve + boost sensor + solenoid | none | valve stays closed: more NOx, possibly slightly higher peak combustion temps; no drivability harm |
| Purge (3L), CDCV (3U), FTP (2A) | EVAP control | none | purge valve closed: canister saturates, fuel smell/vapour venting; tank vapour management lost; no engine harm |
| Heated O2 front (1U heater, 2C signal) | heater PWM, narrowband closed loop | heater low side driven from o2heaterPin; signal read on AUX2; main fuelling on wideband | OK |
| Rear HO2S (3V heater, 3J signal) | catalyst monitor | signal AUX1, heater not driven | sensor cold: nothing breaks |
| Crank / cam (2J, 2H) | Hall, 12 V from main relay | read with 5 V pull-ups | OK |
| Coils (3G,3H) | logic level to coil-pack igniters | 5 V logic from buffer | OK; no igniter feedback exists on NB |
| Knock (2F) | knock IC | software knock via amp | documented |
| Immobiliser (non-US) | S3 (2001+ Aus) shows an immobiliser module line; AMP offers a "Europe w/ immobiliser" fuel pump jumper for the 1999-2000 box | none | car will not run on immobilised-market cars (UNVERIFIED which 1999-2000 markets) |
| Fuel pump relay (3N) | low side, PCM controlled prime | OUT_FP | OK; stock key-on prime duration behaviour is firmware |
| Fans (1R, 1I) and A/C (1S, 1P) | PCM controls both fans and clutch relay | all driven | OK; A/C request polarity depends on firmware acSwitch default (active high, matches) |
| Power steering switch (1G) | idle-up | not read | slight idle dip when turning at standstill |
| Clutch (3I) / neutral (1V) | starter/cruise / fuel-cut logic | 3I read but needs R22; 1V ignored | no launch/clutch features unless R22 fitted |
| Data link (1D,1L) / MIL | diagnostics | MIL lamp only | no Mazda scan tool |
| Keep-alive +B (1A) | KAM | none | no loss (config in flash) |
| MAF (2L) / IAT | stock MAF kept as AUX3 | OK |  |
| Connector | 64 positions, 3 plugs | 76-position header (64 used + 12 unused) or 64P on ordered | OK |

## Sources actually read
- w2000.pdf pages 14-25, 30-33, 49 (Mazda 2000 wiring diagram scan; pages 19, 21, 23, 25, 33, 49 read in detail), neomiata.com URL.
- wiki.rusefi.com/Mazda-Miata-1999, bartuneengineering NB8A and NB8B/SE pinout pages, AMP MM9900 installation page, search results (Mazda tech tip 1998, miataturbo), rusEFI Hellen NB1 board files (main.yaml, board_configuration.cpp), AMP rear options connector PDF (text only, not used).
- forum posts on VICS polarity via search summary (not opened: UNVERIFIED).
- kb/interconnect.md cur/ord mb9900 tables, firmware/board/miata_pins.h, miata_board.cpp, motherboards/1999-2000/README.md.

## Not checked
- Cluster VSS output type (2D); A/C amplifier output type; generator 250 Hz / duty direction; VICS polarity from a Mazda manual; 1999 wiring diagram colours (only 2000 book read); daughterboard side (JD1/JD2 to MCU) and driver circuit currents; AMP rear options connector pinout PDF; fuel pump/ fan pages (B-2, B-3).
