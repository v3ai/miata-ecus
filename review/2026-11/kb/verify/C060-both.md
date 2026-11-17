# C060 verdict: partly (low-value as a board finding)
Checked: GitHub API for rusefi issues 6349/5730/5728/5729 (today).
- #6349 (uaEFI 150/460 ms dwell at sync loss) is CLOSED as completed 2024-04-18. Reporter confirmed "cannot reproduce" after rusefi commit 4bc38d3. The claim "open upstream" is wrong for this item. Pinned firmware (1374bd0) is far newer. Also uaEFI overdwell was a firmware trigger issue on a bench stim, not a hardware design issue.
- #5730 (short the oscillator test) is open: only a test request, no result.
- #5728/#5729: titles/bodies only (M73 damage photo, IGBT fire); no cause, not tied to this design.
- Not documented in repo VERIFICATION.md (grep dwell/watchdog), but firmware has an always-on overdwell cut at 1.5x dwell per upstream devs.
- Applies to ordered boards only as generic ECU risk; no netlist fact was checked by the claim.
Corrected statement: upstream sync-loss overdwell (#6349) was fixed in 2024; the oscillator-failure stuck-output test (#5730) remains untested; smoke incidents have no established cause. Generic risk, not a design defect.
Fix: keep the cheap first-article test (short oscillator, check ignition pins; spare coil/igniter at first start). Do not treat as a defect.
