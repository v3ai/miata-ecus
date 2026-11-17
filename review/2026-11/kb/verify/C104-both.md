# C104 verdict: partly
Checked repo/scripts/order_bom.py (JLC_ROT lines 217-224, JLC_OFFSET 238-240), repo/VERIFICATION.md 288-293 and 1086-1091, evidence/cur_db/pcb_footprints.csv.
- TO-252 is NOT unconfirmed: order_bom.py comment and VERIFICATION.md say TO-252 +180 was read off JLC's preview of the rev 0.5 daughterboard. Claim wrong for Q1-Q8, Q101 (though their footprint/part differs, 2-pad TO-252-2 here; only the package family was seen).
- True: PG-DSO-8 (U3/U14) +270 is by analogy with SOIC (seen on SOIC-8/16); J4 has no JLC_OFFSET; microSD (Molex 47219, rotation 180 in KiCad, no correction), tact switches, new TVS/diodes were not in the rev 0.5 preview. VERIFICATION.md 1090 lists only the card socket's rotation as an open item; the rest is not listed.
- No community entry claim is unverifiable/irrelevant; the repo's source is JLC preview, not a community list.
- Ordered boards: not affected as a design flaw; fab CPL rotation is checked in JLC's preview at order time and could be fixed at JLC. Claim says ordered=false; no contrary evidence found.
Corrected: PG-DSO-8, microSD (J4 offset), new TVS/diodes, switches rotations unconfirmed; TO-252 was confirmed on rev 0.5. Severity low-medium (caught by viewing JLC's preview before paying; assembly review also shows it).
Fix: view CPL in JLC's preview for those refs and record offsets.
