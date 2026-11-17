# C007 source check
Verdict: partly (facts true; not news; the "over shutdown at 85 C" is an inference).
- Ordered db (evidence/ord_db pcb_nets/footprints): OUT_INJ1-4 go only to J1 + Q1-Q4 drain; no D42-D49 (they exist in cur_db: ES1D + 1.5SMC16A). Ordered mb9495/9697/9900/0105 have no TVS (D1/D2 SS34 freewheel only); ord_mb8993 has D3/D4 SMCJ30A. TRUE.
- VND7NV04 VCLTH 36 V min (datasheet txt line 337). TRUE.
- Thermal numbers (+78-86 K at 20 mH, +46-50 at 8 mH) match F05 notes of tool output; repo VERIFICATION "The ordered rev 0.9 boards" already states 60-86 C above air at 20 mH (35-50 at 8 mH), 1.06 W per driver, and that rev 0.10 added the clamps (A3, rev0.10 section). Not independently re-run.
- 85 C air + 86 K = 171 C > 150 C shutdown: simple addition by the reviewer, model assumes 1.2 A at 80% duty at 7200 rpm every injector (severe), h assumed; injector L unmeasured.
Already documented: yes (review brief s6 "injector inductance unknown", VERIFICATION A3 + ordered-boards section). Affects ordered boards: yes, hand-reworkable only via external TVS at harness/ ES1D+TVS wired per injector.
Corrected statement: the ordered boards have no per-injector clamp so the driver clamp absorbs ~15 mJ/shot at 20 mH (3-6 mJ at 4-8 mH); model junction rise 78-86 K (20 mH) at 7200 rpm sustained; high-ambient shutdown is an unmeasured extrapolation.
Fix: measure injector L; limit sustained high rpm; optional wired 16 V TVS to VBAT_IN.
