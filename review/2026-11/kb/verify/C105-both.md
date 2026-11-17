# C105 verdict: partly (low value, not news)
Checked:
- evidence/{cur,ord}_db/fab_*self_order_bom.csv line 2: DB headers J1/J2 (C2977586) note "Solder while plugged into a motherboard's sockets so they come out straight". So the DB headers cannot be JLC-placed. This is documented by the repo itself. P18.06/R21.11 are right about the DB.
- kb/parts_manifest.md:123: motherboard J1 TE 174917-6 is [self-order]. Live (tools/lcsc.py): C592838 Extended, stock 32, $12.92@1, $12.74@10. JLC stocks it, so a JLC THT quote is possible. Sockets JD1/JD2 C124412: extended, stock 65. C412098 (JST S08B-PUDSS-1): extended, stock 10084, $0.36@1, $0.29@50.
- The "conflict" is no conflict. Headers (DB) cannot be machine-placed. MB-side parts (J1 harness header, sockets JD1/JD2, JST J2) could be, as the suggested fix says.
- The benefit is unquantified. The claim's own figures: $3.58 per order + $0.0164 per joint, plus extended-part fees. The MB-side parts have about 48 + 80 + 8 joints. At that rate JLC THT costs about $2-3/board in fees, against a few minutes of seller labour. Stock of 32 for J1 caps the batch. The claim gives no saving figure.
- The I did not verify JLC's current THT page myself.
Ordered boards: no. This is an ordering and process choice, not a board defect. Nothing to rework.
Corrected statement: DB J1/J2 must stay hand-soldered in-socket (repo documents this). Only MB-side THT parts (harness header J1, sockets, JST) could go to JLC THT; the saving is small and unquantified, and J1 stock is 32.
Fix: optionally get one JLC quote with MB THT parts as library parts; do not expect a large saving.
