# C014 consequence check
Verdict: partly. Severity should be medium; already documented.
- Repo already documents it: review brief s6 ("harness headers are hard to buy") and VERIFICATION.md line 1113 names 176122-6 as obsolete at Mouser, "buy the headers ahead".
- Not "nearly unobtainable": Octopart (web search today) lists 176122-6 at Onlinecomponents/Master ~$16.43 falling to ~$9.78, 510 units; Verical $19.9 with 510; Newark 54M8253 $9.92 0 stock. Authorised stock zero, brokers have stock. Need is 1 per board, so a handful of pieces at ~$10-20 is a cost issue, not a blocker. Octopart data ~411 days old, unconfirmed.
- Consequence: affects only the seller's BOM/lead time (one part, hand-fitted, not JLC-assembled). Ordered boards can't change footprint; the 64P footprint is fixed. Board is unusable without a 64-pos header (or direct wire), so buy now.
- Fix: buy 10-20 from a broker/Sager now; check authenticity (pre-tinned pins, shape). Alternatives (178764-1 DigiKey stock 1679, Ballenger) footprint unverified; do not assume drop-in. The cheap fix is just buying now.
- Unverified: live stock; footprint equality of substitutes.
