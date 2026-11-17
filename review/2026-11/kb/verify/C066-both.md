# C066 verdict: partly (already documented, low news value)
Checked: repo/.github/workflows/sim.yaml (on: workflow_dispatch only, comment "On demand only ... push triggers follow"); VERIFICATION.md:545,594 say "in CI (sim.yaml)"; firmware/sim/README.md ("Limits": sensors are voltages through the board's divider values; LSU plant uses firmware's own scale factors, analog front end covered by tools/circuit_sim_full.py; Renode gaps table lists own ADC/DMA/NVIC/F103 ROM bootloader models); run_ecu.py:116-154 hard-codes dividers (33k/6.8k, 5.6k/10k).
True: the sim does not test PCB wiring; the wording "in CI" overstates (manual dispatch, and README says "the CI workflow runs every model year").
Not true / overstated: it is not hidden. The README states the limits itself, and wiring/pin correctness is covered by separate checks (netlist vs design, check_pins.py, circuit_sim_full.py). Claimed pin-error blindness is only partly right: pins are firmware-config pin names, divider constants are not read from the netlist. Not run here (no Renode).
(a) Mostly already documented (README Limits). Only the "in CI" wording is new.
(b) Ordered boards: not a board defect; applies equally (sim models rev 0.9 via --board 0.9), nothing to rework.
Corrected statement: Renode FIL validates firmware self-consistency, not board wiring (documented in sim/README Limits); VERIFICATION.md calls it "in CI" though sim.yaml is workflow_dispatch-only. Severity low/info.
Fix: reword "in CI" to "manual workflow"; optionally derive divider constants from the netlist.
