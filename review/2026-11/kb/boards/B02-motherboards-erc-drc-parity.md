# B02 - Motherboards: KiCad 9 DRC / ERC / schematic-parity triage

Status: COMPLETE (2026-11-16). Scripts and outputs in work/B02-motherboards-erc-drc-parity/ (partition.py -> partition_out.txt, summ_drc.py, summ_erc.py, geom.py -> geom_all.txt, viapad.py).

## Summary
1. VERIFIED: schematic-vs-PCB net partitions are IDENTICAL on all 9 boards (4 current + 5 ordered): 0 groups only in schematic, 0 only on PCB, 0 renamed-identical nets, 0 value/footprint differences, pcb_nets.txt == pcb_pads.csv. No real connectivity difference exists. All KiCad parity "issues" (37/67/52/60 current) are artefacts.
2. Parity artefacts: (a) 8 USB-C J4 pins (TX/RX pairs A2/A3/A10/A11/B2/B3/B10/B11) exist in the symbol, not in the 16-pin GCT USB4105 footprint (USB2-only part, correct); (b) "pad N is net unconnected-(...)" = deliberately unconnected pads (J1 harness, J2 pins 4/7, J4 SBU, U2 NC pins 4-6); (c) 'Exclude from BOM' flag mismatch on 8-10 footprints.
3. DRC: only 5 types fire in KiCad 9 (lib_footprint_issues, silk_over_copper, silk_overlap, silk_edge_clearance, starved_thermal); 0 copper clearance / edge / hole / short / unconnected violations on any board. lib_footprint_issues = KiCad 9 has no library table in the run (artefact). silk_* = cosmetic.
4. Only DRC "errors" = starved_thermal (GND pads of JD1/J5/JD2 with 1 spoke into a small zone island). Not a connectivity fault (unconnected_items = 0, islands carry stitching vias); only a soldering-heat/mechanical-strength nuance. See table.
5. ERC: footprint_link_issues + lib_symbol_issues = missing library artefacts; power_pin_not_driven (U2 MPX5700AP VS and GND, no PWR_FLAG) = artefact; global_label_dangling VIGN_IN on 96-97/99-00 = intentional (see 6).
6. Harness pads: unconnected-pad sets on the PCB equal the README "Not connected:" lists exactly on all four current boards (12/44/29+12 bay/35). 1999-2000 additionally has 12 bay pads XA-XL (header positions with no harness plug; README line 48; no schematic pin). VIGN_IN (JD1.3) is floating on 1996-97 and 1999-2000 (current and ordered): intentional, VERIFICATION.md l.139-153 (ignition sense only on 2003-05).
7. Geometry (pcbnew): copper/holes >= 0.5 mm from board edge everywhere (min: mounting pads H3-H6 0.5 mm, via 0.9 mm); harness pad rings 0.35 mm (1.8/1.1) or 0.203 mm (1.51/1.1 on 1989-95 family incl. ordered 8993/9495); no hole-to-hole problem except USB-C footprint-inherent spacings (0.30-0.34 mm).
8. Nothing found that blocks ordering or needs rework of the ordered boards from this scope; findings below are low/info.

## Detail

### DRC violation types (counts per board: cur 8995/9697/9900/0105 | ord 8993/9495/9697/9900/0105)
| type | sev | counts | verdict |
|---|---|---|---|
| lib_footprint_issues | warn | 39/25/26/28 \| 35/25/24/25/27 | artefact: KiCad 9 run lacks fp-lib-table (ecu_mb, Resistor_SMD...). Footprints are embedded in the PCB; parity shows 0 footprint differences |
| silk_over_copper | warn | 49/1/1/3 \| 49/49/1/1/3 | 8995-family (8993, 9495, 8995): 48 J1 pad numbers/outline touch pad mask openings (pin labels 1A..2U sit right at pad rings, see work/.../j1_8995.png); JLC clips silk on pads automatically. Cosmetic; labels remain legible but crowded (e.g. 1T/1V) |
| silk_overlap | warn | 5/10/10/8 \| 5/5/10/11/8 | ref designators R20-R22, R6/R1, HD1/HD2 over a silk line, J1 pin text on J1 outline: cosmetic |
| silk_edge_clearance | warn | 4/6/6/4 \| 2/2/4/2/2 | J1/J2 outline silk crosses board edge: cosmetic |
| starved_thermal | ERROR | 2/1/3/14 \| 4/2/4/4/4 | GND thermal reliefs of JD1/JD2/J5 pads: 1 spoke to a small island (zone min spokes 2). Real but benign: DRC shows 0 unconnected items, every island has vias/pads (island mode "remove all islands without connection"). Effect: weaker pad-to-plane tie, easier hand solder; worst cur_mb0105 (14 pins: JD1 20,21,23,24,26,27,29,30; JD2 2; J5 16,18) |
Repo's own KiCad 7 run (fab_drc_report.txt) additionally lists 4x hole_clearance (J4 NPTH 0.65 mm hole to A1/B12 GND pad 0.194 mm vs project rule 0.25) on every board; KiCad 9 here did not report it. It is the GCT USB4105 land pattern (hole centre (177.11,204.995) to pad edge) VERIFIED by geometry; fab acceptance of 0.19 mm NPTH-to-copper UNVERIFIED (JLC rule from memory ~0.2 mm).

### Parity (partition.py)
All 9 boards: schematic groups == PCB groups (87/110/96/103 current; 84/80/110/96/103 ordered). Single-pin named net VIGN_IN (JD1.3) on 9697, 9900 (current + ordered) = floating by design. Net count differences schematic 263/257/247/261 pins vs PCB 255/249/251/253 numbered pads: the 8 J4 pins; 9900 PCB has +12 bay pads.

### ERC (114/84/85/93; ord 106/84/80/81/89)
footprint_link_issues 25-38 and lib_symbol_issues 53-74: library-table artefact. power_pin_not_driven x2 (U2 pins 2 GND, 3 VS): no PWR_FLAG on the MAP supply, artefact. global_label_dangling: VIGN_IN (9697/9900 only). No pin_to_pin, no unconnected-wire, no off-grid errors. Net ERC conclusion: nothing real.

### Zones / islands
GND zones both layers on all boards; main pour 19-20k mm2, plus 2-29 islands (smallest 0.37 mm2, largest ~130 mm2) each tied by 0.6/0.3 stitching vias (1093 vias on 0105). 1989-93/95 boards also have OUT_INJ1/2 copper zones (47-121 mm2). No orphan copper left (mode "always remove").

### Holes / edge / annular rings (geom.py)
Outline bbox 154.1 x 161.6 mm (x 99.95-254.05, y 49.95-211.55) all boards. Holes: H1-H6 4.5 mm PTH, 7.0 pad (ring 1.25), HD1-4 3.2 NPTH, J1 PTH 1.1 mm, pad 1.8 (ring 0.35) or 1.51 (ring 0.203; 1989-95 / ord 8993, 9495), J1 NPTH 3.5, J2 0.75/1.2, J5/JD1/JD2 1.0/1.7, U2 0.81/1.52 and 3.3/4.0, vias 0.3/0.6 (ring 0.15). Min wall-to-edge 1.05 mm (via), copper-to-edge 0.5 mm (H3-H6 pads at x=104/250: board edge 100/254). Hole-to-hole <0.5 mm: J4 shield slot vs GND via 0.304; J4 NPTH vs shield slot 0.34 (footprint inherent); ord_mb9900 only: two same-net VBAT_IN vias at (127.5,92.805)/(128.099,92.805) 0.299 mm wall-to-wall (same net, harmless). JLC numeric limits are from memory (UNVERIFIED): PTH ring 0.15, hole spacing ~0.5 (diff net).
Vias inside SMD pads (unfilled/untented status not checked): 12-19 per board (C1-C3, D1-D5, F1-F4, R2/R3, U4, J4 A12/B1 GND). Via-in-pad solder wicking is a minor reflow-yield risk for 0603/SOD pads.

### Harness pads
See summary item 6. J1 pad counts 48/76/76/72. Connected pads equal README table pins.

## Sources actually read
evidence/{cur,ord}_mb*/drc_kicad9.json, erc_kicad9.json, sch_netlist.xml, pcb_nets.txt, pcb_pads.csv, fab_drc_report.txt, INDEX.txt, layers/top_all.png (8995 crop); repo/motherboards/*/README.md ("Not connected" lines, pin tables), VERIFICATION.md l.139-153, kicad_pcb files via pcbnew (geom.py, viapad.py), repo .kicad_pro rule values.

## Not checked
JLC capability numbers (not fetched, from memory); whether vias are tented/filled in the gerbers; gerber-level silk-over-pad rendering; whether J1 harness header pin cross-section fits the 1.1 mm drill (no pin drawing read).
