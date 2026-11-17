# C024 source check (international shipping, import VAT/DDP)
Verdict: confirmed for every USPS price; VAT/DDP rules plausible but not re-checked by me (secondary for me, primary per R26).
Checked against kb/research/files/R26/usps_notice123_2026-10-04.txt (Notice 123):
- FCPIS 9-16 oz retail (price-group tables): Canada(g1) 26.00; AU/NZ(g12) 41.25; FR(g15) 29.40; DE(g16) 29.95; JP(g17) 33.95; UK(g20) 31.95. All match. Country-group mapping (FR 15, DE 16, JP 17, NZ 12, UK 20) matches the country table.
- PMI 1 lb retail: CA 43.55; AU/NZ 70.65; FR 69.50; DE 82.30; JP 66.05; UK 69.70. All match.
- Intl insurance PMI/PMEI: up to 200 USD fee 0.00; 300.01-400 = 17.55. So CA 43.55+17.55=61.10, UK 69.70+17.55=87.25. Correct. (Note: this means 200.01-300 = 13.85; 400 cover is the 17.55 tier.)
- Prices include the holiday temporary increase (to 2027-01-17) per R26's assumption; may fall slightly after.
Not re-checked: gov.uk 135 GBP VAT rule, EU 150 EUR IOSS, USPS DDP country list (Postal Bulletin 22707), express DDP fees (R26 itself marks these secondary/unverified).
(a) Not in review brief section 6 or VERIFICATION.md (no international shipping content there; website README only mentions a Shipping page). Not news in the sense of being undocumented, but it is business-policy advice, not a board defect.
(b) Does not affect ordered boards (ordered=false is right).
(c) Premises true; the "saving" (DDP so buyers see no border bill) is not quantified: no USPS DDP fee stated, none for AU/NZ/JP. Assumes seller is in the US (R26 assumption, owner location unknown). The statement truncated in clusters.json mentions "Royal Mail 8 GBP" fees as secondary.
Corrected statement: as written, with the caveat that the seller is assumed US-based, DDP fee unknown, and the VAT/threshold figures are from R26's reading of gov.uk/Postal Bulletin, not independently confirmed here.
Severity: medium (policy/cost advice, no design impact).
Fix: quote international shipping at checkout (PMI with full cover ~61 CA, ~87 UK), use USPS DDP where available (CA, DE, UK 135-900 GBP, many EU), warn AU/NZ/JP buyers of GST/consumption tax.
