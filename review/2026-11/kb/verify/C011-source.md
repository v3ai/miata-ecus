# C011 source verification (primary sources lens)
Verdict: PARTLY. Facts about the placeholder are true but already documented. "Real data exists" is overstated: the Hellen holes are Hellen's own design, not proven to be the stock Miata case.

Checked
- repo/scripts/mb_na6.py:18-60 and mb_later.py:1-12: 96-05 boards reuse the NA notched 154x161.5 outline, holes (17,7.3)(137,7.3)(4,84)(150,84)(4,143)(150,143). mb_later.py literally says PROVISIONAL, "Do not order this board before the case is measured". repo/README.md:175-177 and :253 also say the case geometry is a placeholder. So not news (review brief s.1 "Problems affecting ordered boards", but this one is a known open item).
- evidence/ord_mb9697 pads: H3..H6 are 4.5 mm PTH at (104,134),(250,134),(104,193),(250,193) -> the same NA placeholder holes, so the ORDERED 96-97 board has them. Whether it mounts is unknown (see below).
- Hellen NA8-96 / NB1 / NB2 KiCad (ext/hellen-miata-NB1, NB2; work/B10.../ext_dl/hellen-miata-NA8): six MountingHole_4.5mm_Pad footprints at x 26.098/170.098/170.049, y 16.805/98.805/165.605. Origin offset 21.1,11.7 gives holes (5.0,5.1)(149.0,5.1)(5.0,87.1)(148.95,87.1)(5.0,153.9)(149.0,153.9). Identical in all three boards (same Hellen 64-pin template). Claim text has a typo: last hole is y=153.9, not 153.1.
- Offsets vs placeholder: x 1 mm, y 3.1 mm mid pair, bottom pair 143 vs 153.9 = 10.9 mm; top pair missing in the Hellen sense (Hellen has y=5.1, ours 7.3 at x 17/137 -> different x, 12 mm). True as stated. Board height 159.0 vs 161.5 = 2.5 mm. True.
- Not verified: "5.0 mm drill" (footprint name says 4.5 mm; audits measured pad data elsewhere) and "R7 corners"; I did not re-extract these. Header 1A position not re-derived.

Why "real outline" is overstated
- Hellen's own NB README/finding B11.02: Hellen ships in a donor Camry case with its own mounts. The identical hole pattern on NA8, NB1 and NB2 boards suggests a Hellen design reused, not the Mazda case. No primary source (R18.06, R19.08, R17.03) gives the stock 96-05 case dimensions. NA6 notched outline matching the old Hellen NA6 board is plausible for NA 89-95 only.

Corrected statement
The 96-2005 motherboards (ordered and current) use the NA 89-95 outline and holes as a documented placeholder. rusEFI Hellen NA8/NB1/NB2 boards use a 154x159 outline with six holes (5.0,5.1)(149.0,5.1)(5.0,87.1)(148.95,87.1)(5.0,153.9)(149.0,153.9); these are a candidate, not confirmed to match the stock Miata case. Whether the ordered board fits a stock case cannot be settled without measuring a case or ECU.

Fix: measure a stock 96-05 ECU case (or board); until then do not rely on either pattern. Low-cost hedge: add Hellen's six holes as extra slots if the case is unknown (new revision; ordered boards cannot be changed).
