# C005 consequence check: via-in-pad on ordered 4-layer daughterboard
Verdict: PARTLY. Geometry true; "fill unspecified" is expected, not a defect; real risk is only if the order lacked the fill option.

Checked
- Ordered PCB (repo/ordered-boards/2026-11/daughterboard/miata_ecu_daughter.kicad_pcb): 1423 vias, all 0.6/0.3 mm (pcb_stats.json). My own crude centre-in-SMD-pad count (bbox test, SMD pads only) gives 511 (Q 229, C 92, R 68, U 55, D 48, RN 12...); the other audits' 620-664 use finer rules. Order of magnitude "hundreds" holds; exact number is rule-dependent.
- The repo does tell the owner to order filled+capped: ordered-boards/2026-11/daughterboard/README.md lines 37-38 and "Before ordering" item 9 (line 321), and line 15-16. So it is partly documented, but only for DPAK tabs; the ~250 vias under 0402/0603/SOT/diodes are not named. Not in VERIFICATION open items.
- JLC fill (epoxy filled and capped) is an order-form option, not something carried in gerber/drill/gbrjob files. So "files carry no fill information" is normal; no repo file could show it. The only evidence is the order confirmation, which is not in the workspace. Unknown whether the owner ticked it (JLC applies the option to all vias, so ticking it covers every pad, not just tabs).
- Arithmetic: 0.3 mm hole x 1.6 mm = 0.113 mm3; 25 per tab = 2.8 mm3. Tab paste ~37 mm2 x ~0.12 mm = ~4.4 mm3, ~half metal = ~2.2 mm3. Holes could take about all the solder if fully wicked, but bottom side is mask-tented (viasonmask false), so wicking stops at the bottom and fills are partial; typical result is voiding, not an open joint. Unfilled thermal vias in DPAK pads are common practice and usually work; Rth rises somewhat (the 48 C/W estimate has margin: 84 C at 60 C ambient). 0402/0603 pads are the worse case (hole 0.113 mm3 vs ~0.015 mm3 of solder on a 0402 pad): tombstoning/starved joints likely if unfilled.
- Not checked: JLC 4-layer fill surcharge (no live quote fetched).

Corrected statement
Ordered rev 0.9 has roughly 500-660 of 1423 0.3 mm vias inside SMD pads, including all 8 DPAK tabs and ~250 small passive/IC pads. This is only a problem if the JLC order did not select epoxy-filled and capped vias (an order-form option, default only at 6+ layers, so the gerbers cannot show it). The README instructed it, but only justified it for the tabs.

Severity: medium (high only if the option was not ticked). Affects the ORDERED boards; cannot be fixed after fabrication, only inspected and hand-reworked.

Fix (cheapest)
1. Look at the JLC order confirmation / order page for "Via Covering: Epoxy filled & capped" (one minute, free).
2. If absent: X-ray/visually inspect Q1-Q8 and rework 0402s by hand on arrival; hand-reflow with extra paste on tabs. Future: keep the option for all orders or move vias out of small pads (via-in-pad on 0402 should be removed in the generator).
