# C132 verdict: partly (true but not a board finding)
- Source forum threads (MSPNP2 wideband ground pin 21/22) were not fetched; the MSPNP anecdote is unverified by me. It concerns an external wideband wired to the ECU, which this product replaces with an on-board LSU 4.9 controller (no ground-pin wiring exists).
- Exhaust leak reading lean is general physics, true. INSTALL.md (line ~285) covers only the bung for LSU thread; no leak check or placement advice found by grep.
- Not a design error; no effect on ordered boards (ordered:false). Not in review brief section 6.
- Corrected statement: low-severity documentation suggestion: add sensor placement / exhaust-leak check note to INSTALL.md. The ground-pin part is not applicable.
