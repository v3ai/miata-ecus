# B08 - DFM, assembly, test access, mounting-hardware clearance

STATUS: complete (partial; see Not checked).

## Summary
1. Biggest finding (ORDERED 4-layer rev 0.9 daughterboard): 1423 vias, all 0.6 / 0.3 mm. About 620 of them have their centre inside an SMD pad: 373 in the 8 DPAK tab pads (Q1-Q8) and at least 245 in other pads (76 in 0402 passives, 57 in 0603 passives, 21 SOT-23, 14 SOD-323, SOIC, TSSOP, SMA/SMC, 1206 ...). The repo only mentions DPAK tabs and clamp TVS pads. JLC's filled and capped via-in-pad is the free DEFAULT only for 6+ layers; on 4 layers it is an optional extra. If the order did not select it, expect wicking, starved joints and tombstones across the board, not only at the DPAK tabs. VERIFIED geometry, INFERRED effect.
2. For the current 6-layer rev 0.10 the repo is right: JLC page says the fill is the default for 6+ layers (VERIFIED, capabilities page). Drill 0.3 is inside JLC's 0.15-0.55 mm range.
3. Courtyard overlaps (101 on cur_db, 91 on ord_db): the real minimum pad-to-pad gap over all overlapping pairs is 0.200 mm (four 0805 pairs R51-R59), then 0.219 mm (0402/0603 pairs). JLC's table needs 0.18 (0805-0805, 0603-0402) and 0.2 (chip-SOT). All pass. The overlaps are harmless. Checked, correct.
4. J1/J2 hand soldering: DPAK tabs are not a problem (nearest DPAK pad is 2.76 mm or more from a J1/J2 annulus). But J2 pins 3, 6, 7, 8 have only 0.18-0.22 mm between their 1.7 mm annulus and 0603 resistor pads (R138, R33, R36), and 15 of 80 pins are under 1 mm from an SMD pad. Soldering from the top, with the header body on the bottom, so the iron works among the 0603s.
5. No test points anywhere on the daughterboard (no TP footprints), no fiducials, no rails on any board. SWD for the F407 is a Tag-Connect TC2030 (J3) on top. The F103 wideband SWD (J102) is on the BOTTOM, so it is covered once the board is mated.
6. Mounting hardware: nothing can short. Daughterboard H1-H4 have only GND vias and GND pours under any standoff. Motherboard HD1-HD4 and H1-H6 carry only mask-covered tracks or GND, at 3.14 mm or more from hole centre. M4 case holes are plated GND pads, so they tie GND to the case.
7. Panel: JLC adds 5 mm rails and fiducials by default for standard assembly. Parts are at least 1.9 mm from the edge. The board qualifies for Economic PCBA (single-sided SMD, 2-6 layers), which needs neither.

## 1. Courtyard overlaps and spacing (cur_db: 101 pairs, ord_db: 91)
Method: pcbnew dump (work/B08.../geom/*.json), shapely, courtyard pairs on the same side with overlap area above 0.01 mm2, then the minimum pad-to-pad copper distance (`crt.py`, output `crt_cur_db.json`).
Worst 20 by pad gap (all top side, VERIFIED computed):

| Pair | Pad gap mm | JLC min mm (VERIFIED, jlc_min_spacing.txt) |
|---|---|---|
| R51/R52, R54/R53, R57/R56, R59/R58 (0805-0805, VR inputs) | 0.200 | 0.18 |
| R38/R37, R30/R29, R31/R32, R40/R39, R44/R43, R35/R34, R27/R28, R41/R42 (0402-0603) | 0.219 | 0.18 |
| C36/R27, C38/R31, C40/R37, C41/R39, C39/R34, R41/C42, R43/C43, C37/R29 (0402-0603) | 0.241 | 0.18 |
| R31/R33, R33/R34, R37/R36 (0603-0603) | 0.250 | 0.18 |
| R139/D36 (0603-SOT-23) | 0.269 | 0.20 |
| D32/R145 (SOD-123-1206) | 0.275 | 0.25 |

Counts: 0 pairs below 0.15 mm, 0 below 0.2 mm, 20 below 0.25 mm. JLC measures body to body (spacing_method.png shows body edges). For chips the pad extends beyond the body, so pad-to-pad is the conservative number. The repo's jlc_spacing.py could not be run (no shapely in system python); my own check agrees with the repo's statement "bodies clear, pad spacing meets table". Not covered by JLC's table: DPAK, SMA/SMC, SOT-223, microSD, tact switches (judged as SOT or SOP by the script; the overlap pairs involving them are all above 0.2 mm in my list).

Tombstoning (INFERRED, low confidence): 220 two-pad chips; on a crude metric (pad area plus same-net copper within 2 mm) 79 have a ratio above 5 and 33 above 10, typically a GND-pour pad against a thin-trace pad (C69, C114, C118, C72, R130, C60, R66, D1-D5 LEDs). This overstates the imbalance if the pours use thermal relief spokes (not measured per pad). The vias in pads (section 2) are the larger contributor. No courtyard-shadow problem found: the tall parts (D6 SMC, inductor L1, electrolytic-free) sit away from small parts; not rigorously checked (no 3D heights).

## 2. Vias in SMD pads, ordered rev 0.9 (4-layer) vs current (6-layer)
VERIFIED (geom dump of both boards, `vip.py`, `dpak.py`):
- ord_db: 1423 vias, all dia 0.6 / drill 0.3, tent flags True front and back. 373 vias centre inside a TO-252 pad (the tab pad of each of Q1-Q8 has 24-26 vias, plus the small lead pads); Q101 (LSU heater DPAK) has none. About 245 more in: 0402 R (33) and C (43), 0603 R (24) and C (33), 0805 C (9), SOIC-8 (12+3), TSSOP-24 (6), SOT-23 (21), SOT-23-5 (5), SOT-223 (7), SOD-323 (14), SOD-123 (5), SMA (5), 1206 C (6), LED 0603 (6), R-arrays (8), L1 1210, FB1, SW2.
- cur_db: same pattern (366 in DPAK, about 270 elsewhere).
- JLC capabilities page (VERIFIED, capabilities_pcb-capabilities.txt line 189): epoxy or copper filled and capped via-in-pad "is the default for 6-layer and above", compatible with 0.15-0.55 mm vias. The 2022 JLC blog says it is "readily affordable for four-layer boards", so on 4-layer it is a paid option. A tented via in a pad gets no plug: JLC "Plugged vias" cannot be used in pads or within 0.35 mm of a mask opening (pcb-via-covering).
- INFERRED: a 0.3 mm open hole in an SMD pad draws paste and solder down the barrel. With 0402 or 0603 pads this gives uneven wetting (tombstoning, starved joint, voids). With the DPAK tab it pulls solder away (the repo's own concern, daughterboard/README.md item 9, tab_copper.py header). The repo documents only DPAK and clamp-TVS pads and says nothing about the other ~245.
- Action for the ordered boards: check the order confirmation / JLC DFM sheet for "epoxy filled and capped" and whether all vias or only vias in pads are filled. If not filled, the first articles need X-ray or visual check of Q1-Q8 and hand rework of 0402 parts. Cannot be repaired after the fact.

## 3. Mounting hardware (script `holes.py`, `hd.py`, `m4.py`; R = 3.0 M3 pan head, 3.2 hex corner on 5.5 AF, 4.0 M4 pan)
| Board | Hole | Items within radius (centre-to-copper-edge) | Verdict |
|---|---|---|---|
| cur_db H1-H4 (3.2 NPTH, 4.5 mm from edges) | all | GND vias (2-4) and GND pours on F, In1-3, B; no pads, no signal tracks, no parts, no courtyard | Safe; GND under a metal standoff is harmless |
| cur_mb8995 / 9697 / 9900 / 0105 HD3 (3.2 NPTH) | M3 standoff | LSU_HTR_N 1.0 mm track on F and B, edge 3.14 mm from hole centre; GND via | Inside hex corner (3.17) by 0.03 mm, outside pan head (3.0). Mask-covered. Negligible |
| cur_mb8995 HD2 | M3 standoff | HARN_2O 0.2 mm track edge at 3.15 mm; GND via | Same, negligible |
| other HD1/HD2/HD4 on every board | | GND via only | Safe |
| M4 H1-H6 (PTH 4.5 drill, 7 mm GND pad) on cur_mb8995 | case screws | H3: OUT_ALT B.Cu edge 3.95 mm; H4: IN_AUX3 track edge 4.09 mm and via 3.89 mm | At the edge of an M4 pan head (radius about 4 mm; head size UNVERIFIED). Mask-covered. Low |
| H1/H2/H5/H6 | | nothing | Safe |
Daughterboard hole offsets relative to J1.1 (-8.5/107.5, 1.75/68.75) match the motherboard HD offsets relative to JD1.1 (VERIFIED, equal). Nothing is crushed on the mb: all THT parts sit at least 1.85 mm from SMD pads (MPX5700AP to C2) and nothing is near the standoffs apart from the tracks above.
Observation: M4 holes are plated, GND-connected, with exposed copper (mask opens for the PTH pad). Screwing into the case grounds the board GND to chassis at 6 points. Whether the stock ECU did the same was not checked (UNVERIFIED), and the 1996+ outlines are placeholders anyway.

## 4. Hand soldering (script `jdist.py`)
- J1/J2 headers are mounted on the bottom with their pins soldered from the top (order_bom.py: "Bottom side. Solder while plugged into a motherboard's sockets"). Pad annulus 1.7 mm, drill 1.0.
- J2 nearest SMD pads (annulus edge to pad edge): J2.8-R36 0.18 mm, J2.7-R33 0.20, J2.6-R33 0.21, J2.3-R138 0.22, J2.14/13/15-R64/R62 0.36-0.39, J2.19-22 to R56/58/53/51 0.53. 15 pins are under 1 mm, 31 under 1.5 mm of an SMD pad. J1 closest is R145/R146 at 1.17 mm. DPAK tabs: nearest is 2.76 mm (J2.40 to Q101), Q1-Q8 3.2-3.4 mm from J1 pins. So the DPAK tabs next to J1 are not an access problem.
- Motherboards: all SMD and THT on top, THT soldered from the bottom (nothing on the bottom): free access. DRC "starved_thermal" on GND PTH pads of JD1/JD2/J5/J1 (cur_mb0105: 14, mb8995: 2, 9697: 1, 9900: 3): these pins have fewer thermal spokes than the zone setting wants; helps hand soldering, costs some GND current path (the 2-layer pour still connects them).

## 5. Test access, programming
- No TP footprints on the daughterboard (misc.py). Rails are reachable only on component pads.
- J3 (TC2030-IDC-NL, top): +3V3, SWDIO, NRST, SWCLK, GND, pin 6 NC. Works for F407. J102 (TC2030, bottom): +3V3, WB_SWDIO, WB_NRST, WB_SWCLK, GND: covered by the motherboard when mated; the F103 has no USB, so it must be programmed unmated (JLC offers programming only if the interface is reserved and the board photo is supplied; capabilities FAQ).
- F407 USB DFU: USB D+/D- on J2.30/31 go to the motherboard's USB-C, so DFU works only when mated.
- A simple fixture: bed-of-nails on the bottom-side pogo pins at J102, plus a TC2030 plug-of-nails on J3; add TPs for +12V/VBAT, +5V, +3V3, GND, NRST, and the key outputs. Cheap to add: a 1 mm pad each.

## 6. Silkscreen
About 49 of 338 daughterboard designators are visible on silk (98 visible text items counting field plus text duplicates, 1.0 mm / 0.15 mm); the rest are hidden by design. The mb8995 has 41 of 88. Board texts (HTR, ACT, OK; mb harness cavity labels) are present. DRC: silk_over_copper 70, silk_overlap 125 on cur_db (JLC clips silk off pads). Polarity marks / pin-1 marks and J1/J2 pin labels vs nets NOT checked.

## 7. Panelization, rails, fiducials, edge
- Boards have no fiducials and no rails (README says to let JLC add them). JLC (VERIFIED, help_article how-to-add-edge-rails): standard PCBA needs rails of at least 5 mm and 3-4 fiducials of 1 mm (3.35 mm from the board edge); JLC ships with rails attached unless the order requests removal (fee). Economic PCBA: single-sided placement, 2/4/6 layers, qty 2-50, rails/fiducials not necessary, fixed 255 C reflow (capabilities page). Both boards have SMD on the top only (bottom has only THT J1, J2 and J102 pads), so Economic PCBA is applicable (cost lever for other audits).
- Closest copper to edge: J1 pads 1.9 mm (cur and ord). ord_db VBAT_IN track is 0.62 mm from the edge (cur_db: 2.25 mm). Outline has 52 points (cut-outs); a V-cut cannot do that, so mouse bites or JLC rails.
- JLC wave-soldering of THT is irrelevant here: the SMD parts are on the same face as the header pins, so the headers are hand-soldered.

## 8. Conformal coating (INFERRED)
Mask: J3 and J102 pads, microSD J4, SW1/SW2, the USB-C, MPX5700AP port, harness connector, JD1/JD2 sockets and J1/J2 pins, J5 IDC header, JST PUD J2, pin headers JP1-6. All vias are tented. Fine-pitch LQFP and 0402 are coatable. Not tested. A 1.6 mm sealed case still needs a vent for the MAP port, so the MAP sensor port and the vent should be masked.

## Sources actually read
the review brief; evidence/cur_db and ord_db drc json; pcb dumps (work/B08.../pcb, geom); web/capabilities_pcb-assembly-capabilities.txt, capabilities_pcb-capabilities.txt (line 189), jlc_min_spacing.txt, help_article_pcb-via-covering.txt, help_article_how-to-add-edge-rails..., blog_Free-Via-in-Pad..., repo daughterboard/README.md items 8-9, ordered-boards/2026-11/daughterboard/README.md item 9, scripts/tab_copper.py, scripts/order_bom.py, evidence/cur_db pcb_pads.csv (J3, J102), layers/top_all.png crop.

## Not checked
- Whether the actual JLC order selected epoxy-filled vias (no order record in the workspace).
- Actual gerber F_Mask: that pad openings override via tenting inside pads (INFERRED from KiCad behaviour).
- Ordered motherboards' mounting-hole clearances (only cur_mb8995/9697/9900/0105 and ord_mb M4 holes).
- Silk polarity / pin-1 marks and connector pin labels vs nets; 3D heights and shadowing of tall parts; conformal coating tests; JLC placement-preview rotations; the repo's jlc_spacing.py was not run (shapely missing in system python).
