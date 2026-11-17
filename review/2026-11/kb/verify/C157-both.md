# C157 verdict: partly (true, trivial)
Checked: cur_mb9900 BOM (J5 2x10, no LCSC), ord_mb9900 BOM (J5 = C3406 2x8), repo/additional-parts/order_all_boards.csv row 21 (Optional, DigiKey 302-S201), `tools/lcsc.py C3405`.
- True: current J5 has no LCSC code and names On Shore 302-S201 (self-order, "Optional"). C3405 is a live BOOMELE 2x10 IDC box header, 3 A, JLC stock 42623, extended, $0.1462@1, $0.0784@500, $0.0748@2500, $0.0724@5000. The "$0.072@2000" figure is slightly off (it is the 5000 tier). Same-family-as-C3406 is plausible but I did not open a C3405 drawing (not in datasheets/).
- C3406 JLC title says "2x5" while params say 2x8P: true (manifest).
- Not news-worthy: the part is optional, hand-fitted, bought by the seller; saving is cents. Not in VERIFICATION.md as an item. Ordered boards use C3406 on a 2x8 footprint, so not affected (ordered=false).
Fix: add C3405 as the alternate in the self-order BOM after checking its datasheet pin length. Low value.
