# C053 verdict: unverifiable (as a defect); arithmetic shows ample margin for any plausible input

Checked: design.py:297-335 and ord_db footprints. The ordered rev 0.9 board has the same chain (TC4427 at +5V, R15-18 100R 1206, D31-34 B5819W, R144-147 3.3k 1206), so the claim applies to the ordered boards.
Arithmetic (my own): the load is the 3.3k pull-down plus the igniter input. With the Schottky near 0.2-0.3 V at a few mA and the TC4427 at about 1 ohm, the high level is:
- 3.3k only: about 4.6 V.
- igniter input of 1k (about 5 mA total): about 4.1 V.
- igniter input of 500 ohm: about 3.6 V.
The usual 5 V IGT logic threshold is 2-3.5 V, and Hellen uses 5 V drive too. No primary source for the stock igniter's input current or threshold was found, here or by the originating audit.
So the fear is speculative: the margin only fails for an input under about 500 ohm, which is unlikely for a logic-level IGT line (stock ECUs drive it from a small driver).
Not documented in review brief section 6 or VERIFICATION. Mention of "Unprotected ignition outputs" only covers short protection.
Corrected statement: high level is about 4.1-4.6 V for input impedances of 1k or more; the actual igniter threshold and input impedance are unknown, so a bench scope check at first power-up is prudent. Severity low.
Fix: none needed. Scope the loaded IGT pin at first run. The 47R change is unnecessary (it would also cut short-circuit protection of the 1206).
