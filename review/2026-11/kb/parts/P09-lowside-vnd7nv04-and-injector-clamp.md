# P09 - Low-side drivers VND7NV04 (Q1-Q8), input resistors, pull-downs, and the external injector clamp (D42-D49)

STATUS: complete (2026-11-16). Tags: VERIFIED / INFERRED / UNVERIFIED per review brief section 5.

## Summary (10 lines)
1. Pin-by-pin audit of all eight VND7NV04 (cur_db rev 0.10): pad1 = INPUT (from R15x/R19-26), pad2 + tab = DRAIN (OUT_*), pad3 = SOURCE (GND). Matches ST's DPAK diagram p.1. VERIFIED, no error found.
2. Clamp chain: D42-45 ES1D anode on OUT_INJx (pad2), cathode on INJx_CL (pad1); D46-49 1.5SMC16A cathode (pad1) on INJx_CL, anode (pad2) on VBAT_IN. Reverse-biased TVS in series with a forward diode, returning to the battery: correct orientation (it must be, otherwise the TVS would conduct forward from VBAT to a grounded drain). VERIFIED.
3. Copper claim in daughterboard README checked from the .kicad_pcb (filled zones): OUT_INJ1 F.Cu 94, In2/In3/B.Cu 107 mm2, 41 vias; INJ4 100/108, 45 vias. README says 84-100 / 95-108 and 34-42 vias: confirmed (vias slightly MORE than claimed). VERIFIED.
4. Energy per turn-off (my own calc, 14.4 V, 14 ohm, Rds 0.1): 20 mH: 10.4 mJ stored; own clamp (45 V) dumps 15.3 mJ in the driver (0.92 W at 7200 rpm sequential, 60 events/s, ~ +44 C at 48 C/W); external clamp puts ~0 in the driver and 10.4 mJ in TVS+diode (0.63 W). At 8 mH: 6.1 mJ vs 0.37 W driver (+18 C): the clamp is not needed for the driver at 8 mH or less. Repo's 8.8 mJ for the TVS is a little below the 10.4 mJ stored at 14.1 ohm (consistent only with ~16 ohm injectors); immaterial.
5. The decision hinges on injector inductance, which nobody has measured; my searches found NO measured mH for a Miata/Denso high-Z injector (only the repo's 20.3 mH published fit for one other 14.8 ohm injector). UNVERIFIED either way. One LCR-meter reading decides keep (>= ~12 mH) or delete (<= ~8 mH) for sequential cars.
6. For 1989-93 one-driver-per-wire (2 injectors, ~2.0 A) the external clamp is the thing that keeps the driver inside ST Fig. 32 (repetitive 125 C curve: 2.2 A at 10 mH); keep it there.
7. Above Vbat ~24 V the external clamp stops being the lowest-voltage path (24+16.8+0.9 = 41.7 V vs driver clamp 40-55 V, threshold 36 V): at jump start the driver shares, in load dump (SMCJ30A D6 holds VBAT_IN to ~34-37 V) the driver's 45 V clamp takes everything. No new hazard vs no clamp, but the clamp's "protection" is limited to Vbat < ~22 V.
8. Dead time: clamp voltage across the coil is ~17.7 V fixed instead of (45 - Vbat). Decay time 20 mH, 1 A: 1.15 ms vs 0.67 ms; and the difference between 9 V and 14.4 V supply grows (0.72 -> 1.15 ms vs 0.35 -> 0.67 ms). Absorbed by the dead-time offset/voltage table, but must be measured; repo already says "check dead time".
9. Cost: 8 clamp parts = $0.56 at qty 150 (ES1D 4 x 0.0074, 1.5SMC16A 4 x 0.179) + 2 extended-part loading fees; the VND7NV04 itself is 8 x $1.82 = $14.6 (qty 100), the largest line here. Alternates in notes section 5.
10. Only 3 pinout checks reported as info.

## 1. Identity (parts manifest + live lookup 2026-11-16, tools/lcsc.py)
| Ref | LCSC | MPN / pkg | Class | Stock | Price tiers |
|---|---|---|---|---|---|
| Q1-Q8 | C155605 | VND7NV04TR-E, TO-252-2 (ST) | Extended | 2391 | 1: 2.685, 10: 2.302, 30: 2.062, 100: 1.816, 500: 1.705, 1000: 1.658 |
| D42-45 | C116492 | ES1D SMA (Jingdao) 200 V 1 A 35 ns | Extended | 231753 | 1: 0.0111, 500: 0.0088, 1500: 0.0074 |
| D46-49 | C1973780 | 1.5SMC16A DO-214AB (Littelfuse) 13.6 V stand-off, VBR 15.2-16.8, Vc 22.5 V @ 67.6 A | Extended | 1699 | 1: 0.259, 50: 0.203, 150: 0.179, 500: 0.149 |
| R152-159 | C25091 | 220 ohm 0402 1% | Basic | 1.7 M | 0.0014 |
| R19-26 | C25804 | 10 k 0603 1% | Basic | 42 M | 0.0016 |
Identity: VERIFIED (manifest lines 56-59, live lookup). The JLC/LCSC class text "High Side Switch" is a catalogue mislabel: the datasheet title is "OMNIFET II fully autoprotected Power MOSFET", a LOW-side device (drain/source/input), p.1, p.6.
Stock of the TVS (1699) is adequate for ~400 pieces (100 boards) but is the thinnest of the group.

## 2. Datasheet digest (ST Doc ID 7383 Rev 4, Sept 2013, LCSC copy; ST current sheet is the same family, not re-downloaded)
- Function: monolithic low-side power MOSFET, 60 mohm, linear current limit, thermal shutdown (Tjsh 150/175/200 C, restart ~15 C lower), 45 V integrated drain clamp, input pin drawn IISS 100-150 uA, fault feedback Igf 15 mA sunk through input at thermal shutdown (p.8-10).
- Abs max (Table 2, p.7): VDS/VIN internally clamped; IIN +-20 mA; **RIN MIN 150 ohm = minimum series impedance in the input** (it is an application/rating requirement: the input clamp VINCL 6-8 V takes the current when the input is driven above ~7 V or when the drain couples); IR (reverse DC) -10.5 A; Ptot 60 W at Tc 25; EMAX 40 mJ (L 0.7 mH, 9 A, Vbat 13.5, Tjstart 150 C); ESD HBM 4 kV, output pin 16.5 kV.
- Thermal: Rthj-case 2.1 C/W; Rthj-amb 65 C/W on 0.5 cm2 (sic "0.5 mm2") single-sided copper (Table 3 note).
- Characteristics (Table 4): Vclamp 40/45/55 V at 3.5 A; VCLTH min 36 V at 2 mA; VINTH 0.5-2.5 V; Rds(on) 60 mohm typ / 120 mohm max over temperature at 5 V, 3.5 A; Ilim 6/9/12 A (VDS 13 V); Eas 200 mJ (25 C start, 24 V, L 24 mH); td(off) 0.5 us, tf 0.35 us with 150 ohm gate, 3.6 us with 2.2 k; body diode VSD 0.8 V.
- Pins, DPAK (p.1 drawing, Fig.1 block diagram): 1 = INPUT, 2 = DRAIN (also the tab), 3 = SOURCE. VERIFIED from the page image.
- Fig. 32 (DPAK max turn-off current vs L, VCC 13.5 V, RL 0): A single pulse Tjstart 150 C (top), B repetitive Tjstart 100 C, C repetitive Tjstart 125 C (bottom). Digitised from the vector graphics (work/P09.../fig32_digitized.json): A/B/C at 4 mH ~ 5.2/4.3/3.0; 8 mH ~ 4.1/3.4/2.3; 10 mH 3.8/3.2/2.2; 20 mH 3.1/2.5/1.77 A. Repetition rate / cycle count of curves B, C is not stated by ST.
- Land pattern: ST p.34 Fig.55 DPAK footprint; repo footprint is KiCad TO-252-2 (tab pad 6.4 x 5.8 plus 4 sub-pads, leads 2.2 x 1.2, pitch 4.56). Matches the usual 2.28 mm pitch DPAK. Not dimension-checked against Fig.55 beyond pitch.

## 3. Usage audit (cur_db rev 0.10; ord_db rev 0.9 differs as stated)
### 3a. Pin table (evidence/cur_db/pcb_pads.csv, pcb_nets.txt; sch pinfunctions)
| Pad | Net (Q1 example; Q2..Q8 identical pattern) | ST function | Verdict |
|---|---|---|---|
| 1 | /Outputs/INJ1_IN = R152.2 + R19.1 (also Q5: IACV_IN, Q6 VVT_IN, Q7 BOOST_IN, Q8 ALT_IN) | INPUT | OK |
| 2 (+4 sub-pads, tab) | OUT_INJx / IACV / VVT / BOOST / ALT, with J1.19,22,25,28,31,34,37,40 | DRAIN | OK |
| 3 | GND (one per Q) | SOURCE | OK |
R152-159: pad1 = *_DRV from U11 (SN74LVC4245A, 5 V side), pad2 = *_IN: series 220 ohm, >= 150 ohm RIN MIN: OK. R19-26 10 k from *_IN to GND (pull-down so gates stay low while U11 outputs are high-Z, enable R71 pulls up): OK, keep. IISS 150 uA x 220 = 33 mV; 10 k divider costs 2 % of the 5 V drive. Power-up with undefined U11 outputs: pull-down holds injectors shut. INFERRED.
Diodes: ES1D D42-45: pad1 (cathode, K) = INJx_CL, pad2 = OUT_INJx. 1.5SMC16A D46-49: pad1 (cathode) = INJx_CL, pad2 (anode) = VBAT_IN. Motherboard D1/D2 SS34 (D_SMA): pad1 K on the valve's +12 V feed (VBAT_IN, or IAC_12V / OCV_12V through F2/F3 on 1996+), pad2 A on OUT_IACV / OUT_VVT; sch netlist: D1 pin 2 pinfunction A. Orientation correct as freewheel on 1989-95 (D1,D2), 1996-97 (D1), 1999-2000 (D1 on IAC_12V), 2001-05 (D1 IAC_12V, D2 OCV_12V). VERIFIED. Boost valve D5 to AUX_VBAT, D5 on 1989-95 only list; ALT and O2-heater have no freewheel (documented H2).
### 3b. Footprint / copper
Pitch/pad sizes consistent (leads 2.2 x 1.2 mm at +-2.28 mm, tab 6.4 x 5.8 + 4 sub-pads). Copper per driver from the PCB file today: see summary item 3. TVS columns INJ1_CL: F 37, In2/In3 52, B 30.6 mm2, 7 vias (README says 176-196 mm2 effective over four layers: consistent: 37+52+52+31 = 172 plus the via stitch). Layers In2 and In3 appear identical in area (GetFilledPolysList, both signal layers). I did not inspect layer images for loop area; clamp loop (OUT_INJ -> ES1D -> TVS -> VBAT_IN) is a slow (ms) 1 A loop, loop inductance irrelevant.
### 3c. Electrical stress
| Condition | Result | Tag |
|---|---|---|
| 14.4 V normal, 14 ohm injector | I = 1.02 A; Rds hot (0.12) conduction 0.12 W; clamp see section 4 | INFERRED |
| Cranking 6 V | I = 0.43 A; trivial; injector may not open fully (not this part) | INFERRED |
| 24 V jump start | I = 1.7 A; turn-off 29 mJ; drain would clamp at 24+VBR(15.2-16.8, hot up to ~18.9)+0.8 = 40-43.7 V; driver clamp 40/45/55 V (VCLTH 36): the two clamps share, at worst the driver takes 29 x 45/21 = 62 mJ per event (<< Eas 200 mJ single pulse); minutes only | INFERRED |
| Load dump, suppressed 35 V (D6 SMCJ30A: VBR 33.3-36.8) | injector I = 2.5 A, stored 63 mJ; external clamp would need 35+17+0.8 = 53 V so the driver's own 45 V clamp conducts instead: 63 x 45/(45-36) = 315 mJ per turn-off at 20 mH (> Eas 200 mJ, 25 C) or 126 mJ at 8 mH. Same with or without D42-49; hits any ECU with 45 V drivers. Load dump needs a dead battery lead + running engine; ~400 ms = up to ~25 events per injector | INFERRED, low-prob |
| Reverse battery | VBAT_IN -14 V: TVS/ES1D chain has no path of consequence (all reverse or series); injectors' own path is the main-relay/harness. Drivers' body diode IR rating -10.5 A | INFERRED |
| Harness pin shorted to battery | body diode/clamp not involved (output pulled high: drain high, driver off: no current into driver except IDSS); shorted to ground: Ilim 6-12 A then thermal shutdown (Tjsh 175) | INFERRED |
| Hot 85 C air, 7200 rpm, 20 mH, no ext. clamp | Tj ~ 85 + board rise (23-31) + 44 + 6 = 158+ C > shutdown; with clamp ~ 85 + 27 + 6 + ~5 = ~123 C. So at 20 mH the clamp is what keeps it out of thermal shutdown; at 8 mH and below it is not needed | INFERRED (48 C/W is the repo's copper-area fit, not measured) |
### 3d. Required external parts
OMNIFET II needs only the >=150 ohm RIN: present on cur_db (220), ABSENT on ord_db rev 0.9 (documented). No decoupling needed. Unused inputs: INJ3/INJ4 outputs on 1989-93 boards switch into nothing: harmless (no load).
### 3e. References
rusEFI Hellen uses AUIPS2041L and Speeduino NA6 PNP VNLD5090 (repo/research/other_miata_pnp_boards.md lines 33-34): both rely on the driver's own clamp, no external injector clamp. Nobody else puts a Vbat-referenced TVS per injector (INFERRED from that table; ext/ not re-grepped).
### Loads (kb/interconnect.md, VERIFICATION H2, line 1149)
Injectors 12-16 ohm (~1 A each); 1989-93 stock harness: 2 injectors per wire (~2 A, current limit 6-12 A OK, driver Rds loss 0.45 W). Idle valve ~1 A PWM (SS34 freewheel D1 on every motherboard); VVT ~1 A (D2, 2001-05 and purge solenoid on 1989-95); boost valve (D5 on the AUX path); alternator control and O2 heater: no freewheel (resistive/unknown). Currents UNVERIFIED beyond the repo's statement.

## 4. Injector data, clamp energy and thermal numbers
Resistance 12-16 ohm: UNVERIFIED secondary (Mazda value per repo; web searches today repeat "12-16 ohm typical high-impedance"). Inductance: NO measured value for a Miata/Denso injector found on the web; repo cites one 14.8 ohm port injector fit of 20.3 mH (Sensors 2020, 20, 4151, "read" by an earlier audit, not re-read by me). Using 4-20 mH.
Per-event numbers, 14.4 V, R_coil 14 + Rds 0.1 ohm, I = 1.02 A (python, in this review):
| L | stored 1/2 L I^2 | in driver, own 45 V clamp (x45/(45-14.4)) | W/driver at 60 ev/s (7200 rpm seq.) | dT at 48 C/W | in TVS+diode with ext. clamp | decay time own / ext |
|---|---|---|---|---|---|---|
| 4 mH | 2.1 mJ | 3.1 mJ | 0.18 W | 9 C | 2.1 mJ (0.13 W) | 0.13 / 0.23 ms |
| 8 mH | 4.2 | 6.1 | 0.37 | 18 | 4.2 (0.25) | 0.27 / 0.46 |
| 14 mH | 7.3 | 10.7 | 0.64 | 31 | 7.3 (0.44) | 0.47 / 0.81 |
| 20 mH | 10.4 | 15.3 | 0.92 | 44 | 10.4 (0.63) | 0.67 / 1.15 |
At 16 V / 12.5 ohm-class worst case, 20 mH: 20 mJ (1.2 W, +58 C) own clamp, 12.9 mJ ext. Driver Fig. 32 check, single injector 1.02-1.13 A: below curve C (125 C start) at every L up to 20 mH (1.77 A) by 1.6x in current / 2.4x in energy; the curves require Tjstart <= 125 C, which the 85 C-air 20 mH case without the clamp violates (INFERRED).
1989-93 paired wire, 2.04 A, L/2: 2 mH: 6.1 mJ/driver (0.37 W); 4 mH: 12.3 mJ (0.74 W); 10 mH: 30.7 mJ (1.84 W); Fig. 32 curve C at 10 mH = 2.2 A: ~zero margin. External clamp needed here for 20 mH-class injectors (INFERRED).
Dead time (INFERRED from L I / dV): closing is delayed by the ratio of coil voltages (17.7 V vs 30.6 V at 14.4 V). Absorbed by the dead-time table, which in rusEFI is a function of battery voltage; but the voltage dependence is different (ext: the delay scales ~ with Vbat, own clamp: slightly less). Tune at 3 voltages. Linearity at ~1 ms pulses: the extra 0.2-0.5 ms of decay is a constant offset only if the pintle closes at a fixed current fraction (UNVERIFIED).

## 5. Cost and simplification
- Clamp removal (D42-49): saves 8 pads/parts, $0.56 + ~$0.1 SMT at qty 150, two extended fees (~$3 each per order), and ~12 cm2 of top-side area, but loses 0.3-0.6 W of driver margin at >= 14 mH, and the 1989-93 paired case. Recommendation: measure L; keep if >= 12 mH or if 1989-93 matters; otherwise the clamp may be left off the sequential channels... but the board is universal, so the saving is only realised by a DNP option. Medium.
- TVS cost: SMBJ14A (VBR 15.6-17.2, 600 W, SMB) C152106 $0.03-0.066 (stock 12786), C908795 $0.02-0.038: 600 W is ample for 1.3 A pulses; but SMB pads have less copper/thermal area (0.5-0.6 W average) and a different footprint (layout change). Saves ~$0.1-0.14 x 4 = ~$0.5/board. Specs seen only in the JLC listing text (not manufacturer sheet): UNVERIFIED datasheet. Do NOT use SMBJ16A (VBR 17.8-19.7 would put the drain at ~36 V at 15.5 V, into the driver's 36 V threshold).
- ES1D -> SS14 (C2480, BASIC, $0.0088-0.019, 40 V, 550 mV @ 1 A): works as the blocking diode (reverse stress 14-24 V; at load dump 35 V it is within 40 V but with little margin, leakage 300 uA at 40 V); saves the extended fee of C116492 (the only use). Not recommended unless the extended fee matters: ES1D is $0.007.
- Driver cost: 8 x $1.82 = $14.5/board. NCV8406A SOT-223 (C459816, $0.45 at 100, stock 4875, extended; datasheet read: pins gate/drain/source 1/2/3, clamp 60-70 V, Ilim 5-9.5 A, Rds 210 mohm @25 C, 445-520 mohm @150 C at 5 V, EAS 110 mJ, RthJA 100 C/W min pad) would save ~$1.37 per channel. It was the rev 0.9 part. With the external clamp on injectors its 60 V clamp lets the TVS win at all supplies below ~42 V (better in a load dump than the VND7NV04 whose 45 V clamp pre-empts the TVS). But 0.12 W -> 0.5 W conduction at 1 A hot and SOT-223 copper; paired 1989-93 (2 A, 2 W) not feasible. A plausible mixed option: NCV8406A on IACV, VVT, BOOST, ALT (4 x $1.37 = $5.5/board), VND7NV04 on injectors. Needs a footprint change and thermal check; confidence low-medium. NCV8402A (C77755, $0.29, SOT-223, 2 A) NOT recommended: datasheet could not be downloaded, specs unread.
- Resistors: R152-159 and R19-26 are 16 basic parts at $0.0015: negligible; keep (the only cost is 16 placements ~ $0.03).

## Sources actually read
datasheets/txt/C155605_VND7NV04TR-E.txt (pp.1-12, Fig.32 page image/graphic); datasheets/extra/NCV8406A_lcsc.pdf/.txt (ratings, electrical table); work/P09.../fig32_digitized.json; evidence/cur_db pcb_footprints.csv / pcb_pads.csv / pcb_nets.txt; evidence/cur_mb8995/9697/9900/0105 pcb_nets.txt, sch_netlist.xml (D1); repo/daughterboard/README.md; repo/VERIFICATION.md (A3, A4, injector clamp table, N8); repo/research/rev0.10_design_audit.md A3, A4, A11; repo/research/other_miata_pnp_boards.md; kb/interconnect.md; kb/parts_manifest.md; lcsc.py live lookups; PCB zone areas/vias from repo/daughterboard/miata_ecu_daughter.kicad_pcb via pcbnew (work/P09.../cu.py); 3 web searches (no inductance values found).

## Not checked
ES1D and 1.5SMC16A datasheets (C116492, C1973780) not opened line by line (specs taken from LCSC listing: 200 V/1 A/35 ns; 15.2-16.8 V). Fig. 46 single-pulse Zth (per-event junction spike) not digitised; the per-event spike (43 W x ~0.7 ms) is therefore not quantified. Fig.55 land pattern not dimension-checked. No SPICE rerun of sim_inj_clamp.py. No measured Miata injector inductance. Idle/VVT/boost currents taken from repo. ST current datasheet (newer than Rev 4) not downloaded. Layer images not viewed.
