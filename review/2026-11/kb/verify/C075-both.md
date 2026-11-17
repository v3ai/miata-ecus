# C075 verdict: partly (medium -> low)

Checked:
- Pin: repo/firmware/wideband/miata_wbo_f103.txt = 27e115b (2026-01-24). work/R02.../master_not_in_pinned_log.txt lists 9295698 (2026-04-10 "avoid trying to heat when battery voltage is low") and 91aa7c6 (2026-04-03 "ignore firmware update request without an ID") as not in the pin. True.
- git show 9295698: in can.cpp, vbatt < HEATER_BATTERY_OFF_VOLTAGE now forces NotAllowed. Before, vbatt < 5 was treated as bogus and replaced by 14 V (so USB-only could look like 14 V). That does address the #71 scenario.
- #71 (rusefi/wideband) is open, F042, created 2026-01-21, as quoted. The pinned heater_control.cpp (lines ~55-80) already has a partial guard: with Allowed it still checks supply voltage < 8.5 V. The remaining hole is the CAN vbatt<5 -> 14 V default. #71 and #348 are F042/CAN-voltage cases; this board has no local heater-voltage sense, so it relies on ECU-reported vbatt.
- Issue 348 is in mck1117/wideband (closed, 2026-02-07), not open. The note's "via API" is right only for that repo; rusefi/wideband/348 is 404. The claim "filed after the pin" is true (Feb 7 vs Jan 24); it was closed, not unresolved.
- Rest of R02.05/R31.07 (295, 303, 309 unprotected inputs; JLC rev B boards reading 1.01) were not re-checked. 309 is open (inputs not protected); the repo already lists it as N3 in VERIFICATION.md (line ~505) and "LSU drive resistors sacrificial" in review brief section 6.

Already documented? Partly: USB-only bench power is in VERIFICATION.md (line 1168, back-feed only) and N3 is known. The pin lag and the #71 underheat latch are not documented (grep for 27e115b, underheat, 9295698 in repo finds nothing outside the pin file).

Ordered boards: hardware is not affected; this is wideband-MCU firmware flashed after the boards arrive, so no rework needed. It can be fixed in the firmware pin.

Corrected statement: The pinned wideband firmware (27e115b, Jan 2026) lacks ~41 later upstream commits, including 9295698 (no heating when ECU-reported battery voltage is low), which addresses open issue #71 (underheat latched when ECU runs on USB only with forced heating). Impact is bench/USB-power use; no PCB change. The 91aa7c6 fix is minor.
Fix: bump or cherry-pick 9295698 and 91aa7c6 after diff review, rebuild miata_wbo_f103.bin, and bench-test USB-only then 12 V. Costs nothing but a rebuild.
