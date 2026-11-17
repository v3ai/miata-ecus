# P19c Harness header J1 TE 353830-5 (72 pos, 2001-05)

## Summary
- Footprint TE_353830-5_72P: all 72 pad positions, rows (0 / 3.6 / 8.0 mm), 2 pegs (3.5 mm, 5.45 mm beyond the outer row, y 7.5 and 64.3) match TE customer drawing C-353830 rev C2 (2017) PCB layout view EXACTLY. VERIFIED (drawing page image, dl/drawA.pdf from octopart sigma copy of TE drawing; also rev C1 2007 identical).
- Same pads vs Hellen NB2 footprint (hellen72_NB2.kicad_pcb P2, NB2:8-5353015-1): max deviation 1e-14 mm for all 72 pads after aligning 2A with Hellen pad 101 (/OUT_INJ1) at x 52.1. VERIFIED (work/.../cmp5.py).
- Pad NAMES: net function at each cavity on cur_mb0105 agrees with Hellen's net at the same physical position for every mapped signal (2A-2D,2G,2J inj, 2K AC, 2M FP, 2Q IAC, 2R MIL, 3A/3B/4A grd, 3F/3I IGT, 3M gen, 3O tach, 3T VSS, 3V cam, 3Y crank, 4D/4R OCV, 4F, 4I, 4L, 4M, 4N, 4P, 4V, 4AF) and with the 2005 Mazda FSM PCM terminal tables (fsm.txt lines 1148-1570). VERIFIED.
- Naming scheme: OEM plugs 2 (17), 3 (24), 4 (31), housings 353027/353029/353031 per TE drawing note 4; no plug 1. Within each plug, inner row = A, D, G.. (every third letter), middle B,E,H.., outer C,F,I..; letters skipped (2L,3G,3R,4G,4Q,4Y) have no cavity. 
- Ordered rev 0.7 vs current rev 0.9: J1 footprint and positions identical; only net rename 4N HARN_IAT -> IN_IAT.
- Differences found: drill 1.1 (TE 1.2 +-0.1, Hellen 1.2/1.6 pad) - low; README says "terminal 1A" (should be 2A) - doc.
- Sourcing: TE lists the part ACTIVE (datasheet 2-5353830 family, octopart "Production/Active"); stocked at DigiKey (123 pcs, ~$13.37), Newark, TME, RS, Powell, Master (octopart snapshot); JLC C5368971 extended, stock 0, $13.51@1 / $13.08@10-1000; LCSC stock 3 $13.40/$12.97. 1123038-2 = same housing, PRE-TIN contact finish, paper box (same drawing, same PCB layout). Ballenger sells "72 way ECU header" CONN-100752 $59.99 special order. Hellen uses the 122-pos TE 8-5353015-1 (superset).

## Pad table (J1, cur_mb0105; ord_mb0105 identical except 4N net name)
Positions rel. 2A (x,y): see repo/mb/ecu_mb.pretty/TE_353830-5_72P.kicad_mod; origin on board = (140.95,66.6) page coords = (40.95,16.60) board coords.
Net by pad: 2A INJ1,2B FAN,2C LS7,2D INJ2,2G INJ3,2J INJ4,2K AC,2M FP,2P IAC_12V,2Q IACV,2R CEL,3A/3B GND,3F IGN1,3H MAINRLY,3I IGN2,3M ALT,3O TACH,3T SW1,3V HALL2,3Y HALL1,4A GND,4O GND (analog sensor ground, FSM: sensor ground, VERIFIED GND on both boards),4AA AUX1 (FSM: HO2S rear),4AF VBAT_IN,4D OCV_12V,4F SW2,4I SW3,4L V5_EXT,4M KNOCK,4N IAT,4P CLT,4R VVT,4S VIGN_IN,4V TPS,4W AUX2 (FSM HO2S front),4X AUX3 (FSM MAF). Open: the list in README line 92 / 148 (4AG backup power left open - documented).
FSM check: 2P IAC +, 2Q IAC -, 3H main relay, 4D OCV +, 4R OCV -, 4AF power, 4AG back-up, 4L 5 V ref, 4S ignition sense all consistent.

## TE drawing data (VERIFIED, drawing C-353830)
72 x holes dia 1.2 +-0.1; pegs 2 x dia 3.5 +-0.1; pin 0.64 sq; PCB 1.6 recommended (TE datasheet); 12 VDC, -30..105 C; width 79.4; 16 max body beyond rows. Part table: 353830-5 contact finish selective tin both sides, 4 per box; 1123038-2 PRE-TIN x72, 3 per box; 353830-4/-7/-2/2-353830-1 have gold on power circuits.

## Not checked
Per-contact current rating; mating plug/terminal availability; case fit of the 7.4 mm body overhang above the top board edge (placeholder outline, documented); Mouser; real DigiKey tiers (page was read via a summarising tool, so prices are INFERRED/UNVERIFIED).

## Sources
dl/drawA.pdf, dl/drawB.pdf (octopart technical drawings), dl/353830-5-TE-Connectivity-datasheet-180073661.txt, dl/fsm.txt (mellens.net 2005 FSM), octopart page, DigiKey 353830-5 page, ext/hellen-miata-NB2/hellen72_NB2.kicad_pcb, evidence/*mb0105/pcb_pads.csv, pcb_nets.txt, repo/scripts/mk_hdr_fp.py, kb/interconnect.md, tools/lcsc.py C5368971.
