# C004 source verification
Verdict: partly (technical content true, but already documented; not news).
Checked:
- Design: evidence/ord_mb8993/pcb_nets.txt line 40: OUT_FP = J1.2T, JD1.6 (2T is wired to the daughterboard output). kb/interconnect.md:104,229.
- repo/INSTALL.md:170-180 already states: pump switched by AFM contact, stock harness has no wire in 2T, AFM removal needs wire from F/P to 2T, "Unchecked on this board". README.md:97 repeats it. kb/pinouts/PIN-8993-B notes 2T "documented (INSTALL.md:170)".
- Car side: kb/pinouts/PIN-8993-B-car-inward.md:70 and wiring diagram transcription: AFM FC (LT GRN)/E1 contact goes to circuit-opening relay; ST signal also energises pump. Not independently re-read from the diagram image by me.
- Only real gap: repo/motherboards/1989-95/README.md:87 lists 2T "fuel pump relay" for all years (no caveat for 1990-93), a minor doc inconsistency. B14.08's point (F/P terminal identity unverified, may blow fuse) is covered by "Unchecked on this board" in INSTALL.
Ordered boards: electrically unaffected; 2T just stays unwired in the stock harness. Nothing to rework; only the install instruction matters.
Corrected statement: INSTALL/README already tell 1990-93 users the pump is AFM-switched and how to add an F/P->2T wire; remaining nit is the motherboard README table row, and the F/P wiring remains unverified against the workshop manual.
Fix: add "1990-93: no wire on stock car" to motherboards/1989-95/README.md row 2T; cite workshop manual for F/P terminal.
