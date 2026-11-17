# C023 consequence check

Verdict: partly. Severity medium (not high). Does not affect ordered boards (docs/firmware default only). Already partly documented (README step 11, INSTALL step 4).

Checked:
- INSTALL.md 322-326 (step 4) and firmware/README.md 112, 249-251: the repo does tell the user to lock timing at 10 deg, check with a light, correct Trigger Angle Advance, return to dynamic. So "no restore-dynamic warning" is false: both say "Unlock it again" / "set back to dynamic".
- rusefi_book.txt 821-889: the rusEFI procedure is a CRANKING check with plugs removed and injectors disabled, hence FIRE DANGER. The repo's check is a running-engine check (step 3 starts the engine, step 4 checks a running idle at fixed 10 deg). Disabling fuel is only needed for the plugs-out cranking method; a lit-engine fixed-timing check is the standard Miata practice. The omission is therefore a doc mismatch, not a safety hole.
- Real issue that holds: ordering. Step 3 starts the engine with globalTriggerAngleOffset at its default 0 (grep of rusefi config/engines and hellen boards, repo/firmware/board: no Miata preset sets it; only the 36-1 NB2 variant per F02.07). Timing check comes after first start, and README lists it as step 11. Consequence is a possibly mistimed first start (hard start, kickback/backfire if the error is tens of degrees); size of the real default error not measurable without a car (unverifiable).
- Not an engine-damage-class risk at idle; the stated "high" rests on MSPNP marketing language (R04.06), not repo facts.

Corrected statement: INSTALL.md puts the timing check after the first start, and the default trigger offset is 0 for every Miata preset except one, so the first start runs on unverified timing. The rusEFI "disable fuel" steps apply to its cranking method, not to the running-engine check the repo uses; restore-to-dynamic is already documented.

Fix (cheap): in INSTALL step 3 say "set Timing Mode fixed 10 first (via the Popular Vehicles button or by hand), then crank"; move the timing check ahead of drive instructions. Optionally ship the tune with timingMode=fixed 10 as the first-boot state (F02.07), with a visible reminder. Firmware auto-revert is unnecessary; one doc line costs nothing.
