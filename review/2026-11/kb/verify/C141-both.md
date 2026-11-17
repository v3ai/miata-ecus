# C141 verification: production test list from field history
Verdict: partly (reasonable process recommendation; evidence base thin, not a defect)
Checked:
- Case table in kb/research/R31-field-failures-open-ecus.md: sensor-5V short rests on ONE report (C1, NA6); ignition-stuck cases C22-C24 are mostly firmware/dwell discussions, C24 is discussion only; DFU/SD/wideband items map to C3/C9/C4/C27-29. The audit itself marks the row "inferred", and the implication list item 6 is the same advice.
- Repo: grep of README, VERIFICATION.md, firmware/README.md finds no per-unit test list or assembly/QC procedure; INSTALL.md section 1 "Bench check" is a customer step (USB light, year button, wideband flash, SD), not a seller test. So not already documented.
- Ordered boards: not specific to them; it is process, applies to any build including the ordered ones (continuity of hand-fitted pins is useful on them), but no rework item.
Caveats: "ESD/arrival damage: no public cases" is an absence-of-evidence statement. Shorting sensor 5V on every unit is itself a risk test; a current-limited supply should be used. "Stop the MCU clock" test is a first-article bring-up test, not per-unit.
Corrected statement: Sensible, low-cost QA/process recommendation (continuity of every hand-fitted pin, DFU, SD, wideband heater, USB, first-power on current-limited supply). Its link to "field history" is thin (one 5V-short case). Not documented in repo; no board change.
Fix: add a seller-side test sheet to the assembly procedure, keep per-serial log; run clock-stop and 5V-short tests on first articles only.
