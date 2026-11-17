# C052 verdict: confirmed (as a statement of absence), low importance, already partly documented

Checked:
- ext/wideband-mck1117/firmware/lambda_conversion.cpp l.18-19, 39-40: comment "accurate within 0.5% from 0.8 to 1.0 ... when compared to the lookup table in the Bosch datasheet" (author claim, not independently tested); l.63 "Accurate with 0.005 lambda from 0.65-1". Matches the claim.
- R02 notes sec.10 step 5 and 6 contain the bench plan; sec.8/9 state no published validation found. The "no validation exists" part is a negative search and cannot be proven here.
- Bosch +-0.007/0.01/0.05 figures: PDF text not extractable here (no pdftotext/pypdf); matches my recollection of the LSU 4.9 datasheet, not re-checked.
- repo/VERIFICATION.md "Not covered" (about l.1208-1212) lists "analog accuracy" and wideband pump-loop behaviour as needing real hardware, so the repo already admits it.
- Note: the claimed validation gap is of the upstream FOME circuit/firmware, which is a widely deployed design; the new risk is this project's new layout, and that is already an open item.

Corrected statement: the wideband accuracy rests on Bosch's sensor spec plus firmware author's 0.5% fit claim to Bosch's table; no independent bench/gas comparison was found. Applies equally to ordered rev 0.9 boards, but it is not a defect, just a test item, and it is already listed as not covered.
Fix: bench plan R02 sec.10 (step 6 side-by-side with a commercial controller is the practical one). Do not rework boards.
