# C022 consequence check: verdict PARTLY
Checked live 2026-11-16 with tools/lcsc.py: C12345 JLC stock 96 (LCSC 24), $5.05@1, $3.57@100, extended. C56621 (F405VGT6) stock 1050, $7.62@1, $5.37@100.
- Stock figures are noisy (74/126/72/96 in one day), so "falling" is not shown; it fluctuates around 70-130 and restocks. "Tiny" is true: under 100 pcs.
- Consequence: a small batch (tens of boards) is buildable now. About 100 boards would need a restock or consignment, which JLC supports (buy from LCSC/DigiKey and consign) at a cost of roughly $5-10 per MCU. This is a build-planning risk, not a design error. No defect in the boards.
- Distributor price ~2x JLC: plausible (TME $8.70-9.97), not rechecked; irrelevant because JLC price ($3.57@100) is lowest.
- F405 swap: same die class, LQFP100, same pinout (F405 lacks only Ethernet/camera, which are unused). But it costs about $1.8 MORE per MCU at 100 (5.37 vs 3.57), so it is a supply hedge, not a saving. rusEFI F4 firmware for F407 boards should run on F405, but this was not tested here.
- Ordered boards: the daughterboard rev 0.9 BOM uses C12345 as well, but nothing is reworkable by this finding. If the order already had the MCU assembled it is moot; if JLC flagged shortage the owner would already know.
- Not in review brief section 6 / VERIFICATION.md (only other parts' stock is discussed).
Severity: medium (planning risk before volume builds), not high. Cheaper fix: before each batch, check stock; for a run above stock, consign F407 from LCSC/DigiKey. Keep F405 C56621 as a fallback. The claim's statement "a batch of 100 cannot be built from it" is true only of today's stock, a snapshot.
