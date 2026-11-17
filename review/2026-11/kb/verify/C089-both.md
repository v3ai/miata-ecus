# C089 verdict: confirmed (small saving; low urgency)

Checked:
- Design: evidence/{cur_db,ord_db}/pcb_pads.csv, U10 and U106 pads 1 TXD, 2 GND, 3 +5V, 4 RXD, 5 +3V3 (VIO), 6 CANL, 7 CANH, 8 STB tied to GND. Same on both boards. BOM is C485806 x2.
- Live data today (tools/lcsc.py): C485806 TCAN1042VDRQ1 extended, stock 207, $0.5957@30 / $0.5155@100 / $0.4042@1000. C132227 TJA1042T/3/1J extended, stock 62,251, $0.3142@30 / $0.2635@100 / $0.2406@1000.
- NXP TJA1042 datasheet (fetched, datasheets/extra/TJA1042_nxp.pdf): SO8 SOT96-1, TJA1042T/3 has the VIO pin (pin 5), the plain TJA1042T and CT have SPLIT on pin 5 instead. VIO range 2.8 to 5.5 V, VCANH/VCANL -58 to +58 V, STB low = Normal mode, CAN FD to 5 Mbit/s, Tvj -40 to +150 C. The "/3" in C132227 is the VIO variant, so it matches the 3.3 V VIO on pin 5 and the STB-to-GND wiring.

Corrections:
- Saving is $0.56/board at the $0.60/$0.31 tiers (2 parts) and is quantity dependent: about $0.51 at 100 and about $0.33 at 1000. Not a flat $0.55.
- No change in extended-fee line count (one extended line replaced by another).
- The claim's "$0.60 / $0.52" matches the 30 and 100 tiers. Stock of 207 is enough for 100 boards but thin, and the manifest recorded 257 earlier, so it is falling.
- The TJA1042 also has a wider temperature range than the TCAN (150 vs 125 C), so no spec regression found. I did not compare slew/propagation delay; both are CAN FD parts, irrelevant at the CAN speeds this board uses.

(a) Not documented: VERIFICATION.md only records TCAN1042V-Q1 as the fix for the 24 V rating (lines 575, 1123), nothing on alternates or stock.
(b) Ordered boards: the same part is on ord_db, but this is a cost/stock item, not an error. Nothing to rework; apply on the next order only. If the ordered assembly was blocked by stock this is moot now.
(c) Premises true, saving real but small.

Fix: change LCSC to C132227 on U10 and U106 for the next order. Check the JLC footprint rotation in the preview. Doing so also makes the part pin-compatible with the plain TJA1042T/3 family.
