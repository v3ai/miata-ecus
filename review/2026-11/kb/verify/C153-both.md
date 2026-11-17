# C153 verdict: partly (unverifiable prices, trivial inference)
- Architecture premise true: README/products.json say two boards (universal daughterboard + year motherboard) in the customer's stock case; customer supplies the case ("You add ... your stock ECU case").
- Daughterboard-only RMA is the audit's own inference (R28.13 marked INFERRED, confidence low). Plausible but a business-process idea, not a design fact. Caveat: the daughterboard sits on 2 headers + 4 standoffs inside the case, so the customer must open the case; the motherboard (harness header, MAP) can also fail and would still need the full unit.
- AMP/DIY $75 RMA fee: not checked (no primary source in workspace); the ECU-price figures (R28.16) are an undated search summary, "verification: unverified". I could not reproduce them.
- Not documented in repo (grep README/INSTALL/website: no donor/RMA text), so not "already known". Does not affect ordered boards (no design content).
- Fix: none for hardware. Optional: state in store copy that the customer supplies a case (a donor ECU is a customer cost, check immobiliser/transmission variants), and plan RMA as daughterboard swap with spares.
