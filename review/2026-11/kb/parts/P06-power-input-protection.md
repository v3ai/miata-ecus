# P06 - Supply input and protection chain (D6, D7, D8, F1, D12, L1, R7, C16-C18; battery / ignition feeds; key-off)

STATUS: complete (single pass, economical). Tags: VERIFIED / INFERRED / UNVERIFIED as in review brief section 5.

## Summary
1. Topology (VERIFIED, evidence/cur_db/pcb_nets.txt + sch_netlist.xml): J1.1/J1.2 VBAT_IN -> D6 SMCJ30A (K on VBAT_IN, A on GND) crowbar/clamp; VBAT_IN -> D7 SS34 (A on VBAT_IN, K on +12V_IN); VIGN_IN (J1.3) -> D8 B5819W (A on VIGN_IN, K on +12V_IN); +12V_IN -> F1 PTC -> node +12V (D12 SMAJ33A K=+12V A=GND, C24/C62 1u, TLS115 U3/U14 VIN+EN, R7) -> L1 2.2 uH -> +12V_F (C17/C18 10u/50V, C71 100n, LMR14020 U2 VIN+EN). R7 1 ohm + C16 10u/50V is an RC damper on the +12V node.
2. All pad->net->datasheet-pin checks pass; polarities of every diode correct; footprints match land patterns. Nothing in the chain is wired wrong.
3. Real weaknesses are margins, not wiring: PTC hot derating (0.52 A at 85 C for the 1.1 A part, about 0.23-0.25 A for the ordered 0.5 A part, vs 0.15 A steady / 0.45 A at 8 V cranking from the repo's own figures) and the fact that both TVSs (1500 W / 400 W 10/1000 us rated) can only handle a SUPPRESSED load dump (test B), never an unsuppressed test A (hundreds of joules).
4. The "TVS crowbar blows the car fuse" argument holds for realistic loop resistance (>= ~20 mOhm: 100-290 A for ~1 ms, inside the 200 A / 8.3 ms IFSM). It does not for a high-resistance reversed path (~0.3 ohm: 37 A for seconds), where D6 would cook (fails short = safe direction, board lost).
5. Key-off: no motherboard connects a permanent-battery pin. VBAT_IN is main-relay output on every year; VIGN_IN is the START signal (1989-95), IG1 sense 4S (2003-05) or unconnected (96-97, 99-00, 2001-02). ECU key-off battery draw = 0 (INFERRED).
6. Cost: D6/D12 brand swap to MDD saves about $0.18/unit (datasheets read, same key specs); R7+C16 damper is functionally almost irrelevant in my sim (about $0.10/unit) but Hellen uses the same network, so leave until bench-tested.

## Parts identity (step 1; tools/lcsc.py run today 2026-11-16)
| Ref | LCSC | MPN / maker | Package | Lib | Stock | Price |
|---|---|---|---|---|---|---|
| D6 | C224048 | SMCJ30A Littelfuse | DO-214AB | ext | 11,826 | 0.2975@1, 0.237@50, 0.211@150 |
| D12 (and D11) | C223988 | SMAJ33A Littelfuse | DO-214AC | ext | 11,605 | 0.135@1, 0.1117@50, 0.0999@150 |
| D7 | C8678 | SS34 MDD | SMA | basic | 2.65 M | 0.0351@1, 0.0282@200 |
| D8 | C8598 | B5819W SL JSCJ | SOD-123 | basic | 732 k | 0.0256@1, 0.0195@200 |
| F1 (cur) | C883150 | BSMD1812-110-33V BHFUSE | 1812 | ext | 40,610 | 0.0742@1, 0.0573@100 |
| F1 (ord) | C70077 | nSMD050-33V Techfuse | 1206 | ext | 133,597 | 0.0577@1, 0.0478@100 |
| L1 (cur) | C177247 | FXL0530-2R2-M cjiang, 7.5 A Isat, 29 mOhm | 5.4x5.2x3 | ext | 49,707 | 0.1537@1, 0.1208@50 |
| L1 (ord) | C70960 | CMI322513U2R2KT FH, multilayer ferrite chip, 500 mA, 0.3 ohm | 1210 | ext | 3,467 | 0.0902@1, 0.0727@50 |
| R7 | C22936 | 1R 0603 Uniroyal | 0603 | basic | 456 k | 0.0031 |
| C16/C17/C18 | C13585 | CL31A106KBHNNNE 10u 50V X5R | 1206 | basic | 4.5 M | 0.121@1 |
All match the intended parts in kb/parts_manifest.md. All capacitors on the rail are 50 V parts (C24/C62 C15849 1u 50 V, C71 C14663 100n 50 V).

## Datasheet digests (step 2; the ones that matter)
- SMCJ30A (Littelfuse, datasheets/txt/C224048): VR 30 V, VBR 33.3-36.8 V @1 mA, Vc 48.4 V @ Ipp 31 A (10/1000 us), PPPM 1500 W, IFSM 200 A 8.3 ms (forward, unidirectional only), VF 3.5/5.0 V @100 A, RthJL 15, RthJA 75 C/W, alphaT (VBR temp coefficient) 0.1 %/C, "typical failure mode is short". Cathode = band = positive supply side. Rated with 8x8 mm copper per terminal.
- SMAJ33A: VR 33 V, VBR 36.7-40.6 V, Vc 53.3 V @7.5 A, 400 W, IFSM 60 A, alphaT 0.1 %/C.
- BSMD1812-110-33V (BHFUSE 2025): Ihold 1.10 A, Itrip 2.2 A, Vmax 33 V, Imax 40 A, R 0.045-0.25 ohm, trip 8 s @ 8 A(?), derating table (Ihold A): -40C 1.60, 0 C 1.28, 25 C 1.10, 40 C 0.92, 50 C 0.83, 60 C 0.71, 70 C 0.66, **85 C 0.52**. Max operating ambient 85 C. (VERIFIED, datasheet derating chart.)
- nSMD050-33V (Techfuse QR0429): Ihold 0.50, Itrip 1.0, Vmax 33 V, Rmin 0.15, Rtyp 0.30, R1max 0.70 ohm, no derating curve in the sheet. Scaling from the BHFUSE BSMD1812-050 row (0.50 -> 0.23 A at 85 C, 46 %) gives about 0.23-0.25 A (UNVERIFIED proxy, different maker).
- LMR14020 (C187824): VIN/EN abs max 44 V (VERIFIED line 187). TLS115B0EJ (C3743696): VIN -16..45 V abs max, reverse polarity protected, VEN -16..45 V.
- L1 FXL0530: land pattern a=2.2, b=6.0 (overall span), c=2.5 mm.

## Usage audit (step 3)
### a. Pin table (current rev 0.10 daughterboard; ordered rev 0.9 identical nets for these refs)
| Ref | Pad | Net | Datasheet function | Verdict |
|---|---|---|---|---|
| D6 | 1 | VBAT_IN | cathode (K) | OK |
| D6 | 2 | GND | anode | OK (TVS clamp, cathode on positive; reverse polarity conducts forward) |
| D7 | 1 | /Power/+12V_IN | K | OK |
| D7 | 2 | VBAT_IN | A | OK (blocks reversed battery) |
| D8 | 1 | /Power/+12V_IN | K | OK |
| D8 | 2 | VIGN_IN | A | OK |
| D12 | 1 / 2 | +12V / GND | K / A | OK |
| F1 | 1 / 2 | +12V_IN / +12V | non-polar | OK |
| L1 | 1 / 2 | +12V / +12V_F | non-polar | OK |
| R7 / C16 | | +12V - DAMP - GND | RC damper | OK |
Checked three ways: pcb_nets.txt, sch_netlist.xml (pin functions K/A in the schematic symbols), pads csv. KiCad Diode_SMD footprints D_SMC/D_SMA/SOD-123 have pad 1 = cathode: consistent. Ordered rev 0.9: same, except F1 is the 1206 nSMD050 and L1 the 1210 CMI322513 ferrite chip; VBAT sense differs (not in scope).
### b. Footprints
D6 pads 3.3x2.5 at 6.8 mm pitch (standard DO-214AB), D7/D12 2.5x1.8 at 4.0 (DO-214AC), D8 0.9x1.2 at 3.3 (SOD-123), F1 1812 pads 1.125x3.4 at 4.275, L1 pads 1.9x2.5, centres 4.1 apart (span 6.0, matches FXL0530 recommended b=6.0, c=2.5; pad length 1.9 vs a=2.2, within 0.3 mm): OK. This closes the repo's "FXL0530 land pattern not checked" item (rev0.10_design_audit).
### c. Stress table (numbers)
Series budget at 0.4 A: D7 about 0.40 V, F1 0.02-0.28 V (0.045-0.70 ohm), L1 0.012 V (cur) / 0.12 V (ord, 0.3 ohm), so cranking at 6 V leaves about 5.1-5.5 V at the buck. Normal 14.4 V and 24 V jump start: D6 and D12 off (VR 30 / 33 V; hot VBR rises, cold VBR_min 33.3x(1-0.065)=31.1 V at -40 C > 28.8 V truck charge). Hot 85 C: D6 VBR max about 39.0 V, D12 VBR min about 38.9 V (alphaT 0.1 %/C x 60 K): bands overlap.
- Reverse battery 12.6 V: D7 reverse voltage about 14 + VF(D6) = 20 V < 40 V OK; D8 same; TLS115 -16 V OK; LMR14020 isolated by D7 OK. D6 forward: VF 3.5-5 V @100 A, so loop current = (12.6 - ~1)/(Rloop + ~0.03) = 166 A at 40 mOhm, 290 A at 10 mOhm, 37 A at 0.3 ohm. 100-290 A for about 1 ms is within IFSM 200 A / 8.3 ms energy (1-8 J). Fuse clearing time of the car's 15-30 A fuse not read: UNVERIFIED (I assume order of 1 ms at >10x).
- Load dump test A (ISO 16750-2, unsuppressed 79-101 V, Ri 0.5-4 ohm, 400 ms): TVS current (Us-Vc)/Ri = 13 A (101 V, 4 ohm) to 68 A (79 V, 0.5 ohm); energy about Vc x I x 0.4 s = 250-1200 J. D6 rating: 1500 W x 1 ms is about 1.5-2 J. Roughly 100x too small. D12 (400 W) cannot take the share either. Test B (suppressed Us*=35 V, 40-400 ms): D6 only just conducts (VBR 33.3-36.8) and the downstream sees about 36-38 V (below 44/45 V). My ngspice ISO 7637-2 pulse 2a model (50 V, 2 ohm, 50 us; D6 BV 33.3-36.8, D12 36.7-40.6, F1 0.15 ohm, L1/C17 derated): buck VIN peaks 35.2-38.9 V (<44 V abs max); the repo's 36.4 V claim holds (it is the +12V node, the buck sees about the same). Pulse 1 (-100 V, 10 ohm, 2 ms): about 10 A through D6 forward for 2 ms OK. 3a/3b: negligible energy.
- A hard (low-impedance, fast) step of 14 -> 40 V at the +12V node rings the L1/C17 filter to about 52 V in my sim (damped or not): only a theoretical case (needs a 40 V source of milliohm impedance with <1 us edge); ISO pulses are limited by Ri and TVS action and stay <=39 V.
- Cranking: repo figure 0.45 A at 8 V (design.py comment, VERIFICATION 684) scales to about 0.6 A at 6 V (constant power 3.6 W). Steady: 0.15 A at 12 V (design.py comment).
### d. Required external parts: LMR14020 input C (>=4.7 uF ceramic) present (C17+C18 20 uF nominal, about 12 uF with bias derating), C71 100 nF added at pins; stability of the filter: Z0 = sqrt(2.2u/12u) = 0.43 ohm, Rs about 0.2 ohm so Q about 2, peak filter output impedance about 0.7-0.9 ohm vs converter |Zin| = Vin^2/P = 36/3.6 = 10 ohm at 6 V cranking: Middlebrook margin >10x even without the damper.
### e. Compare with Hellen (ext/hellen-one/modules/power_12and5V/0.3): V12_RAW -> PTC F410 0.5 A (SMD1206P050TF/24) -> SS-type B5819W D416 -> V12; SMCJ30A D418 on V12_RAW (before the PTC, "30V MAX"); VIGN via B5819W D417 into V12 with NO TVS; input filter R420 1 ohm + C427 4.7 uF damper, L420 2.2 uH 1210 (C36828), 4x10 uF; LMR14020. Ours: same skeleton plus SMAJ33A D12 clamping the node that the ignition path also feeds, and the PTC after D7 (D6 sits outside the PTC so the crowbar is not limited by it, same as Hellen).

## Findings (also in the structured output)
See final list; extra low items: the 2001-05 / 1996-2000 boards leave VIGN_IN open (D8 and divider unused: fine), 1989-95 VIGN_IN is the START wire (D8 can back-feed the logic from the starter signal wire when VBAT_IN sags below it while cranking, up to about 0.6 A: wire gauge and fuse of the START circuit not checked, UNVERIFIED, low).

## Sources actually read
evidence/cur_db and ord_db pcb_nets.txt, pcb_pads.csv, pcb_footprints.csv, sch_netlist.xml; kb/interconnect.md (harness pins 1B/1C/4B/1B/4AF/4S rows); repo/VERIFICATION.md lines ~684, 1155-1190, 970-990; repo/daughterboard/README.md; repo/scripts/design.py comments (L205-235); repo/motherboards/*/README.md pinout rows; repo/research/pinouts_9605.md conflict notes; datasheets/txt: C224048, C223988, C883150 (derating table), C70077, C177247 (land pattern), C70960, C187824 (abs max), C3743696 (abs max); datasheets/extra/C408374_SMCJ30A_MDD and C113966_SMAJ33A_MDD (downloaded today); ext/hellen-one power_12and5V 0.3 BOM and schematic; tools/lcsc.py live look-ups; work/P06-power-input-protection ngspice decks (lc0/lc1.cir, p2a.sh).

## Not checked
Car fuse time-current curve and real harness resistance; Miata alternator load-dump behaviour (zener-clamped or not): UNVERIFIED; VF curve of D6 at 200 A (read only the 100 A figure); thermal copper around D6 vs the datasheet's 8x8 mm pad rating; PTC trip dynamics between hold and trip current; clone-maker PDFs for the 3 alternates only partially read (MDD SMCJ30A, MDD SMAJ33A); nSMD050 85 C derating (no curve); ordered-board layer images not viewed (nets/pads only).
