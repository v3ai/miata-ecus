# R08 - Low-side driver landscape (injectors, valves, relays): cheaper or simpler parts that JLCPCB stocks

Status: COMPLETE (2026-11-16). JLC/LCSC data pulled live 2026-11-15/16 with tools/lcsc.py (raw JSON in work/R08-low-side-driver-landscape/jlc/*.json, 116 keyword searches). Datasheets read are in datasheets/extra/ (list at the end).
Prices are USD per piece at the stated JLC tier (30 / 100 pieces), 2026-11-15/16. "ext" = JLC Extended (chargeable $3.07 per unique non-preferred line per order, kb R21); SN74LVC4245A is Preferred (free).

## Summary (10 lines)

1. Baseline per board (rev 0.10): 8 x VND7NV04 ($2.06 @30 / $1.82 @100) + 11 x ZXMS6004FF ($0.4386 / $0.3846) + 2 x SN74LVC4245A ($0.393 / $0.344) = **$22.11 @30 / $19.45 @100** per board, parts only (VERIFIED prices).
2. Same-die-in-cheaper-package FAILS on price: VNN7NV04 (SOT-223) costs $2.07 / $1.87, the same as the DPAK. Only the smaller OMNIFET II VNN3NV04 (SOT-223, 120 mohm max, $1.06 / $0.87) is cheaper, and it is a different (weaker) die.
3. **Best low-risk change: NCV8401B (onsemi, DPAK, C604055) in the existing DPAK footprint**: pinout 1 gate / 2 drain+tab / 3 source equals the VND7NV04 usage, 28 mohm typ 34 max at 5 V, 42 V clamp, EAS 800 mJ, $0.9605 / $0.8099, stock 2200. Saves $8.8 / $8.0 per board, no re-layout, keeps the 5 V shifter. Caveat: current limit 25-35 A at 5 V (VND7NV04: 6-12 A), so a shorted wire pulls tens of amps until thermal shutdown.
4. **Best cost change: NCV8403A (onsemi, SOT-223, C266786)**: 63 mohm typ / 76 max at VGS = 5 V, I = 3 A, 135 mohm at 150 C, limit 10-20 A, EAS 470 mJ, Vth 1.0-2.2 V, $0.7396 / $0.6283, stock 1908. Its published typical curve (Fig. 8) shows about 80 mohm (25 C) and 130 mohm (150 C) at VGS = 3 V, so a 3.3 V GPIO can probably drive it directly (typical curves only; not guaranteed at 3.3 V). With U11 deleted: $5.9 for 8 channels instead of $16.5.
5. **The 7 relay channels already accept 3.3 V by datasheet**: ZXMS6004FF (and ZXMS6005DG/DGQ) list VIH = 3 V min, VIL = 0.7 V max, Rds 400-600 mohm at VIN = 3 V. So the relay level shifter U12 (and its enable gating) can go; CEL already drives its FET directly in rev 0.10.
6. Multi-channel ICs are not viable at JLC: TLE8104, TLE8110, TLE6240, TLE9104(high side!), MC33810 have zero or no stock/entries; TLE8888 $10 (50 pcs) is a whole ECU-support chip. Only ST L9826 (octal 450 mA, 1.5 ohm, SPI, $1.73 @30, 951 in stock) fits, for light loads, with weaker protection: not recommended.
7. Duals: NCV8402AD (SO-8, $0.653 per 2 channels, stock 28 k) is a fair light-load part (about $0.9 per board saving) but 230 mohm at 5 V and its 3.3 V behaviour is not characterised; VNLD5160 (SO-8, $1.67 per 2) needs a 5 V drive (input = supply pin) and puts two injectors' heat in one SO-8.
8. Injector energy: only one published inductance figure found (14.8 ohm port injector, L = 20.3 mH, Sensors 2020; the repo cites the same). 1/2 L I^2 = 9.6 mJ at 14.4 V / 14.8 ohm, 18 mJ at 16 V / 12 ohm. With the rev 0.10 external clamp the driver never sees it, so driver clamp ratings do not matter for the choice; what matters is Rds(on) x I^2 and package heat.
9. Not recommended: plain MOSFETs (lose the current limit / thermal shutdown the repo added to survive wire shorts), 30 V parts such as AO3400A (clamp peak battery + 16.8 V can exceed 30 V), unread datasheets.
10. Another rusEFI precedent: the Hellen NA6 94 board BOM lists 8 x ZXMS6005SGTA (SOT-223) plus ULN2003 (ext/hellen-miata-NA6 BOM).

## 1. What the board uses today (VERIFIED, repo/scripts/design.py)

- Q1-Q8 VND7NV04TR-E (C155605), channels INJ1-4, IACV, VVT, BOOST, ALT (design.py:98, 332-346), input through 220 ohm from U11 (SN74LVC4245A, 5 V side) with 10 k pull-down; per-injector external clamp diode ES1D + 1.5SMC16A to VBAT_IN (design.py:355-373).
- Q9-Q15 ZXMS6004FFTA (C95063) relays FP, MAINRLY, AC, FAN, CEL, TACH, LS7 through U12 (second LVC4245A) except CEL (direct, 1k). Q16-Q19 ZXMS6004FF as ignition pull-downs behind TC4427 + 74HCT04 (design.py:268-330).
- JLC text mislabels VND7NV04 "High Side Switch": it is a low-side OMNIFET II (VNN7NV04 datasheet pin table).

## 2. Live JLC stock and price (VERIFIED 2026-11-15/16, tools/lcsc.py; $ per piece at 30 / 100)

| LCSC | MPN | package | lib | stock | $30 | $100 | note |
|---|---|---|---|---|---|---|---|
| C155605 | VND7NV04TR-E (baseline) | DPAK | ext | 2391 | 2.0619 | 1.8164 | |
| C501115 | VNN7NV04PTR-E | SOT-223 | ext | 1966 | 2.0697 | 1.8734 | same price as DPAK, no gain |
| C443999 | VNN3NV04PTR-E | SOT-223 | ext | 1438 | 1.0553 | 0.8737 | 120 mohm max |
| C604055 | NCV8401BDTRKG | DPAK | ext | 2200 | 0.9605 | 0.8099 | drop-in |
| C500319 | NCV8408BDTRKG | DPAK | ext | 2129 | 0.7838 | 0.6709 | latched thermal fault |
| C5209048 | NCV8405BDTRKG | DPAK | ext | 100 | 1.2435 | 1.0832 | stock too low |
| C266786 | NCV8403ASTT1G | SOT-223 | ext | 1908 | 0.7396 | 0.6283 | |
| C223559 | NCV8405ASTT1G | SOT-223 | ext | 1962 | 0.8050 | 0.7069 | 120 mohm max at 5 V |
| C459816 | NCV8406ASTT3G | SOT-223 | ext | 4875 | 0.5203 | 0.4467 | 240 mohm / 520 hot at 5 V (the repo's original, rejected) |
| C77755 | NCV8402ASTT1G | SOT-223 | ext | 38787 | 0.3305 | 0.2831 | 230 mohm at 5 V |
| C109030 | NCV8402ADDR2G (dual) | SO-8 | ext | 28493 | 0.6529 | 0.5547 | per package, 2 channels |
| C3235503 | ZXMS6005DGQ-13 | SOT-223 | ext | 7758 | 0.3551 | 0.2995 | |
| C95063 | ZXMS6004FFTA (baseline) | SOT-23F | ext | 13869 | 0.4386 | 0.3846 | |
| C377942 | VNLD5160TR-E (dual) | SO-8 | ext | 3054 | 1.6738 | 1.4906 | per package |
| C262999 | VNL5160N3TR-E | SOT-223 | ext | 142 | 0.4467 | 0.3829 | stock too low; 5 V drive only |
| C155658 | VNL5300S5TR-E | SO-8 | ext | 787 | 0.3166 | 0.2507 | separate 5 V supply pin |
| C2149847 | VNL5050S5TR-E | SO-8 | ext | 6980 | 1.075 | 1.0063 | 50 mohm |
| C2680403 | VNL5090N3TR-E | SOT-223 | ext | 723 | 0.7494 | 0.6496 | |
| C2653794 | BSP78 (Infineon HITFET) | SOT-223 | ext | 10632 | 1.0095 | 0.8541 | 45/60 mohm at 5 V, 500 mJ |
| C150926 | BTS3410G (dual HITFET) | SO-8 | ext | 2738 | 1.021 | 0.8623 | per package |
| C534771 | BTS3800SL | SCT-595 | ext | 3077 | 0.5122 | 0.432 | 800 mohm |
| C155567 | L9826 (octal) | SO-20 | ext | 951 | 1.7313 | 1.5071 | SPI |
| C158111 / C540055 / C540057 / C3231959 | TLE6240GP / TLE8104E / TLE8110 / TLE8104EXT | | ext | 0 | | | no stock |
| C2650386 | TLE9104SH | | ext | 535 | 3.28 | 2.83 | HIGH-side, not applicable |
| C1518732 | TLE8888QKXUMA1 | LQFP-100 | ext | 50 | 10.13 | 9.19 | |
| C3232951 | L9733CNTR | SSOP-28 | ext | 40 | 5.81 | 5.68 | |
| - | MC33810, NCV7512 | | | 0 hits | | | |

Other hits (no datasheet read, so not shortlisted): VNN1NV04 ($0.525), VNS/VND3NV04, NCV8403A-HXY (TO-252, HXY clone $0.643), VBsemi/JSM clones of BSP75 (stock 1-1182).

## 3. Datasheet facts (VERIFIED from the PDFs in datasheets/extra/, file name given)

| Part | input / drive | Rds(on) | current limit | clamp | energy | thermal | notes |
|---|---|---|---|---|---|---|---|
| VND7NV04 (baseline, via VNN7NV04P-E_lcsc_C501115 sheet, same OMNIFET II family) | Vth 0.5-2.5 V; Rds specified at 5 V; Rin min 150 ohm | 65 mohm max @5 V 25 C, 130 hot | 6-12 A @5 V | 40-55 V | EMAX 40 mJ (0.7 mH, 9 A), Eas 200 mJ (24 mH) | Tjsh 175 (150-200), SOT-223 Rthj-amb max 96 | diagnostic via input current |
| VNN3NV04P-E (C443999) | Vth 0.5-2.5 V; Rin min 220 ohm; Fig. 12: typ 115 mohm at Vin 3.5 V, 25 C, ~255 hot | 120 mohm max, 240 hot @5 V, 1.5 A | 3.5-7 A | 40-55 V | Eas 100 mJ | 175 C | needs 220 ohm min series; exactly the 220 ohm already fitted |
| NCV8401B DPAK (C604055; NCV8401BDTRKG.txt) | Vth 1.0-2.0 V; IGON 50-100 uA @5 V | 34 max @5 V 25 C, 60 hot | 25-35 A @5 V 25 C, 11-21 A @150 C | 42-50 V (40 at 150 C per family) | EAS 800 mJ (L 120 mH) | RqJA 110 / 60 (DPAK note 1/2); shutdown 150-200 C, hysteresis 15 | pin 1 G, 2 D/tab, 3 S |
| NCV8408B DPAK (C500319) | Vth 1.0-2.2 V; internal gate R 25.5 kohm | 60 max @5 V 3 A, 120 hot | 10-16 A | 40-51 V | EAS 185 mJ | LATCHED protection, resets when input < ~1.4 V (VLR 0.8-1.9 V) | different fault behaviour: firmware sees a lock-off until the input is dropped |
| NCV8403A SOT-223 (C266786) | Vth 1.0-2.2 V; IGSS 50-125 uA @5 V | 76 max @5 V 3 A, 135 hot; Fig. 8 typical ~80 mohm 25 C / 130 150 C at 3 V | 10-20 A @5 V | 40-51 V | EAS 470 mJ | SOT-223 RqJA 110 / 80 (notes); DPAK variant 95 / 50 | 3.3 V: only the typical graph, no spec |
| NCV8405A SOT-223 (C223559) | Vth 1.0-2.0 V | 120 max @5 V, 210 hot | 6-11 A | 42 V | 275 mJ | 130 / 72 | |
| NCV8402A SOT-223 (C77755) | Vth 1.3-2.2 V | 230 max @5 V, 460 hot; Fig. 8 starts at 4 V; Fig. 6: Id saturates ~1.9 A at VGS 3 V, ~3.9 A at 3.5 V | 3.7-5 A @5 V (2.3-3.7 hot) | 42-55 V | EAS 150 mJ | 114 / 72 | |
| NCV8402AD dual SO-8 (C109030) | same die | same | same | same | 150 mJ | 157 / 77 per package | |
| ZXMS6004FF (C95063; ZXMS6004FF_diodes.pdf) | VIH 3 V min, VIL 0.7 V max, "optimised for 3.3 V and 5 V"; Vth 0.7-1.5 V | 400-600 mohm @ VIN 3 V (0.5 A) | 0.7 min / 1.7 typ A @ 3 V | 60-70 V | 90 mJ | 150 / 83; trip 150-175 C | |
| ZXMS6005DGQ SOT-223 (C3235503; ZXMS6005DGQ_diodes.pdf, July 2026, AEC-Q101) | VIH 3 V min | typ 170 / max 250 mohm @3 V 1 A (ZXMS6005DG sheet) | 2.2 min A @3 V, 3.3 min @5 V | 60-70 V | 490 mJ | 96 / 42; Tj 150 | JLC text says 125 C, the Diodes sheet says -40..150 C |
| VNL5160 N3/S5, VNL5090, VNL5050, VNLD5160 (OMNIFET III) | N3 and dual: INPUT is also the 3.5-5.5 V supply (Vsupply = Vin); S5 singles: separate SUPPLY pin (5 V) and logic input VIL 0.9 / VIH 2.1 V | 160/170 max @5 V (VNL5160); 300 mohm (600 hot) VNL5300 | 3.5-7.5 A (5160); 2-3.8 A (5300) | 41-52 V | Eas 37 mJ (5160, 8.5 mH), 26 mJ (5300, 19 mH) | TTSD 150-200 C, SO-8 103-115 C/W, SOT-223 147 C/W | status pin open drain (S5 / dual); only the 5300 and 5050/5030 S5 are separate-supply parts |
| BSP78 HITFET (C2653794) | Vth 1.3-2.2 V (0.8 V min at 150 C) | 60 max @5 V 3 A, 100 hot | 18-30 A @10 V | 42-55 V | 500 mJ | | |
| BTS3410G dual HITFET (C150926) | Vth 1.3-2.2 V | 240 max @5 V 1.4 A, 480 hot | 5-10 A @10 V | 42-55 V | 150 mJ | | 1.3 A nominal/channel |
| BTS3800SL (C534771) | device ON from 2.7 V input | 800 mohm typ, 1.6 ohm max hot | | | 65 mJ | RthJA 110 | 3.3 V OK; costs more than ZXMS6004FF |
| L9826 (C155567) | SPI, VDD 5 V | 1.5 ohm typ, 3 ohm max hot, 450 mA per channel | only outputs 1-2 have current limit and thermal shutdown; 3-8 only over-current / short shutdown | 45-62 V | | 90 / 75 C/W | 8 channels |

## 4. Injector inductance and clamp energy

- Mazda specifies resistance only: 12-16 ohm at 20 C for the 1.8 DOHC family (repair-manual listings, secondary; aftermarket EV14 sets listed 12.5 ohm). UNVERIFIED as to the Miata's inductance.
- One published fit: a 14.8 ohm injector, L2 = 20.3 mH (needle open), R/L = 729 1/s; Sensors 2020, 20(15), 4151, PMC7435933, read 2026-11-16 (formula line "R/L = 14.8/0.0203"). VERIFIED for that injector; a single source, port injector of unknown make. Nexperia AN uses 5 mH for a peak-and-hold solenoid and a forum cites 6.5 mH for a 2.3 ohm Datsun injector (UNVERIFIED, not high impedance). No other measurement for saturated 12 ohm injectors was found in four searches.
- INFERRED energy (L = 20.3 mH): I = 14.4 / 14.8 = 0.97 A gives 9.6 mJ; 12 ohm at 16 V gives 1.33 A and 18 mJ; with 20 mH and 1.2 A 14.6 mJ. If the driver's own clamp took it (45 V clamp, 14.4 V supply) the driver would dissipate E x 45 / (45 - 14.4), about 21 mJ per event at 1.2 A, i.e. 1.3 W average at 60 events/s (sequential, 7200 rpm); twice per revolution pairs on 1989-93 wires. That would overheat any SOT-223 and is why the external clamp matters. Single-pulse ratings (EAS 150-800 mJ) are far above one event, but they say nothing about 60 Hz repetition.
- With the rev 0.10 per-injector ES1D + 1.5SMC16A clamps (design.py:368-373) the drain peaks at about VBAT + 16.8 + 0.9 V (about 32 V at 14.4 V). Every shortlisted 40-42 V part clamps above that, the 60-70 V ZXMS parts even more so. Hence all candidates are electrically equivalent for inductive energy; the decision is Rds(on), current limit, package copper and drive voltage.

## 5. Options ranked, with total cost per board (8 heavy + 11 light + level shifters; parts only; $ at 30 / 100 pieces)

Baseline: 8 x 2.0619 + 11 x 0.4386 + 2 x 0.3928 = **22.11**; at 100: 8 x 1.8164 + 11 x 0.3846 + 2 x 0.3437 = **19.45**. (Resistors, about $0.003 each, ignored.)

| # | Option | removes | per board @30 | @100 | saving @30 / @100 | main risks |
|---|---|---|---|---|---|---|
| a1 | 8 x NCV8401BDTRKG replaces VND7NV04 in the same DPAK pads | nothing but the part cost (lines: one ext line replaced by one) | 7.684 + 4.825 + 0.786 = **13.30** | 6.479 + 4.231 + 0.687 = **11.40** | 8.81 / 8.05 | current limit 25-35 A at 5 V (11-21 hot) against 6-12 A: a shorted output draws tens of amps for the time to shutdown, stressing the 12 V trace/fuse; no 150 ohm Rin spec (the 220 ohm stays harmless); stock 2200 (about 275 boards); 3.3 V drive not examined |
| a2 | 8 x NCV8408BDTRKG (DPAK) | same | 6.27 + 4.825 + 0.786 = 11.88 | 5.37 + 4.231 + 0.687 = 10.29 | 10.2 / 9.2 | latched thermal protection (reset needs input low): behaviour change for the firmware and for ALT/BOOST outputs; 60 mohm max, 120 hot |
| a3 | 8 x VNN3NV04P (SOT-223, ST same family) | DPAK footprint | 8.442 + 5.611 = 14.05 | 6.99 + 4.918 = 11.91 | 8.05 / 7.54 | re-layout, 120 mohm (240 hot), Eas 100 mJ, 3.5-7 A limit, 1438 in stock |
| a4 | same die in other package (VNN7NV04) | - | 16.56 + 5.61 = 22.17 | | -0.06 | no saving: reject |
| a5 | 8 x NCV8403ASTT1G (SOT-223), keep U11 | - | 5.917 + 4.825 + 0.786 = **11.53** | 5.026 + 4.231 + 0.687 = **9.94** | 10.58 / 9.51 | re-layout for SOT-223 (RqJA 110 min pad / 80 with 2 in2 copper); thermal model must be rerun |
| a6 | a5 plus drive U11 channels straight from 3.3 V GPIO | U11 (0.393), 8 x 220 ohm (replace by 1k or 220) | 5.917 + 4.825 + 0.393 = **11.14** | 5.026 + 4.231 + 0.344 = **9.60** | 10.97 / 9.85 | 3.3 V is not a datasheet condition (typ curve only, Vth max 2.2 V); current limit at 3.3 V not published; hardware gating (DRV_EN_N is a GPIO on the same MCU, so no independent kill is lost, but outputs rely on the 10 k pull-downs while the pin floats in reset) |
| b1 | relays and ignition pull-downs: NCV8402AD duals (6 packages for 11 channels) | none | 6 x 0.6529 = 3.917 instead of 4.825 | 3.328 instead 4.231 | 0.91 / 0.90 | 230 mohm at 5 V, 3.3 V Rds not specified (Fig. 6 ~1.9 A at 3 V); SO-8 area; only small gain |
| b2 | heavy channels as 4 x VNLD5160 (SO-8) | 4 packages | 6.695 + 4.825 + 0.786 = 12.31 | 5.962 + 4.231 + 0.687 = 10.88 | 9.80 / 8.57 | input is also supply: 3.5-5.5 V needed, keep U11; two injectors per SO-8 (each ~0.5 W hot, SO-8 103-111 C/W) |
| c1 | L9826 octal for the light relays | U12, RN2/RN3, 7 x ZXMS6004FF | 1.731 vs 3.07 + 0.393 | 1.507 | 1.7 / 1.6 | needs SPI pins and firmware, 450 mA / 1.5 ohm per channel (3 ohm hot), only outputs 1-2 current-limited |
| c2 | TLE8104 / TLE8110 / TLE6240 / MC33810 / TLE9104 | | not buyable at JLC (0 stock / no listing; TLE9104 is high side) | | | none |
| d | discrete logic MOSFET + external clamp (AO3400A $0.079 basic / $0.042 @100, 2N7002 basic $0.0158) | | tiny | | | no current limit or thermal shutdown (the repo changed from ULN2003 to IntelliFETs exactly for wire shorts); 30 V rating below clamp peak 31-32 V for injectors; no datasheet read, not recommended |
| e | 19 x ZXMS6005DGQ-13 (3.3 V, SOT-223), like Hellen NA6 | U11, U12, VND7NV04 and ZXMS6004FF lines (unique ext lines 2 -> 1: -$3.07 per order) | 19 x 0.3551 = **6.75** | 5.69 | 15.4 / 13.8 | 250 mohm max at 3 V (about 0.4 hot): up to 0.75 W at 1.33 A and 100 % duty in SOT-223 (42 / 96 C/W); current limit min 2.2 A at 25 C is thin when hot; injector duty at 7200 rpm about 90 % |

## 6. Level shifter findings

- Deleting U12 (relays): supported by Diodes (VIH 3.0 V min on ZXMS6004FF and ZXMS6005DG/DGQ; 3.3 V rail min 3.135 V from the 3.3 V LDO -> INFERRED margin 0.1 V over VIH min, STM32 VOH near VDD at light load). Saves $0.39 @30, one TSSOP-24, 7 pull-ups/gates remain (RN2/RN3 keep outputs off in reset). Loses the DRV_EN_N hardware gate for these (a GPIO on the same MCU anyway).
- Deleting U11 (heavy): only works with a part whose input threshold is well below 3.3 V and whose Rds is stated or plotted near 3 V: NCV8403A typical curve (see sec 3), VNN3NV04 curve to 3.5 V. Not with OMNIFET III N3/dual parts (input is the 3.5 V+ supply). Not guaranteed by any of the shortlisted heavy parts: UNVERIFIED in the worst case, medium confidence.
- A sound compromise: keep the 5 V shifter for the injectors and delete only U12.

## 7. Implications for this project (goals in review brief section 1)

1. Goal 3/5 (cheaper parts, cheaper board): replace the 8 VND7NV04 with NCV8401B in the same DPAK pads. Saves about $8.8/board at 30, $8.0 at 100 (about 20-40 % of the board parts bill per R21's $37-48 figure). Changes: BOM line C155605 -> C604055 in design.py and the ordered/next fab BOM; no layout change; firmware unchanged. Evidence: datasheets/extra/NCV8401BDTRKG.txt, JLC listing 2026-11-15. Confidence: medium-high (the datasheet read, but not verified on a board; pinout from the marking diagram and the package-style pin table; high short-circuit current is the open item).
2. Goal 3/5: if the SOT-223 respin of the injector strip is acceptable, NCV8403A (C266786) at $0.74 is the stronger SOT-223 part (76 mohm max vs 120-240 for the rest); a 3.3 V direct drive then removes U11. Confidence medium; needs the thermal model rerun for SOT-223 copper (repo scripts/board_thermal.py).
3. Goal 2 (free removals): U12 and the relay-channel level shifting (ZXMS6004FF VIH = 3 V); check that the MCU pin numbers on the relay gates keep their pull-downs. Saves one extra TSSOP-24 and $0.39. Confidence high on the datasheet fact, medium on the effect on the enable architecture.
4. Goal 3: ZXMS6005DGQ-13 is cheaper than ZXMS6004FF at the same 3 V logic and has 2.2-3.3 A limit, 490 mJ; but SOT-223 vs SOT-23F footprint: only $0.08/ch, no layout gain; mention, not a priority.
5. Goal 5: using one part for everything (option e) saves most money ($15.4) and one chargeable extended line per order ($3.07), but is thermally marginal for injectors in a hot cabin; precedent: Hellen NA6 BOM uses ZXMS6005SGTA (the BOM does not say which outputs).
6. Goal 1 (errors): VNLD5160 / VNL5xxxN3 are not 3.3 V parts (input doubles as the 3.5-5.5 V supply); the earlier rusEFI assumption that they take a 3.3 V GPIO is wrong for those variants. Any future swap to them must keep the 5 V shifter.
7. Goal 1/4: ZXMS6004FF rev 0.9 ordered boards need nothing from this research; the ordered rev 0.9 board can use 5 V drive as built. No rework suggested from this task.
8. Doc: the repo's claim "injector clamp energy matters" is moot with the external clamps: record that driver choice is driven by Rds x I^2, not by single-pulse EAS. Inductance still unmeasured (only one published figure, 20.3 mH).
9. Supply risk (goal 3 / logistics): stock levels matter for 100 boards x 8 = 800 pieces: NCV8401B 2200, NCV8408B 2129, NCV8403A 1908, VNN3NV04 1438, VNL5160N3 only 142, VNL5300S5 787, TLE8xxx 0.

## Sources actually read

- JLC/LCSC live lookups (tools/lcsc.py, work/R08-low-side-driver-landscape/jlc/*.json), 2026-11-15/16; also C7859, C95063, C155605 re-queried 2026-11-16.
- Datasheets (LCSC copies of manufacturer PDFs unless noted; text files beside them) in datasheets/extra/: NCV8402ASTT1G_lcsc_C77755, NCV8402ADDR2G_lcsc_C109030, NCV8403ASTT1G_lcsc_C266786, NCV8405ASTT1G_lcsc_C223559, NCV8405BDTRKG, NCV8406ASTT3G_lcsc_C459816, NCV8401BDTRKG, NCV8408BDTRKG, VNN7NV04PTR-E_lcsc_C501115, VNN3NV04PTR-E_lcsc_C443999, VNL5160N3TR-E_lcsc_C262999, VNL5300S5TR-E_lcsc_C155658, VNL5050S5TR-E_lcsc_C2149847, VNL5090N3TR-E_lcsc_C2680403, VNLD5160TR-E_lcsc_C377942, ZXMS6004FF_diodes.pdf, ZXMS6004FFTA_lcsc_C95063, ZXMS6005DG_diodes.pdf, ZXMS6005DGQ_diodes.pdf (July 2026), BSP78_lcsc_C2653794, BTS3410G_lcsc_C150926, BTS3800SL_lcsc_C534771, L9826_lcsc_C155567; downloaded but only skimmed, not relied on: L9733, TLE9104SH, VNL5030S5, VNS1NV04DP.
- Page images viewed: NCV8402A p.5-6 (Fig. 2-12), NCV8403A p.5 (Fig. 8-13), VNN3NV04P p.12 (Fig. 12-13).
- Repo: repo/scripts/design.py lines 98, 268-375; repo/research/rev0.10_design_audit.md A3; kb/research/R21-jlcpcb-cost-model.md; ext/hellen-miata-NA6 BOM.
- Web: PMC7435933 (Sensors 2020, 20, 4151) text, R = 14.8 ohm and L = 20.3 mH; web search summaries (injector resistance 12-16 ohm, Nexperia 5 mH model) are secondary.

## Not checked

- Inductance of Mazda injectors, saturated 12 ohm injectors in general (no measurement found).
- Currents of the IACV, VVT, BOOST and ALT loads (needed to decide whether the 4 non-injector channels can use weaker parts): not looked up.
- NCV8401B and NCV8408B behaviour at 3.3 V (graphs not viewed), VND7NV04-specific graph at 3.3 V, NCV8403 current limit at 3.3 V.
- Thermal model reruns for SOT-223 copper; JLC footprint/rotation for each candidate; short-circuit surge effect of 25-35 A on the board's 12 V traces.
- Parts without a read datasheet (HXY NCV8403A-HXY, VBsemi/JSM clones, VNN1NV04, NCV8409/8412/8415, TLE8888, L9733, MC33879, AUIPS/IPS) are only listed, not recommended. TLE8104/8110/6240/MC33810 datasheets not read: they are unavailable at JLC so no recommendation is made.
- Chinese equivalents with real datasheets: not surveyed beyond JLC listing hits.
