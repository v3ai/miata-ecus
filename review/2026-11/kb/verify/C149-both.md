# C149 verdict: partly
Output true, mechanism wrong.
- Reproduced: scripts/track_current.py on repo daughterboard pcb prints "[OK] INJ1_CL worst 0.0 C: 0.00 A in 0.0 mm on - ... 4 pour(s)" (also in repo/daughterboard/fab/track_current.txt lines 8-11).
- Name mismatch is NOT the cause: main() maps each load net to the board net via its pads (on_board[(D42,'1')] = '/Outputs/INJ1_CL'); Net(b,'/Outputs/INJ1_CL') finds the 1.41 mm 0.8 mm F.Cu segment and both pads (D42.1, D46.1).
- Real cause: INJn_CL nets carry filled copper zones (zones list has /Outputs/INJ2_CL, INJ4_CL ...; "4 pour(s)"). The script treats a pour as a perfect conductor joining both pads, so the loop has no track current -> 0.00 A. By design of the model, not a lookup bug.
- Consequence: check passes vacuously for these nets, true; exposure is 0.2 A rms on 0.8 mm track plus pour (dT ~0.1 C like OUT_INJ at same 0.2 A/0.8 mm), so harmless.
- Not documented as an open item in review brief/VERIFICATION.md (only general method at VERIFICATION.md:840). Current design only (rev 0.10); ordered boards not affected by this tool output.
Corrected statement: the INJn_CL rows report 0.00 A/0.0 mm because the nets' own copper pours are modelled as ideal conductors between D4x.1 and D4(x+4).1, not because of a net-name mismatch; no real risk.
Fix: low value; optionally exclude pours for these nets or label "pour-bridged, not evaluated".
