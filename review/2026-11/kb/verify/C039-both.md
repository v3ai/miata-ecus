# C039 verdict: partly (low-medium; documented; affects ordered 1996-2000 boards, rework = fit 1 resistor)
Checked:
- Ordered mb9697/mb9900 BOM: R20-R22 4.7k 0603 exist as footprints, not fitted (evidence/ord_mb*/sch_bom_grouped.csv).
- repo/motherboards/1999-2000/README.md:130 and VERIFICATION.md M4 (line 215) already say: pull-ups R20-R22 are not fitted by default; fit if the signal is switch-to-ground/open collector. So the mechanism is known; only the 3I per-car polarity is new.
- Wiring diagram (3I BR/W to clutch switch B1-21, other side ground) not re-opened by me; only seen in PIN-9900-B notes (kb/pinouts/PIN-9900-B-car-inward.md:74,138). A switch with one leg to ground is a switch to ground by construction, so likely true, but FSM p.25 not independently read.
- Firmware: miata_board.cpp:113 sets clutchDownPin = MIATA_SW3; no clutchDownPinInverted/Mode set (grep), so with R22 fitted, closed switch = low; polarity must be checked/inverted in rusEFI config.
- PIN-9697-A.07 half is speculative (low confidence, "cannot be verified"); no evidence for VSS (1M) polarity.
Corrected statement: On 1996-2000 boards the clutch input 3I appears to be a switch to ground (per Mazda diagram, not re-read); R22 is not fitted by default, so clutch is unread until it is fitted, and firmware polarity (clutchDownPinInverted) is unset. Documented as a per-car option in README/VERIFICATION M4; the missing piece is the default and the inversion.
Ordered: yes (mb9697 rev0.7, mb9900 rev0.7 have the unfitted R22); hand-fit R22 (0603 4.7k) possible. Affects only clutch-based features (launch/clutch idle), not running.
Fix: fit R22 on MT cars, set clutchDownPinInverted=true, update README wording "12 V driven" for 3I.
