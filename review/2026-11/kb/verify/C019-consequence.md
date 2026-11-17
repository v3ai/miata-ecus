# C019 consequence check
Verdict: partly. Facts true; severity overstated (high -> medium); it is a documentation gap, not a design defect. Ordered boards unaffected.

Checked:
- .github/workflows/firmware.yaml: `uploads: ''`, so the rusEFI online-ini upload step (custom-board-build/action.yaml:445-460, gated on contains(uploads,'ini')) never runs. True. CI does publish the .ini as an artifact and in the bundle (firmware/README.md:34-36).
- ext/rusefi stm32f4ems/efifeatures.h:406-407 EFI_EMBED_INI_MSD FALSE; the miata board does not override it. True. Other boards that embed (uaefi, nucleo_f767) are F7/large-flash targets; 77 kB spare flash vs ~196 kB gz ini means embedding is not feasible on the F407 (flash figure from the audits, not re-measured).
- INSTALL.md:124 says "open TunerStudio, connect, press your year under Popular Vehicles" with no step to load the .ini. The Popular Vehicles buttons (board_popular_vehicles.ini) live inside the generated .ini, so they exist only after the .ini is loaded; a first-time user has no way to know that. This is the real consequence: first-connect confusion, not a failure of the product.
- Not news for rusEFI generally: every custom rusEFI board without FTP secrets works this way; the user creates a TS project, Browse to the .ini from the bundle. It is one-time, and the signature matches the same-build firmware. The risk is a firmware/ini mismatch after updates (ini must be re-loaded per build).
- Not in review brief s6/VERIFICATION.md as an open item (grep found no hits for embed_ini/online ini).

Corrected statement: Detect cannot fetch an online .ini for this custom build, and the F4 cannot embed one, so customers must create a TunerStudio project from the .ini in the release bundle; INSTALL.md omits that step and the need to reload the .ini after each firmware update.

Fix (cheap): add INSTALL step "Create Project, Browse, pick rusefi_miata-ecu.ini from the release"; ship the bundle's ready TS project; name the .ini by version; the seller can pre-flash and include a card/QR link. Embedding or paying for online hosting is unnecessary. Medium effort: zero hardware. Affects ordered boards: no.
