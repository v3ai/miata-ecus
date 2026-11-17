# C151 verdict: partly
Checked design.py:297-330, parts_manifest.md (lines 29,47,55), evidence/{ord_db,cur_db}/pcb_footprints.csv, VERIFICATION.md 570/1117/1161.
- Parts exist in both ordered rev 0.9 and current rev 0.10 (Q16-19, U13, D31-34 identical refs/positions). Affects ordered boards, but only by hand removal (not recommended).
- Savings: Q16-19 4x(0.337..0.60) + U13 (0.104..0.21) = 1.45..2.61 USD depending on tier; ~1.7 is inside that range (live manifest prices, not re-fetched).
- Consequence: with FETs gone the TC4427 cannot pull the output low at all (D31-34 are in series, blocking), so the low level is only the 3.3k (R144-147); the design comment (design.py:319-321) says that is why the FET exists (spark edge). Schottky blocks battery short, so survival is kept. Statement is correct.
- The suggested_fix "Schottky-free 100 ohm" contradicts the statement (which keeps the Schottky): a Schottky-free chain would lose short-to-battery protection (driver back-fed, 100R 1206 burning, which VERIFICATION.md 1161 says happened before rev 0.8). Fix as worded is wrong.
- Not news: VERIFICATION.md 570/1117 documents these as deliberate rev 0.8 protections. Reference (Speeduino/Hellen) unprotected is an argument, not a defect. No igniter input measurement exists.
Corrected: Removing Q16-19+U13 (keep D31-34, R144-147) saves ~1.5-2.6 USD/board but leaves the output low only via 3.3k through the igniter load, slow falling spark edge, less noise margin. Low value; owner decision; do not rework ordered boards.
