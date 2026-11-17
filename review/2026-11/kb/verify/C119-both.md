# C119 verdict: partly (numbers true; not a board finding)
Checked kb/research/files/R26/usps_notice123_2026-10-04.txt (USPS Notice 123 text):
- GA commercial parcels <16 oz, zones 1-9: 7.33..8.95 (4/8/12/15.999 oz identical). TRUE.
- GA retail: 4-8 oz 8.40-10.20; 12-15.999 oz 10.05-13.65. Claim's 10.05-13.65 holds only for 12-16 oz.
- Insurance 300.01-400 = 6.05; 100.01-200 = 4.50. TRUE. Signature Confirmation GA commercial electronic 4.15 (retail 5.15). TRUE.
- Total 7.33-8.95 + 4.15 + 6.05 = 17.5-19.2 before box, so "14-18 all-in" is understated by roughly 2-4 USD (box extra). The 3.5-4.5% figure becomes ~4.4-5%.
- Parcel weight <16 oz is assumed, not measured; if above 1 lb, commercial is 8.01-11.22 (zone 1-9, 1 lb). Whether the shipment includes any stock case is unclear (customer's case is used).
- Consequence "299 USD uninsured": the "100 USD included" figure was not verified by me in Notice 123 (not in the fee table); plausible.
- Prices are temporary holiday rates to 2027-01-17 (per originator; not independently checked).
Not documented in review brief s6/VERIFICATION.md (no shipping hits). Not a board issue: ordered=false, no effect on ordered boards. A business-practice suggestion, not an error.
Corrected statement: USPS GA commercial <16 oz 7.33-8.95; Signature Confirmation 4.15 and 399 USD cover 6.05 add ~10.2; with box about 18-21 USD (~4.5-5% of 399), not 14-18.
Fix: budget ~20 USD/order; buy labels at commercial rates; re-check after 2027-01-17.
