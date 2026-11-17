# C101 verdict: partly (numbers true, consequence overstated, already documented)
- Datasheet C883150 derating table (datasheets/txt/C883150_BSMD1812-110-33V.txt L170-182): BSMD1812-110 = 1.10 A @25C, 0.71 @60, 0.66 @70, 0.52 @85. TRUE.
- 0.45 A at 8 V cranking is the repo's own figure (design.py L212; VERIFICATION.md L684). Cranking load 0.45 A < 0.52 A hold even at 85 C. Hold is the no-trip guarantee; trip is >= ~2x hold (2.2 A at 25 C), so a trip at 0.45-0.6 A is not expected at any temperature inside the part's rating. Only at 85 C AND 6 V (~0.6 A) does load exceed hold, and then it is a slow trip region, for seconds of cranking.
- 85 C is the part's absolute limit; the claim's "5 V rail could drop out" is not supported (no trip evidence; PTC series drop ~0.2 V).
- Already documented: VERIFICATION.md L684-686 lists exactly this risk (hot soak test); rev 0.10 was the fix. Not news.
- Ordered boards: NOT affected; ord_db has nSMD050-33V 0.5 A (C70077), a different, worse-margin part (0.5 A hold derates to ~0.25 A at 85 C); that is the real exposure and VERIFICATION.md already notes hand rework.
Corrected: rev 0.10 F1 hold at 85 C (0.52 A) is just above the 0.45 A load; margin thin only in an extreme hot-soak, weak-crank case; hold not trip. Severity low/info.
Fix: bench hot-soak crank test (already listed); no design change needed.
