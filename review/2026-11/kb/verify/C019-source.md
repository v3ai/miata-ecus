# C019 verify (primary sources)
Verdict: partly (core true; "no online ini" is a consequence of an unproven rusEFI-side mechanism, and the docs gap is narrower than stated).
Checked:
- repo/.github/workflows/firmware.yaml:43 `uploads: ''` (no rusefi.com upload); lines 59-63 upload the ini as a GitHub Actions artifact `rusefi_miata-ecu.ini`.
- efifeatures.h (stm32f4ems) 406-409: EFI_EMBED_INI_MSD FALSE default, comment "Save flash on F4"; repo grep finds no override for miata-ecu. Other boards (uaefi, subaru_eg33, nucleo_f767) opt in.
- VERIFICATION.md:102 "77 KB spare" (documented); ini ~196 kB gzip is a proxy measurement from another build, so "does not fit" is sound by margin (>2x) but not measured on this build.
- INSTALL.md:124 says only "Open TunerStudio, connect, press your year" - no ini step. But firmware/README.md:34-36 does document the bundle containing the .ini and a standalone rusefi_miata-ecu.ini; README.md:192 mentions it. So it is documented for builders, not in the customer install path.
- Not verified: rusefi.com/online/ini lookup/FTP-secret behaviour (no network check); stated from rusEFI wiki per audits.
Not affecting ordered boards (firmware/docs only). Not in review brief s6 / VERIFICATION open items as a customer-UX item.
Corrected: The F4 build does not embed its ini and CI does not upload it to rusefi.com, so TunerStudio cannot auto-fetch a matching ini for the miata-ecu signature; the ini exists only in the CI bundle/artifact, and INSTALL.md's bench-check step does not tell the customer to load it. Severity medium-high (seller can preload it on the sold-assembled unit).
Fix: link/ship the ini with each release and add a Create Project -> pick .ini step to INSTALL.md (zero cost); embedding not feasible without freeing ~120 kB+ flash.
