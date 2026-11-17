# C006 source check
Verdict: partly (facts true; hot derating and 6 V numbers are estimates; already documented as an open item).
Checked:
- Ord db footprints: F1 nSMD050-33V C70077 1206; L1 CMI322513U2R2KT C70960 1210 (evidence/ord_db/pcb_footprints.csv).
- C70077 datasheet Table II: Ihold 0.50 A, Itrip 1.00 A @25C, R 0.15/0.30/0.70 ohm. True. The datasheet has NO temperature derating curve; 0.23-0.25 A at 85 C is a proxy from BHFUSE/generic polymer curves (about 50%).
- C70960: 2.2uH, 300 mohm, 500 mA (parts_manifest). True.
- design.py L205-218 and VERIFICATION.md line 684 state the 0.45 A at 8 V cranking figure; the 6 V / 0.6 A and dropout 5.4-5.6 V numbers are the audits' extrapolations, not measured (LMR14020 UVLO 3.5-3.9 V; VIN min 4 V, so no shutdown, only dropout sag).
- Already documented: VERIFICATION.md open item "F1 / L1 (logic supply, 0.5 A)" gives the same risk and the same rework (about 1 A 1206 PTC + 1210 inductor, hand rework on the ordered boards). Not news. Rev 0.10 already fixed (1.1 A 1812 F1, 7 A L1).
- Affects ordered boards: yes (ord_db rev 0.9), hand rework possible.
Corrected statement: Ordered F1 (0.5 A hold, 1.0 A trip at 25 C) and L1 (500 mA) have little margin against the repo's own 0.45 A cranking estimate at 8 V when hot; hot-derating and 6 V sag figures are unmeasured estimates. Known open item, fixed in rev 0.10.
Fix: swap F1 for ~1.1 A 1206 PTC (e.g. C48985884), L1 for >=1 A 1210 or 0 ohm; measure supply current at 6/8/13.8 V and hot-soak first.
