# P16 - Resettable fuses (PTC) on every board

STATUS: complete (2026-11-16). Tags: VERIFIED / INFERRED / UNVERIFIED per review brief rule 1.

## Summary
1. All 5 LCSC codes are the intended parts and packages (kb/parts_manifest.md, lcsc.py today). Pad nets checked on PCB and netlist: PTCs are non-polarised, orientation irrelevant, pad1 = supply side, pad2 = load side on every instance. Checked, correct.
2. Voltage ratings 30-33 V (24 V jump start OK; PTCs are untripped in a load dump so only I*R across them; D6 SMCJ30A on the db clamps).
3. REPO CLAIM WRONG: VERIFICATION.md:529 says F1 3 A part has "about 2.4 A hold at 60 C". Datasheet (C22446884 derating table, row 2920L300) says 1.99 A at 60 C, 1.34 A at 85 C. The firmware ramp starts at 7 V effective (ext/wideband-rusefi heater_control.cpp:109): 7 V / 2.5 Ω cold = 2.8 A rms, above the 60 C hold, and above the derated trip current at 85 C (about 2.2 A). Hot-ECU heater nuisance trip is plausible.
4. Ordered db F1 (nSMD050-33V, 0.5 A): derated hold 0.34 A at 60 C, 0.24 A at 85 C vs logic load 0.25 A (13.8 V) and 0.45 A (8 V cranking): marginal/likely nuisance trip when hot. Fixed on rev 0.10 (1.1 A). Ordered F4 (0.5 A) also too small for the 0.45 A boost valve the INSTALL doc mentions.
5. Supply: SMD1812-200-30 (C46641168) JLC stock 57 today (manifest 4): blocks 9900/0105 builds >~28 boards. Swap to BHFUSE BSMD1812-200-30V C960026 (194k stock, same table).
6. F2/F3 (2 A) derate to 1.45 A at 60 C, 1.09 A at 70 C, 0.80 A at 85 C; idle valve mean current at high duty on a hot day can exceed that; low-medium risk.
7. Repo statement "No 1812 part holds 3 A above 8 V" is false: BSMD1812-300-24V C7500481, 1812L300/30GR C48985875 exist (not cheaper; no need to change).
8. db F2 nSMD010 in the LSU VM wire: Ri 1.6 ohm min, R1max 15 ohm; adds series resistance in the pump return path (see 3.5).

## 1. Inventory (VERIFIED: kb/parts_manifest.md, evidence/<board>/pcb_pads.csv)
| Board | Ref | BOM value | LCSC | Real MPN | Pkg | Pad 1 net | Pad 2 net |
|---|---|---|---|---|---|---|---|
| cur_db (rev 0.10) | F1 | BSMD1812-110-33V | C883150 | BHFUSE | 1812 | /Power/+12V_IN | +12V |
| cur_db | F2 | nSMD010 | C70065 | TECHFUSE (Sea&Land) | 1206 | LSU_VM | WB_VMS |
| cur_mb all | F1 | 3A | C22446884 | 2920L300/30GR LUTE | 2920 | VBAT_IN | HTR_PWR |
| cur_mb all | F4 | 1.1A | C883150 | BSMD1812-110-33V | 1812 | VBAT_IN | AUX_VBAT |
| cur_mb9900/0105 | F2 | 2A | C46641168 | SMD1812-200-30 hongjiacheng | 1812 | VBAT_IN | IAC_12V |
| cur_mb0105 | F3 | 2A | C46641168 | same | 1812 | VBAT_IN | OCV_12V |
| ord_db (0.9) | F1 | nSMD050-33V | C70077 | TECHFUSE | 1206 | +12V_IN | +12V |
| ord_db | F2 | nSMD010 | C70065 | | 1206 | LSU_VM | WB_VMS |
| ord_mb all | F1 | 3A | C22446884 | | 2920 | VBAT_IN | HTR_PWR |
| ord_mb all | F4 | 0.5A | C70077 | nSMD050-33V | 1206 | VBAT_IN | AUX_VBAT |
| ord_mb9900/0105 | F2 | 2A | C46641168 | | 1812 | VBAT_IN | IAC_12V |
| ord_mb0105 | F3 | 2A | C46641168 | | 1812 | VBAT_IN | OCV_12V |
(1989-95 mb has F1 and F4 only; nets VERIFIED in evidence/cur_mb*/pcb_nets.txt. HTR_PWR = F1.2 + J2.8 only; IAC_12V = D1.1 F2.2 J1; OCV_12V = D2.1 F3.2 J1; AUX_VBAT = D5.1 F4.2 J5.15. db +12V = C24 C62 D12 F1.2 L1 R7 U3.7/8 U14.7/8 (TLS115B0EJ 5 V trackers).)

## 2. Datasheet digest (VERIFIED, datasheets/txt/*)
| Part | Ihold/Itrip 25C | Vmax/Imax | Rmin / R1max | time to trip | Ihold 60C / 85C |
|---|---|---|---|---|---|
| BSMD1812-110-33V C883150 | 1.10/2.20 A | 33 V / 40 A | 45 mΩ / 250 mΩ | 0.3 s @8 A | 0.71 / 0.52 A |
| nSMD010 C70065 | 0.10/0.25 | 60 V / 100 A | 1.6 Ω / 15 Ω | 1.0 s @0.5 A | 0.070 / 0.055 A |
| 2920L300/30GR C22446884 | 3.0/5.0 | 30 V / 40 A | 12 mΩ / 48 mΩ | 20 s @15 A | 1.99 / 1.34 A (also 40C 2.52, 50C 2.26, 70C 1.79) |
| SMD1812-200-30 C46641168 | 2.0/4.0 | 30 V / 40 A | 20 mΩ / 100 mΩ | 2 s @ 8 A | 1.45 / 0.80 A (70C 1.09) |
| nSMD050-33V C70077 | 0.5/1.0 | 33 V / 100 A | 150 mΩ typ(100 min) / 700 mΩ | 0.1 s @8 A | no table; generic nSMD curve (image work/.../nsmd_derate.png) 68% / 48% = 0.34 / 0.24 A (INFERRED from graph) |
| 1206L110/33NR C48985884 (read, datasheets/extra) | 1.1/2.2 | 33 V / 40 A | 40 mΩ / 270 mΩ | 0.3 s @8 A?(col) | 0.72 / 0.55 A |
Trip current at temperature is not tabulated; INFERRED by scaling Itrip with the hold ratio: 2920L300 trip ~3.3 A @60C, ~3.0 A @70C, ~2.2 A @85C. Datasheet notes (C883150 p.8): hold is "not a long-term continuous rating", keep away from heat sources, no hot-air rework, soldering iron >1.5 mm away, max 3 s.
Time-current curves (images in work/P16-ptc-fuses/): 2920L300 trips in about 3 s at 10 A, about 0.03 s at 40 A; below about 5 A not within 100 s (25 C).

## 3. Per-fuse usage audit
### 3.1 db F1 (logic supply), cur 1.1 A / ord 0.5 A
Load: buck (U2 LMR14020) -> 5 V and 3.3 V rails, two TLS115 trackers, SD card. Repo figures: 0.25 A at 13.8 V, 0.45 A at 8 V cranking (VERIFICATION.md:684,1146) (repo model values, not measured). Drop: 0.25 A x 45-250 mΩ = 11-63 mV (cur); ord 0.15-0.7 Ω x 0.25 A = 38-175 mV (INFERRED; the repo itself notes VBATT reads 0.3-0.6 V low).
- cur: hold 0.71 A (60C), 0.52 A (85C) vs 0.45 A worst -> margin 15 % at 85 C and cranking at once; acceptable. 
- ord: hold 0.34 / 0.24 A vs 0.25 A steady and 0.45 A crank. At 85 C hold < steady load; trip current ~0.48 A (85C). A hot ECU can trip or run the PTC hot (rising R, brown-out). Worth fixing on ordered boards: 1206 pads fit 1206L110/33NR (C48985884, 33 V, 1.1 A, 25.6k stock, $0.079@50, $0.0757@150; datasheet read) or nSMD110-24V C19108403 (datasheet not read). Hand rework of PTC: datasheet forbids hot-air; iron method with care.
- Voltage: 33 V part, series with D12 SMAJ33A (Vbr min 36.7 V). 24 V jump: fine. Fault current available: D7 Schottky, car fuse; PTC Imax 40 A.
- Pads: 1812 pads 1.125x3.4 mm, pitch 4.275 (gap 3.15) vs datasheet pad 1.78 wide (smaller toe, standard KiCad part; INFERRED, low).
### 3.2 mb F1 (LSU heater supply) 3 A hold, 2920
Load VERIFIED from Bosch LSU 4.9 sheet (datasheets/extra/LSU49_bosch.txt): 7.5 V nominal, 7.5 W steady = 1.0 A rms; Bosch strategy 1.5 V -> 8.5 V -> ramp to 13 V. rusEFI ext firmware: preheat then ramp starts 7 V effective, +0.4 V/s, to 12 V max (heater_control.cpp:109,173-176). Cold R 2.5-4 Ω is the repo's figure (UNVERIFIED value). Start current 7/2.5 = 2.8 A rms (1.75 A at 4 Ω), falling as R rises.
- vs hold: 1.99 A @60 C, 1.34 A @85 C. 2.8 A exceeds hold above about 45 C ambient and approaches trip (~3.0 A @70C, ~2.2 A @85C). Steady 1.0 A OK even at 85 C (1.34 A).
- A trip kills warm-up (timeout 60 s, HEATER_WARMUP_TIMEOUT) = no wideband until PTC cools. Likelihood needs ECU interior above about 70 C at cold sensor; hot-soaked car start. Medium.
- Drop at 2.8 A: 34-134 mΩ*... = 0.03-0.13 V.
- Options: (a) lower rampVoltage start in miata_f1 (e.g. 5.5 V; firmware only, free); (b) 2920L400/30GR C19078761 (same datasheet C22446884: 4 A/8 A, 30 V, 8/40 mΩ; hold 2.65 A@60C, 1.79 A@85C; 39.6k stock, $0.165@1, ~$0.09@4500): but 8 A trip is worse for the 1.0 mm track (Onderdonk adiabatic melt of 1 oz 1.0 mm, about 100/I^2 s: 1.6 s at 8 A, 1 s at 10 A; PTC ~5 s at 8 A) -> not recommended without thicker track. Neither track nor PTC protection is fast at 10 A: at 10 A the track (INFERRED, adiabatic, ignores substrate) reaches melting about as fast as the PTC trips; the car's own fuse is the real protection for a hard short.
### 3.3 mb F2 (IAC) / F3 (OCV VVT), 2 A hold 1812 (0.8 mm tracks)
Coil resistance: idle valve NB: forum figures 7.7-9.3 ohm spec (one owner measured 9 ohm at 10 C, another 10.7 ohm) up to 10-12.5 ohm (UNVERIFIED, forums; repo uses 11 ohm/20 mH, circuit_sim.py:229, NA BAC valve). OCV: repo assumes 7.5 ohm (UNVERIFIED; no source found). Peak at 14.4 V: 1.2-1.9 A (idle), 1.9 A (OCV). With the flyback diode on the output side of the PTC the mean current is D*V/R: idle at 50 % duty 0.8-0.9 A; 100 % duty 1.2-1.9 A. Hold 1.45 A @60C, 1.09 @70C, 0.80 @85C: nuisance trip needs hot ECU AND high duty/low-R coil (cold coil R is 15-20 % lower). OCV (VVT) duty can be 100 % for long periods only when commanded fully advanced; typical is low. Low-medium risk, UNVERIFIED loads.
- Drop: 20-100 mΩ x 1.5 A = 0.03-0.15 V; the valve gets a bit less voltage (negligible).
- What it protects: 0.8 mm 1 oz track (INFERRED 4 A trip -> ~48 C rise by IPC-2221) and the harness pin shorted to ground; car's main-relay circuit fuse is much larger. Keep.
- Supply: stock 57 pcs today (manifest said 4). 9900 needs 1/board, 0105 2/board. Alternative C960026 BSMD1812-200-30V (BHFUSE; same 1812, 2.0/4.0 A, 30 V, 40 A, Rmin 20 mΩ, R1max 100 mΩ, same derating row as the BSMD1812 datasheet I read; 194,147 stock, $0.0887@50, $0.0778@150; extended). Same footprint, no layout change. C883157 (24 V) is $0.0997@1.
### 3.4 mb F4 (AUX +12 V, header J5-15)
Feeds only J5 pin 15 -> external loads, e.g. boost valve via D5 flyback to OUT_BOOST (INSTALL.md:336: MAC valve about 0.45 A, UNVERIFIED). cur 1.1 A: 0.71 A @60C, 0.52 A @85C (OK for 0.45 A). ord 0.5 A: 0.34 / 0.24 A: a 0.45 A valve at 100 % duty will trip when hot; docs say 1.1 A (INSTALL.md:59,336 describe the current board). 1.1 A matches the 0.5 mm AUX_VBAT track (2.2 A trip -> ~26 C rise). Keep at 1.1 A; do not raise. Rework for ordered boards: 1206L110/33NR (as 3.1).
### 3.5 db F2 nSMD010 in LSU_VM
Pump current return in VM wire: Ip range -2 mA (lambda 0.65) to about +2.5 mA (Bosch table to lambda 1.7; air value UNVERIFIED). Series R 1.6 Ω (min) to 15 Ω (R1max) +/-33 % (thermal shock) -> 3-40 mV offset at full pump current, in addition to R109 10 Ω (INFERRED; effect on Nernst reference not simulated). At lambda 1 Ip ~ 0 so negligible at stoich. Hold 0.1 A (55 mA @85C) vs mA loads: fine. Fault: VM to 14.4 V -> 1.4 A through R109 (10 Ω, ~20 W): R109 opens before/with F2 (already documented as sacrificial family; not re-reported). Voltage 60 V ample.
Reference check: ext/wideband-mck1117 has no PTC in VM (grep) -> F2 is an addition by this repo.

## 4. Pad/footprint check
Footprints Fuse_1812_4532Metric / 1206 / 2920 match the package sizes; PTC two-terminal symmetrical (no polarity). Pad 1 = supply net on all (table 1). Checked, correct.

## Sources actually read
datasheets/txt C883150, C70065, C22446884, C46641168, C70077; extra/1206L110 (LUTE C48985884), extra/LSU49_bosch.txt; evidence/*/pcb_nets.txt, pcb_pads.csv; kb/parts_manifest.md; kb/interconnect.md; repo VERIFICATION.md lines 209-217, 269-275, 503-529, 573, 684-690, 1124, 1146; INSTALL.md 59/77/336; scripts/mb_common.py, wideband.py:148-190; ext/wideband-rusefi/firmware/heater_control.cpp; tools/lcsc.py live lookups 2026-11-16; one web search (forum IAC resistance).

## Not checked
OCV coil resistance (no source), NB idle valve exact spec, boost solenoid current, ECU interior temperature, actual LSU cold heater resistance, nSMD050 derating table (used generic graph), reflow/hand rework effects, 1989-93 rev 0.11 board differences beyond net list, thermal effect of neighbouring parts on db F1 placement, 24 V and 1812L300 alternates' datasheets (not read, not recommended).
