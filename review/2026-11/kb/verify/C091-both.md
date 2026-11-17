# C091 verdict: confirmed as fact, but already documented and already handled (not news)
Facts: R19 notes cite 2002 vs 2003 CHARM manual images (3H/4S unused vs main-relay control / IG1). Not re-viewed images; the repo and rusEFI wiki agree.
Already handled: repo/VERIFICATION.md l.154 ("2001-02 and 2003-05 share a motherboard but not the wiring... separate buttons"); firmware/README.md l.55-63; firmware/board/miata_board.cpp l.281-285 (3H/4S used only for 2003-05; mainRelayPin Unassigned otherwise) and board_configuration.cpp l.154 (2001-02 preset). Firmware per-year handling is the suggested fix and already exists. No jumper needed: 3H/4S are unwired on 2001-02 harness.
Ordered boards: same shared mb0105 netlist (3H=OUT_MAINRLY, 4S=VIGN_IN, interconnect.md l.700/696); no hardware rework; firmware-only.
Residual risk: user picks wrong button (documented in firmware/README l.63).
