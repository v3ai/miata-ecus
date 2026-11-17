# C006 consequence check: verdict PARTLY (real but overstated; already documented; severity medium)

Checked
- Ordered F1 = nSMD050-33V: Ihold 0.50 A, Itrip 1.0 A @25C, R 0.15-0.7 ohm (datasheets/txt/C70077 Table II). L1 = 500 mA / 0.3 ohm (VERIFICATION.md l.270).
- Derating: only a proxy exists (C883150 chart, BSMD1812-050 row: 0.50 A @25C, 0.35 @60C, 0.23 @85C). The nSMD050 curve itself is not in the datasheet text.
- Repo circuit sim (firmware/tools/circuit_sim_full.py l.507) is the source of 0.25 A @13.8 V, 0.45 A @8 V, ~0.6 A @6 V. Not independently measured; nobody has built the board.
- Drop at 6 V / 0.6 A: D7 ~0.4 + F1 (0.3-0.7 ohm) 0.18-0.42 + L1 0.18 -> U2 Vin ~4.8-5.2 V. LMR14020 dropout curve (Fig. 7) puts +5V below regulation under ~5.4 V. Arithmetic holds.

Consequence
- Hold current is not trip current. Trip is ~2x hold (about 0.7 A at 60C). The Miata ECU sits in the cabin, so 60C is more realistic than 85C. At 60C hold is 0.35 A, which covers the 0.25 A steady load. Only a 0.45-0.6 A cranking pulse of a few seconds exceeds hold, and it stays under trip. So a nuisance trip is unlikely and takes a hot, long, weak crank. The likely effects are the PTC heating, its resistance rising, and a bigger drop.
- The worst real effect is the brown-out. +5V sags to ~4.5-4.9 V while cranking at 6 V. The 3V3 rail is a regulator off 5V, so it likely stays up. Sensor readings and the wideband may glitch for about a second. A reset is possible but not shown.
- 85C ambient is not realistic for a cabin ECU. 85C plus self-heat is the only case where the steady 0.25 A load exceeds hold.
- So "high" is too strong. Medium: it is a low-probability hot-soak or weak-battery start issue, not a failure at first power-up.

Already documented: yes. VERIFICATION.md l.684 lists "F1 / L1 (logic supply, 0.5 A)... hot car with weak crank could trip it... a 1206 PTC of about 1 A hold and matching 1210 inductor fit the same pads (hand rework possible on the ordered boards)". rev 0.10 already fixed it (1.1 A 1812, 5050 L1). It is not news, except for the dropout/brown-out arithmetic.

Affects the ordered boards: yes (ord_db rev 0.9 has the 1206 F1 and 1210 L1).

Fix
- Cheapest: do nothing to the boards. Bench-measure supply current at 6/8/13.8 V and voltage across D7, F1 and L1. Hot-soak test the first car start. Rework only if it misbehaves.
- If you rework: swap F1 for a 1206 ~1.1 A PTC (check 33 V rating; the 1206L110/33NR C48985884 suggested was not checked by me) and L1 for a >=1 A 1210 or a 0 ohm link. Shorting L1 only loses the input filter and helps the drop. Jumpering F1 removes the logic-fault protection, so do that only as a bench test.
