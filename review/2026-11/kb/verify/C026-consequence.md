# C026 consequence check
Verdict: partly. Severity medium (not high). Not board-affecting (firmware/docs only; ordered boards unaffected).
Checked:
- repo/firmware/README.md "Base tune" (l.88-111): every year button loads a full Miata VE/ignition tune, stock injector set per year (212/254/265/256/265 cc), cranking/warm-up/idle curves, closed-loop wideband trim +-10% on by default, note that bigger injectors need flow and dead time entered. "First start" step 8 (watch wideband) and step 11 (timing-light check, Trigger Angle) exist. So "base-map step missing" and "no timing-light checklist" are false.
- repo/INSTALL.md sec 8 (l.304-327): has key-on check, crank, timing light at 10 deg, watch wideband, light drives. It does NOT ask the owner to confirm injector size/impedance, fuel pressure or engine size before cranking; sec 4 only discusses injector inductance. This part of R28.07 is true.
- The R12 evidence (other cars/ECUs on miataturbo/Speeduino, wrong trigger pattern on a different product) is about other ECUs; here trigger patterns are per year button and sim-tested (VERIFICATION.md l.698-722). Ranking it "top first-start failure" for this product is unsupported.
- Consequence: a stock-injector car runs on the shipped table with +-10% trim, so wrong cc matters only for non-stock injectors (turbo/modified cars), where the README already says a tuner is needed. Failure mode is rich/lean first start, not hardware damage.
Corrected statement: Base tune and timing-light steps exist; the real gap is a one-line pre-crank check in INSTALL sec 8 (injector cc matches the year's stock set, else enter flow/dead time; fuel pressure; correct year button). Named per-injector tune files are optional extras.
Fix: add 3 lines to INSTALL.md sec 8 pointing at the Base tune table; zero cost.
Already documented: partly (base tune, timing, injector note in firmware/README), checklist item not.
