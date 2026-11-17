## Recommendation

Date of all checks: 2026-11-17. Scratch work: `work/followup/Q3-no-filled-vias/` (scripts `dump.py`, `analyze.py`, `reloc.py`, `mkvar.py`, `th.sh`; result CSVs `*_vias_in_pads.csv`, `*_reloc_cl0.2.csv`).

1. **Next revision: design so that no via hole lies in any SMD pad, except on the exposed pads of the regulators (U2, U3, U14, 2-3 vias each). Then fill is not needed.** Keep 6 layers (fill is free there, so it stays as a second line of defence), but the board no longer depends on it. Record the rule in the fab outputs (see item 6). [recommendation, INFERRED from the measurements below]
2. **The eight DPAK tab pads (Q1-Q8, about 200 vias): delete the vias in the tab pad and keep the copper columns plus the vias around the tab.** The repo's own thermal model (`firmware/tools/board_thermal.py`, run today on a copy of rev 0.10) says that taking out all 200 tab vias raises the Q1/Q2 junction by +2 C in the worst case (batch1, 0.55 W: 72 C to 74 C above air); taking out every via within 3 mm of every tab (357 vias) raises it by +3 C (75 C). VERIFIED as model output (`thermal.txt`); it is a model, not a measurement.
3. **The roughly 230 vias in small pads (0402 / 0603 / SOT-23 / diodes / ICs) move to a short dog-bone.** On a copy of the current rev 0.10 board, with no re-routing, 63 % (146 of 232) can be moved to a site outside every pad within 0.5 mm, 85 % within 1.0 mm, 90 % within 1.5 mm, at 0.2 mm clearance (0.127 mm: see section 4b). **Fact-check: these figures use a rule that lets the new via's copper ring overlap the pad edge by 0.05 mm (hole plus 0.1 mm mask web = 0.25 mm centre to pad edge). With a rule that keeps the whole 0.6 mm ring clear of the pad plus a 0.1 mm mask web (0.40 mm), I re-ran it: within 0.5 mm only 21 % (57 of 269), within 1.0 mm 69 % (185), within 1.5 mm 82 % (221), 30 vias not within 2 mm.** Plan for the lower set of numbers. The remaining 10 % (24 vias) need a local re-route; the router run with a via keep-out inside pads does that.
4. **Scripts to change** (section 5): `route.py` (via keep-out inside SMD pads, lines 162-172 / 660-765), `finish_route.py` (`via_in_pad`, line 374, and its caller at line 411), `tab_copper.py` (in-tab vias, lines 84 and 138-148), `clamp_copper.py` (vias in the SMC pads), plus a new gate in `jlc_fab_check.py` that fails if a via hole lies in an SMD pad. Estimated size: about 60 lines.
5. **Optional, cheap: drill the vias that must stay in an exposed pad at 0.2 mm (via diameter 0.45)**. JLC's capabilities page lists 0.2 mm hole with 0.45 mm via as the preferred minimum without the cost surcharge (it says "0.2 mm or 0.25 mm hole size with via diameter less than 0.45 mm will cost more"). Hole volume drops to 44 % of a 0.3 mm hole.
6. **State the via covering in the order**: write "Via covering: tented, no vias in SMD pads; epoxy filled and capped is not required" (or, if the 6-layer default is wanted anyway, "epoxy filled and capped, all vias") in the README and in `ORDER_NOTES.txt` (`ORDER_NOTES.txt` is only the owner's own reminder: JLC does not read files inside the gerber zip, so the choice must be made in the order page's via-covering option and the order remarks, and checked by a person; the via-covering help page says: "leave a note or upload an image ... to explain which vias should be filled. Alternatively, you can specify to fill all vias of a particular diameter", `web/pcb-via-covering.html.txt` line 235).
7. **Ordered rev 0.9 boards** (4-layer, 1423 vias, 472 hole centres in SMD pads, 544 if vias whose copper only overlaps a pad are counted): nothing can be done about the vias themselves. First look at the bare board against light: through-holes visible in the pads = not filled (INFERRED, JLC says capped vias are plated over). Then see section 6 for which joints to look at first (Q1-Q8 tabs, U2/U3/U14 exposed pads, 0402/0603 on the GND/+3V3 plane drops).
8. **Price of fill on 4 layers: I could not get a dollar figure.** JLC's pages say it is paid on 4 layers and free on 6 layers, and an August 2026 notice (titled "Temporary Adjustments", expected to last about 15 days, so stale today) said 4-layer resin-filled via prices would "experience a slight increase". A quote needs the interactive quote page (UNVERIFIED, see Not checked). Do not pay for it: the layout fix costs nothing at the fab.

## Options compared

| Option | Needs fill? | Cost at the fab | Layout effort | Risk | Verdict |
|---|---|---|---|---|---|
| (a) vias only in the large thermal pads, made safe without fill (small drill / tent far side / paste windows) | Partly (still wicks; onsemi AND8432 p.6: unfilled vias "will draw solder from the mounting surface during package mounting reflow"; SMTA study via search: wicks at any diameter, UNVERIFIED) | 0 | Low | Voids under tab, starved fillet | Only for U2/U3/U14 (3 vias each). Not for the DPAK tabs |
| (a2) ring of vias outside the DPAK tab, none in the tab | No | 0 | Low (delete in-tab vias; ring already exists, 19 per driver within 3 mm) | Model: +2 C junction at 0.55 W | **Recommended for Q1-Q8** |
| (b) dog-bone every small-pad via | No | 0 | Medium: 63 % within 0.5 mm, 85 % within 1.0 mm, 10 % need a local re-route | Longer stubs on GND (negligible) | **Recommended for passives, diodes, ICs** |
| (c) stay on 6 layers and rely on free fill | Yes, as an order requirement | 0 on 6 layers (VERIFIED, JLC capabilities: "default for 6-layer and above") | None | Order note lost or option unchecked; the gerbers cannot carry it; this rev 0.9 problem repeats | Keep as backup only |
| (d) pay for fill on 4 layers | Yes | Extra, unquoted (UNVERIFIED), "slight increase" Aug 2026 | None | Same order-note risk; 4-layer relayout is also not done | Not recommended |

## Evidence

### 1. Measurement (VERIFIED: computed from the PCB files)

Method: copies of `repo/daughterboard/miata_ecu_daughter.kicad_pcb` (rev 0.10, 6 layers, 1349 vias) and `repo/ordered-boards/2026-11/daughterboard/...` (rev 0.9, 4 layers, 1423 vias), pcbnew exact pad polygons (`TransformShapeToPolygon`), shapely containment of the via centre. All vias are 0.6 mm / 0.3 mm. Classes: "link" = the via joins a track or pad on at least two layers; "plane-drop" = pad on an outer layer to a GND / +3V3 plane or pour on another layer; "thermal array" = pad with at least 4 vias. No via is "stitch only" or dangling.

| | ordered rev 0.9 | current rev 0.10 |
|---|---|---|
| vias | 1423 | 1349 |
| hole centre inside an SMD pad | **472** | **473** |
| copper ring overlaps a pad, hole outside | 72 | 66 |
| of which DPAK / SOT-223 tab arrays | 201 (8 x 25) | 204 (200 DPAK + 4 microSD shell) |
| link vias (needed for connectivity) | 44 | 44 |
| plane-drop vias (GND 179 / +3V3 and power 48) | 227 | 225 |

By footprint class (centre in pad; ordered rev 0.9 / current rev 0.10): 0402 76 / 66; 0603 (incl. LED, R-array) 72 / 65; 0805 9 / 11; 1206 and 1812 13 / 7; DPAK 212 / 206; SOT-223 7 / 8; SOT-23, SOD, SMA, SMC diodes 52 / 64; ICs (SOIC, TSSOP, DSO) 29 / 38; other (inductor, switches, microSD) 2 / 8.
By net class (rev 0.9 / rev 0.10): ground 179 / 170; power 261 / 273 (this includes the OUT_x drain nets under the DPAK tabs, 201 / 200); signal 32 / 30.
Cross table, rev 0.10: plane-drop ground 166, plane-drop power 59, link power 14, link signal 30, thermal array power 200 (+4 microSD ground). Files: `cur.analyze.txt`, `ord.analyze.txt`.

Remark on counts: the earlier B08 note says 373 vias in the DPAK pads and about 620 in total. My exact-polygon count of 212 for DPAK (fact-check: an independent pcbnew `HitTest` count gives 482 / 481 vias in SMD pads against 473 / 472, DPAK 206 / 212 identical; the ~9 difference is edge tolerance, so quote 470-480) agrees with the repo's 25 vias per tab (8 x 25 = 200); I cannot reproduce 373. Whether B08 counted vias in the tab column rather than the pad is UNVERIFIED. The 500-660 range in REPORT.md stands as a range; the best exact number is 472 (544 with ring overlap).

Pads of 4 mm2 and more carrying vias that are not DPAK arrays (rev 0.10, 37 vias): the SMC clamp TVS pads D46-D49 (1-3 each) and D6 (3), SMA pads D12, D9, D44, D45, D7 (1-3), Q20 and U4 (SOT-223 tab, 2 each), and the exposed pads of U2 (2), U3 (3), U14 (1). Of these, only the regulator pads and the SOT-223 tabs have a real thermal job; the diode pad vias are plane/copper joins (see below).

### 2. Which code puts vias in pads, and why (VERIFIED: read files)

- `scripts/route.py:162-172` (`Grid.via_ok`): a via is allowed on every cell where the net's own copper or free space is (`own | good`, line 155-157). Pads of the same net are "own copper", so nothing forbids a via inside a pad. There is no comment or rule about it.
- `route.py:660-765` `gnd_stitch`: each GND / +3V3 SMD pad gets a stitching via; its target set `tg` is every `via_ok` cell within 4 mm, including cells of the pad itself, so a zero-length path ends in the pad. The header comment (line 15) says only "each GND SMD pad gets a short stub to a stitching via". `thermal_and_stitch` (line 744-755) puts vias at the centre of every GND pad of 4 mm2 or more, at 0, +0.9 and -0.9 mm: these are the regulator exposed pads.
- `route.py:543-549`, `finish_route.py:304-312`: the A* layer changes (`runs` / `commit`) can put the layer change on the pad cell.
- `finish_route.py:374-395` `via_in_pad()`: explicit: "A boxed-in pad on a six-layer board: the via goes into the pad itself (JLCPCB fills and caps every via on a six-layer board, so a via in a pad solders like the pad)". Called at line 411 as the last fallback. Added in commit `2f4f357` ("WIP rev 0.10 ...").
- `tab_copper.py:8-10, 84, 138-148`: thermal vias in the DPAK tab pad on purpose: "order the board with the vias epoxy-filled and capped, JLC's via-in-pad process; a solder-mask plug is not for vias in pads; or leave them open and accept a little solder wicking into the 0.3 mm holes". Comment changed in commit `3cb7343` ("vias in the tab pads want filled-and-capped, not plugged"). Line 84 exempts the driver's own tab pad from the via clearance test.
- `clamp_copper.py:9, 100-115`: vias on a 1.2 mm grid inside the SMC clamp pads, comment "JLCPCB fills and caps vias in pads on six-layer boards".
- `ordered-boards/2026-11/daughterboard/README.md:15, 37, 321`: asks for epoxy fill but names only the DPAK tabs (C005).
So the reason is: the router treats the own pad as free space; the fill was assumed (and, on 6 layers, is free) so nobody added a rule.

### 3. JLCPCB and others (read today)

- Fill option on 4 / 6 layers: JLC capabilities page, "JLCPCB Via-in-Pad Process / Epoxy Filled & Capped / Copper paste Filled & Capped": "default for 6-layer and above", via diameters 0.15 to 0.55 mm (https://jlcpcb.com/capabilities/pcb-capabilities, saved `web/pcb-capabilities.html.txt` lines 347-354). VERIFIED.
- JLC blog: "via-in-pad on 6-20 layer PCBs are upgraded to POFV for free ... (POFV for 4-layer PCBs still requires charges.)"; POFV: annular ring 0.05 mm minimum, hole 0.2 to 0.5 mm (https://jlcpcb.com/blog/Free-Via-in-Pad-on-6-20-Layer-PCBs-with-POFV). VERIFIED.
- Price on 4 layers: the blog says only "requires charges". JLC notice dated Aug 06, 2026: "4-Layer PCBs with Resin Filled Vias: Prices will experience a slight increase" (https://jlcpcb.com/news/pcb-lead-time-and-price-adjustment-august2026). VERIFIED text; no dollar figure. A search result snippet says the quote page upgrades 6+ layers to epoxy fill for free (UNVERIFIED, search snippet only). No price for 4 / 6 layers at 125 x 76 mm, qty 5 / 30 could be read (the quote page is script-driven): **UNVERIFIED, requires a manual quote.**
- What JLC says about open vias in pads: blog comparison photo caption: "The pad on the right was produced with a regular process and the via hole is exposed; this is undesirable because during reflow soldering the solder can be wicked into the hole, leaving too little on the surface to secure the component" (same blog). Via covering help page: untented via "Risk of flowing tin and filled vias when assembly"; "For untented vias or tented vias, there may be tin beads remaining in the hole" (https://jlcpcb.com/help/article/pcb-via-covering, `web/pcb-via-covering.html.txt` lines 158, 195). VERIFIED. Plugged (ink) vias: "holes in pad, and vias with a distance less than 0.35mm from the pad cannot be plugged with ink. Such vias can be plugged with epoxy or copper" (line 196). VERIFIED. The assembly capabilities page has no via-in-pad statement (grep, nothing found).
- Minimums: via 0.15 mm hole / 0.25 mm diameter on multilayer; preferred 0.2 mm hole; "0.2 mm or 0.25 mm hole size with via diameter less than 0.45 mm will cost more"; via diameter 0.1 mm (0.15 preferred) larger than the hole; PTH annular ring multilayer 1 oz: recommended 0.20, absolute minimum 0.15 mm; via hole to hole 0.2 mm; track/space 0.15/0.15 mm (capabilities page, lines 198-226, 281-300). VERIFIED. The repo's 0.6 / 0.3 via has a 0.15 mm ring, at the absolute minimum.
- Manufacturers: onsemi AND8432/D (2009), p.6: for unfilled thermal vias "(not recommended, as they will draw solder from the mounting surface during package mounting reflow)"; with 25 um walls keq falls to 10.2 W/mK; silver epoxy fill gives "negligible" improvement (10.5); copper fill is the good one. (https://www.onsemi.com/pub/Collateral/AND8432-D.PDF, downloaded and read.) VERIFIED. Consequence: JLC's epoxy fill gives no thermal gain (epoxy 4 W/mK); only the copper-paste option (8 W/mK, JLC page) would, and it is not needed here because the model shows the tab vias hardly matter.
- IPC-7093 "plug the via" recommendation, tented vias reducing voids but also solder volume, solder wicking independent of diameter: from a web search summary only (SMTA paper, circuitsassembly.com); not read in the primary source: UNVERIFIED. I did not find or read TI, ST or Infineon notes (see Not checked). The Microchip and Pericom PDFs did not parse.
- Reference designs in `ext/` (VERIFIED, pcbnew `HitTest` on SMD pads, `refcount.txt`): hellen-miata NA6 759 vias, 19 in SMD pads (NB1 743 / 13; NB2 830 / 11), none under power packages; these three are 2-layer boards (re-checked: only F.Cu and B.Cu), so they say nothing about 4/6-layer fill; the hellen-one and wideband modules are 4-layer; wideband-mck1117 and wideband-rusefi controller modules 63 vias, 0 in pads; hellen1-mcz33810 72 / 6; hellen1-motor-driver 27 / 7; hellen1-wbo 80 / 0; hellen1-uaefi 0 vias. So the open designs keep vias out of small pads and DPAK tabs. Fabrication notes: no text in the READMEs, scripts or .kicad_pro files of those repos asks for epoxy fill or via covering (grep over `ext/*.md, *.txt, *.sh, *.json` found no match for epoxy / via fill / via-in-pad; the hellen-miata gerbers folders were not read for a notes file).

### 4a. Thermal effect of not having vias in the DPAK tabs (VERIFIED as model output; the model is the repo's, h = 10 W/m2K, 20 mH, 7200 rpm)

Run: `th.sh <board> --case seq,batch1,batch` on copies of rev 0.10 (the model counts via copper barrels only, so epoxy vs open is not distinguished; fill matters for solder, not for this model).

| variant | vias | Q1 pad / junction batch1 (0.55 W) | Q1-Q4 junction batch (0.14 W) | Q1-Q4 junction seq |
|---|---|---|---|---|
| as is (200 vias in the 8 tabs) | 1349 | +70 / +72 C | +56 / +58 / +58 / +56 | +40 / +41 / +41 / +39 |
| no vias in the tab pads | 1149 | +72 / +74 | +57 / +59 / +58 / +56 | +40 / +41 / +41 / +39 |
| 4 vias per tab | 1181 | +72 / +73 | +57 / +58 / +58 / +56 | +40 / +41 / +41 / +39 |
| no vias within 3 mm of any tab | 992 | +73 / +75 | +57 / +59 / +59 / +56 | +41 / +41 / +41 / +40 |

(Q2 batch1 junction in the same four cases: +71 / +72 / +71 / +73.) Valve drivers Q5-Q7 move by at most +1 C. Reading: the copper columns on four layers carry the heat; the tab vias add about 2 C to the worst case, i.e. about 3.6 C/W of 55. A lower-bound cross-check: dropping a whole 3 mm ring of vias costs 3 C. INFERRED that the real board behaves the same; the thermal model has never been checked against a measurement (repo's own limitation).

### 4b. Dog-bone feasibility (VERIFIED: computed on copies)

Rules used (`reloc.py`): the new via centre must be 0.25 mm or more from any SMD pad edge (hole 0.15 plus 0.1 mask web), 0.6 mm from the board edge, 0.2 mm copper clearance (0.127 mm run too) to other-net tracks, pads and vias on all layers, via hole-to-hole 0.25 mm, THT holes 0.25 mm; the stub from the old to the new position (0.2 mm wide) must clear other-net copper on the pad's layer and on every layer where a track ends at the via. Zones refill and are ignored. Vias are moved one after the other (earlier moves block later ones). Search radius up to 2.0 mm on a 0.05 mm grid. Vias in the DPAK tab arrays are excluded (handled by 4a).

| | 0.5 mm | 1.0 mm | 1.5 mm | not within 2 mm |
|---|---|---|---|---|
| rev 0.10, 269 vias in pads (incl. 37 in big pads), clearance 0.2 | 148 (55 %) | 214 (80 %) | 241 (90 %) | 15 |
| rev 0.10, same, clearance 0.127 | 165 | 226 | 253 | 6 |
| rev 0.10, 232 vias in pads under 4 mm2 only | 146 (63 %) | 198 (85 %) | 208 (90 %) | 15 (24 need more than 1.5 mm) |
| ordered rev 0.9, 271 vias, clearance 0.2 | 142 | 219 | 244 | 20 |

Per class, rev 0.10 (n, within 0.5, 1.0, 1.5 mm, none within 2 mm): 0402 66, 40, 56, 59, 6; 0603 65, 51, 61, 61, 3; 0805 11, 5, 9, 10, 1; 1206 7, 4, 5, 6, 0; IC 38, 11, 26, 31, 2; SOT-223 8, 2, 5, 7, 0; SOT-23 and diodes 64, 30, 44, 58, 2; small-pad "DPAK leads" 6, 3, 6, 6, 0.
Worst areas, rev 0.10, vias that need more than 1.5 mm or cannot move (board coordinates, mm): around the SOIC-8 U6 (147.0, 78.75 and 146.0, 83.75), U9 (163.75, 111.5 / 112.75), U106 (196.5, 86.75 and 194.0, 86.0), the 0603 resistor arrays RN1/RN2 (147-148, 85-87.5 and 130.5, 67.5), regulators U3 (113.0, 100.5) and U8 (110.75, 111.0), U105 (207.5, 105.0); clamp diodes D46/D48 (159.75, 72.0 and 173.6, 78.8), the SMC D6 (118.0, 75.5), the microSD J4 pin 7 (211.25, 80.75), 0402 passives C34, C39, R13, R70, R72, R104, R111 in the dense MCU / analog corners (x 129-205, y 75-121), and Q20 (197.75, 78.5), R146 (153.5, 55.5). Full list: `cur_reloc_cl0.2.csv` (empty `dist` column = none within 2 mm). These are the "boxed-in" pads where `finish_route.via_in_pad` was used; they will need a re-route or a footprint change (for example moving the resistor array), not just a nudge.
Caveat: the greedy search is sequential and does not re-check that every moved stub keeps track-to-track clearance with the later 6-layer re-fill of In1-In4 planes; INFERRED that a real run in KiCad DRC would find a few more conflicts.

### 5. Scripts that would change (INFERRED, read the code)

1. `route.py`: in `Router.__init__` after the pads are loaded (line 183-200, where `mark_via` is applied), set `g.vexcl` for every SMD pad polygon grown by 0.25 mm, except an allow-list of exposed-pad refs (U2.9, U3.9, U14.9). This stops `via_ok` from returning cells inside pads; `gnd_stitch` (line 660) then ends its A* path outside the pad with a stub (its `astar(..., w in (0.3, SIG_W))` already makes the stub). `thermal_and_stitch` (line 744): limit the pad vias to the allow-list (3 vias at 0.2 mm drill if wanted: `VIA_DRILL` is global at line 35, so a second via class is needed).
2. `finish_route.py`: remove `via_in_pad` (line 374-395) and the fallback at line 411 (or gate it by an env var `ALLOW_VIP=1` that is off); `VD, VDRILL` at line 35 stay. `daughter_make.sh` line 22-27 (`--free` loop) will report "NO VIA SITE" for the 15-24 boxed-in pads; fix those by hand or with `finish_route.py --free`.
3. `tab_copper.py`: drop the in-tab exception (`own` argument at line 84, `in_tab` at 138-148): vias are placed only where `near_tab` is false; keep the 1.2 mm grid outside. This leaves about 19 vias per driver within 3 mm (357 - 200 = 157 over eight tabs in the "novia" test, so about 20 each). Update the header text (line 8-10).
4. `clamp_copper.py`: in `_clear` (line 52-60) do not exempt the own pad (same change as 3); put the vias in the copper column beside the pad. Its header (line 9) mentions the free fill.
5. `jlc_fab_check.py` (or `drc.py`): add the check I used (`work/followup/Q3-no-filled-vias/dump.py` + `analyze.py`: via centre inside an SMD pad polygon, minus the allow-list) and make the release (`daughter_release.sh`) fail on any hit. Add `ORDER_NOTES.txt` to the zip and the README: `order_bom.py` / README line 37 and "Before ordering" item 9.
6. `build_pcb.py` / `daughter_rev10.py`: nothing to change except the README text; re-run `daughter_make.sh` and the DRC; re-run `board_thermal.py` and `track_current.py`.
Effort estimate: about 60 lines, a re-route, and a DRC pass. INFERRED.

### 6. The ordered rev 0.9 boards

Facts (VERIFIED, computed): 1423 vias, 472 hole centres in SMD pads; of those 201 in the eight DPAK tab arrays (25 each) and 271 elsewhere, of which 227 are plane drops (GND 179) and 44 links. Mask: all vias tented on both sides in the file (B08), but a pad opening overrides the tent where the hole lies in the pad (INFERRED, KiCad behaviour).
Whether the vias are filled is unknown: it is an order option, not carried in the gerbers (C005). Do this in order:
1. Order record: look for "Via covering: epoxy filled & capped" on the JLC order page (free).
2. Bare board: hold it against light. Through-holes visible inside SMD pads = unfilled; pads that look closed and flat (the cap is plated over, then finished) = filled. INFERRED from JLC's description of the process.
3. If unfilled, inspect after assembly in this order of importance (INFERRED): (a) Q1-Q8 tabs (each tab pad has 25 open 0.3 mm holes: about 2.8 mm3 of hole against about 4.4 mm3 of paste under the tab, C005 arithmetic; the bottom is tented, so wicking stops at the back, solder may bulge back there), by looking at the lead-side fillet and with a thermal camera under load; the solder fillet at the tab's long edge must exist; (b) U2, U3, U14 exposed pads (2-3 vias each) and the SOT-223 tabs of Q20 / U4; (c) the clamp and load-dump diodes D6, D9, D12 (SMC / SMA, 2-3 vias each); (d) 0402 and 0603 parts on the 60 + 62 plane-drop vias (hole volume 0.113 mm3 against about 0.015 mm3 of paste on a 0402 pad: tombstoning or a starved joint, INFERRED from C005's figures).
4. Rework if found bad: hot-air the part and add flux and solder along the pad edge, or for a tab add solder from the lead side with a hot air gun from the back; there is no way to re-fill the vias. Q1-Q8 have 2 C of model sensitivity to the vias (4a), so a tab that is soldered at its edge but has voids underneath is probably acceptable; a tab with no fillet is not.
5. The repo's note stays valid: thermal-camera Q1-Q8 under dummy load at 3 W and 6 W before the board goes in a car.

## Sources read today

- Files: `the review brief`; `REPORT.md` S1 item 3 and S3 section 6 (lines 20, 83, 222, 550, 559, 601); `kb/boards/B08-dfm-assembly-mounting.md` (section 2); `kb/verify/C005-consequence.md`; `repo/scripts/route.py` (lines 1-35, 155-175, 385-400, 660-770, 795-825), `finish_route.py` (285-315, 370-415), `tab_copper.py` (1-30, 60-165), `clamp_copper.py` (1-30, 100-125), `daughter_finish.py` (60-135), `daughter_make.sh`, `hand_route.py` (175-195), `wb_build.py` (135-160); `repo/firmware/tools/board_thermal.py` (whole header, `Model`); `repo/ordered-boards/2026-11/daughterboard/README.md` (via grep lines 15, 37, 321); `evidence/{cur_db,ord_db}/pcb_stats.json`, `pcb_footprints.csv`; the two daughterboard `.kicad_pcb` files (copies in the work dir); `ext/` PCB files listed in section 3.
- Web (all fetched with curl or the search tool, 2026-11-17): https://jlcpcb.com/capabilities/pcb-capabilities ; https://jlcpcb.com/capabilities/pcb-assembly-capabilities ; https://jlcpcb.com/help/article/pcb-via-covering ; https://jlcpcb.com/blog/five-via-finishes ; https://jlcpcb.com/blog/Free-Via-in-Pad-on-6-20-Layer-PCBs-with-POFV ; https://jlcpcb.com/news/pcb-lead-time-and-price-adjustment-august2026 ; https://www.onsemi.com/pub/Collateral/AND8432-D.PDF (p.6) . Search results (snippets only, not primary): SMTA / circuitsassembly / bestpcbs articles on wicking and IPC-7093.
- Computed: `work/followup/Q3-no-filled-vias/` (`ord.analyze.txt`, `cur.analyze.txt`, `cur.reloc.txt`, `ord.reloc.txt`, `*_reloc_cl0.2.csv`, `thermal.txt`, `refcount.txt`, `web/`).

## Not checked

- **JLC prices** for 4-layer and 6-layer, 125 x 76 mm, qty 5 and 30, with and without epoxy fill: the quote page is not readable without a browser session; no dollar figure was found. A manual quote is the only way (UNVERIFIED). Also what the fill costs on 4 layers if only "vias in pads" are filled; JLC's page says to specify the hole sizes in the order notes.
- What JLC's assembly line itself does with unfilled vias in pads (a process statement beyond the blog's "solder can be wicked into the hole"): not found in any JLC page.
- IPC-4761 via types, IPC-7093, and application notes from TI, ST, Infineon: not read (only onsemi AND8432 was read; the Microchip and Pericom PDFs did not parse). The wicking and tenting statements from the web search are secondary.
- The via and pad geometry of the 3D stack: JLC's actual 4-layer and 6-layer stackups (the thermal model uses "recalled" stackups).
- Dog-bone result is not DRC-checked in KiCad after the moves; no re-route was tried; zones were ignored; clearance rules other than the ones listed were not applied.
- Whether the repo's ordered boards were ordered with the fill: no order record in the workspace.
- The rev 0.9 boards were not run through the thermal model; the numbers are rev 0.10 (6 layers).
- The `ext/` reference designs' fabrication notes (hellen gerber folders, BOM notes) were only grepped for text; the hellen-miata boards are 2-layer, so they cannot say anything about 4/6-layer fill requirements.
- The 373 DPAK-via figure of B08 versus my 212: not resolved.

## Fact-check log

Date 2026-11-17. Work dir `work/fc-q3/`.

Re-run and confirmed:
- Via counts (1349 / 1423, all 0.6 / 0.3 mm), layer counts (6 / 4), DPAK-class counts (206 / 212): re-counted with pcbnew `HitTest`; the hole-in-SMD-pad total comes out at 482 / 481 against the file's 473 / 472 (edge tolerance). Headline "about 470-480" stands. The class tables in the file come from `cur.analyze.txt` and were read, not rebuilt.
- Thermal table: `thermal.txt` read; the 200-via and 357-via deltas (1345 to 1145 and 988 vias) match. +2 C / +3 C at Q1 batch1 holds as model output. Not re-run (the model is the repo's, never calibrated against a measurement).
- Code references: `finish_route.py:374` (`via_in_pad`) and 411, `tab_copper.py` header and 84 / 138-148, `clamp_copper.py:9`, `route.py:155-172`, `route.py:744-755`, commits `2f4f357` and `3cb7343`, README lines 37 and 321 (the ordered README): all match.
- JLC pages re-fetched live (via-covering, capabilities, POFV blog): "default for 6-layer and above", "POFV for 4-layer PCBs still requires charges", exposed-via wicking caption, via diameters 0.15-0.55 mm, annular ring 0.05 mm min: all confirmed. The ordered `fab/` folder contains no via-covering note: confirmed.
- onsemi AND8432/D re-downloaded: "unfilled (not recommended, as they will draw [solder]...)", 10.2 W/mK unfilled, 10.5 W/mK with epoxy fill: confirmed.
- Reference designs: `refcount.txt` read; numbers match.

Corrected or downgraded:
- Dog-bone feasibility is sensitive to the pad-to-via rule. With the ring clear of the pad (0.40 mm) the numbers are 21 % / 69 % / 82 % at 0.5 / 1.0 / 1.5 mm and 30 vias not within 2 mm, not 63 / 85 / 90 %. Worst areas unchanged (U6, D46, D47, Q20, U106, U3, U2, RN1, J4, U9); the 0402 class gets worse (13 of 66 not within 2 mm).
- ORDER_NOTES.txt in the zip is not read by JLC; the order page option and remarks are what count.
- The "slight increase" notice was a temporary 15-day adjustment from Aug 2026; no current 4-layer fill price is known.
- "All 2-layer" for the reference designs applied only to hellen-miata.
- The via-covering help page (not the five-via-finishes page) carries the "write which vias to fill" sentence.
- New caveat: JLC's POFV table in the blog lists hole/diameter pairs (0.2/0.3 ... 0.3/0.45, "0.3 (Free)") and says POFV vias should be more than 0.45 mm from regular PTHs / NPTHs. The repo's 0.6 mm via is not in that table; whether the 4-layer surcharge depends on diameter is unknown.
- The thermal comparison is for rev 0.10 (6 layers) only; rev 0.9 was not modelled.

Still unverified: dollar price of fill on 4 layers and 6-layer price at 125 x 76 mm qty 5 / 30; what JLC assembly does with unfilled vias in pads; IPC-7093 / IPC-4761 and TI / ST / Infineon notes (not read); KiCad DRC of the moved vias; whether the ordered boards were filled; the 373 vs 212 DPAK-via discrepancy.
