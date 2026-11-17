# C042 verification (both: factual + consequence)
Verdict: PARTLY. Derating numbers and topology are true; trip at realistic conditions is marginal, effect is fail-safe. Severity low (not medium).

Checked
- Datasheet datasheets/txt/C46641168 (Thermal Derating Chart): SMD1812-200 hold 2.00 A @25C, 1.80 @40, 1.66 @50, 1.45 @60, 1.09 @70, 0.80 @85. Matches claim. Itrip 4.0 A.
- Board: evidence/ord_mb0105 pcb_footprints F2,F3 = C46641168; kb/interconnect.md: OCV_12V = D2.1 F3.2 J1.4D, VBAT_IN to F3.1. Freewheel diode D2 is on the load side of F3, so PTC carries only the on-time current (mean = D*I, rms = I*sqrt(D)); it does not see recirculating current.
- Firmware miata_board.cpp:288-294: VVT PWM via auxPid[0], max 90 %.
- Coil: 6.9-7.9 ohm at 20 C (2002 FSM via PIN-0105-B notes; not re-fetched by me). 14.4/6.9 = 2.09 A peak; 13.8/7.4 = 1.87 A.
- Correction to the claim: "about 1.1 A rms at 50 %" is the mean; rms is 2.09*sqrt(0.5)=1.48 A (PTC heats on I^2R). Threshold rms 1.45 A at 60 C is reached at about 48 % duty with a cold 6.9 ohm coil and 14.4 V, but about 60-70 % with a warm coil (R rises about 0.4 %/K, 8.5 ohm at 14 V gives 1.65 A, 1.45 A rms needs 77 %). At 25 C ambient trip needs more than 2.0 A rms, i.e. near 100 % duty at 14.4 V on a cold coil.
- Trip is slow (hold-to-trip region, seconds to minutes), PTC resets after cooling. Failure mode: spool returns to full retard (per FSM inspection note), no damage.
- Not hold-at-100 %-duty typical: Mazda OCV runs mid duty; no firmware or measured duty profile found. I could not verify the duty seen by a real NB2 in a hot case, nor the 60 C case-ambient assumption (stock case is in the cabin under the passenger side).

(a) Already documented? Not for F2/F3 derating. VERIFICATION.md N5 and line 684 cover only F1 PTCs; line 1182 and 1136-1137 mention F2/F3 only as 2 A resettable. review brief section 6 only lists PTC voltage ratings. So it is new but small.
(b) Ordered boards: yes, ord_mb0105 (rev 0.7) has F3 = C46641168, same as current. F2 exists on NB1 (1996-97, 1999-2000) and NB2 boards; F3 only on 2001-05. Rework by hand is possible: 1812 footprint, swap to a higher-hold part is hard (no 1812 3 A part above 8 V per N5), so the practical hand fix is a jumper/3 A 2920 or a bodge; or do nothing and accept fail-safe.
F2 (idle valve, 7.7-12 ohm, mean about 0.8-1.9 A) is less exposed than F3.

Corrected statement: F3 (VVT, 2001-05 only) and F2 (idle) are 2 A-hold PTCs that carry the valve on-time current (flyback on load side). Hold derates to 1.45 A at 60 C; with a 6.9-7.9 ohm OCV, rms current reaches that at about 50-75 % duty. A trip needs a hot case plus sustained high VVT duty; consequence is temporary full retard, self-resetting, no damage. Low severity, unverified duty cycles.
Fix: next revision use a higher-hold PTC for F3 (2920 3 A like F1, C22446884) or a 3 A fuse; or firmware cap on VVT duty. Cost small. Better: measure OCV duty on a real car.
