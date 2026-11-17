# C054 verdict: confirmed arithmetic, already documented (partly)
Checked datasheets/txt/C90152_MPX5700AP.txt lines 69-75: accuracy 2.5 %VFSS (0-85C), VFSS 4.5 V, sensitivity 6.4 mV/kPa, absolute Voff 0.184-0.409 V.
2.5% x 4.5 V = 0.1125 V; /6.4 mV/kPa = 17.6 kPa (17.5 with 6.43). 17.5/35 = 50%, 17.5/100 = 17.6%. Offset spread 0.225 V = full +-0.1125 band. Arithmetic correct.
Caveats: this is the guaranteed worst case, not typical; a fixed offset is absorbed by a tune on that car (stated in claim). rusefi_config.txt:1242 useFixedBaroCorrFromMap exists (verified).
Already documented: repo/VERIFICATION.md:692 ("about +-18 kPa worst case against a 30 kPa idle ... MPX4250AP about +-3.5 kPa. Kept for now; per-order choice for NA cars"). Not news.
Ordered boards: yes, all use MPX5700AP, so affected, but the part is hand-fitted; the only rework is swapping the sensor (MPX4250AP same case/pinout per repo), no board change.
Fix: as suggested (MPX4250AP option for NA). Did not verify the MPX4250AP +-3.5 kPa figure myself.
