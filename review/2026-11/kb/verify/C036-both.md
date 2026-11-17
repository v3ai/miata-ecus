# C036 verdict: partly
Checked: repo/VERIFICATION.md lines 790-825 (Board temperature section). Cluster entry C036.
- TRUE: the model uses h=10 W/m2K both faces (line 794), self-test 54 C/W vs "as recalled, not re-read" datasheet 40-50 (line 796). Area 125x76 mm = 0.0095 m2, so mean rise = P/(2*A*h): 5.9 W -> 31 K matches the table. Rise scales 1/h; the audit's rerun (h=5: mean 63 C no pins) is simple arithmetic.
- ALREADY DOCUMENTED in part: the repo states "rise above the air around the board", "air around the board is the air inside the ECU case, which is warmer than the cabin" (line 825), and brackets with/without pins. Not news that case air is excluded; the size of the case offset is not quantified there.
- NOT VERIFIED: that h is really 3-5 in the closed case and the 10-20 K case-to-cabin figure. These are the reviewer's own assumptions (best_evidence says so). h=10 for a board in a case is optimistic but a stock ECU in the same case is similar; no measurement exists. The "allowable air 54/34 C" numbers inherit the unproven h.
- Ordered boards: the daughterboard rev 0.9 is affected equally (same thermal scale), but it is a risk to test, not a reworkable defect; mitigation is measurement or VGT7 MCU.
Corrected statement: the thermal model's h=10 and the case air offset are unvalidated (repo admits uncertainty); if the true h is 4-5 the MCU margin at sustained 7200 rpm shrinks to roughly 34-54 C case air. Unproven in either direction.
Severity: low-medium (risk, partly documented).
Fix: rerun with h=4-5 and a stated case offset; measure a built board in the case at 3 and 6 W.
