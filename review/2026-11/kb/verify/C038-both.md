# C038 verdict: partly
Checked:
- Datasheet datasheets/txt/C22446884 rows 102-107 and 306: 2920L300 hold 3.0 A at 25 C, trip 5.0 A, derating 1.99 A at 60 C, 1.79 A at 70 C, 1.34 A at 85 C. True.
- repo/VERIFICATION.md:529 (N5 fix) says "about 2.4 A hold at 60 C" with 2.25 A rms worst case. The datasheet says 1.99 A at 60 C, so the repo misquotes the derating (true, small).
- heater_control.cpp: ramp starts at 7 V, +0.4 V/s (true). 7 V / 2.5 ohm = 2.8 A rms. The 2.5 and 3.2 ohm cold values are the repo's/secondary web figures, not from the Bosch datasheet (unverified). Current falls as the heater warms (resistance rises), and warm-up is about 13 s, so the peak is brief.
- Trip current at temperature is inferred (5/3 ratio gives about 2.2 A at 85 C); trip is time-dependent, so a brief excursion just over it may not trip. No measurement exists.
- Ordered boards: all five ord_mb* BOMs use F1 = C22446884 (2920L300), so the finding applies to the ordered boards. Rework is a hand swap of one 2920 part, but it is only worth doing if the risk is real.
- Already documented: the earlier risk (N5, 2 A part) is in VERIFICATION.md:507 and was "fixed" with the 3 A part. The residual hot-case risk is partly known. The new part is the 2.4 vs 1.99 A misquote.
Corrected statement: the repo misquotes F1's 60 C hold as 2.4 A (datasheet 1.99 A). Only if the PTC itself sits near 85 C does the 7 V warm-up current (about 2.2-2.8 A rms, assuming 2.5-3.2 ohm cold, unmeasured) exceed the inferred trip current. At 60 C it is below the inferred trip (about 3.3 A) but above hold. Nuisance trip is plausible in an extreme hot soak, not demonstrated. Severity low-medium.
Fix: measure cold heater R and F1 temperature on the first build; if needed swap to 2920L400/30GR (C19078761 per P16; hold 1.79 A at 85 C, trip 8 A) or lower the ramp start voltage in firmware. Correct the 2.4 A text in VERIFICATION.md.
