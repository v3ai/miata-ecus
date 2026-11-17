# C005 source verification (primary-sources lens)
Verdict: PARTLY (core fact true; counts are rule-dependent; fill status unverifiable from repo files)

Checked
- Ordered DB (repo/ordered-boards/2026-11/daughterboard/miata_ecu_daughter.kicad_pcb, evidence/ord_db/gerbers/*job.gbrjob): LayerNumber 4; evidence/ord_db/pcb_stats.json: 1423 vias, all 0.6/0.3 mm. TRUE.
- Own count (work/verify/C005/c.py): via centre inside the bbox of an SMD pad (pcb_pads.csv, no same-net filter, both orientations tried): 498 of 1423; Q refs 228 (about 28 per Q1-Q8 tab), C 92, R 68, D 47, U 46, RN 10, SW 4. Same-net rule (664) and the 620/719/730 figures cannot all be right; counts of roughly 500-660 are all "hundreds". Q-tab figure of 373 (B04) not reproduced (228 by centre-in-pad); treat as unverified.
- Fill info absent: the gbrjob has no via-fill field; the drill files are plain. No order record in repo. TRUE. README (ordered-boards/.../daughterboard/README.md lines 37-38, 321 item 9) tells the owner to order epoxy-filled and capped vias, but names only the DPAK tabs ("most in the tab pad"), not the ~270 vias in 0402/0603/SOT/IC pads.
- JLC "fill is default only on 6+ layers" claim: NOT re-checked by me (no live fetch); relies on B08/B04 quoting JLC capabilities page. Volume/paste numbers (2.8 mm3 vs ~2 mm3) are the audits' estimate with assumed stencil thickness; not checked.

Already documented? Partly. README item 9 documents the DPAK-tab fill requirement; review brief section 6 and VERIFICATION open items do not list via-in-pad on small parts or the missing order record. Not fully news for the tabs, news for passives/ICs.
Affects ORDERED boards: yes (4-layer rev 0.9); only hand rework/inspection possible. Whether the order was placed with fill is unknown to the files.

Corrected statement: The ordered 4-layer daughterboard has 1423 open-spec 0.3 mm vias, of which roughly 500-660 (depending on counting rule) lie inside SMD pads, about 28 per Q1-Q8 DPAK tab plus ~270 under passives/ICs/diodes. Nothing in the repo records via fill; the README asks for epoxy fill but only mentions DPAK tabs. Whether the vias were filled depends on the actual order confirmation.
Fix: check the JLC order/DFM sheet for via covering = epoxy filled and capped; if not, inspect Q1-Q8 and 0402 joints (X-ray/visual) on arrival; fix README wording to "all vias" for future orders.
Severity: high stays reasonable if the fill was not ordered; medium if confirmed filled.
