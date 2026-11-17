# P04 - LSU 4.9 heater path (Q101 VND14NV04, heater fuse F1, header pins, sensor connector, firmware limits)

## Summary
1. Q101 (VND14NV04TR-E, C2649436, DPAK) is wired correctly: pad1=INPUT<-1k from WB_HTR_PWM (PB10), tab pad2=DRAIN=LSU_HTR_N, pad3=SOURCE=HTR_GND. VERIFIED (pcb_pads.csv, ST DS p.5 fig.1). Low-side switch. The LCSC "High Side Switch" tag is wrong; the circuit uses it correctly as low side.
2. ST requires only RIN MIN = 10 ohm (not 150 like VND7NV04); 1k is fine. Gate drive 3.3 V is below the 5 V at which RDS(on) is specified (VINTH max 2.5 V): inferred OK (transfer curve fig.15 shows >10 A at 3.0 V, typ), margin thin at worst-case Vth.
3. Firmware (pinned 27e115b = built image): 390 Hz PWM (400 kHz/1024), preheat 5 s @ 2.0 V eff, ramp start 7 V +0.4 V/s, cap 12 V, closed loop 7.5 V +/- PID, off at >=23 V supply. All inside Bosch limits (1.5 V condensation, 8.5 V step, 0.4 V/s, 13 V max, >=100 Hz) except preheat 2.0 V vs Bosch 1.5 V (minor).
4. Battery sense = R120 100k/R121 10k from VBAT_IN (before motherboard F1), PB0. Heater supply HTR_PWR is after F1: error is mV-level. OK.
5. Current: heater cold 3.2 ohm (secondary source) -> 4.5 A pulse peak at 14.4 V; RMS 2.2 A at ramp start; hot 7.5 V/7.5 W -> ~1 A RMS. F1 2920L300/30GR hold 3.0/1.99/1.34 A at 25/60/85 C: no trip in normal use at <=60 C; at ~85 C case air with a cold sensor the ramp-start RMS (2.2 A) sits at the derated trip level -> nuisance-trip risk (INFERRED).
6. F1 cannot protect the sensor from a harness short of H- (pin 2) to ground (heater then runs continuously at ~14 V, 4.5 A cold falling to ~2 A hot, below PTC trip) - inherent, no diagnostic.
7. Q101 dissipation <0.5 W realistic (copper ~0.4 cm2 drain, Rth ~75 C/W): fine. Tracks 1.0 mm, header 2 pins per net (2.25 A/pin peak): fine. JST PUD 3 A/contact (repo claim) vs 2.2-3 A RMS at ramp: thin but OK.
8. No cheaper drop-in with the same protections. Plain logic MOSFET ($0.10-0.19) would save ~$1.2 but loses current limit / OT / clamp; not recommended without analysis.

## 1. Circuit as built
- cur_db rev 0.10 and ord_db rev 0.9 identical here. Q101 footprint Package_TO_SOT_SMD:TO-252-2, pad1 (207.5,118.54) 2.2x1.2, pad3 (212.06,118.54), pitch 4.56 mm, tab 6.4x5.8 + 4 side pads 3.05x2.75 (VERIFIED evidence/cur_db/pcb_pads.csv:425-431).
- R125 1k WB_HTR_PWR->gate; R126 1k PWM->GND (keeps gate low while PB10 floats at reset); R127 1k PWM->WB_LED_H (LED shows heater PWM). U102.21 = PB10 (TIM2_CH3 remap 2, board.h:97, board.c:52-55).
- J2.37/38 = LSU_HTR_N, J2.39/40 = HTR_GND (pcb_nets.txt:157,184). All 9 motherboards: JD2.37/38 LSU_HTR_N, JD2.39/40 GND (VERIFIED pcb_pads.csv each board).
- Motherboards: F1 (VBAT_IN -> HTR_PWR) 2920L300/30GR, JST S08B-PUDSS-1 J2 pin 8 = HTR_PWR, pin 2 = LSU_HTR_N (current); ORDERED mb: same F1, J2 = Molex Micro-Fit 430450600 2x3: pin3 LSU_HTR_N (H-), pin4 HTR_PWR (H+) (rated 8.5 A, C127367, stock 40264, $0.31@1000). VBAT_IN = harness cavity 1B.
- VBAT_IN protection on daughterboard: D6 SMCJ30A to GND (Vbr 33-37 V), D7 SS34 to +12V_IN. D6 clamps VBAT_IN (pcb_pads D6/D7).
- Tracks (pcb_net_routing.csv): HTR_PWR 1.0 mm (12.5 mm F + 11.2 mm B on current mb; 12 + 8.25 ordered), LSU_HTR_N 1.0 mm min (100 mm F + 35 mm B, two parallel branches to JD2.37/38), daughterboard LSU_HTR_N 1.0 mm (10.7 mm), HTR_GND 1.0 mm (4.7 mm). Repo's own fab_track_current.txt: 2.00 A, 6.7 C rise worst.

## 2. Datasheet digests
### VND14NV04 (ST Doc ID 7393 rev 9, datasheets/C2649436_VND14NV04TR-E.pdf, read tables 2-4, figs 11/12/15/34, p.5 block diagram)
- OMNIFET II autoprotected low-side MOSFET. Pins DPAK: 1 INPUT, 2 DRAIN (tab), 3 SOURCE. Vclamp 40/45/55 V (ID 7 A), Ilim 12/18/24 A, Tjsh 150/175/200 C reset 135, RDS(on) 35 mOhm max @5 V,7 A,25 C (70 mOhm over temp), VINTH 0.5-2.5 V, IISS 100/150 uA, RIN MIN 10 ohm, IIN +/-20 mA, IR -15 A, ESD 4 kV HBM, EAS 400 mJ (24 mH), EMAX 93 mJ, Rthj-case 1.7, Rthj-amb 65 (0.5 cm2) ; fig.34: ~80 C/W at minimum pad, 52 at 2 cm2.
- Rise/fall with 2.2k Rgen: tr 9.7 us, tf 10 us (max 30). With 1k: ~half. Pulse at preheat (duty 1.9% at 390 Hz) is ~49 us: still above td+tr.
- RDS(on) curves (fig 11/12) start at Vin 3.5 V: 7 A 25 C about 34 mOhm, 150 C about 61 mOhm; below 3.5 V extrapolated higher. Transfer curve fig 15 (Vds 13.5 V): 9-13 A at 3.0 V, ~14 A at 3.25 V (saturation, typ).
### 2920L300/30GR (LUTE 2020 rev, C22446884)
- Ihold 3.0 A, Itrip 5.0 A (25 C), Vmax 30 V, Imax 40 A, R 12-48 mOhm, ttrip max 20 s at 8 A, Pd 2 W, -40..85 C. Derating Ihold: -40 C 4.53, 0 C 3.51, 25 C 3.00, 40 C 2.52, 50 C 2.26, 60 C 1.99, 70 C 1.79, 85 C 1.34 A (p.4 table). Trip scales roughly with hold (INFERRED: Itrip(85C) ~2.2 A).
### Bosch LSU 4.9 (datasheets/extra/LSU49_bosch.pdf, Bosch Motorsport 69034379, read p.2)
- Heater nominal 7.5 V, steady 7.5 W, system supply 10.8-16.5 V, control frequency >=100 Hz, heater strategy graph: 1.5 V during condensation phase, step to 8.5 V, ramp max 0.4 V/s, to 13 V max. Pin 3 H-, pin 4 H+.
- Cold heater resistance NOT in the sheet. Secondary (web search summary of a Bosch tech doc, not opened): 3.2 ohm at 20 C incl. cable, 1.8 ohm at -40 C min (UNVERIFIED). Hot R from 7.5 V/7.5 W = 7.5 ohm (INFERRED).

## 3. Firmware (repo/firmware/wideband, pinned wideband 27e115b = work/P04-wideband-heater/wb_pinned; ext/wideband-rusefi d14ce8a is newer and differs: refactor, no HEATER_SUPPLY_* names)
- PWM 400 kHz/1024 = 390 Hz (heater_thread.cpp:9). HEATER_CONTROL_PERIOD 50 ms, PREHEAT 5 s, WARMUP_TIMEOUT 60 s, SUPPLY_ON 9.5 V, OFF 8.5 V, STAB 0.5 s (wideband_config.h:43-53). HEATER_MAX_DUTY and FAST_HEATING not defined.
- Preheat 2.0 V eff, ramp starts 7 V (9 V if fast threshold) +0.4 V/s up to 12, closed loop 7.5 V - PID (limit 12 V), duty=(Veff/Vbat)^2, >=23 V supply -> duty 0, Stopped after warmup timeout/over/underheat 0.5 s (heater_control.cpp).
- Supply voltage = board PB0 divider R120/R121 (BOARD_HAS_VOLTAGE_SENSE, port.cpp:77-91): 14.4 V -> 1.31 V at ADC, 24 V -> 2.2 V ok. Sensed at VBAT_IN, before F1: F1+track drop at 2 A about 0.1 V = <1% duty error.
- Main rusEFI sends heater-enable over CAN (rusefi_wideband.cpp:206-217); without CAN the wideband auto-starts at >9.5 V after 0.5 s.

## 4. Current and thermal quantification (R_cold 3.2 ohm UNVERIFIED secondary; Vbat 14.4)
| State | Veff | duty | on-state peak | I RMS | I avg |
|---|---|---|---|---|---|
| Preheat | 2 V | 1.9% | 4.5 A | 0.63 A | 0.09 A |
| Ramp start | 7 V | 23.6% | 4.5 A | 2.19 A | 1.06 A |
| Ramp 8.5 V (cold R) | 8.5 | 34.8% | 4.5 | 2.66 | 1.57 |
| Hot closed loop | 7.5 V | 27% | ~1.9 A (R 7.5) | 1.0 A | 0.52 A |
At 13.5 V peak 4.2 A; cold -40 C (1.8 ohm) ramp start RMS 3.9 A but PTC hold is 4.5 A at -40 C.
Compare F1 hold: 3.0 A (25), 1.99 (60), 1.34 (85). Nuisance trip: unlikely <=60 C; at 85 C air marginal at ramp start (first seconds; R rises quickly as the element heats, so duration limited). Never-trips: heater short at connector -> Q101 current-limits 12-24 A, F1 trips within seconds (8 A: <=20 s; more at higher I), Q101 cycles thermal shutdown (designed). Heater H- shorted to GND: continuous 14 V on heater, F1 holds (hot ~2 A), sensor over-driven (>13 V Bosch limit) - no firmware defence since Q101 bypassed.
- Voltage drop (INFERRED): F1 <=48 mOhm + HTR_PWR 1 mm x 24 mm 12 mOhm + LSU_HTR_N ~35-65 mOhm + header/JST contacts ~30 mOhm + Q101 50-100 mOhm => ~0.2 ohm; 4.5 A pulse drops 0.9 V (6%) on-state, closed loop PID absorbs. Per header pin 2.25 A peak, 1.1 A RMS (limit ~3 A for 2.54 mm pins, UNVERIFIED typical).
- Q101: conduction at ramp start 4.5^2 x 0.06 x 0.236 = 0.29 W + switching ~0.1 W; worst realistic ~0.5 W -> dTj ~35-40 C at 75-80 C/W (drain copper about 0.4 cm2, F.Cu pad+1 mm trace, no pour, layers/q101_fcu.png). At 85 C air Tj ~125 C < Tjsh 150. OK.
- Overvoltage: TVS D6 SMCJ30A Vbr 33-37 V (clamp max 48.4 V, UNVERIFIED value from memory) vs Q101 Vclamp 40-55 V: TVS acts first. Jump start 24 V: F1 30 V, Q101 40 V ok, firmware heater off at 23 V. Reverse battery: VBAT_IN clamped about -0.7 V by D6 body; Q101 IR -15 A fine.
- Ordered boards: same F1, same tracks (1.0 mm), Molex Micro-Fit 8.5 A contacts (better than JST 3 A). Connector mismatch with the AEM harness already documented in repo research A13.

## 5. Cost
- C2649436: $1.5251@30, $1.3599@100, stock 1902, EXTENDED (JLC lookup 2026-11-16). Only ST-original DPAK; C155647 stock 1. VND7NV04 (C155605 $1.66@100) is same footprint but Ilim ~6 A class (cold 4.5-8 A peaks) - no saving.
- Discrete logic MOSFET e.g. IRLR2905-class ($0.10-0.19, extended): datasheets NOT read; loses Ilim/OT/clamp, 3.3 V gate marginal. Not recommended.
- F1 C22446884: $0.116@50, $0.104@150, stock 6333, extended.

## Sources actually read
evidence/cur_db, ord_db, cur_mb8995/9697/9900/0105, ord_mb8993-0105 pcb_pads/nets/net_routing/footprints; kb/interconnect.md; kb/parts/P16; datasheets VND14NV04 (full text + p.5, p.18, figs 11/12/15), 2920L300 (text); datasheets/extra/LSU49_bosch.pdf (p.2-3); firmware heater_control.cpp, heater_thread.cpp, wideband_config.h, can.cpp, repo miata_f1 board/port files; repo INSTALL.md, research/rev0.10_design_audit.md A13; tools/lcsc.py.

## Not checked
Cold/hot heater resistance from a Bosch primary source (only web summary); IPC current limits only quick-estimated; JST PUD datasheet not opened (3 A from repo); Micro-Fit datasheet; wire harness gauge; ECU case air temperature data; any circuit_sim result for the heater (repo's circuit_sim_full.py not rerun); reference designs in ext/ (wideband-mck1117 uses same VND14NV04 + 1k per repo audit, not re-read).
