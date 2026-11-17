# C062 verdict: partly (mostly already documented)

Checked:
- Cavities 4J/4O/4P/4T/4Z/3H/3J are "(no net)" on cur/ord 96-97 board (kb/interconnect.md; motherboards/1996-97/README.md line 85 "Not connected"). True. Ordered rev 0.7 has the same pinout (evidence/ord_mb9697 not changed in this respect).
- Not news: review brief s6 and repo/README.md line 102 already state no EGR, purge, VTCS, rear O2 sensor support; the 96-97 README lists 3D as rear HO2S input only. repo/research/pinouts_9605.md lists 4J/4O/4P/4T as "Unknown test pad" and 4Z as "rear HO2S heater, N/C in DIY, Hellen drives OUT_O2H2".
- NOT verified by me: the specific FSM wire colours/functions (4T purge, 4O/4P EGR, 4J PRC, 4Z VIO rear heater, 3H/3J EGR inputs). Wiring PDF has no extractable text here and no PDF tools are installed; the repo's own research table disagrees (it calls 4O/4P/4T/4J unknown, and 3H/3J on 96-97 are unknown test pads). The claim's PRC identity for 4J is single-source and its hot-restart effect is explicitly unverified.
- "Safe when de-energised": plausible (low-side loads, open = off); purge/EGR off is the standard consequence. An OBD-II 96-97 car will not run catalyst/purge monitors: no CEL on its own from these (MIL not driven anyway).

Corrected statement: the stock low-side solenoid/EGR/rear-heater cavities on 96-97 are unconnected (true, same on ordered boards); this is already documented as "no EGR/purge/rear O2" except PRC (4J) and the rear heater (4Z) specifically, which are minor additions of unverified function. Severity low/info.

Fix: add 4J/4Z to the README "not supported" line only after confirming function from the FSM; optional driver exposure is feature work, not an error.
