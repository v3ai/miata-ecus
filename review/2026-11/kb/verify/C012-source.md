# C012-source: partly confirmed

Verified:
- Store: repo/website/theme/templates/index.json:276 FAQ says swapped autos covered; products.json "Fits ... manual and manual-swapped" for all 5 products. No product body mentions automatic untested, Mazdaspeed, OBD-II or immobiliser (checked first two bodies). README.md:104-106 says automatics untested, transmission signals mostly unconnected, Mazdaspeed unsupported, no OBD-II/EGR/VTCS.
- Boards: ord_mb8993/9495 pcb_nets.txt: 1V on IN_SW3 (JD2.17); ord_mb9697 and cur_mb9697: 1L on IN_SW3. 1R only on OUT_LS7 (8993). firmware miata_board.cpp:113 clutchDownPin = MIATA_SW3 for all years.
- Already documented: README untested line; VERIFICATION.md lines 112-116 (1989-93 A/T 2Z, 1N), 1202. Not news for engineering; the store/README mismatch is the new part.

Not verified / caveats:
- A/T pin colours (1V BLK-BLU to ignition) rest on FSM wiring diagram cited by audit; FSM not in the workspace, only the audit note (kb/pinouts/PIN-8993-A-design-outward.md:12,51). 1R/1T/4Y being A/T lines likewise.
- "Reads clutch down permanently" depends on input polarity; not derived. R22 pull-up appears in the schematic BOM and footprints (dnp=0), while mb_common.py:112-116 says NOT FITTED, so its status is ambiguous.
- "high" severity overstated for engineering; as a store-accuracy and sale-to-wrong-customer issue it is a valid medium/high.

Affects ordered boards: yes, same pin map on ord_mb8993/9495/9697, but nothing to rework; the fix is store wording (and optionally leaving R22 off).

Fix: edit FAQ line and Fits rows to "manual gearbox; automatic untested; not Mazdaspeed/OBD-II-monitor/immobiliser".
