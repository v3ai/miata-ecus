# B14 - Docs vs design consistency (user-facing documents checked against the design files)

STATUS: complete for the scope listed under "Sources actually read"; items in "Not checked" remain open.

## Summary
1. The motherboard harness tables (all four READMEs) match the PCB and the schematic netlist pin for pin (script `work/B14-docs-vs-design-consistency/pin_tables.py`: every J1 row, all 20 J5 rows, NC lists; VERIFIED). Only wording quirk: 1999-2000 footprint has 76 pads, 12 (XA-XL) unconnected bay pads are described in prose, not in the NC list.
2. J5 and J2 orientation statements (pin 1 right / left, odd row nearer the daughterboard / away from the board edge, pin 1/2 first column) match pad coordinates on all four boards (J5 pin1 x=88.43, odd pins y=128.25 upper; J2 pin1 x=21.5, odd y=149.4, board bottom edge y=161.5). header_pinouts.png and annotated_motherboard_1989-95.jpg agree (VERIFIED, CORRECT).
3. Jumper tables JP1-JP6 (1989-95) match the netlist: JP1 pin1 INJ2/pin2 INJ3/pin3 2Y (PAIR=1-2, SEQ=2-3); JP2 INJ1/INJ4/2Z; JP3 1R/LS7/2S; JP6 AUX3/2O/BOOST; JP5 TACH/2I; JP4 OUT_ALT/2R. Silkscreen in the picture agrees. CORRECT.
4. Coil-on-plug cylinder mapping (IGN3 = cylinder 2, IGN4 = cylinder 4, IGN2 = cylinder 3) is CORRECT: miata_board.cpp:76-80 sets ignitionPins[1]=IGN3, [2]=IGN2, and rusEFI spark_logic.cpp:105,150 indexes coils by cylinder number.
5. Fuses (F1 3 A 2920 30 V, F4 1.1 A 1812, F2/F3 2 A), part numbers (C124412 sockets, C49257 headers, C90152 MAP, C22446884, C883150), order_all_boards.csv quantities (8 sockets, 8 pin headers, 4 MAP, 16 standoffs, 32 screws, 6 shunts, 4 x 1x3, 2 x 1x2) all consistent with the boards. CORRECT.
6. Stale/wrong items found: VERIFICATION.md "Safety review" tables still describe superseded hardware (F1 0.5 A, motherboard F1 2 A, F4 0.5 A, ULN2003 relays, paired-injector text, SMCJ40A); INSTALL.md "six M4 holes" is wrong for 1996-97 and 1999-2000 (4 holes in the PCB); firmware/README says IAT curve is "as set by JP1" (jumper removed in mb rev 0.12/0.8); stock quantities quoted for the clamp TVS are out of date (2,709 quoted, 1,699 today).
7. Nothing found in the car-damaging instruction set (TPS links, JP2 SEQ warning, R27/R28, alternator pull-up, boost valve wiring) that contradicts the design files. The F/P-to-2T fuel pump wiring advice and the "bridge F/P to GND" test advice come from third-party guides and cannot be verified from the repo (UNVERIFIED).

## Verdict tables

### README.md (top level)
| Statement | Verdict | Evidence |
|---|---|---|
| 4 injector outputs, 4 ignition outputs, two on harness two on AUX | CORRECT | J1.14-17 OUT_IGN1-4; J5 pins 1,2 IGN3/4 |
| Board revs: db 0.10, mb 0.13 / 0.9 / 0.9 / 0.9 | CORRECT | fab file names, schematic titles |
| Harness headers: 174917-6 48 pins; 178780-1 76; 353830-5 72 | CORRECT | footprint pad counts 48/76/72 |
| 1999-2000 board "64-position 176122-6, same housings" | CORRECT (board carries the 76-pad footprint, 12 bay pads unconnected) | pin_tables.py output |
| MAP 15-700 kPa MPX5700AP | CORRECT | parts_manifest C90152 |
| J5 12 V pin fused 1.1 A | CORRECT | F4 BSMD1812-110-33V 1.1 A hold |
| By-year table (sequential 1994+, pairs 1989-93, VVT 2001-05, heater driven 1996-2000, main relay 2003-05) | CORRECT against harness tables (1U/3M OUT_VVT = front O2 heater on 9900/9697; 2001-05 OUT_VVT = VVT 4R; 3H main relay) |
| 1989-93 "two jumpers for one wire per injector" | CORRECT | JP1/JP2 SEQ |
| Clamp TVS "2,709 at JLCPCB on 2026-11-15" | STALE | lcsc.py today: C1973780 stock 1699 (2026-11-16); C135134 2713, C310102 7285 (doc: 2,862 / 7,830) |
| Status block: "rev 0.5 / 0.6 ..." history, "4 failures left" etc. | HISTORIC log, fine, but top-level reader sees rev 0.7-0.9 numbers beside current ones |
| "The stock case has to be cut for ... " | consistent with J2 centre 24.5 mm, J4 80 mm | pads |
| 1996-2005 "1990-95 outline and mounting holes" | PARTLY WRONG: 1996-97 and 1999-2000 PCBs have only 4 holes (H3-H6; H1/H2 absent); 2001-05 has 6 | pcb_footprints.csv |

### INSTALL.md
| Statement | Verdict |
|---|---|
| J5 pin 1 at right, odd pins nearer daughterboard; J2 pin 1 at left, odd away from edge | CORRECT (pad coords) |
| J5 pin table; flex/nitrous need rev 0.10 | CORRECT |
| Openings: J2 centre 24.5 mm, USB-C 80 mm, board width 154 | CORRECT (J2 pads 21.5..27.5; J4 at 80.0) all four years |
| "header is 33 mm in from the bottom edge" | CORRECT to within 1.5 mm (J5 rows at 33.2 and 30.7 mm from bottom edge; centre 32) |
| MAP barb "points toward the middle" | CORRECT per footprint/picture (UNVERIFIED against a real part, already documented) |
| "Screw the board down through its six M4 holes" | WRONG for 1996-97 and 1999-2000 (four holes) |
| 1990-93 fuel pump: no wire in 2T, add wire from diagnosis box F/P to 2T; F/P-GND bridge runs pump | UNVERIFIABLE here (source ME221 guide, Speeduino manual). Design side OK: 2T = OUT_FP. |
| JP table (JP1/2 no shunt on 89-93, SEQ 94-95, JP3, JP4, JP5, JP6) | CORRECT |
| Never JP2 SEQ on 89-93 automatic (2Z = A/T control unit) | consistent with README 2Z note; external fact UNVERIFIED |
| TPS: fit R28 and move R29 to R30 | CORRECT per netlist (R28 1N<->V5_EXT, R29 2L<->AUX1, R30 2L<->IN_TPS); R27 pull-up option correct |
| Boost valve between pin 15 and pin 3, D5 freewheel | CORRECT (D5 pad1 AUX_VBAT cathode, pad2 OUT_BOOST) |
| Flex: signal pin 12, +12 V pin 15, ground 16 | CORRECT |
| "Knock sensor (1990-97, which have none)" | consistent with README; external fact UNVERIFIED |
| Wideband J2 colours/pins | pin functions match LSU_RT/HTR_N/VM/IP/UN/HTR_PWR on pads 1,2,3,5,6,8; colours are from AEM doc, UNVERIFIED, already flagged by the repo |
| "heater + 12 V through the board's 3 A fuse" | CORRECT (F1 2920 3 A) |
| COP mapping (cyl 2 on pin 1, cyl 4 on pin 2) | CORRECT, see summary 4 |

### daughterboard/README.md
| Statement | Verdict |
|---|---|
| 8x VND7NV04, 7x ZXMS6004FF relay/lamp/tach/spare, plus one ZXMS6004FF per ignition channel | CORRECT (Q1-Q8; Q9-Q19 = 11) |
| 4 injector clamps ES1D D42-45 + 1.5SMC16A D46-49 | CORRECT |
| F1 1.1 A, L1 2.2 uH, LMR14020, 2 x TLS115, LDL1117, TL431+BCP53, TC4427 x2, LMV321, LM2903, TCAN1042V x2, MCP6004, AD8628, REF3033, VND14NV04, STM32F103C8 | CORRECT (sch_bom_grouped.csv) |
| 220 ohm in series on drivers | CORRECT in rev 0.10 (R152-R159) |
| analog divider 5.6k/10k = 1.56; battery (33k+6.8k)/6.8k = 5.85 | CORRECT arithmetic and BOM |
| MCU pins (PA3 knock, CAN2 PB12/13, PC6/PC7 = J2-24/25, SPI2, VR PE13/PE12) | CORRECT vs design.py comments / miata_pins.h / J2 table (full MCU-pin-to-pad netlist check not redone) |
| TVS C1973780 stock "2,709" | STALE (1,699 on 2026-11-16) |
| "Tag-Connect TC2030 SWD pads" in MCU row | the BOM has both J3 (SWD) and J102 (SWD WBO); doc names only J102 elsewhere: minor |

### motherboards/*/README.md
| Statement | Verdict |
|---|---|
| Hole tables | 1989-95: CORRECT (6 holes). 2001-05: CORRECT (6). 1996-97, 1999-2000: CORRECT (4) |
| 1A coordinates (39.70,18.13) / (16.00,18.13) | CORRECT; 2001-05 "1A (40.95,16.60)" is actually pad 2A (that header has no plug 1) |
| Harness tables, NC lists | CORRECT (pin_tables.py) |
| J5 tables | CORRECT, 20/20 on four boards |
| JP tables, TPS text, R27-R30 | CORRECT |
| Rev history lines mentioning "J3", "JP1 IAT jumper", "SMCJ40A", "0.5 A" | historic, labelled by revision; OK |
| 1989-95 "D3/D4 ... not fitted with a rev 0.10 daughterboard" | footprints are present in pcb_footprints (not DNP-flagged); depends on fab BOM; not checked |

### firmware/README.md
| Statement | Verdict |
|---|---|
| Pin map table (J1/J2 pin numbers) | CORRECT vs interconnect.md |
| "stock or the M12 sensor, as set by JP1" (CLT/IAT paragraph) | STALE: no IAT jumper since mb rev 0.12/0.8; miata_pins.h:90 comment "JP1 on the motherboard picks stock or M12 sensor" likewise |
| ignition pins 1/3/2/4 | CORRECT |
| NB alternator step 7 (1O 1999-2000, 3M 2001-05 = OUT_ALT) | CORRECT per harness tables; pull-up recipe (1k + 1N4148 from J5-14 anode to J5-4) is electrically sound, but J5-4 is the same net as the 94-95 JP4 solenoid output only on 1989-95 (not relevant for NB) |
| VVT/idle/purge claims | consistent |

### additional-parts and website
| Item | Verdict |
|---|---|
| order_all_boards.csv quantities | CORRECT (see summary 5) |
| shopping_list.html vs CSV | MINOR MISMATCHES: header 1x40 male is "Sullins PRPC040SAAN-RC" in the HTML but ZHOURI C2977586 in the CSV; MAP nut "nylon-insert locknut" vs "M3 hex nut"; 4.7k resistors 3 per motherboard (HTML) vs 13 total including R27 (CSV) |
| products.csv/json: connectors 48/76/64/72-pin, "8 low-side drivers, 7 protected relay and lamp outputs, 4 ignition", 700 kPa MAP | CORRECT vs design (64-pin for 1999-2000 is the car's own; the board takes the 76-position header) |
| products text "manual and manual-swapped" | consistent with "automatics untested" |

### VERIFICATION.md: superseded hardware presented in current-looking tables
- Lines 1132-1139 "Fuses on the boards": F1 0.5 A (now 1.1 A), motherboard F1 "2 A" (now 3 A), F4 0.5 A (now 1.1 A).
- Line 1150 "Relays about 0.18 A each through the ULN2003"; lines 1160 (ULN2003 note OK as history) and 1109 (struck through, OK).
- Lines 1190-1205 "1989-93 paired injectors ... Rev 0.6 halves the current per driver ... removes the risk ... SMCJ40A ... 47 V TVS": superseded twice (rev 0.8 SMCJ30A, 2026-11-15 one-driver-per-wire). Reader will take "risk removed" as current; current README says this is the hottest case.
- Lines 208-217, 267-275 (rev 0.5/0.5b tables: ULN2003, NCV8406, 0.5 A PTC, SMCJ40A): these sit under dated rev headings, acceptable as history but not flagged as superseded.
- Line 568 table says D3/D4 SMCJ30A on "copper islands"; the 1989-95 motherboard no longer needs them with a rev 0.10 daughterboard.
- Summary (line 21+) still lists "five motherboards".

## Sources actually read
the review brief; repo/README.md, INSTALL.md, motherboards/1989-95/README.md (full), 1996-97, 1999-2000, 2001-05 READMEs (non-table parts and selected rows), daughterboard/README.md (Files to Before ordering), firmware/README.md (lines 95-252), additional-parts/order_all_boards.csv and shopping_list.html data rows, website/README.md and products.csv, VERIFICATION.md (grep + safety section); evidence/cur_*/pcb_pads.csv, pcb_footprints.csv, sch_bom_grouped.csv; kb/interconnect.md J1/J2 table; firmware/board/miata_pins.h, miata_board.cpp:70-80; rusEFI spark_logic.cpp:95-160; images/header_pinouts.png, annotated_motherboard_1989-95.jpg; live lcsc.py lookups C1973780, C135134, C310102, C1982018.

## Not checked
- annotated_1996-97 / 1999-2000 / 2001-05 and the three assembled annotated images, assembly_*.jpg (not viewed).
- products.json vs products.csv equality; make_products.py.
- Full MCU-pin-to-J1/J2-pad netlist check for every pin named in docs (spot checks only).
- External facts (Mazda cavity functions, F/P diagnosis-box procedure, AEM wire colours, Kia TPS pinout): no primary source in repo.
- Rest of firmware/README (lines 1-94, 253+), INSTALL "Sources" links, BOM DNP state of D3/D4.
