# C068 verification: cheaper injector drivers (NCV8401B / NCV8403A / ZXMS6005)

Verdict: PARTLY (the NCV8401B drop-in is true; the NCV8403A / delete-U11 variant is plausible but unproven).

Checked
- Q1-Q8 (VND7NV04, C155605) are the 8 injector/IACV/VVT/boost/alt drivers, fed one-to-one by U11 (SN74LVC4245A), see evidence/cur_db/pcb_nets.txt (INJx_IN, IACV_IN, VVT_IN, BOOST_IN, ALT_IN <- U11 channels). Same on ord_db.
- Live prices (tools/lcsc.py, today): VND7NV04 2.0619 @30 / 1.8164 @100; NCV8401BDTRKG C604055 0.9606 / 0.8101, stock 2500, extended; NCV8403ASTT1G C266786 0.7397 / 0.6284, stock 1897. Saving 8 x (2.0619-0.9606) = $8.81 @30 (matches R08.01). The $11 figure = 8 x (2.0619-0.7397) + U11 (~$0.4) = ~$11.0, arithmetic consistent.
- NCV8401B datasheet (datasheets/extra/NCV8401BDTRKG.txt): DPAK, 1 G / 2 D / 3 S (same as VND7NV04 usage), clamp 42-50 V (44 min at 150 C), RDS 34 mohm max @5 V, EAS 800 mJ, Vth 1.0-2.0, no series-input-resistor requirement stated. ILIM 25-35 A (11-21 A hot) vs VND7NV04 6 A: a shorted output stresses harness/driver more before limiting; this is the caveat. Clamp min 42 V is above the existing 16 V TVS-to-battery clamp (~31 V), so the external clamp still works.
- NCV8403A: datasheet gives Vth 1.0-2.2 V, ILIM 10-20 A @5 V, 42 V clamp. 3.3 V gate drive rests on a typical curve (Fig. 8, graph not machine-readable); not guaranteed at Vth max 2.2 V. Deleting U11 also loses the DRV_EN_N output-enable gating (U11 pin 22) and needs a SOT-223 re-layout, rerun of thermal model (DPAK to SOT-223 loses copper/thermal margin; N8 in VERIFICATION.md already says drivers are the thermal limit). Savings only if ALL 8 U11 channels move off 5 V logic.
- Repo search: no mention of NCV8401/NCV8403 anywhere in repo/. Not in review brief section 6. A1 (150 ohm RIN-min on VND7NV04, ordered boards lack it) is documented; NCV8401B would also remove that issue, a benefit the cluster did not state.
- Cluster bundles unrelated members (ZXMS6005 no-external-clamp, SMBJ14A TVS, Blitzbox AO3400A). Dropping the external clamp is a separate, riskier claim (project simulates 20 mH injectors; ZXMS6005 480 mJ vs VND 200 mJ); not verified here. AO3400A bare low-side is unproven, not recommended.

Ordered boards: cost only; ordered rev 0.9 has VND7NV04 soldered, nothing to rework (hand-swap not worthwhile, and the DPAK swap would mainly cure A1). Respin item.

Corrected statement: NCV8401BDTRKG (C604055) is a pin-compatible DPAK replacement for VND7NV04 at ~$8.8 less per board at qty 30 ($8.0 at 100), with 25-35 A current limit as the main trade-off. Moving to NCV8403A SOT-223 with 3.3 V gate drive and deleting U11 could save ~$11 but needs re-layout, thermal rerun and a bench test of 3.3 V drive; unproven.

Fix: for next respin swap C155605 to C604055 (no layout change); evaluate SOT-223/3.3 V as a separate bench experiment.
