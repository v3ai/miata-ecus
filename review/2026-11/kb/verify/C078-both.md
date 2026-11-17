# C078 verification: partly
Checked:
- default_ignition.cpp:112-115 (pinned rusEFI): setConstantDwell(4); voltage-corr bins 8..15 V, values all 1.0. TRUE. Cranking dwell 4 ms set in repo/firmware/board/miata_board.cpp:212.
- ignition_state.cpp:352-388: dwell = base * voltage correction; no clamp. Correction table is user-editable, so the capability exists; only the default is flat.
- "No max-dwell guard": only partly true. spark_logic.cpp:561-575 checks dwell angle > cycle/2 (or cycle/cylinders/1.1 for one coil) and raises warning CUSTOM_DWELL_TOO_LONG, but it only warns, does not clamp. The maxdwell check at engine_controller.cpp:599 is MC33810-only (true). No guard limits absolute ms for GPIO igniters.
- Consequence: a constant 4 ms is not over-dwell by itself (4 ms is rusEFI's standard conservative coil default; at 6500 rpm a 4-cyl wasted-spark period is ~18 ms). Coil death needs a firmware fault or user mis-tune holding the output on. Low-voltage cranking under-charge is real but is a tuning matter: the voltage table exists. Forum claim (miataturbo threads) not re-checked; no stock NA igniter/NB coil dwell figure was found by anyone, so the right dwell is unknown.
- Documented? Not in VERIFICATION.md as an open item (only simulated "4.00 ms dwell", line 404). Not news-critical, though.
- Ordered boards: hardware unaffected; firmware-only, applies to any build flashed. Nothing to rework by hand.
Corrected statement: Defaults are flat 4 ms with 1.0 voltage correction; rusEFI only warns (no clamp) on excessive dwell angle and has no ms cap for GPIO coils. Real risk is low-battery under-charge and unverified coil spec; over-dwell would need a fault/mis-tune.
Fix: before first drive, confirm coil dwell from coil datasheet/known-good tune, fill dwellVoltageCorr table (e.g. >1 at 8-11 V), cap with a lower table max; cheap, firmware config only.
