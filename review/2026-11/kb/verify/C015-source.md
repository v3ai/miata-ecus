# C015 verify (primary sources)
Verdict: confirmed (minor wording fixes).
Checked: tools/lcsc.py C46641168 C960026 (live): C46641168 SMD1812-200-30 hongjiacheng, extended, JLC stock 57 (LCSC 55); C960026 BSMD1812-200-30V BHFUSE, extended, stock 194229, $0.0887@50, $0.0778@150; both 1812, 2A hold/4A trip, 30V, 40A, 20mohm/100mohm post-trip, 4.73x3.41x1.5 mm (identical).
BOMs: C46641168 is F2 on 9900 (cur rev0.9, ord rev0.7), F2,F3 on 0105 (cur rev0.9, ord rev0.7). Not in other boards.
Ordered boards: yes, 9900 and 0105 ordered boards use it, but already sent to fab; only a risk if a reorder is needed. Not in review brief s6 (which only lists PTC voltage ratings 24-33V).
Corrections: "about 28 boards of 0105" is arithmetic (57/2); a snapshot, stock moves; alone 9900 needs 1/board. The $0.11 in B05.02 is the qty-1 price. Alternate is not a datasheet-checked electrical match beyond the vendor-listed parameters (same BHFUSE family as F4).
Fix: switch F2/F3 to C960026 in mb_*.py for 9900/0105 next rev (same footprint, cheaper at volume: 0.0887 vs 0.1071 @50).
