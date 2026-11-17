# C022 verification (primary sources)
Verdict: partly.
Checked (tools/lcsc.py live, 2026-11-16): C12345 = STM32F407VGT6, LQFP-100, extended, JLC stock 96 (LCSC 24), $5.05@1, $4.04@30, $3.57@100, $3.34@1000. C56621 = STM32F405VGT6, extended, stock 1050, $7.62@1, $5.37@100 (more expensive than F407, not cheaper). APM32F407VGT6 C2990873 stock 1107, $4.43@1 / $2.89@90 (cheaper, Geehy clone, not recommended). F427VGT6 C117815 stock 2585 $9.01@1.
Stock readings in the claim (126, 72, 74) vs 96 now: it fluctuates, so "falling" is not shown; "tiny" is true (about 1 batch of 100).
C12345 is used in repo/scripts/design.py:169 and evidence/ord_db BOM (ordered rev 0.9 uses it).
Not checked: distributor prices (TME, DigiKey, Newark, lead times) - no distributor access; DS8626 pin table equality (F405/F407 LQFP100 are known pin-compatible, not re-derived).
Documented? grep of repo/VERIFICATION.md finds no MCU stock item, so not already known.
Ordered boards: the boards are already ordered; only reorders/volume builds are affected. No rework impact.
Corrected statement: C12345 (F407VGT6, extended) has only about 70-130 pcs at JLC (96 today, varying, not demonstrably falling), so a 100-board run cannot be sourced from JLC stock. F405VGT6 C56621 (1050 in stock) is a pin-compatible alternate but costs MORE ($7.6@1, $5.4@100 vs $5.05/$3.57). APM32F407VGT6 C2990873 is cheaper with 1107 stock but is an unverified clone.
Fix: before a volume order, buy/consign F407 stock or qualify F405 (rusEFI F405 build support unverified); confirm stock again before ordering.
