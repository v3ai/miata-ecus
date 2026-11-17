# C026 verification (primary-sources lens)
Verdict: PARTLY.
Checked repo/INSTALL.md (sec 1 step 2, sec 8), repo/firmware/README.md (Base tune table l.88-111, First start l.208-245), VERIFICATION.md l.698.
- True: the year button loads one default injector set per year (212/254/265/256/265 cc/min, README l.94-98). INSTALL has no pre-crank injector cc/impedance or fuel-pressure checklist. "Bigger injectors need flow and dead time entered" is only in firmware/README l.111, not in INSTALL's start-up steps.
- False/overstated: "base-map step missing". INSTALL step 1.2 loads the year's base tune and links it; base tune table, weak spots, timing-light step (INSTALL sec 8 step 4, README step 11), wideband watch and "light throttle" are all documented. Base tune is documented in VERIFICATION.md "Base tune and closed-loop fuel" (2026-11-12), so not news as such.
- R12.02 evidence is forum anecdotes on other ECUs (Speeduino, stock-ECU cars), not this product; "top first-start failure" is an unsupported ranking. "Ship NB 1.6 base map" is moot: 1989-93 uses a 1.6 table already.
- Not hardware; ordered boards unaffected (docs/firmware only).
Corrected statement: INSTALL.md/firmware README document the year base tune and timing-light check, but lack an explicit pre-crank checklist for injector size/dead time (non-stock injectors), fuel pressure and engine size; the year button silently assumes stock injectors. Severity medium (docs).
Fix: add 3-4 lines to INSTALL sec 1 / sec 8: confirm stock injectors (else enter flow+dead time first), fuel pressure, engine displacement, then crank.
