# C121 verdict: partly (mostly already documented; low value)
Checked repo/INSTALL.md lines 93-105, 185, 241 and repo/motherboards/1989-95/README.md lines 135-156, evidence/cur_mb8995/pcb_footprints.csv, kb/parts_manifest.md.
- True: JP1-JP6 exist (JP1/2/3/6 are 1x3, JP4/5 1x2). 94-95 needs JP1,JP2 SEQ, JP3 94-95, JP4, JP6 AFM = 5 shunts; 89-93 needs JP3 and JP6 = 2. BOM carries 6 shunts (C5305), which covers both. A 94-95 car left in the default state would have 2Y/2Z undriven, as stated.
- Not true: "repo has no per-year assembly sheet". INSTALL.md has a per-year jumper table (1989-93 vs 1994-95 columns), a 1989-93 line (l.185) and a 1994-95 line (l.241); the 1989-95 README has the full table. 6 shunts is not a mismatch (max needed is 5).
- R20-R22: README l.148 states they are NOT fitted by default and fit only if the car's signal switches to ground; "default stated" is therefore true (not fitted).
- Open JP3 is undriven fan2 (not a safety issue); documented as a jumper function.
- Remaining small gap: no seller-side one-page sheet saying which shunts to fit at assembly for a given year; unclear whether the board is sold with the year fixed. Also the B.03 text about JP1/JP2 default pre-dates the 2026-11-15 change (no shunt = stock 89-93, now documented).
- Ordered boards: not affected as a new finding (cur_mb8995 rev 0.13 only; ordered 1989-93 / 1994-95 are separate boards).
Fix: optional one-line seller checklist per year; severity low.
