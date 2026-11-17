# C018 source check: verdict PARTLY (substance true; severity overstated)
Checked 2026-11-16:
- rusEFI boards readme (repo/firmware/ext/rusefi/firmware/config/boards/readme.md): F4/F7 most supported, H7 alpha, kinetis/cypress/AT32 "experimental/abandoned". True. "AT32 port targets F435/F437" is not in that readme (not verified by me).
- GitHub issue #8396 (live API): open, created 2025-08-04, 0 comments, "ChibiOS upgrade makes apm32f407 Hardfault", no USB detection, hardfault. True. It is one user report, no maintainer response.
- GitHub search "gd32" in rusefi/rusefi issues: 0 hits (live). Absence of evidence only, not proof GD32 fails.
- Prices (tools/lcsc.py live): GD32F407VGT6 C115906 4.04/2.97(@90)/2.80(@1080), stock 20600, JLC lists 512KB. APM32 C2990873 4.43/2.89/2.61(@900), stock 1107. AT32F407VGT7 C528446 3.97/2.59/2.34, stock 1254. ST STM32F407VGT6 BOM code C12345 5.05/3.57(@100)/3.34(@1000), stock only 96. All match. Saving ~0.6 (GD) to ~1.0 (AT32) per board at 100.
- Note: AT32F407 has 80 I/O and different peripherals/clock; "pin-compatible" is not guaranteed.
Corrections: "No pin-compatible clone supported" is true as "not officially supported/validated". Severity "high" is too strong: nobody proposes a clone; BOM uses ST. Real adjacent risk is ST stock (96 pcs) at JLC, which makes clone fallback relevant.
Ordered boards: not an error; ordered daughterboard uses ST part. Recommendation sound but already implicitly BOM state; likely not documented in VERIFICATION.md (grep for gd32/apm32/at32/clone: no hits) so mild news.
Fix: keep ST; check ST stock before assembly order; clones only as bench-validated variant.
