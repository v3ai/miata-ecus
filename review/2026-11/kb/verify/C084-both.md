# C084 verdict: confirmed (mechanism), consequence partly overstated
Checked repo/firmware/ext/rusefi at 1374bd0:
- mazda_miata_1_6.cpp:146 sets idleRpmPid.minValue = 20; no maxValue set. Default maxValue = 20 (engine_configuration.cpp:525). efi_pid.cpp:114-118 clamps max first then min, so PID output = 20 always.
- Repo board code (board/miata_board.cpp) only overrides idleRpmPid for NB (lines 220-226); NA6/NA94 presets (l.303-326) just call setMazdaMiataNA6/NA94. Same in ordered-boards copy.
- Open-loop: miata_base_maps.cpp:33-34 tuned 28->20 curve is commented "todo"; default (engine_configuration.cpp:365-371) is 75->50 %.
- idle_thread.cpp:466-483: iacPosition = openLoop + closedLoop, clamped. So closed loop = constant +20 offset, no RPM feedback: README "closed-loop idle" (README:51) not delivered on 1989-95 (also only if TPS valid).
Corrections: "clamped to constant 20%" is exact, but "may be unstable" is wrong: a constant offset cannot oscillate; the real risk is idle far off target (open loop 75..50 +20 = 95..70 % duty, probably very high RPM) with no correction. Duty-vs-valve mapping not verified on a car. Upstream rusEFI bug, inherited unchanged (also present on Hellen NA6).
(a) Not documented in VERIFICATION.md/README as an open item (grep found nothing). Not news-free.
(b) Firmware only; affects ordered boards equally but fixable by reflash, no hand rework.
Fix: in miataApplyYearPreset NA cases set idleRpmPid.maxValue (e.g. 40) and minValue (e.g. -20), plus load 28->20 cltIdleCorr curve; test on car. Cost: a few lines.
