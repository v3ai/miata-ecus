# C070 verdict: partly (packaging advice; facts mostly true, parts unverified, not a board defect)
Checked (saved Uline/LCSC pages in kb/research/files/R25/):
- S-5891 pink bag page says "Does not meet MIL-PRF-81705D & E", resistivity <10^12 ohm/sq: TRUE.
- LCSC C7543868 = MOLONG static shielding bag 7.5 mil 210x240 mm: exists. I did not extract its $0.056 price.
- Uline S-15325 24x24x1 in foam: $15 at 1, $13 at 6+ (page table): TRUE. 4 pads of 9x9 per sheet = 2 top+bottom kits, so $7.5/kit: arithmetic OK.
- Box: 9x9x4 in = 229x229x102 mm. (229-154)/2=37, (229-162)/2=33, (102-35)/2=33.5 mm: arithmetic OK. Uline S-21587 is a 9x9x4 box.
- Alibaba die-cut prices/MOQ (UNVERIFIED in source), MLCC flex 2-3 mm vs 5-10 mm (secondary vendor claims, marked unverified by its author), "shield bags stop ~97%" (secondary).
Not verified: custom foam prices, MLCC flex figures, that shielding bag is needed at all (a pink or shield bag is a choice, not an error).
(a) Not in review brief or repo/VERIFICATION.md (no hits for foam/ESD/shield); it is a review recommendation only, not news-free but low stakes.
(b) Ordered boards: only shipping packaging, nothing to rework on boards. The MLCC-near-holes check is a layout idea, unverified, no specific capacitor identified.
Corrected statement: Pink poly is low-charging, not shielding (Uline-confirmed); metal-in shield bags cost cents (LCSC) to $0.57 (Uline). A 9x9x4 in box fits the stack with 25 mm foam (arithmetic). Stock pick-and-pluck foam is about $7.5 per top+bottom kit. Custom foam prices and MLCC flex limits are unverified secondary claims. Severity low.
Fix: ship in a shield bag with foam supporting at the standoffs and rim; get a foam quote before committing.
