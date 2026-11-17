# C016 consequence check
Verdict: PARTLY. Severity medium, not high (low for the naturally aspirated cars the product targets).

Facts confirmed in firmware:
- default_fuel.cpp:336 lambdaProtectionEnable=false; :405 mapEstimateTable flat 60 kPa; limp_manager.cpp:168-171 boostCut only if boostCutPressure!=0 AND MAP valid; default_base_engine.cpp:443 only the CLT rev-limit X bins are set, useCltBasedRpmLimit off. The repo's board code (firmware/board) sets none of these (grep: only rpmHardLimit=7200).
- Flat-60 fallback: speed_density_airmass.cpp:187-193, used only when Sensor::get(Map) is invalid (sensor/wiring failure). WOT NA ~100 kPa fuelled as 60 kPa gives about 40 % too little fuel (lean) until the sensor fault is fixed; rusEFI raises a MAP fault code but keeps running.

Consequence:
- Boost cut matters only on forced-induction cars. Stock Miatas never exceed ~100 kPa, so a 0 default is harmless; the base tune VE table is flat 80 % above 100 kPa (firmware/README.md:109-110) and the README (:243, README.md:86) already says a turbo car needs a tuner before full throttle. So documented, not news, for boost.
- Lambda protection is a rusEFI-wide default-off feature that needs a tuned wideband target and thresholds; enabling it on an untuned base tune risks false cuts. Fix of "enable with sensible limits on all presets" is unsafe without per-car tuning; boostCutPressure ~150-160 kPa preset is cheap and safe only for cars that stay NA/low boost (it would never trigger on NA, so harmless, and gives a backstop for a bolt-on turbo owner).
- CLT limit: Miata fan temps are set; overheating protection by rev limit is a convenience, not a base-tune safety item.
- Flat MAP fallback is the only item with real NA consequence, but it needs a sensor fault (rare); cheap fix: fill mapEstimateTable with a plausible TPS x rpm table (e.g. 35-45 kPa idle to ~95 kPa WOT) in the preset, a firmware-only change.

(a) Partly documented (turbo needs a tuner; weak-tune note). Fallback table and CLT limit not documented.
(b) Ordered boards: not a hardware issue; firmware is flashable, no rework. "ordered: true" is moot.
Fix: set boostCutPressure (e.g. 160 kPa) and a mapEstimateTable in presets; document lambdaProtection as opt-in. No cost.
