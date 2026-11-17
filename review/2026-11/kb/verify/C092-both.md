# C092 verdict: partly (facts confirmed; consequence is documentation only, already largely handled)
Checked by eye: kb/research/files/R18/charm1999_pid_terminal_1_A-C-B.png (B+2 = "Constant: B+", PCM terminal 1H), _2_C-F.png (FTL V fuel tank level, 3K), wiring2000_B1a_connector1_table.png (1H = G/R, 1A = L/R, so 1A/1H are distinct always-hot feeds). The 30 A FUEL INJ fuse source of 1H was not independently seen.
Repo: pinouts_9605.md already marks 1H and 3K do_not_drive=YES ("Never drive"), and 1A (B+) in the 99-00 summary; 2K tach already listed with 3 sources vs Alex Engineering (flagged "Verify"). Only the labels ("unclear", "N/C or fuel gauge") are stale.
Boards: interconnect.md shows ord_mb9900 and cur_mb9900 have 1A, 1H, 3K with no net, 2K = OUT_TACH. Nothing is driven; no hardware risk, nothing to rework on ordered boards.
Corrected statement: Mazda's own tables identify 1H as constant B+ (B+2) and 3K as fuel-tank-level input; the repo's labels are vague but its handling (unconnected) is already correct. Doc-only, low severity.
Fix: relabel 1H/3K (and 1A) in pinouts_9605.md; optional.
