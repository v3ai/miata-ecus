# C043 verdict: partly (true but already documented; does NOT affect ordered boards)
- Fact: no source names the 8-way housing; PUDP-08V-S is inferred from AEM "SPUD-001T-P0.5" text (kb/research/files/R15/aem_30-0300_fae.txt l.105-113) plus owner photo. Pin-1 end rests on the photo. True.
- Already documented: repo/VERIFICATION.md l.895-912 (inference, photo, "Still not done: real harness plugged in") and open-items row l.1107 ("No AEM harness has been plugged into a board"); review brief s6 l.120.
- Ordered boards: evidence/ord_mb* J2 is Molex Micro-Fit 2x3 "LSU 4.9" (C127367), not the JST PUD. Claim's ordered=true is wrong. Only cur_mb* (J2 = S08B-PUDSS-1) are affected.
- Fix: plug a real 30-3427 into a sample before ordering current motherboards (already the repo's own next step).
