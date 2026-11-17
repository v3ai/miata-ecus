# C103 verify: JST PUD 3 A contact vs LSU heater ramp
Verdict: PARTLY (facts true, "thin / zero margin" overstated; severity low, not medium). Not ordered boards (ordered mbs use Micro-Fit 8.5 A).
Checked:
- 3 A / -25..+85 C / SPUD 22-26 AWG: repo VERIFICATION.md l.895-902 and kb/parts/P21 (JST ePUD catalog). True. 3 A is a continuous rating incl. temp rise.
- Heater current: kb/parts/P04 l.41-45 table: ramp start 7 V eff, 4.5 A pulses, 2.19 A RMS (cold R 3.2 ohm, secondary source), 1.06 A at 8.5 V... hot ~1 A. 2.2 A RMS is 73% of 3 A. The 3.9 A figure needs 1.8 ohm cold at -40 C, an unverified assumption, and -40 C is outside the JST -25 C rating anyway (cold contacts also self-heat less); that case is a seconds-long transient, not continuous.
- Ramp is time-limited (R rises as element heats, closed loop ~1 A RMS after ~13 s), so contact heating over a 3 A continuous rating is not a real exposure. Pulses (4.5 A, 390 Hz) are averaged thermally.
- The AEM gauge itself drives the same LSU heater through this same connector/terminal family (AEM specifies SPUD-001T-P0.5), so using the contact is the manufacturer's own practice; the board adds no new risk beyond the harness.
- Hot cabin: ECU case air ~85 C is the only real concern; but then F1 PTC (hold 1.34 A at 85 C) is far more limiting than the contact (already N5 in VERIFICATION.md, fixed with 3 A part).
- Wire gauge unknown is true but irrelevant to the contact rating; wire is the harness maker's.
Already documented: contact rating yes (VERIFICATION l.902); margin analysis no; F1/heater warm-up current yes (N5).
Corrected statement: J2 JST PUD contacts (3 A continuous) carry ~2.2 A RMS worst-case (nominal) for seconds during heater ramp, ~1 A steady; margin is modest but adequate and equals AEM's own use. Low / info.
Fix: none needed; optionally measure real heater cold resistance when a sensor is available.
