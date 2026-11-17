# C130 verdict: partly (true, but it is a "keep it" non-finding, already documented)
Checked: work/P08.../inj.py arithmetic (D40 path (V-Vr-Vf)/47: 14.4 V ~0.21 A, 24 V ~0.43 A; reproduces). D40/D41/Q20/U15 present identically on cur_db and ord_db (evidence/*/pcb_footprints.csv).
repo/VERIFICATION.md:573-574 already documents D40/D41 -> +3V3 and the U15 TL431 + Q20 shunt as the fault-current-into-+3V3 protection (Q20 342 mA/1.22 W worst case).
- Not a removal that can be made: the claim itself says keep the clamp. The "only because of D40/D41" part is not shown: the shunt also guards against an LDO failure/overvoltage on the MCU rail, which the note did not analyse. Ordinary-input injection ignores the F407 load too, so the 19.5 mA comparison against the F103 load is conservative, but "not needed" for other reasons is not established.
- Cost saving (~$0.43 + 2 extended fees) not independently priced; irrelevant since advice is not to remove.
- Ordered boards: shunt and D40/D41 exist on ord_db; no action.
Fix: none. Do not remove.
