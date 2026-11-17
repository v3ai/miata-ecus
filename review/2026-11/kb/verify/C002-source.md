# C002 source check
Verdict: partly.
Verified: ord_mb9495 and ord_mb8993 pcb_nets: OUT_TACH = J1.2I + JD1.11 (no jumper); ord_db: OUT_TACH = J1.11 + Q14.3 (low-side FET drain). cur_mb8995: HARN_2I = J1.2I + JP5.2, open. Ordered firmware (repo/ordered-boards/2026-11/firmware/board/miata_board.cpp:86) sets tachOutputPin=MIATA_TACH and has no miataNoTachOutput() at all, so the default tune drives 2I. Current firmware calls miataNoTachOutput() for 1989-93 and 1994-95 presets.
Not verified: that 2I is an igniter input on every car, and that the stock ECU supplies a pull-up. Both stay open (members disagree). Mazda tables not re-read here.
Already documented: repo VERIFICATION.md item 6 (line 119) and ordered-boards ABOUT.md:28 and INSTALL.md:258 say 2I may be the igniter signal and to set tach output to none. So it is known, but the ordered firmware default conflicts with the docs.
Affects ordered boards: yes (ord_mb8993, ord_mb9495). Cheapest fix is software: set tachOutputPin to none in the tune (or flash the current firmware). Hardware rework (cut trace or lift) only if the car needs an ECU tach.
Corrected: pull-up part is hypothesis; "dead tach" depends on car.
