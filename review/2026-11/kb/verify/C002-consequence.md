# C002 consequence check

Verdict: PARTLY. The wiring fact is true. The severity is overstated, the issue is already documented, and the fix is a firmware setting, not hardware rework.

Checked:
- evidence/ord_mb9495/pcb_nets.txt:48 and ord_mb8993/pcb_nets.txt:52: OUT_TACH is on J1.2I and JD1.11 with no jumper. The current board has JP5 and R37 (cur_mb8995 pcb_nets:12,57). True.
- repo/firmware/board/miata_board.cpp:95 sets tachOutputPin = MIATA_TACH. Lines 317 and 327 call miataNoTachOutput() for NA6 and NA94 (1989-93 and 1994-95). The frozen ordered firmware (ordered-boards/2026-11/firmware/board/miata_board.cpp:86) has no such call, so the tach is on by default there. The fix is already in the current firmware. Re-flashing over USB/DFU, or setting the tach output to none in TunerStudio, removes the contention. No board rework.
- The tach driver is a ZXMS6004FF low side (open-drain, current-limited, thermal shutdown). If the igniter output is also a low-side open collector, the two outputs are wire-ANDed and nothing is damaged. Nothing in the firmware reads 2I, so the ECU itself is unaffected. The worst case is a push-pull igniter output pulled low at 2 pulses/rev by a current-limited FET. That is unlikely to be destructive but is unmeasured.
- The "no pull-up, tach may be dead" claim (R09.01, PIN-9495-A.01) is not shown. Per the FSM members (PIN-8993-A.02), the cluster tach is fed directly from igniter terminal D and 2I comes from terminal E. The firmware has no IGf/2I input, so a missing ECU pull-up affects nothing in the ECU. I could not verify the wiki "MRE supplies pull-up" statement here. It is unverifiable without a car measurement.
- Already documented: repo/VERIFICATION.md lines 119-122 (pinout finding 6, "2I input or output?"), the open item at line 1110, and review brief section 6. The ordered INSTALL.md:258 says to check 2I. So it is not news.
- Ordered boards affected: yes (ord_mb8993, ord_mb9495), but only through firmware default and the unresolved direction of 2I.

Corrected statement: the ordered 1989-95 boards hard-wire the ECU tach driver to 2I. The ordered firmware enables it by default, and the current firmware disables it. The direction of 2I is still unresolved in the repo and unverifiable without a car. Severity is medium, not high. On a stock-igniter car, set the tach output to none or flash the current firmware before first start.

Fix: use the current firmware (miataNoTachOutput). Then measure 2I at key-on with the ECU unplugged (the stock car) and plugged. Only if a pull-up is needed, tack a ~1 k resistor to 5 V on 2I by hand. It is not needed before power-up.
