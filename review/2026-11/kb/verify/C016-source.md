# C016 source verification
Verdict: partly (code facts true; severity overstated; not a board issue)
Checked in repo/firmware/ext/rusefi/firmware:
- default_fuel.cpp:336 lambdaProtectionEnable=false; :405 setTable(mapEstimateTable,60) (flat 60 kPa) - true.
- speed_density_airmass.cpp getMap(): mapSensor.value_or(logAndGetFallback) - fallback is mapEstimateTable[rpm][TPS], flat 60 by default - true.
- limp_manager.cpp:165-171 boostCut only when boostCutPressure!=0 and map.Valid; default is 0 (not set in repo board code; grep of repo/firmware/board finds no boostCut/lambdaProtection/useCltBased override) - true. useCltBasedRpmLimit defaults off (limp_manager.cpp:69) - true. Hard rpm limit 7000 is set (default_base_engine.cpp:432).
- Repo VERIFICATION.md/review brief s6 do not document it (not news), but README.md:41 says turbo needs no sensor change, so boosted use is advertised.
Caveats: stock Miata is naturally aspirated and miata_nb_tune.cpp:9 admits VE above 100 kPa is untuned; overboost cut is irrelevant on NA. "No oil protection sensor" is a hardware non-issue (no sensor on car). Stock rusEFI defaults, not a regression. Firmware only: no effect on ordered PCBs (ordered flag moot).
Corrected statement: Protection features (boost cut, lambda protection, CLT rev limit) ship at rusEFI defaults (off); MAP-failure fallback is flat 60 kPa. Relevant mainly to turbo/supercharged users. Severity medium/low for NA product.
Fix: in firmware/board set boostCutPressure (~150-160 kPa) and optionally enable lambdaProtection/CLT limit; document in README for boosted use. Effort: few lines + test.
