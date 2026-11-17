# C041 verification: partly (pin-table conflict refuted; VICS-not-driven true but documented)

Checked:
- rusEFI hellenMiataNB1/connectors/main.yaml: 1U = front O2 heater, 3Q = VICS (type inj), 4E = VVT (rusEFI board uses a 4-row connector).
- repo/scripts/mb_nb1.py:32-33,53,81: 1U -> net OUT_VVT (front HO2S heater, "no VVT on NB1"); 3Q -> net OUT_MAINRLY (VICS solenoid). evidence/ord_mb9900/pcb_nets.txt: OUT_VVT = J1.1U+JD1.34, OUT_MAINRLY = J1.3Q+J5.5+JD1.7. Same on cur_mb9900 (interconnect.md).
- firmware/board/miata_board.cpp:267-269: o2heaterPin = MIATA_VVT (1U heater); mainRelayPin unassigned on NB1; comment says MAINRLY drives VICS, rusEFI has no VICS strategy. test_miata_ecu.cpp:695 asserts this.
- research/pinouts_9605.md:153,187: 1U front HO2S heater, 3Q VICS solenoid (matches rusEFI).
- Documented: README.md:103 ("VICS solenoid is wired but not set up"), INSTALL.md:51, daughterboard.yaml:15.

Result: R30.05's "conflict" is a misreading of net NAMES (OUT_VVT/OUT_MAINRLY are just the driver channels reused). Function by cavity agrees with rusEFI: 1U = O2 heater, 3Q = VICS. No conflict, no wrong output on a heater/VICS wire. Not newly wrong; same on ordered boards (rev 0.7).

Remaining true part: the NB1 VICS solenoid is never driven in firmware (stays off). Consequence (VICS stuck in one state, torque loss at low/mid rpm) rests on an unverified forum report; which state de-energised gives is not established here (FSM needed). No damage. Already known/documented in README, but the performance consequence is not spelled out. Affects ordered boards equally (wiring is correct; it is firmware only, fixable by a GPPWM/ rpm-based output in firmware, no rework).

Fix: none for hardware. Optionally add a firmware GPPWM/rpm rule for MAINRLY on NB1 after confirming polarity from the 1999 FSM; mention the possible low/mid torque effect in README.
