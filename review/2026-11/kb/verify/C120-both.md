# C120 verdict: partly (direction right, numbers box-dependent, carrier rules not primary-verified)
Checked: kb/research/R25 and R26 notes, clusters.json C120, repo docs (no mention of dim weight or carriers in VERIFICATION.md or review brief).
- Arithmetic OK: 9x9x4 RSC outside 9.375x9.375x4.625 = 406 in3; /139 = 2.9 (3 lb) nearest-rounded; 10x10x5=500 /139 = 3.6 (4 lb) rounded up. R26 used a different parcel (9x7x3, 189 in3 -> 1.36 -> 2 lb). The two findings assume different boxes; the stated 3-4 lb applies to the box actually proposed in R25.
- USPS DIM only above 1 cu ft (1,728 in3): matches general knowledge of DMM 283; R25 reports it fetched. The 139 divisor for UPS/FedEx is secondary (R25/R26 both say so). Price figures (12-16 USD UPS/FedEx, 7-9 USD USPS) are aggregator-level and unverified; I did not re-fetch live rates.
- Not documented in repo. Does not affect ordered boards (packaging/shipping only).
Corrected statement: for the proposed 9x9x4 box UPS/FedEx would bill about 3-4 lb versus 1-1.5 lb actual, while USPS stays weight-priced, so USPS Ground Advantage is likely cheaper; exact savings unverified (no live rate quotes).
Fix: get live quotes for the real packed box from USPS/UPS/FedEx (or a shipping platform) before deciding; default to USPS GA. Low-medium severity, advisory.
