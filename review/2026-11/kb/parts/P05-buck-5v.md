# P05 - 5 V buck converter (daughterboard U2 LMR14020 + L2, D9, C17/C18/C71, C19, C20, C21, C22/C23/C59, R8, R9, R10)

Run 2026-11-16. Tags: VERIFIED / INFERRED / UNVERIFIED as in review brief section 5.

## Summary
1. Pinout, wiring and footprint of U2, L2, D9 and all passives are CORRECT on cur_db (rev 0.10) and ord_db (rev 0.9). No wiring error found. (VERIFIED: pcb_pads via pcbnew, design.py:227-241, TI SNVSAA5B p.3, Sunlord land pattern, KiCad SMA convention pad1 = cathode.)
2. RT 10 k gives fSW = 32537 / 10 = (3253.7)^(1/1.045) = 2.295 MHz (TI eq.5), slightly above TI table value 10.5 k = 2.2 MHz. Datasheet tolerance (400-600 kHz at 500 kHz) is +-20 %, so the top of the spread (about 2.75 MHz) exceeds the 2.5 MHz recommended maximum. Harmless in practice (higher switching loss only), low.
3. Inductor ripple at 2.3 MHz / 10 uH is only 0.14 A at 14.4 V (K_IND about 0.07 at 2 A, 0.18 at 0.8 A); TI wants 20-40 % of Iout max but at the real 0.3-0.8 A load it is a normal 20-45 %. Peak current with a 2 A load would be 2.07 A, far under L2 Isat 5.2 A (typ) and under the 3.8 A (max) current limit.
4. Output capacitance: 3 x 10 uF X5R 25 V 0805 (+ C26 10 uF at U4) is about 25-30 uF effective at 5 V (derating 60-75 %, UNVERIFIED, Samsung DC-bias curve not retrievable). TI's example says "for stability consideration one 47 uF output capacitor is needed at least" (p.19, example at 1 MHz / 5.5 uH). The TI doc gives no formula or table to scale that to 2.3 MHz / 10 uH, so whether 25-30 uF is stable is NOT provable from the datasheet. Only a bench loop measurement settles it. Risk: medium-low.
5. Load budget: 5 V rail about 0.3 A typical, about 0.7 A worst case (CAN dominant + SD write); 2 A part is oversized but price-neutral. A 1 A part (LMR14010) costs more at JLC. Keep U2.
6. Cheaper alternate: none worth it. Buck group costs about $0.9 total; U2 is $0.445 @100. AP63205 (32 V / 85 C) and TPS5430 (5.5-36 V, different pinout) are not drop-in and fail input range. Only saving is JLC extended-part fee (one-off per order) if a basic part were used: not worth redesign.
7. Cranking: dropout begins near Vin 5.6 V at 2 A / 5.4 V at 1 A (TI fig 5-8, 2.2 MHz). With 6 V at battery, U2 Vin about 5.3-5.5 V, so 5 V sags to about 4.8-5.0 V, 3.3 V LDO still fine.
8. Input surge margin: D12 SMAJ33A allows VIN to rise above the buck's 44 V abs max only in an UNSUPPRESSED load dump (inferred, see F5).
9. Ordered rev 0.9 daughterboard differs: no C71, F1 = nSMD050 (0.5 A hold), L1 = 1210 500 mA part. The buck's input current is below that hold current only at moderate temperature (see F6).

## 1. Identity (VERIFIED: tools/lcsc.py run today, kb/parts_manifest.md)
| Ref | LCSC | Part | Pkg | Type | Stock | Price |
|---|---|---|---|---|---|---|
| U2 | C187824 | TI LMR14020SDDAR | HSOP-8-EP (DDA) | Extended | 14,545 | $0.506 @30, $0.445 @100 |
| L2 | C132141 | Sunlord MWSA0603S-100MT 10 uH | 7.0x6.6x2.8 | Extended | 23,129 | $0.070 @60 |
| D9 | C94193 | Diodes B360A-13-F 60 V 3 A | SMA | Extended | 30,253 | $0.081 @150 |
| C17,C18 | C13585 | Samsung CL31A106KBHNNNE 10 uF 50 V 1206 | | Basic | 4.5 M | $0.121 |
| C71,C19 | C14663 | Yageo CC0603KRX7R9BB104 100 nF | | Basic | | $0.010 |
| C20 | C57112 | FH 0603B103K500NT 10 nF 50 V | | Basic | | $0.010 |
| C21 | C1603 | Samsung CL10B221KB8NNNC 220 pF | | Basic | | $0.007 |
| C22,C23,C59 | C15850 | Samsung CL21A106KAYNNNE 10 uF 25 V X5R 0805 | | Basic | 9.1 M | $0.031 |
| R8 10k / R9 68k / R10 12k | C25804 / C23231 / C22790 | Uniroyal 0603 1 % | | Basic | | <$0.004 |
All identities match the intended parts. LMR14020SDDAR is the TI orderable (datasheet SNVSAA5B, Dec 2024, same family sheet as LCSC copy).
Sunlord data (datasheets/extra/MWSA_chipdip.pdf, series sheet rev 2018/11/30, VERIFIED): 10 uH +-20 %, DCR 68 mOhm max, Isat 5.2 A typ, Irms 4.5 A typ (JLC listing says 5.5 A / 4.5 A and repo comment says "Isat 5.5 A": the sheet says 5.2 A; 5.5 A is the 8.2 uH part). Body 7.0 x 6.6 x 2.8 mm; land pattern pad 2.35 x 3.5 mm, gap 3.7 mm (centres 6.05 mm).

## 2. Datasheet digest (TI SNVSAA5B, VERIFIED, p.numbers are printed pages)
- 4-40 V buck, 2 A, 90 mOhm (180 max) high-side FET, peak-current mode, internal compensation, 200 kHz-2.5 MHz by RT, sleep mode 40 uA, SS pin, EN precision 1.2 V (1.05-1.38), VIN UVLO 3.7 V rise / 285 mV hysteresis, current limit 2.5 / 3.2 / 3.8 A (p.5), Vfb 0.750 (0.735-0.765 over temperature), tON_MIN 75 ns typ, DMAX 97 % (p.6), thermal shutdown 170 C.
- Abs max (p.4): VIN, EN 44 V; BOOT-GND 49; SW -3..44; BOOT-SW 5.5; FB 5.5; RT/SYNC 3.6; SS 5; Tj 150. Recommended: VIN 4-40, Tj -40..125.
- Thermal: RthJA 43.2 C/W (JEDEC), RthJC(bot) 7.8.
- Pins (DDA HSOIC-8, p.3): 1 BOOT, 2 VIN, 3 EN, 4 RT/SYNC (not float, not short), 5 FB, 6 SS, 7 GND, 8 SW, 9 thermal pad = GND.
- Required externals: CBOOT 0.1 uF X7R/X5R >= 16 V; CIN 4.7-10 uF + 0.1 uF at pins; Schottky >= 1.25 x Vin_max; L from eq.10; COUT per eq 11-14 plus the 47 uF stability remark; RT eq.5; CSS = tSS*3 uA / 0.75 V.
- Layout (p.22): FB divider close to pin, CIN at VIN/GND pins, L close to SW, COUT near L/D junction, single-point ground.
- Land pattern (DDA0008B): pads 1.55 x 0.6, row-to-row centres 5.4 mm (outer 6.95), EP package pad 2.11-2.71 x 2.8-3.4, paste 2.71 x 3.4 (0.125 stencil).

## 3. Usage audit
### 3a. Pin table (cur_db, pcbnew pads; ord_db identical for U2)
| Pad | Net | Datasheet function | Verdict |
|---|---|---|---|
| 1 | BUCK_BOOT (C19 to SW) | BOOT | OK |
| 2 | +12V_F | VIN | OK |
| 3 | +12V_F | EN (tied to VIN = TI's "simplest" enable, p.16) | OK (EN abs max 44 = VIN) |
| 4 | BUCK_RT (R8 10k to GND) | RT/SYNC | OK |
| 5 | BUCK_FB (R9 68k top, R10 12k bottom, C21 220 pF across R9) | FB | OK |
| 6 | BUCK_SS (C20 10 nF to GND) | SS | OK |
| 7, 9 | GND (EP has 2 GND vias 0.3 mm, tented) | GND, thermal pad | OK |
| 8 | BUCK_SW (D9.1 cathode, L2.1, C19.2) | SW | OK |
Schematic netlist, design.py:227-229 and PCB agree. Pin 1 position (top-left, pads 1-4 left side, 5-8 right going up) matches the standard SOIC orientation.
- D9: pad 1 = BUCK_SW = cathode (KiCad D_SMA pad 1 is cathode), pad 2 = GND = anode. Correct freewheel orientation.
- L2: pad 1 SW, pad 2 +5V. C19 pad 1 BOOT, pad 2 SW. C21 pad1 +5V. All correct. Vout = 0.75 (1 + 68/12) = 5.000 V; worst case with Vfb +-2 % and 1 % resistors about 4.88-5.12 V (INFERRED).
### 3b. Footprint
- U2: KiCad SOIC-8-1EP 3.9x4.9 EP2.29x3: pads 1.95 x 0.6, centres 4.95 apart (outer 6.9), EP 2.29 x 3.0 + 4 paste sub-pads. TI example pads 1.55 long at 5.4 centres (outer 6.95). Same outer extent; EP pad smaller than the package pad (about 6.9 vs 9 mm2) so thermal contact is about 25 % less than the TI example: immaterial at 0.4 W. EP clearance to pin pads 0.36 mm. OK.
- L2 pads 2.35 x 3.5, centres 6.05 mm = Sunlord recommended pattern exactly. D9 SMA standard.
- Layout (crop images in work/P05-buck-5v/): SW node is a straight 9 mm run U2 pin 8 -> D9 -> L2 on the top layer; D9 and L2 right next to U2. C71 100 nF is 2.2 mm from VIN, C17/C18 are 7-10 mm away (rev 0.10 added C71 for this reason). Output caps at 130 mm x, 5-9 mm from L2. Layout is reasonable, no error.
- Only 2 EP vias (tented, in pad, uncovered pad opening): solder wicking / voids possible at reflow, immaterial thermally (Tj below).
### 3c. Electrical analysis (INFERRED from datasheet equations)
- fSW = 2.295 MHz (R8 1 %: 2.28-2.31; IC spread +-20 % per p.6 spec at 500 kHz, may not scale).
- Duty / on-time: 14.4 V: D = 0.35, tON = 151 ns (> 75 ns). 16 V: 135 ns. 24 V jump: 98 ns. 35 V: 67 ns: below tON_MIN so pulse-skipping above about 30 V (eq.6 fSWmax about 2.1 MHz at 35 V) = only more ripple, no harm. At the +20 % frequency edge 24 V gives 81 ns, marginal. Low.
- Inductor: dIL = Vout (1-D)/(L f) = 0.142 A @14.4 V, 0.149 @16 V, 0.187 @36 V. Eq.10 minimum L at 36 V, 2 A, K=0.4: 2.3 uH, so 10 uH is 4x the minimum, giving less slope/noise ratio (TI warns "not too small") but fine at real loads; also drops to DCM below about 75 mA. Peak at 0.8 A = 0.87 A; current-limit 3.8 A < Isat 5.2 A, so no saturation even in a short. 4.7 uH would also work; saving is about $0.02: not worth.
- Diode: Vr 60 V > 1.25 x 44; Pd = 0.5 V x 0.7 A x 0.65 = 0.23 W (SMA fine); 3 A rating >= current limit, OK. Leakage 500 uA @60 V irrelevant.
- Output ripple: dVC = dIL/(8 f C) = 0.15/(8 x 2.3 M x 25 u) = 0.3 mV, ESR part < 1 mV: switching spikes dominate.
- Transient: eq.13 C > 3 dI/(f dV) = 3 x 0.7/(2.3M x 0.25) = 3.6 uF; eq.14 C > (0.7^2) x 10u / (5.25^2-25) = 1.9 uF. Fine.
- Stability: 47 uF remark (see summary 4). Current design has 3 x 10 uF at U2 side + 10 uF C26 near U4.
- Soft start: tSS = 10 nF x 0.75 / 3 uA = 2.5 ms (TI example 5 ms/22 nF). Inrush into 30 uF + loads about 60 mA + load. Fine.
- Boot: 100 nF X7R 50 V (>= 16 V) per TI.
- Input cap: Irms = Iout sqrt(D(1-D)) = 0.24 A @0.5 A, 0.95 A @2 A; C17+C18 (10 uF 50 V 1206, about 60 % at 14 V = 12 uF) handle it, ripple 4 mV at 0.5 A. Fine.
- Thermal: Pout 3.5 W (0.7 A worst) at about 82 % eff = 0.77 W total, IC share about 0.4 W; x 43.2 C/W = +17 C; at 85 C air Tj about 100 C < 125 C. At 2 A (not reachable) thermal shutdown protects. INFERRED; efficiency assumed.
- Cranking: path D7 (SS34 about 0.4 V) -> F1 (PTC R1max 0.25 Ohm, hotter more) -> L1 (29 mOhm). With 6 V battery and 0.6 A: U2 Vin about 5.3-5.5 V. TI fig 5-8 (5 V out, 2.2 MHz): Vout follows Vin down from about 5.4-5.6 V, so about 4.8-5.0 V; 3.3 V LDO (LDL1117) still regulates to Vin about 3.8 V. Below 5 V battery the 5 V rail and TCAN (4.5 V min) drop: only a very deep crank; UVLO rises at 3.7 V.
- EMI: 2.3 MHz is above the AM broadcast band (0.53-1.8 MHz) and the fundamental clears it with +-20 % spread (1.84 MHz low edge); harmonics 4.6/6.9 MHz. This is the standard automotive reason for 2.2 MHz. UNVERIFIED that this is the author's intent; good choice. Input filter L1 2.2 uH + 20 uF helps.
- Abs-max per condition: normal 14.4 V (VIN 13.9 after D7); jump start 24 V: fine (44 V). Reverse battery: D7 SS34 blocks; D9 is not exposed (behind D7). Harness pin short to battery: wiring passes through D7/F1. Load dump: see F5. 85 C: Tj 100 C.
- Sequencing/pull-ups: none required; EN to VIN means start at UVLO; no external UVLO divider, so with a slowly rising/falling battery the buck starts at 3.7 V and may chatter in a deep crank (RT, SS handled).

### 3d. +5 V / +3.3 V load budget (from pcb_nets.txt +5V / +3V3 and datasheets)
| Consumer | Rail | Estimate | Source |
|---|---|---|---|
| U4 LDL1117S33R feeds all +3V3 | 5 V | = 3.3 V load | |
| STM32F407 (168 MHz, all periph.) | 3.3 | 93 typ / 109 @85 C / 117 max mA | C12345 datasheet table line 5261 (VERIFIED) |
| STM32F103 (72 MHz, all periph.) | 3.3 | 33-50 mA | C8734 lines 2340-2365 (VERIFIED) |
| microSD write | 3.3 | up to about 100 mA | UNVERIFIED (SD spec memory) |
| 5 LEDs, pull-ups, op-amps, LVC4245 VCCA, TCAN VIO, REF3033 | 3.3/5 | 15-30 mA | INFERRED |
| 3.3 V total | | about 0.2 A typ, 0.3-0.35 A peak | |
| 2x TCAN1042V (U10, U106) | 5 | 2.5 mA recessive max each, dominant max 110 mA each (datasheet line 129 note), about 50-70 typical on 60 Ohm | VERIFIED |
| 2x TC4427 + 4 coil inputs | 5 | 2 mA each + about 5 mA per coil input | datasheet line 143 (VERIFIED) / INFERRED |
| 74HCT04, LM2903, LVC4245 VCCB | 5 | < 5 mA | INFERRED |
| Trackers U3/U14 | 12 V side | only the +5V reference pin sees 5 V; sensor load comes from +12V (via F1/L1), not from the buck | INFERRED from design.py:244, 491 |
5 V total: about 0.25-0.3 A typical, about 0.7 A worst; Pin at 12 V about 0.35 A worst; at 5.4 V about 0.7 A. Buck loading 15-35 % of its 2 A. LDO dissipation 1.7 V x 0.35 A = 0.6 W on SOT-223 (see P08).

### 3e. Reference designs
ext/ hellen boards use their own 5 V supplies; no direct LMR14020 equivalent checked (not checked; not found by quick grep of ext/*.md). UNVERIFIED comparison.

## 4. Cost / simplification
- Whole buck group about $0.95/unit @100 (U2 0.445, L2 0.063, D9 0.081, C17/C18 0.24, caps/R 0.11). A "free" removal: none credible. C21 (220 pF feed-forward, $0.007) is not in TI's application circuit and could be dropped, but its effect on loop phase is unknown (UNVERIFIED): do not remove without bench data.
- Alternatives (LCSC data only, datasheets NOT read, so NOT recommended): AP63205WU-7 C2071056 TSOT-23-6 $0.25-0.46, but 3.8-32 V and -40..85 C: fails input range. TPS5430DDAR C9864 BASIC $0.35-0.58, 5.5-36 V, 500 kHz, SOIC-8-EP, but different pinout, input min 5.5 V fails cranking, 500 kHz in AM band. AP64200SP-13 C3192345 SO-8-EP 3.8-40 V, 2 A, $0.46 @100: not cheaper. XL1509-5.0E1 C61063 basic $0.12-0.25, 150 kHz, 4.5-40 V, 2 A: needs big inductor and different pinout, noisy for AM. TPS54302 3 A 28 V: too low. Conclusion: keep LMR14020.

## Findings (see structured output) F1-F8
F1 output cap vs TI 47 uF stability remark (risk). F2 RT tolerance. F3 Isat doc error. F4 ordered F1/L1 0.5 A hold vs buck input current. F5 abs-max margin in unsuppressed dump (D12 Vc 53.3 V @7.5 A, VIN abs max 44 V). F6 EP via-in-pad. F7 checked-correct pinout/footprint. F8 cranking dropout. F9 alternates rejected.

## Sources actually read
evidence/cur_db and ord_db pcb_nets.txt, pcb_footprints.csv; pcbnew pad dump of cur_db (work/P05-buck-5v/geom2.py); repo/scripts/design.py 196-262, 296-327; datasheets/C187824 TI SNVSAA5B (work/P05-buck-5v/LMR14020_SNVSAA5B.txt; pp. 3-6, 12-22, fig 5-8 image); datasheets/extra/MWSA_chipdip.pdf (Sunlord MWSA series); C883150 BSMD1812-110 table; C223988 SMAJ33A, C224048 SMCJ30A tables; C12345, C8734, C485806, C20551; tools/lcsc.py lookups and keyword searches (AP63205, LMR14010, AP64200, TPS54240, TPS54302, SY8205, LM2596, XL1509, TPS5430).

## Not checked
Samsung DC-bias curve for CL21A106KAYNNNE at 5 V; any bench loop measurement; B360A datasheet full read (specs taken from LCSC parameters); hellen reference boards; SD card current; efficiency curve of the part (TI sheet has efficiency graphs for 12 V only); 85 C thermal using actual copper area (analytic only).
