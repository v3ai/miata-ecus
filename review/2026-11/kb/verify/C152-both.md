# C152 verdict: partly (true, but small and a judgment call)
Checked:
- evidence/cur_db/pcb_nets.txt:218 V5_SENS = C25.1 J2.1 U3.1; all four cur_mb* nets: V5_SENS = C1.1 C2.1 JD2.1 U2.3 (MAP only; no harness wire). design.py:488-489 says the same. ord_db has the same net.
- design.py:243-248: U3 = TLS115B0EJ, in +5V, supply +12V (C24), out V5_SENS + C25. U14 (design.py:490) stays for harness 5 V, so the extended-part line remains.
- MPX5700AP datasheet: supply current 7 typ / 10 mA max, Vs 4.75-5.25 V. A ferrite (FB1 C80165, 1.4 A, 100 mOhm) costs about 1 mV drop; sensor is ratiometric.
- Price: C3743696 $1.2615 at qty 1, $0.8688 at higher tier (kb/parts_manifest.md); ferrite $0.0149. Saving is about $0.85-1.25 less one cap (C24), about 0.2-0.3 % of $399. The "$1.09" is within that range.
- Not in review brief section 6 and no "tracker/U3" item in repo/VERIFICATION.md, so not documented.
Not true / caveats: "exposes MPX5700AP to short-to-battery" for the Hellen single-tracker style is moot, since V5_SENS never leaves the board and U14 already isolates the harness; the real loss of U3 is current limiting (a failed MAP loads the +5V buck instead of a 150 mA tracker) and tracker PSRR (85 dB) vs a ferrite+1u RC for buck ripple on the MAP supply. "Works on USB-only power" is plausible (U3 needs +12V) but not tested; USB-only MAP matters little.
Ordered boards: ord_db has U3 too, but the saving is cost-only, so no rework value; affects_ordered = no.
Fix: optional rev 0.11 cost cut: replace U3 with FB1-type ferrite +5V -> V5_SENS (keep C25). Keep if MAP isolation preferred.
