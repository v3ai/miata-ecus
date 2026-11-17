# B05 - Fabrication and assembly outputs of the motherboards (gerbers, drills, BOM, CPL, hand-fit parts)

Status: COMPLETE (2026-11-16). Scratch: work/B05-fab-outputs-motherboards/ (drill_summary.py, gerber_bbox.py, pads_by_drill.py, zipcmp.py, jlc_price.html, jlc_cap.html).

## Summary (10 lines)
1. Gerber sets of all 4 current and 5 ordered motherboards are complete for a 2-layer board: 14 files (F/B Cu, F/B Mask, F/B Paste, F/B Silk, Edge, PTH, NPTH, 2 drill maps, job). Edge outline closed (12 lines + 12 arcs), 154.1 x 161.6 mm, 1.6 mm. The zips in repo/ are byte-identical to the evidence-pack gerbers (VERIFIED).
2. JLC BOM == CPL == PCB SMD footprints on every board (17/15/16/18 designators, 14/13/14/14 BOM lines); every SMD that is not in the BOM is a deliberate not-fitted option (R20-22, R27/28/30, R37, D3/D4). No DNP flags are used; "not fitted" is done by leaving parts out of the BOM (works, but the PCB still carries them).
3. Slots / holes: USB-C shell tabs are 4 plated G85 slots (0.6 x 1.4 and 0.6 x 1.7 mm), JLC 2-layer minimum plated slot is 0.5 mm with length >= 2 x width (jlcpcb.com/capabilities/Capabilities, fetched today): OK. M4 case holes are 4.5 mm PLATED (7 mm pad, net GND), M3 standoff holes 3.2 NPTH, connector pegs 3.5 / 1.65 / 0.65 NPTH. Fine.
4. USB-C CPL pad-centre offset verified geometrically (pad field centre y = 206.46 = origin 207.6 - 1.14). Rotations: chip parts/diodes/fuses as KiCad, U4 (SOT-23-6) +180 "assumed" (repo's own comment). A wrong U4 would swap VBUS and GND pins, so it deserves a look in JLC's preview.
5. Silkscreen: harness cavity labels, jumper names, wideband colour key are present; J5 (2x10 add-on header) has NO pin labels on any board, and the not-fitted options carry only reference designators.
6. Supply: F2/F3 fuse C46641168 has only 57 in stock at JLC (live), MAP sensor C90152 is $29.12 each (stock 155), socket C124412 stock 65. J2 JST header has an LCSC number (C412098, 10 k stock) that the BOM does not use.
7. Cost: JLC fixed fees per order about $22 (+$3.07 per extended line) and about $1.3 per board variable; at 25+ boards the assembly adds under $2.5 per board. All-basic substitution would save only $12-15 per order; moving parts to the daughterboard cannot remove the USB-C. Hand assembly beats JLC only below about 5 boards.

## 1. Gerber / drill completeness (VERIFIED, gerber_bbox.py, drill_summary.py)
| Item | Result |
|---|---|
| Files | 14 per zip, all boards; layers F_Cu/B_Cu, Mask, Paste (B_Paste empty, as expected), Silk, Edge_Cuts, PTH, NPTH, drl maps, gbrjob. KiCad 7.0.11 export with --subtract-soldermask --no-x2 (scripts/mb_export.py:18) |
| gbrjob | LayerNumber 2, 1.6 mm, Finish "None" (order-form choice, not in the file) |
| Outline | 99.95..254.05 x 49.95..211.55 mm; 12 lines + 12 arcs; M4 corner notches; same on all boards. 1996-2005 outline is a documented placeholder |
| Copper bbox | 100.4..253.6, so 0.45 mm inside the edge copper-to-edge on the pour (JLC min 0.3) |
| PTH | 0.3 vias (1179 on 8995, 1093-1136 others); component drills 0.6 slots, 0.75 (J2), 0.8128 (U2), 1.0 (headers/sockets/J5), 1.1 (J1), 3.3 (U2 screws, plated), 4.5 (M4) |
| NPTH | 0.65 (J4 pegs), 1.65 (J2 pegs), 3.2 (HD1-4), 3.5 (J1 pegs, 3 on 8995, 4 on 96-00, 2 on 0105 count differs by outline) |
| Slots | 4 G85 plated slots 0.6 x 1.4/1.7 at J4 shell: width >= 0.5 mm, length >= 2 x width, hole-to-hole to the 0.65 NPTH >= 0.8 mm (JLC 0.45) |
| Silk in gerber | B_Silkscreen/F_Silkscreen contain 201/319 flash objects identical to the mask openings: checked, they are CLEAR-polarity (%LPC) cuts from --subtract-soldermask, not printed discs. Harmless |
| Mask/paste | Paste flashes only on SMD pads (74 on 8995); no paste on THT; mask openings per pad |
| DRC (fab_drc_report) | 115 violations on 8995, mostly silk warnings. Only "errors": 4 x hole_clearance 0.194 mm < 0.25 mm between J4 NPTH pegs and GND pads A1/B12/A12/B1 (GCT footprint geometry; ordered boards identical) |

## 2. BOM vs CPL vs PCB (VERIFIED, script over pcb_footprints.csv / fab_*)
| Board | BOM lines | designators | extended lines | notes |
|---|---|---|---|---|
| cur_mb8995 | 14 | 17 (C1-3, R1-3, R6, R29, R35, R36, D1, D2, D5, F1, F4, J4, U4) | F1, F4, J4, U4 = 4 | R29 0805 0R (C17477, basic) fitted as the default link |
| cur_mb9697 | 13 | 15 | 4 | |
| cur_mb9900 | 14 | 16 | 5 (adds F2) | |
| cur_mb0105 | 14 | 18 | 5 (F2 + F3 share one line) | |
BOM == CPL == PCB-SMD-minus-options on all four, and on the five ordered boards. CPL equals PCB position and rotation except: J4 Y (pad-centre offset, below) and U4 rotation +180. Ordered boards: BOM has D3/D4 SMCJ30A (C224048) fitted on 1989-93 and F4 = 0.5 A 1206 (C70077); all consistent.

### JLC placement checks
- J4 USB-C: PCB origin (180, 207.6); CPL Mid Y -206.46. Pad extents (SMD row y=203.92 pad half-length 0.575; shell slots to y=208.675 + 0.9) give a centre of 206.46 mm = origin - 1.14 (matches scripts/order_bom.py JLC_OFFSET). Mating face toward the board edge (y = 211.5) as intended. Whether JLC's own model centre equals the pad centre is the repo's observation from the rev 0.9 preview; not re-verifiable here (UNVERIFIED).
- U4 USBLC6-2SC6: footprint rot 0, CPL 180 (order_bom.py JLC_ROT rule "^T?SOT-23" +180, comment "SOT-23-6 assumed the same"). Pinout from the netlist: pin 5 = USB_VBUS, pins 1/6 = DP, 3/4 = DM, so a 180 degree error exchanges pin 5 (VBUS) with pin 2 (GND). The +180 rule was seen for SOT-23 and SOT-23-5 on the daughterboard, so probably right; still the one SMD where an error is destructive for the USB port.
- D1/D2/D5 SS34 (SMA): no offset (repo saw this in the preview on the rev 0.5 daughterboard); D1/D2 at rot 90, D5 at 0. Polarity is the risk; check cathode band against JLC preview for D5 (rot 0) and D1/D2 (rot 90).
- F1 2920, F4/F2/F3 1812: PTC fuses are non-polar; rotation irrelevant. R29 rot -90 = 270 in CPL, resistors non-polar.

## 3. Silkscreen (VERIFIED from kicad_pcb gr_text list and F_Silk_Fab / top_all render)
- 1989-95: cavity labels 1A..2Z at the harness pins, jumper names FAN2 (90-93 / 94-95), TACH COP, 94-95 2R, INJ3/INJ4 (PAIR/SEQ), 2O (AFM/BOOST), J2 colour key "1 GRN 3 ORG 5 RED 7 -- / 2 WHT 4 -- 6 BLK 8 BRN", DAUGHTERBOARD outline, title + rev.
- No text for: J5 pins (20-pin add-on header: COP, boost, alternator, knock, CAN, 5 V, 12 V ... only in README), J4 USB, MAP orientation (silk says "MPX5700AP marking up" - good), R20-R22/R27/R28/R30/R37/D3/D4 (reference only; the repo gives their function only in README), JP4/JP5 have a name but not "fit / open" meaning. 1996-2005 boards: only J2 key, title and DAUGHTERBOARD.
- Legibility: JLC minimum 0.15 mm line / 1.0 mm text enforced by scripts/silk_jlc.py. In the render "94-95" beside FAN2 pin 3 is crossed by the trace/pour clearance but readable; "AFM", "BOOST" and "PAIR/SEQ" labels sit on the pour with mask opening cuts, 4 silk-edge-clearance warnings (the DAUGHTERBOARD outline crossing the board edge, cosmetic).

## 4. Hand-fit parts per year (seller must solder)
Derived from pcb_footprints.csv (THT/other) and the repo's self-order BOM / README tables. Common to all: JD1, JD2 (1x40 sockets C124412), U2 MAP (C90152, leads bent, 2 x M3x10 + nuts), J2 (JST S08B-PUDSS-1), J5 (2x10 box header 302-S201), J1 harness header, 4 x M3 standoffs + 8 x M3x6 screws, daughterboard J1/J2 1x40 pins (soldered while plugged into the sockets).
| Board | J1 | Jumpers (headers C49257 1x3 / 1x2) | Optional SMD / THT parts (not fitted by default) | Approx. THT joints |
|---|---|---|---|---|
| 1989-95 | TE 174917-6 (48 pins, not orderable) | JP1, JP2, JP3, JP6 (1x3), JP4, JP5 (1x2) | R20-22, R27 (0603 4.7k), R28, R30 (0805 0R), R37 (2512 1k), D3, D4 (SMCJ30A) | 80 + 48 + 8 + 20 + 6 + 16 + 2 pegs ~ 180 |
| 1996-97 | TE 178780-1 (76 pins) | none | R20-22 | 80 + 76 + 8 + 20 + 6 ~ 190 |
| 1999-2000 | TE 178780-1 | none | R20-22 | ~190 |
| 2001-05 | TE 353830-5 | none | R20-22 | ~ 190 |
Defaults and safety if left unpopulated:
- Shunts: JP3 (FAN2: 90-93 on 1989-93, 94-95 on 1994-95) and JP6 (AFM) must carry a shunt for stock behaviour; JP4 only on 1994-95; JP1/JP2 stay OPEN on 1989-93 (one driver per wire; SEQ on 1994-95; NEVER JP2 SEQ on a 1989-93 automatic); JP5 stays OPEN. Open = unconnected, so electrically safe, but with JP3 open the second fan relay (A/C or condenser fan) is never driven (functional / overheating risk, not a hardware risk). So the real shunt count is 2 (1989-93: JP3, JP6) or 4-5 (1994-95: JP1, JP2, JP3, JP4, JP6), while the BOM lists 6 per board.
- R20-R22: unpopulated = no 12 V pull-up on VSS / A/C / clutch inputs: safe for the board; whether the car's signals need them is car-dependent and nothing in the repo tells the seller per year (README: "fit only if the signal switches to ground"). Fitting on a switch that drives 12 V makes the input stay on.
- R27: unpopulated safe; R28/R30: unpopulated = stock switch case (R29 fitted by JLC), TPS conversion needs the hand move R29 -> R30 plus R28 (0805 by hand). R37/JP5: only for coil-on-plug. D3/D4: needed only with rev 0.9 daughterboard + PAIR on 1989-93 (SMD DO-214AB hand soldering).
- Every optional SMD is hand-solderable (0603/0805/2512/SMC) but is on the PCB as bare pads; none is marked on silk.

## 5. additional-parts/order_all_boards.csv vs boards (VERIFIED by count)
Order is 4 daughterboards + 1 of each motherboard. Quantities check out: sockets 8 (2 per MB), 1x40 headers 8, MAP 4, JST 4, box headers 4, M3x6 32 (8 per assembly), M3x10 8, nuts 8, standoffs 16, 1x3 headers 4 (JP1/2/3/6), 1x2 headers 2, 4.7k 13 (3 x R20-22 on 4 boards + R27), 0R 0805 2, R37 1, SMCJ30A 2, harness headers 1 + 2 (178780-1 for 96-97 AND 99-00) + 1. Notes: shunts 6 (see above); LCSC codes C124412/C49257/C5305/C2977586/C90152/C224048 all resolve (live). JST header, box header, 1x2 header and R37 have Digi-Key links only; LCSC alternatives exist (C412098 JST S08B-PUDSS-1(LF)(SN) $0.36, stock 10084; C3405 2x10 IDC box header $0.15 stock 42623; C54315 1k 2512 1% $0.03; C32713268 1x2 header $0.016) so a single LCSC cart could cover all but the harness header, TPS and hardware.

## 6. JLC assembly cost (fees from jlcpcb.com/help/article/pcb-assembly-price, fetched today; part prices from live lookups)
Economic PCBA, one design per order: setup $8.18 + stencil $1.53 + confirm placement $0.45 + feeder loading $3.07 per EXTENDED part ( x4 = $12.28; x5 = $15.35 on 1999-2000 / 2001-05) + hand-soldering labor $3.58 per order (applies if the J4 shell pegs are counted as manual joints, then $0.0164 each) = about $22.4 (without the $3.58) to $26 (with). Variable: SMT joints 52 x $0.0016 = $0.08, J4 shell 4 x $0.0164 = $0.07; parts at 50-pc prices: J4 $0.73, U4 $0.12, F1 $0.116, F4 $0.057, 3 x SS34 $0.105, 0603s/0805 about $0.04 = about $1.2. Per board therefore about $1.3 plus fixed.
| Boards per order | fixed/board | total/board (JLC assembly + SMD parts) |
|---|---|---|
| 4 | $5.6-6.5 | $6.9-7.8 |
| 10 | $2.2-2.6 | $3.5-3.9 |
| 25 | $0.9-1.0 | $2.2-2.3 |
| 50 | $0.45-0.5 | $1.7-1.8 |
| 100 | $0.22-0.26 | $1.5 |
(No large-size surcharge: 154 x 162 = 249 cm2 < 650 cm2.) Alternatives:
- All-basic substitution: extended lines are fuses (F1 3A 2920, F4/F2 1812), USB-C, USBLC6. I found no basic-library equivalent for any of them (JLC basic list has no PTC fuse or ESD array that I verified; UNVERIFIED for USB-C). Even if all 4-5 could be swapped, saving = $12-15 per order = $0.12 (100 pcs) to $0.5 (25 pcs) per board. Not worth board changes.
- Hand assembly of the 17 SMD parts: about 52 joints incl. a 16-pad 0.5 mm-pitch USB-C and a SOT-23-6; at roughly 10-15 min of seller time it only wins for a batch of about 4-5 boards, loses beyond (INFERRED; labour rate assumed $25/h).
- Moving SMD parts to the daughterboard: not possible for J4 + R2/R3/U4 (USB-C must sit on the case edge side, the MB carries it), so the MB would still need PCBA; only F4/D5/D1/D2/F1 etc. could move (the DB already uses C8678 SS34 and C883150 on its own BOM, so no feeder fee is saved on the DB side), saving at most 2 extended fees ($6) per MB order. Not worth it.
- Doing the THT at JLC (Standard PCBA): setup $25.56 + stencil $8.21 + fixtures $16.42 + $1.53 per part line + manual joints $0.0164 x ~185 = $3.0 per board; about $4.5 per board at 50 pcs vs seller labour of ~20 min. Only possible for catalogue parts (harness headers, TPS not), and U2 needs bending. A possible saving but needs a quote; UNVERIFIED.
Bottom line: JLC assembly is 0.3-1.7 % of the $399 price at 25+ boards; do not optimise it before the real cost items (MAP sensor $27-29, daughterboard).

## 7. Ordered boards quick pass
- Same fab structure; ordered 1989-93/1994-95 carry J3 (IAT) and JP1, J5 2x8, 1.02 mm J1 drills, F4 0.5 A 1206; J4 CPL offset identical (-206.46). Ordered 1999-2000 uses TE 176122-6. D3/D4 SMCJ30A are fitted by JLC on 1989-93 (in BOM).
- Same 4 hole_clearance DRC errors at J4 (0.194 mm). Nothing else wrong in fabrication found. Ordered 1999-2000 / 2001-05 use F2/F3 C46641168 (57 in stock now); already ordered so moot.
- Rework items for ordered boards: verify U4 and D1/D2 orientation in JLC's placement preview before production, set J4 offset per preview.

## Sources actually read
the review brief; evidence/cur_mb*/gerbers (all), ord_mb*/gerbers (drills), fab_* CSVs (all 4 current boards), pcb_footprints.csv, pcb_pads.csv, pcb_nets.txt, fab_drc_report.txt, pcb_stats.json, layers/top_all.png + crops; repo/scripts/order_bom.py (rotation / offset / HAND lists), mb_export.py, mb_release.sh; repo/motherboards/1989-95/README.md (jumper table, options), parts_list.csv; additional-parts/order_all_boards.csv; kb/parts_manifest.md; live JLC/LCSC lookups (tools/lcsc.py); jlcpcb.com/help/article/pcb-assembly-price and /capabilities/Capabilities (curl, today).

## Not checked
JLC's own placement preview (no account); JLC basic-library alternatives for USB-C/PTC (not searched exhaustively); mating-peg dimensions of the TE headers against the 3.5 mm NPTH (other audits); whether JLC Economic PCBA accepts J4 with THT shell tabs without Standard PCBA (repo itself says "check in JLC's quote"); LCSC stock of C124412 beyond JLC's number; exact THT joint counts per board (approximate); DB-side effects of unpopulated R20-R22 (VSS input bias).
