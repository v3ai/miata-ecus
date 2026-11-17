# C116 verdict: confirmed (as a removal option; small saving)
Checked:
- Supported cars: research/pinouts_9605.md lines 7-8, 162-164, 251-254: NA 1989-97 CAS is Hall; NB CKP/CMP are 3-wire Hall. Only the 1996-97 crank-pulley CKP (4E/4H) is possibly VR, and no board net connects to it (evidence/cur_mb9697/pcb_nets.txt has no 4E/4H net; Hellen also leaves it open).
- VR nets: kb/interconnect.md lines 70-73, 157-160, 261 show J2.19-22 (VR1/2 P/N) go only to AUX J5.7-10. repo/scripts/mb_common.py: trigger_select() (VR 0R-link option) is defined but never called, so no year board routes crank/cam to VR.
- Group on cur_db: U9 LM2903 (C7549), D15-18 BAT54S, R51-54/56-59 5.1k, R73-80, C48/C49/C60 = about 24 parts (claim says 27); VERIFICATION.md line 274 and 295-305 describe it as "spares". PE12/PE13 = VR1_OUT/VR2_OUT (pcb_nets, design.py:407).
- Cost ~ $0.25/unit at qty 50 (my sum from claim's prices), plus the extended-part fee for C7549 (the BAT54S C19726 is still needed for D36/D37). Real but trivial vs $399.
Corrections / caveats:
- NOT news that no car uses VR: the repo says so (VERIFICATION.md 274). The removal recommendation itself is not documented.
- It is a documented product feature: README.md:78 advertises "two inputs for magnetic (VR) crank and cam sensors" and J5 labels VR1/VR2. Removing it is a feature cut, so also edit README/J5 docs and any firmware config using PE12/PE13.
- Ordered boards: ord_db rev 0.9 also has U9 (sch_bom line 86), but removal would only be hand work with no benefit; this is a future-rev item. Not an ordered-board defect.
Fix: DNP/variant the group (keep harness pads/J5 if wanted) in the next rev; update README/docs. Severity: low (saves ~$0.25 + ~$3/order), not medium.
