# C100 verdict: partly
Checked repo/INSTALL.md 203-237 (one wire per injector), 168-196 (F/P, TPS), line 141, README.md 213-229, VERIFICATION.md grep.
- True: steps 3-5 cut injector 3/4 leads off the 1/3 and 2/4 joints and move them to cavities 2Y/2Z. Stock ECU drives only 2U/2V, so a refitted stock ECU would run only injectors 1 and 2 until the joints are restored. Nothing says so; no undo steps; no "irreversible" label (grep for revers/undo/irrevers: none in INSTALL/README; VERIFICATION only mentions the conversion as a heat remedy).
- Aggravating: INSTALL.md:141 says the old ECU board "is your way back to stock", which the conversion makes untrue.
- Overstated: the F/P wire (one added wire to 2T, unused by stock ECU) and TPS (sensor swap onto switch plug; R28/R30 are board-side) are removable, not one-way in the same sense; TPS sensor replaces the idle/full-throttle switch the stock ECU needs, so that one does matter for going back, but is a parts swap.
- Not a board error; guide/UX only. Affects ordered boards only in that the guide applies to ord_mb8993 owners (no rework relevant). Not in review brief s6/VERIFICATION open items as far as grep shows.
Fix: add a warning to the conversion section (reversal = re-join cut leads at the old joints, remove 2Y/2Z wires; or use splice-in/Posi-tap style so it can be undone), and qualify line 141. Severity low-medium.
