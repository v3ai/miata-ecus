# C134 verdict: partly (competitor fact, unverified; no board defect)
- Source is a 2009 vendor forum post about the MSPNP (R04 notes mark it UNVERIFIED as current behaviour); the "DFIN1" meaning is unknown. I could not check either.
- This project does drive the CEL: pinouts_9605.md (1E / 2R MIL low-side out), VERIFICATION.md lines 137, 160-168, 677, 736, 867 (CEL lit at key-on, expires warnings, driven from the processor pin, outside the driver enable on rev 0.10), rev0.10_design_audit.md line 93.
- README.md:101 already states: not street legal as an emissions device, no OBD-II diagnostics or readiness monitors.
- Ordered boards: not affected (no board error claimed).
Corrected statement: A 2009 vendor post says the MSPNP does not drive the CEL; this is unverified for current products and is competitor context only. The project's own boards drive the CEL, and its non-smog-legal status is already documented.
Fix: none needed; optionally state CEL behavior in website copy.
