# PIN-9697-A design-outward: 1996-97 NA8 (OBD-II, 76-pos header) pinout chain audit

Boards: cur_mb9697 (rev 0.9, daughterboard 0.10) and ord_mb9697 (rev 0.7, daughterboard 0.9). Status: COMPLETE (partial, see Not checked).

## Summary
1. PRIMARY SOURCE FOUND AND READ (image): 1997 Mazda MX-5 System Wiring Diagrams (Mitchell), https://www.mellens.net/mazda/Mazda-Miata-1997/wiring.pdf, Fig. 8 (PDF p.16, ECM terminal list with wire colours) and Fig. 9 (PDF p.18, where each numbered wire goes), Fig. 1 A/C (p.2), Fig. 5 cooling fan (p.10), Fig. 17 cluster (p.34). The repo's own research said no factory source for 96-97 could be read; it can. Crops in work/PIN-9697-A-design-outward/img/. The fan figure states "1996-97" on 1A/1B (1995 used 1L/2S), so the pin map holds for 1996 too (1996 wiring PDF itself not read).
2. Pin MAP verdict: every cavity the board connects is functionally right (checked against FSM + Hellen NA96 yaml + MSPNP-MM9697 doc + rusEFI wiki): 1A,1B,1E,1G,1K,1L,1M,1O,1U,3B,3C,3D,3F,3G,3I,3K,3M,3O,4A-4D,4F,4G,4L,4N,4Q,4R,4U-4X. The PCB, schematic net list and daughterboard chain are consistent (interconnect.md: all JD pin names match except HTR_GND/GND, intended).
3. Wire COLOURS in repo research / rusEFI wiki are partly wrong (FSM 1997): 4G is YEL/BLU (wiki GRN), 4N BRN/YEL (wiki GRN), 4U YEL (wiki WHT), 4V YEL/BLK (wiki YEL), 4E GRN/ORG and 4H GRN/BLK (wiki YEL/BLK, YEL/WHT), 3L is RED = throttle idle switch signal (research: "ground"). Doc-only; a wrong-colour table could mislead a harness probe.
4. RESOLVED open items: 4I = BLU/RED battery backup (hot at all times through ROOM fuse 10A): leaving it open is right. 4E/4H = crank-pulley sensor (VR, 2 leads + shield BLK/LT GRN): leaving open is right. 1D = WHT/BLK data link (K-line) to BOTH DLCs, 1I = LT GRN/YEL to DLC1.
5. Stock ECU outputs/inputs with no board connection, new detail from FSM: 4T purge solenoid (YEL/RED), 4O EGR vent (YEL), 4P EGR vacuum (YEL/WHT), 4J PRC (pressure regulator control) solenoid (YEL/GRN), 4Z rear HO2S heater (VIO), 1H headlight-load input, 1P A/C control unit line, 1Q brake switch, 3P power-steering pressure switch, 3H EGR boost sensor, 3J EGR valve position sensor, 3N BLK/YEL (to EGR boost sensor connector, function unresolved), 3L idle switch, 1D/1I diagnostics, A/T lines 1R, 1T, 4Y. Repo README lists 4J/4O/4P/4T as unknown or absent and calls 4Z only a Hellen item.
6. Fans: radiator fan (1A BLK/GRN) and condenser fan (1B BLU/WHT) are the ECU's job on this year (relay coils fed from engine fuse BLK/WHT, ECU sinks). rusEFI defaults 92/88 C (fan_control.cpp:264-266) so the fans work after the year preset; A/C relay 1G / request 1K wired and configured.
7. No immobiliser, no ECU main-relay control, no alternator/charging wire at the ECU (VERIFIED absent in Fig 8/9; charge lamp is a cluster/alternator circuit). Stock ignition = two coil packs with built-in igniter, 3 wires each (BLK, BLK/WHT +12 V run, BRN/YEL or BRN signal): VERIFIED Fig 8.
8. Nothing found that is a hard error in the 96-97 chain. Risks are consequences (no OBD-II scan/inspection, no EGR/purge/PRC, A/T, VSS and clutch input polarity unknown with R20-R22 not fitted).

## Chain table
Chain: cavity -> MB net (parts) -> JD pin (same on daughterboard J1/J2) -> db conditioning -> MCU pin -> firmware (setMazdaMiata96 + board/miata_board.cpp). Sources: FSM = 1997 Mitchell wiring Fig 8/9 (primary); H = Hellen NA96 main.yaml in rusEFI (firmware/ext/rusefi/.../hellenMiataNA96/connectors/main.yaml); M = MSPNP Pro MM9697 doc (megasquirtpnp.com/docs/mspnp_gP_mm9697.php); W = rusEFI wiki Mazda-Miata-1996; A = allpinouts (weak). MCU pins from miata_pins.h. Verdict correct unless stated. cur and ord identical for these nets except 3K (see end).

| Cav | FSM colour / function / electrical | MB net (parts) | JD | db conditioning, MCU, firmware | 2nd/3rd source | Verdict |
|---|---|---|---|---|---|---|
| 1A | BLK/GRN cooling fan relay coil, ECU sinks (coil +12 V BLK/WHT from engine fuse) | OUT_FAN | JD1.9 | ZXMS6004 low side via LVC4245, PE5, fanPin | H 1A ECF; M fan1; W Fan1 | correct |
| 1B | BLU/WHT condenser fan relay coil, low side | OUT_LS7 | JD1.12 | low side, PE2, fan2Pin | H "AC fan relay"; W Radiator fan 2; M A/C relay (probable typo) | correct (README "fan No.2 / condenser fan") |
| 1C | none | - | - | - | all N/C (H uses it for CAN) | correct, unconnected |
| 1D | WHT/BLK data link, K-line (both DLC1 and DLC2) | none | - | - | A lists 1D WHT/BLK; M N/C | unconnected-by-design: no OBD-II scan tool / smog readiness |
| 1E | YEL/BLK check engine lamp (cluster 1C), ECU sinks | OUT_CEL | JD1.10 | low side PE4 malfunctionIndicatorPin | H, M | correct |
| 1F | none | - | - | - | W "not used" | correct |
| 1G | BLU/BLK A/C relay coil (relay contact BLK/RED to clutch), low side | OUT_AC | JD1.8 | PE6 acRelayPin | H, M | correct |
| 1H | RED/BLK "headlights system" (headlamp-on input, direction inferred) | none | - | - | M N/C | unconnected: no idle-up for lights (minor) |
| 1I | LT GRN/YEL to DLC1 (test enable) | none | - | - | A 1I LT GRN/YEL | unconnected: diagnostics |
| 1J | none | - | - | - | - | correct |
| 1K | LT GRN/BLK A/C request, via refrigerant pressure switch and thermo switch from A/C control unit; 12 V-switched (INFERRED) | IN_SW2 (R21 4.7k to VBAT, DNP) | JD2.16 | divider 22k/10k, PE10, acSwitch | H "A/C pressure in"; M A/C switch in | correct |
| 1L | BRN/WHT clutch/neutral/cruise switch (M/T), TCM (A/T); switch polarity not read | IN_SW3 (R22 DNP) | JD2.17 | PE11, clutchDownPin | H clutch; M clutch | correct pin; polarity cannot verify |
| 1M | GRN/RED VSS pulse from the speed sensor in the instrument cluster (also to TCM and cruise unit); output type not shown | IN_SW1 (R20 DNP) | JD2.15 | PE9, vehicleSpeedSensorInputPin | H VSS; M VSS DFIN2; A | correct pin; drive type cannot verify |
| 1N | none | - | - | - | - | correct |
| 1O | BLK/LT GRN ground (the "clean" ground net that also serves CAS, MAF, JC) | GND | JD GND | - | W/M/A ground | correct |
| 1P | BLU/ORG to A/C control unit (direction unknown) | none | - | - | M N/C | unconnected-by-design; function unresolved |
| 1Q | GRN/BLK brake switch (12 V when pressed) | none | - | - | H brake in; A brake | unconnected: nothing uses it |
| 1R, 1T | GRN, GRN/BLU to transmission, A/T only | none | - | - | W A/T only | unconnected: A/T cars (see below) |
| 1S, 1V | none | - | - | - | - | correct |
| 1U | LT GRN fuel pump relay coil, ECU sinks, coil other side WHT/RED (main relay); also DLC "F/P" terminal | OUT_FP | JD1.6 | PC14, fuelPumpPin | H, M, W | correct |
| 2A-2L | no harness plug (12-pos section unused) | none | - | - | W, M | correct |
| 3A,3E,3H? | 3A, 3E none; 3H BRN/BLK = EGR boost sensor signal | none | - | - | H "EGR boost" on 3S(Hellen)=OEM 4S? see notes | 3H unconnected: EGR sensor not read |
| 3B | RED/WHT MAF signal (analog) | IN_AUX3 | JD2.11 | 5.6k/10k divider, PB1, mafAdcChannel (algorithm stays speed density) | H MAF; W RED/WHT | correct |
| 3C | BLU/RED front HO2S signal (heated zirconia, ref BLK/BLU) | IN_AUX2 | JD2.10 | PB0, no preset use | H, M | correct |
| 3D | RED/BLU rear HO2S signal | IN_AUX1 | JD2.9 | PC5 | H, M | correct |
| 3F | RED/BLK TPS signal | IN_TPS | JD2.4 | PA4, tps1 | W RED/BLK, H, M | correct |
| 3G | BLU/WHT coolant temp thermistor | IN_CLT | JD2.6 | 2.7k pull-up, PA6 | W BLU/WHT | correct |
| 3I | LT GRN/WHT +5 V ref to TPS, EGR boost, EGR position (NOT MAF) | V5_EXT (R35 on cur only) | JD1.13 | protected 5 V | H +5V; M VRef | correct (README says "TPS, MAF": minor doc) |
| 3J | LT GRN/RED EGR valve position sensor | none | - | - | - | unconnected: EGR |
| 3K | RED/BLK IAT thermistor in MAF body | cur: IN_IAT. ord: HARN_IAT -> JP1 | JD2.7 | 2.7k pull-up PA7 | H, M | correct; ord needs JP1 on STOCK (documented) |
| 3L | RED throttle idle-switch signal (to TCM too) | none | - | - | M "ground", W N/C | unconnected; research label "ground" wrong |
| 3M | RED/WHT front HO2S heater return (ECU low side; heater +12 V BLK/YEL from engine fuse, not ECU) | OUT_LS... = OUT_VVT | JD1.34 | PD7, o2heaterPin = MIATA_VVT, driven by rusEFI heaterControlEnabled (engine.cpp:170) | M "O2 heater ground", H PCB jumper | correct |
| 3N | BLK/YEL to EGR boost sensor connector (function unresolved) | none | - | - | - | unconnected; cannot verify |
| 3O | BLK/BLU sensor ground (TPS, ECT, HO2S, EGR) | GND | GND | - | W, M, H GNDA | correct |
| 3P | BLU/YEL power steering pressure switch | none | - | - | - | unconnected: no PS idle-up |
| 4A | BLK/LT GRN to G119 | GND | | | all | correct |
| 4B | WHT/RED +12 V from main relay (key switched) | VBAT_IN (D1, F1, F4, R20-22) | JD1.1,2 | power | W, M, H | correct |
| 4C, 4D | BLK power grounds to G119/G117 | GND | | | M, H | correct |
| 4E, 4H | GRN/ORG, GRN/BLK crank pulley sensor (VR, shield BLK/LT GRN) | none | - | - | W, M leave | unconnected-by-design: no misfire monitor, firmware uses CAS |
| 4F | WHT CAS 4-pulse crank (SGT), open-collector, CAS fed WHT/RED 12 V | IN_HALL1 | JD2.13 | 1k pull-up to V5_EXT, clamp, PE7, triggerInputPins[1] | H 3F crank; M CKP | correct |
| 4G | YEL/BLU CAS 2-pulse cam (SGC) | IN_HALL2 | JD2.14 | PE8, triggerInputPins[0] (primary) | H 3G cam; M CMP | correct (TT_MAZDA_MIATA_NA primary = cam) |
| 4I | BLU/RED battery backup (ROOM fuse) | none | - | - | H +12V_PERM | unconnected-by-design: no keep-alive |
| 4J | YEL/GRN PRC solenoid (pressure regulator control), low side | none | - | - | - | unconnected (hot-restart consequence UNVERIFIED) |
| 4K, 4M, 4S, 4Y? | 4K, 4M, 4S none; 4Y BLU/YEL A/T only | none | - | - | M 4K "condenser fan" conflicts: FSM has no 4K wire | correct; 4Y unconnected (A/T) |
| 4L | BLK/WHT tachometer (cluster 1H), ECU generated | OUT_TACH | JD1.11 | low side PE3, tachPulsePerRev 2 | H 3L, W, M | correct |
| 4N | BRN/YEL igniter coil 1&4 signal (3-wire pack: BLK, BLK/WHT +12 V, signal) | OUT_IGN1 | JD1.14 | TC4427 5 V, PE1 | H, M, W | correct |
| 4O, 4P | YEL EGR vent, YEL/WHT EGR vacuum solenoids | none | - | - | H "EGR boost" on 3S only | unconnected: no EGR |
| 4Q | BLU/ORG idle air control valve, low side, valve +12 V WHT/RED | OUT_IACV + D1 freewheel to +12 V | JD1.31 | PB3, 300 Hz default | H, M, W | correct (polarity = Hellen low side active high) |
| 4R | BRN igniter 2&3 | OUT_IGN2 | JD1.15 | PE0 | H, M, W | correct |
| 4T | YEL/RED purge solenoid | none | - | - | - | unconnected: purge never opens |
| 4U-4X | YEL, YEL/BLK, GRN/WHT, GRN injectors 1-4 (+12 V WHT/RED) | OUT_INJ1-4 | JD1.19,22,25,28 | PB7..PB4, sequential | H, M, W | correct |
| 4Z | VIO rear HO2S heater return | none | - | - | H O2H2 | unconnected: rear sensor never heated; rusEFI ignores it |

(the packed rows 3A/3E/3H and 4K/4M/4S/4Y are as read: 3A, 3E, 4K, 4M, 4S have no wire in FSM.)

## Functional view
- Power and wake: 4B is the main relay output; the relay coil is fed from the engine fuse (BLK/WHT, hot in RUN/START) so the ECU powers up with key at RUN and dies with the key, as stock (no ECU hold-off, no after-run fan). Board: VBAT_IN, VIGN_IN not connected, ignKeyAdcChannel unset (correct for 96-97).
- Fuel pump: runs only when ECU sinks 1U (relay coil other end on main relay WHT/RED). Prime/run is rusEFI's. DLC1 F/P terminal grounding (FSM engine text line 65) still primes the pump without the ECU.
- Fans/AC: see rows 1A/1B/1G/1K. Both fans stop with the key off.
- Idle valve: low-side PWM to WHT/RED-fed valve; board drive active-high low side, D1 flyback. Stock frequency not found (UNVERIFIED); rusEFI default 300 Hz.
- Tach: ECU generated (coil has no tach lead), cluster input 1H.
- Charging: no ECU wire; unaffected. Check engine lamp 1E works.
- Not done by this board: OBD-II (K-line 1D, readiness), EGR (4O/4P/3H/3J), purge (4T), PRC (4J), rear heater (4Z), crank pulley misfire sensor, PS/headlamp/brake inputs, idle switch, battery backup. Driver notices: no scan tool and no smog-test readiness, idle dips when parking with power steering, vapour canister never purged (not harmful to engine), maybe harder hot restart if PRC matters (UNVERIFIED).
- Automatic: 1R, 1T, 4Y, 3L, 1L and VSS are A/T interface lines; none driven. TCM probably runs degraded (UNVERIFIED); README only names 1R/1T.
- Immobiliser: none on US 96-97 (no terminal in Fig 8/9).

## Sources actually read
- 1997 Mitchell wiring PDF (mellens.net) PDF pages 2, 10, 16, 18, 34 (images, read by eye); engine.pdf text for DLC jumper.
- rusEFI wiki Mazda-Miata-1996 (raw GitHub), MSPNP Pro MM9697 page, allpinouts 96-97 (weak), Hellen NA96 main.yaml and board_configuration.cpp, mazda_miata_na8.cpp, mazda_miata_1_6.cpp, fan_control.cpp.
- repo: research/pinouts_9605.md, motherboards/1996-97/README.md, kb/interconnect.md (cur and ord 9697), board/miata_pins.h, miata_board.cpp.

## Not checked
- 1996 wiring PDF itself; 3N function; 1H/1P direction; switch polarity of 1L and VSS drive type; stock IACV frequency; PRC function; wire gauge/current on 4B; Haltech/Link/ECUMaster pinouts (not obtained).
- Fig 9 wire tracing is visual; 4I and 4E/4H assignments are medium-high confidence.
