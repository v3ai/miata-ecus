# C055 verdict: partly (facts true, but it is generic background, not a defect)
Checked via GitHub API:
- hellenNA6_issues #29: PA0 read 0 V; reporter found a possible poor joint on R117 and a dried flux blob on the STM32 PA0 pin; maintainers wrote "jlc fab defect" (an opinion, one unit, no proof it was JLC rather than the user's own handling).
- hellenNA6_issues #23: "JLC seems to have an issue with identifying polarities of diodes ... a few different errors reported by JLC during production". Question is posed, root cause not found; could be the owner's ordering files.
- hellen-NB2-issues #4: "72 rev D was ordered with LMV324IPWR" (hellen-one #63). Cause (shortage or ordering) not stated in #4; the notes' "chip shortage substitution" is inference.
Consequence: no defect in this design. The repo already has JLC placement-preview rotation corrections (VERIFICATION.md ~l.289-293) and flags SOT-23-6/USB4105 for viewer check; BOM check is done at JLC. Partly documented (rotation); flux/joint inspection and "no substitutions" are generic good practice.
Ordered boards: only in the sense that they are at JLC now; nothing actionable beyond inspecting first article (flux, R/diode orientation, op-amp markings) before power-up. Cannot be reworked prior to arrival anyway beyond that.
Fix: none to the design; at receipt inspect flux/joints, verify diode polarity and IC markings, ohm/volt-test analog inputs.
