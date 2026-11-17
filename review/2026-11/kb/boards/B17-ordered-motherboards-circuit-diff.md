# B17 - Ordered motherboards reviewed as built: cavity-by-cavity diff vs current, direct circuit check, first-test list, shipped-docs check

STATUS: complete (2026-11-16). Scratch: `work/B17-ordered-motherboards-circuit-diff/` (`tab.py` cavity diff -> `diff.txt`; `parts.py` part-by-part diff -> `partsdiff2.txt`; `readme_check.py` README harness table vs PCB; `img/molex_crop2.png`).
Tags: VERIFIED = read/computed from design files or datasheet today; INFERRED = reasoning shown; UNVERIFIED = memory.
Pairs: ord_mb8993 and ord_mb9495 vs cur_mb8995 (one merged 1989-95 board, rev 0.13); ord_mb9697/9900/0105 vs cur_mb9697/9900/0105. Daughterboards: ord_db rev 0.9 vs cur_db rev 0.10.

## Summary
1. Cavity diff (harness cavity -> net -> parts on net -> JD pin -> daughterboard net) for all five boards: 0 unexplained differences. Every difference is a documented change: rev 0.12 merge of 1989-95 with jumpers JP1-JP6, R35-R37, D5, 2x10 AUX, F4 1.1 A (README rev 0.12 / 0.8), rev 0.13/0.9 JST wideband connector, J3 + JP1 IAT removed (rev 0.12/0.8), 1999-2000 header changed 176122-6 -> 178780-1 (rev 0.8), 1989-93 pairing dropped (commit 6e346af). Section 1.
2. All 80 JD1/JD2 pins vs ord_db J1/J2 match by net on all five boards; the only name differences are J2-39/40 HTR_GND on motherboard GND (intended). Every harness-cavity row of every ordered README matches the PCB (readme_check.py, 5/5; the two apparent misses on 2001-05 were 4AA/4AF, my regex).
3. Direct checks passed: MPX5700AP pinout (1 Vout, 2 GND, 3 Vcc), 1 uF / 10 nF / 470 pF per Motorola figure; Molex 43045-0600 footprint vs Molex drawing (circuit 1 bottom right nearest the peg, 4-6 above); SS34 / SMCJ30A polarity; USBLC6 pin use; USB-C CC1/CC2 5.1k; J5 pin/row numbering vs INSTALL; JP1 left-two = STOCK. Section 2.
4. Real issues for the owner (all small): tach 2I is hard-wired to OUT_TACH on 1989-93 and 1994-95 and the firmware default turns it on (B03 P6 re-confirmed; a zero-cost physical safeguard is not soldering header pin 2I); 1994-95 README 2I row has no igniter warning; J3 (Molex 436500202, C587650) shows LCSC stock 0; JP1 ships on EXT with nothing on J3 (set STOCK for a first test); no boost flyback D5 on the ordered boards (B03 P3).
5. Shipped docs (ABOUT, READMEs, INSTALL, pin tables) describe the ordered boards, not later revisions: no 2x10 / JST / R35-37 / JP2-6 / microSD references (grep clean). Minor: 1994-95 README gives no sourcing/igniter caveats; ABOUT says commit 4f34615 = freeze (it is the parent of the freeze commit e44b46c; no board files changed between).

## 1. Cavity diff (ordered vs current), with explanations
Script `tab.py`; compares per cavity: net, non-harness parts on the net, JD pins and the daughterboard net on those pins. GND cavities compared by count (25 JD GND-type pins everywhere).
Common to all five (explained): current adds R35 (4.7k V5_EXT->IN_FLEX) on 2K/3I/2I/4L, R36 (10k IN_N2O->GND) on GND net, D5 (SS34 AUX_VBAT->OUT_BOOST), F4 1.1 A 1812 instead of 0.5 A 1206, J5 2x10 (GND 17/18, CAN 19/20, IN_FLEX/IN_N2O on 12/13 instead of UART_TX/RX), J2 = JST PUD 2x4 AEM instead of Molex 2x3, J3/JP1 removed (cavity IAT goes straight to IN_IAT instead of HARN_IAT -> JP1). All in README changelog rev 0.12 (1989-95) / 0.8 (1996-2005) and rev 0.13 / 0.9 (JST). Daughterboard side explained in B03 section 1.1 (J2-24/25 UART -> FLEX/N2O).

| Board | Cavity | Ordered | Current | Explained by |
|---|---|---|---|---|
| 8993 | 1B | VBAT_IN: D1 D2 F1 F4 R20-22 | + R37 (1k 2512 to OUT_TACH) | rev 0.12 JP5 TACH COP (README l.143, 158) |
| 8993 | 1R | OUT_LS7 direct | HARN_1R -> JP3.1 (FAN2 jumper) | rev 0.12 jumpers |
| 8993/9495 | 2I | OUT_TACH direct | HARN_2I -> JP5.2, open by default | rev 0.12: stock igniter drives tach, "firmware has no tach output on these years" (cur README l.158). Ordered firmware has it ON (miata_board.cpp:86) - see Finding 2 |
| 8993/9495 | 2O | IN_AUX3 direct | JP6 (AUX3 / boost) | rev 0.12 |
| 8993/9495 | 2P | HARN_IAT -> JP1 | IN_IAT direct | rev 0.12 J3/JP1 removed |
| 8993 | 2R, 2S | not connected | 2R via JP4, 2S via JP3 | rev 0.12 merged 89-95 board |
| 8993 | 2U/2V | OUT_INJ1/2 + D3/D4 + R23/R24 0R to INJ4/INJ3 (fitted) | JP2/JP1 with no shunt on 89-93 | commit 6e346af 2026-11-15 "one driver per injector wire"; ordered pairing documented (README, ABOUT) |
| 8993 | 2Y/2Z | HARN_2Y/2Z via R25/R26 (not fitted) | via JP1.3/JP2.3 | same |
| 8993 | 2L / 1N / 2K | R29 fitted, R30/R28/R27 not fitted | same R-net, R27/R28 also present | identical (rev 0.11) |
| 9495 | 1N, 2L | nc ; IN_AUX1 direct | HARN_1N/R28, HARN_2L/R29/R30 | cur board is merged and keeps the 89-93 TPS links; 94-95 has none |
| 9495 | 2R/2S/2U/2V/2Y/2Z | OUT_ALT, OUT_LS7, INJ1-4 direct, no TVS | JP4, JP3, INJ1/2 with D3/D4 + JP | rev 0.12; ordered db has no clamps either (B03 P8) |
| 9697 / 0105 | 3K / 4N | HARN_IAT | IN_IAT | J3/JP1 removed |
| 9900 | all | TE 176122-6, 65 cavities | TE 178780-1 NB1, 77 cavities (XA-XL are 12 extra unconnected pads) | rev 0.8 header change; named cavities identical |
Other part-level differences (partsdiff2.txt): D5, R35, R36 absent on 9697/9900/0105 (changelog); sheet-name prefix on nets only (KiCad sheet renamed "LSU, MAP, IAT, USB, AUX" -> "Wideband, ..."): cosmetic.
Unexplained differences: none. Where a difference is a regression of the ordered board relative to current: tach direct (2I), no D5, F4 0.5 A, no 220 ohm (B03 P1): the CURRENT design is right in each, the ordered board is what is "wrong/older" and is reworkable (see 3).

## 2. Direct check of every non-connector part on the ordered motherboards
| Part | Result | Evidence |
|---|---|---|
| F1 3A hold, 2920, LUTE 2920L300/30GR (C22446884) | OK: 3 A hold, 30 V (manifest l.111); 12 mohm-48 mohm; between VBAT_IN and J2.4 (H+). PTC voltage 30 V documented open item | pcb_pads F1.1 VBAT_IN, F1.2 HTR_PWR; track min 1.0 mm |
| F4 0.5 A, 1206, nSMD050-33V (C70077) | OK as designed; J5-15 only; track 0.5 mm. Boost valve takes most of it (ABOUT) | pcb_pads, routing csv |
| F2 / F3 2 A 1812 (SMD1812-200-30, C46641168), 1999-2000 (F2) and 2001-05 (F2, F3) | VBAT_IN -> IAC_12V (J1 3O / 2P) and OCV_12V (4D): ECU supplies the valve +12 V through the PTC, D1/D2 cathode after the PTC. Shipped README l.60/119 describes it. Note: only in JLC BOM, not in my earlier harness table | pcb_nets IAC_12V: D1.1 F2.2 J1.3O |
| D1 (IACV) / D2 (VVT or purge) SS34 SMA | OK polarity: netlist pin K=1=VBAT_IN (or IAC_12V), A=2=OUT_x. 8993, 9495, 0105 have D1+D2; 9697, 9900 D1 only | sch_netlist.xml D1 pins K/A |
| D3 / D4 SMCJ30A SMC (8993 only) | OK polarity K=OUT_INJx, A=GND (unidirectional TVS, 33.3-36.8 V, manifest l.27). Absent on 9495 (clamp left to the db drivers, B03 P8) | netlist |
| U4 USBLC6-2SC6 | OK: pins 1/6 D+, 3/4 D-, 2 GND, 5 VBUS | pcb_pads |
| J4 USB-C | CC1, CC2 each 5.1k to GND (R2/R3): UFP; VBUS A4/B4/A9/B9 joined; SBU nc; shell GND | pcb_pads |
| R1 120 / R6 0R | CAN termination fitted by default; no CAN connector on ordered boards so inert | JLC BOM |
| R20-R22 4.7k VBAT_IN -> IN_SW1-3 | In JLC BOM? No: not placed (self-order optional). Defaults to no pull-up; only for ground-switched signals | JLC vs self-order BOM |
| R23/R24 (8993) | 0R fitted: INJ4->INJ1 (2U), INJ3->INJ2 (2V). R25/R26/R28/R30 not fitted, R29 fitted, R27 not fitted | JLC BOM "R23,R24,R29" |
| JP1 IAT SEL | pad1 HARN_IAT (left), 2 IN_IAT, 3 IAT_EXT. Shunt 1-2 = STOCK, 2-3 = EXT; matches INSTALL l.76 (left two = STOCK). Default per README = EXT | pcb_pads x=152.46/155.0/157.5 |
| J2 Molex Micro-Fit 43045-0600 | footprint: pin1 (129.0,202.3) right/edge row, 2 at 126, 3 at 123; pins 4-6 at y=199.3 above 1-3; pegs at y=206.62. Molex drawing (datasheets/C127367_430450600.pdf p1, PCB layout 6 CKT, component side): circuit 1 bottom-right next to the peg hole, 2 centre, 3 left, 4-6 the upper row, 4 above 1. MATCH. INSTALL pin-1-at-right matches | img/molex_crop2.png |
| J3 Molex 43650-0200 (436500202) | pad 1 x=155 (right), pin 2 GND at 152. Single-row 43650 header, mating 43645-0200 as INSTALL says. Pin-1 side not checked against a Molex drawing (no datasheet in pack) | pcb_pads; UNVERIFIED pin 1 side |
| J5 2x8 IDC | pin1 (185.89,178.25) right end; odd pins at y=178.25 = row nearer JD2 (JD2 y=165.25): matches INSTALL "odd pins nearer the daughterboard". Pinout 1 IGN3, 2 IGN4, 3 BOOST, 4 ALT, 5 MAINRLY, 6 KNOCK, 7-10 VR, 11 AFR, 12 TX, 13 RX, 14 V5_EXT, 15 AUX_VBAT(F4), 16 GND = INSTALL table | pcb_pads |
| U2 MPX5700AP, case 867B | pads 1 IN_MAP, 2 GND, 3 V5_SENS at 2.54 pitch, 4-6 pads unconnected; datasheet style 1: 1 Vout, 2 GND, 3 Vcc, 4-6 V1/V2/Vex (n/c on AP) (datasheets/txt/C90152_MPX5700AP.txt l.270-275). Hole spacing 23.11 mm = 227.81-... check: 203.555-180.445 = 23.11 OK. C1 1 uF + C2 10 nF on V5_SENS, C3 470 pF on IN_MAP = datasheet decoupling figure (l.206). Supply: own V5_SENS from db (not V5_EXT) | pcb_pads, datasheet |

Checked and held up: JD mating (B03), harness tables (below), polarity. Not re-derived: harness header geometry (kb/parts/P19*), tracks (B09-B12), 220 ohm / F1 / L1 / battery sense (B03 P1-P5).

## 3. What the owner must do per ordered board
Hand fit on every board (self-order BOM): harness header, JD1/JD2 (C124412), J5 2x8 (C3406), J2 Molex 430450600 (C127367), J3 Molex 436500202 (C587650, LCSC stock 0 in manifest), JP1 header (C49257) + shunt (C5305), MAP U2 (C90152, lies flat, 2 x M3x10 + nuts), 4 standoffs + 8 x M3x6. JLC fits the SMD parts and USB-C (check JLC quote: USB-C shell pegs).
| Board | Header | Options and first-test state |
|---|---|---|
| 8993 rev 0.11 | TE 174917-6 (salvage/clone) | Fitted: R23/R24 (paired drivers, batch), R29. Not fitted: R25/R26 (sequential only, NEVER R26 on an automatic), R28/R30 (TPS conversion only), R27, R20-R22 (only for ground-switched VSS / A/C / clutch). JP1: STOCK with airflow meter fitted. Tach 2I: see below. Alternator output 2R not wired on 1989-93. 1989-93 injector wire TVS D3/D4 SMCJ30A present |
| 9495 rev 0.9 | TE 174917-6 | No links. JP1 STOCK. 2U/2V/2Y/2Z direct to drivers, no TVS on the board or db (B03 P8): bench-test injector driver temperature first. 2R = OUT_ALT is the pressure regulator solenoid wire (alt control ships off). Tach 2I: see below |
| 9697 rev 0.7 | TE 178780-1 | JP1 STOCK (airflow meter IAT). D1 only. No F2/F3: valve +12 V comes from the car harness |
| 9900 rev 0.7 | TE 176122-6 (BOM alt. 4-174518-7) | JP1 STOCK (separate IAT in airbox). F2 2 A PTC feeds idle valve +12 V on 3O. 1999-2000 main relay/VICS on J5-5 if used |
| 0105 rev 0.7 | TE 353830-5 | JP1 STOCK. F2 (2P idle) and F3 (4D VVT) 2 A PTCs. Main relay on J5-5 on 2003-05 |
Before plugging into a car (reason): (a) 8993 / 9495: stop the ECU driving the tach wire. Firmware default has tachOutputPin set (miata_board.cpp:86); 2I is the igniter's signal into the ECU on a stock car (current README l.77, 158). Software: tach output = none in TunerStudio before the first connection. Zero-cost hardware: do not solder (or clip) harness pin 2I when fitting the header; no other circuit uses it. (b) JP1: shunt must be on STOCK (1-2) when the stock sensor is used, because EXT with nothing on J3 leaves IN_IAT floating on its pull-up (INFERRED; INSTALL l.222). (c) Do not hang a boost solenoid on J5-3: no D5 on the ordered boards and F4 holds 0.5 A (B03 P3). (d) Daughterboard-level reworks (220 ohm on Q1-Q8, F1/L1) are B03 P1-P5. (e) Leave R20-R22 off unless the signal is ground-switched: a 12 V driven signal would read always-on (README). (f) Do not fit R26 on an automatic.

## 4. Shipped documents (repo/ordered-boards/2026-11/)
- ABOUT.md table matches board revisions and headers (8993 rev 0.11, 9495 0.9, 9697/9900/0105 0.7, 48/48/76/64/72 pins) and the PCB footprints.
- Each motherboard README harness table = PCB J1 nets exactly (34/34/32/35/37 connected pins, plus "Not connected" lists = PCB unconnected, all five): VERIFIED by readme_check.py.
- INSTALL J5 / J2 / JP1 maps match the PCB (section 2). J2 wire colours / the "pin 5 RT has no wire" statement: not checked against the Bosch LSU 4.9 datasheet (not in pack).
- grep for later-revision features (2x10, JST, PUD, AEM 30-3427, R35-R37, D5, JP2-JP6, microSD, rev 0.10-0.13, 1.1 A): none in READMEs / INSTALL / ABOUT / VERIFICATION / BOM / shopping list (only "no SD card" statements and 8993's own R2x/J6 history).
- Gaps: 1994-95 README 2I row `OUT_TACH | tach out | (blank)` - no stock-igniter note (the 1989-93 README also blank). ABOUT's "Known points" and firmware README l.204 do carry the warning, so only the per-board README is silent. ABOUT's `4f34615` is the freeze's parent commit (git log: e44b46c "Frozen copy" follows 4f34615 directly; no board file between).
- 1989-93 README says R23/R24 "INJ1 + INJ4 drive 2U" and 2U feeds injectors 1 and 3 on the car (firmware comment): consistent with current research; the current design has since dropped the pairing (6e346af). Ordered boards should be reworked only if the owner wants the current policy (B03 P7: remove R23/R24).

## Sources actually read
evidence/ord_* and cur_* pcb_pads.csv, pcb_footprints.csv, pcb_nets.txt, pcb_net_routing.csv, sch_netlist.xml (ord_mb8993), fab BOMs of the five ordered boards; kb/interconnect.md; kb/boards/B03; ordered 1989-93 and 1994-95 READMEs in full, harness tables of the other three, ABOUT.md, INSTALL.md l.36-82 and 222-225, firmware board miata_board.cpp l.73-92, 170-290; current motherboards READMEs (changelogs, JP5/R37 rows); git log (read-only); datasheets C127367_430450600.pdf p1 (image), C90152_MPX5700AP.txt; kb/parts_manifest.md rows for C587650, C22446884, C224048, C8678.

## Not checked
- Bosch LSU 4.9 plug pin numbers and wire colours (J2 table): no datasheet in the pack.
- Molex 43650-0200 pin-1 side; harness header footprints (see kb/parts/P19*); copper widths and current (VBAT_IN min 0.6 mm segment on 8993/9495/9697/9900, 0.5 mm AUX_VBAT; heater nets 1.0 mm) left to B09-B12.
- Live LCSC stock re-check of C587650 (used manifest value 0).
- Whether the 4-layer daughterboard order used filled vias (B03).
