# C096 verdict: partly
- Live manifest (kb/parts_manifest.md lines 344,377,406,436,466): C587650 = Molex 436500202, stock 0, $0.76-0.80. True.
- But J3 is "hand-fit" and in the repo's own self_order_bom.csv (evidence/ord_mb9495/*self_order_bom.csv row 5), flagged "Yes" self-order; it is not a JLC-assembled line, so stock 0 does not block the order. Only a sourcing note for the owner's hand-fit stock (Molex 43650-0200 at Digi-Key/Mouser).
- Mating plug claim not independently verified here.
Fix: none needed on boards; buy 43650-0200 from a distributor.
