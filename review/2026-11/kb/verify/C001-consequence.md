# C001 consequence check
Verdict: confirmed (severity: high rather than critical; no hardware damage, one-part hand rework).
Checked: kb/parts_manifest.md lines 90/307: C25341 = 1206W4F620LT5E, "620mohm"; tools/lcsc.py C17971 = 1206W4F620JT5E, 62 ohm, extended, stock 123k, $0.0053.
Ordered BOM repo/ordered-boards/2026-11/daughterboard/fab/...rev0.9_jlcpcb_bom.csv:76 "62,R110,...,C25341". Current BOM same; design.py:64, wideband.py:153 (R10->R110).
pcb_nets (ord_db): R110 pins on LSU_RT and LSU_IP.
Firmware ext/wideband-mck1117 sampling.cpp:41: Ip = V / (gain 10 * 61.9). With 0.62 ohm the sense voltage is ~100x too small: 1 mA gives 6.2 mV x10 = 6.2 mV instead of 619 mV (~8 ADC counts per mA on 12 bit/3.3 V is consistent). Reported lambda sits near 1.0 (zero offset) regardless of mixture.
Does it damage anything? No. The pump loop is closed on the Nernst voltage (450 mV), not on measured Ip, so the true pump current is still regulated correctly; the sensor is not overpumped. Heater control uses Nernst AC impedance, unaffected. Only the reported lambda is wrong. Also the 0.62 ohm shunt no longer adds ~62 ohm to the pump loop; headroom just improves.
So: wideband (the product's main selling point) reads wrong, but the board is safe and the ECU still runs on a narrowband-free tune only if the user uses wideband for closed loop/tune: closed-loop lambda would be driven by a false ~1.0, a lean-risk if the user relies on it.
(a) Not documented: VERIFICATION.md:273 mentions R110 as 62 ohm 0603 C23222 (older rev 0.5b) and the 1206 change later reintroduced C25341. Not listed as open. News.
(b) Affects ORDERED daughterboard rev 0.9 (and current rev 0.10).
Fix: ordered boards: hand-replace R110 (1206) with 62 ohm 1% (C17971 or any 61.9/62 ohm 1206, 0.25 W OK; sensor-fault power 0.57 W already noted). Cost cents. A 0603 62R would also be wrong for fault power. Current: change LCSC_R1206['62'] and wideband.py:153 to C17971; add script check of LCSC resistance vs value. Cheaper alternative: none needed; firmware could not fix it (100x gain loss, ADC resolution).
