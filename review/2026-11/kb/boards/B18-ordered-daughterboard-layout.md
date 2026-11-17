# B18 - ORDERED daughterboard rev 0.9 (4 layers) reviewed as built: DRC triage, current paths, thermal, known weaknesses

STATUS: complete (2026-11-16). Scratch: `work/B18-ordered-daughterboard-layout/` (geom.json = pcbnew dump of the frozen PCB; c1..c10.py analysis; thermal_runs.txt, thermal_single.txt = repo's board_thermal.py run on the ORDERED board file).
Tags: VERIFIED = read/computed from the design files or datasheets today; INFERRED = reasoning shown; UNVERIFIED = memory/secondary.
Overlap: B01 (DRC/ERC), B03 (delta + bring-up), B04 (gerbers), B06/B07 (rev 0.10 layout), P05/P09/P16 (parts). Only what is new or re-verified for rev 0.9 is derived here; the others are cited.

## Summary
1. DRC 474 / parity 63 / ERC 920 re-counted from the JSON: 199 lib_footprint_issues (artefact: KiCad 9 run without stock libs), 117 silk_overlap + 67 silk_over_copper (cosmetic), 91 courtyards_overlap (real as a rule, harmless: pad gaps meet JLC spacing, B01); 0 unconnected, 0 clearance/hole/edge. Parity = 57 net_conflict (NC pins "unconnected-(...)" vs no net) + 6 footprint_symbol_mismatch (J3, J102, H1-H4 excluded from BOM): artefacts. ERC: 603 lib_symbol + 312 footprint_link (artefact), 5 power_pin_not_driven (no PWR_FLAG; artefact). Nothing electrical. VERIFIED.
2. Stack: F.Cu signal + GND pour + 8 drain pours / In1 solid GND (88.5 % of board, one polygon, no slots, only via antipads and 8 voids of 24-31 mm2 under the driver tab via-fields) / In2 solid +3V3 (74.9 %, one polygon) with the 8 drain columns cut out of it / B.Cu signal + GND pour + drain pours. 1.6 mm, finish "None" in the gbrjob (the job file says nothing about copper weight or via fill). VERIFIED.
3. Under the driver strip (x 155-215, y 50.6-68) there is NO +3V3 plane (0.1 % cover: the In2 layer is drain copper) and In1 GND is 68 % there. Only the 0.25 mm VBAT_IN sense track (48 mm, F+B) and the INx_IN gate tracks run there. Not a problem, but B.Cu signals elsewhere reference the 3V3 plane, not GND.
4. Output copper is not the limit. Every drain: 6.9 mm wide column on F/In2/B (84-100 / 104-108 / 95-108 mm2), 35-42 vias (24-26 inside the tab), 93-100 % ring contact to the J1 pin on all three layers; source: GND island with 2-19 vias (Q7: 2) + In1 + 17 J1 GND pins each 100 % tied to In1. Resistance < 0.5 mOhm, rise ~0. The limit is the VND7NV04's temperature (and the 0.64 mm header pin, UNVERIFIED rating).
5. Thermal (repo's board_thermal.py run on the ordered PCB, 4-layer stack, h = per face W/m2K): single driver 1 W: junction +24 K/W (h 10), +30 (h 5), +38 (h 3). Injector driver at sustained 7200 rpm incl. own clamp (no external clamp on this board): 8 mH +46..50 K (h 10) / +75..80 (h 5) / +113..118 (h 3) above the air around the board; 20 mH +78..86 / +121..129 / +175..183. On 85 C air and h = 10 the 20 mH case is 163-171 C = over thermal shutdown (150 min); 8 mH 131-136 C. Idle-board base load alone (2.6 W) raises the mean by 14 / 27 / 45 K at h 10 / 5 / 3.
6. Safe continuous current per output on THIS board (Tj <= 125 C, air 85 C, Rds 0.12 ohm hot max, base load on, no inductive clamp heat): 3.0 A (h 10), 1.9 A (h 5), ~0 at h 3 (air must be < 70 C: 1.5 A). Short term the Ilim is 6-12 A (shutdown at 150-200 C). Realistic injector/valve currents (0.3-2 A) are inside this except high-rpm injector clamp heat.
7. Missing 220 ohm: ST states only a rating (p.7, RIN MIN 150 ohm, IIN +-20 mA) and says nothing on the failure mechanism; p.10 even says the part may be driven from a low-impedance source (the fault current Igf 15 mA is then supplied). Practical risk in normal drive is low (5 V < VINCL 6-8 V, IIN ~100-150 uA); it bites only when the input node is forced outside -1..+6.8 V. Rework possible (cut track at pin 1 + 0402/0603 220 ohm bridge, 8 sites) but delicate; recommended only as an option.
8. 4-layer-specific weaknesses vs rev 0.10: inner copper probably 0.5 oz (UNVERIFIED, JLC default), drain heat spread over fewer layers; buck: C71 100 nF absent, bulk caps 4.3-7.8 mm from VIN; F1/L1 undersized. MCU decoupling/crystal geometry is IDENTICAL to rev 0.10 (pad distances equal to 0.1 mm).
9. Known weaknesses list: section 7.

## 1. DRC / ERC triage (recounted; method = JSON counts + B01's proof)
| Class | Count | Verdict | Proof |
|---|---|---|---|
| lib_footprint_issues | 199 | artefact | KiCad 9 run without stock footprint libraries; footprints embedded in PCB; repo's own fab_drc_report has the same counts (B01) |
| silk_overlap | 117 | cosmetic | ref text over lines; JLC clips silk on pads |
| silk_over_copper | 67 | cosmetic | silk exported with mask subtraction (B04) |
| courtyards_overlap | 91 (all severity error) | real rule, harmless | exact pad-pad gaps >= 0.2 mm vs JLC table (B01); no clearance error |
| unconnected | 0 | - | also repo fab_drc_report "0 unconnected pads" |
| parity net_conflict | 57 | artefact | single-pin NC nets (partition compare 269/269 groups equal, B01) |
| parity footprint_symbol_mismatch | 6 | benign | exclude_from_bom flags on J3, J102, H1-H4 |
| ERC lib_symbol_issues / footprint_link_issues | 603 / 312 | artefact | libraries not in KiCad 9 config |
| ERC power_pin_not_driven | 5 | artefact | no PWR_FLAG on nets fed via ferrite/inductor/fuse |
Counts VERIFIED by python on evidence/ord_db/drc_kicad9.json / erc_kicad9.json (474 = 199+117+91+67; 63 = 57+6; 920 = 603+312+5). Real things DRC cannot see (checked here instead): via-in-pad count, plane integrity, current paths (below).

## 2. Layer stack and planes (VERIFIED: geometry c2.py, c10.py)
| Layer | Content | Notes |
|---|---|---|
| F.Cu | all SMD, signal, GND pour, 8 drain pours (84-100 mm2 each) | tab pads 6.4 x 5.8, 25 vias in each |
| In1.Cu | GND, 8421 mm2, 1 polygon, 403 holes (antipads), 88.5 % of board | voids: 8 x 24-31 mm2 under driver tabs, 10-12 mm2 at 4 mounting holes; no slot; neck between tab voids ~2.5 mm |
| In2.Cu | +3V3, 7126 mm2, 1 polygon, 795 holes, 74.9 % | drain columns (6.9 x 17.3 mm each) removed from it: no 3V3 under the strip |
| B.Cu | signal + GND pour + drain pours (95-108 mm2) | |
Cover (1 mm halo) In1 / In2: U1 93/91 %, U2 100/90 %, L2 100/93 %, U4 98/95 %, U3 99/92 %, U14 97/89 %, Y1 90/87 %, U102 83/84 %, Y101 93/90 %, U105 AD8628 81/84 %, U103 REF3033 99/89 %. 8.5 % of 1658 mm of critical signal/analog track (USB, CAN, HSE/OSC, AN_, wideband, NRST, SWD, VR, HALL) crosses an In1 void (141.7 mm, each crossing = a via antipad, < 1.5 mm); B.Cu track (567 mm of the 1658) sees In2 +3V3 and the B.Cu GND pour as reference, not GND. Buck: BUCK_SW is F.Cu only, 6.2 mm of 0.8 mm; In1 solid under U2/L2/D9 (100 %). Return paths therefore fine under buck, MCU, wideband; weaker only in that 3V3 and GND planes are separated by a 1.065 mm core (STACK4 0.21/1.065/0.21 mm, recalled JLC standard, UNVERIFIED), i.e. no inter-plane capacitance; decoupling relies on discrete parts.
Inner copper thickness 0.5 oz and 0.21 mm prepreg are JLC defaults for 4 layers from memory (UNVERIFIED); gbrjob has no weight.

## 3. Current paths (IPC-2221 external, 35 um, k=0.048: I(dT) = 0.048 dT^0.44 A^0.725; R from 1.72e-5 ohm mm; via 0.3 mm drill 18 um plating 1.6 mm = ~1.7 mohm each)
Width limits at 20 K / 10 K rise: 0.2 mm 1.0/0.74 A; 0.25 1.2/0.9; 0.4 1.7/1.2; 0.5 2.0/1.45; 0.8 2.8/2.0; 1.0 3.2/2.4 A (computed). R per mm: 2.5 / 2.0 / 1.2 / 1.0 / 0.61 / 0.49 mohm.
| Path | Min width / length / vias (VERIFIED, c3/c5) | Load | R | dT | Safe max on this board |
|---|---|---|---|---|---|
| J1.1/J1.2 -> D6/D7 (VBAT_IN) | 1.0 mm, 20.5-23 mm, F.Cu | logic 0.25-0.6 A (surge via D6 up to ~30 A for ms) | 11 mohm | <1 K | 3 A track; limited by D7 SS34 3 A and F1 |
| VBAT_IN other branch (R120 sense, wideband) | 0.25 mm, 130 mm, F+B | < 0.1 mA | 0.26 ohm | 0 | irrelevant (100k) |
| D7 -> F1 (+12V_IN) | 0.8 mm, 6 mm | same | 4 mohm | <1 K | 2.8 A |
| F1 -> L1 -> U2 (+12V, +12V_F) | 0.8 mm; +12V path 21 mm with 2 layer hops (8 vias on net) | 0.45 A at 8 V crank | ~13 mohm | <1 K | 2.8 A track; F1 0.5 A hold / L1 0.5 A rated are the limits |
| +5V | 0.5 mm main (640 mm), 0.2 mm stubs 12.9 mm total, 24 vias | 0.64 A (B06 sum) | - | <2 K | ~1.45 A at 10 K on 0.5 mm; buck 2 A |
| +3V3 | In2 plane + 0.3 mm stubs | < 0.4 A | - | 0 | plane |
| Each OUT_INJn / IACV / VVT / BOOST / ALT, drain tab -> J1 pin | pour 6.9 mm wide x ~4 mm (tab to pin), F/In2/B, 35-42 vias, 93-100 % ring contact | 1.2 A (2.4 A paired, 1989-93 R23/R24) | ~0.15 mohm | ~0 | not the board; device thermals, below |
| Driver source -> J1 GND | source pad (2.2 x 1.2) 1-2 vias in pad, F.Cu GND island 69/75/62/100/19/26/10 mm2 with 15/18/10/19/7/12/2 vias (Q1..Q7), Q8 in the main pour (292 vias) -> In1 -> 17 J1 GND pins (4,5,18,20,21,23,24,26,27,29,30,32,33,35,36,38,39) 100 % ring contact | 1.2 A each | < 3 mohm | ~0 | Q7 island has only 2 vias (~2 A) = fine for 0.5 A boost |
| Heater LSU_HTR_N (J2.37/38 -> Q101 tab) and HTR_GND (Q101.3 -> J2.39/40) | 1.0 mm F.Cu 10.7 mm + 1.0 mm B.Cu 2.5 mm; HTR_GND 4.65 + 2.54 mm; 0 vias; pins paired | 2.0 A steady, 2.3-2.8 A warm-up | ~7 mohm | 9 K at 2.3 A, 14 K at 2.8 A (IPC-2221, F.Cu only) | 3.2 A at 20 K; mb F1 3 A hold trips first |
Heater FET Q101 (VND14NV04: Rds 35 typ / 70 mohm max, Rthj-case 1.7 K/W, datasheet C2649436): drain copper is F.Cu only, 50.5 mm2 (tab + 1.0 mm tracks), 0 vias, nothing inner/bottom connected; 2.3 A rms x 0.07 = 0.37 W warm-up for ~14 s (repo), Rthj-amb on this copper ~50-65 K/W (datasheet Fig 34 class, not re-read) -> +20-25 K; steady state 0.04 W. Fine. Q101 heater supply F1 3 A hold is on the motherboard.
Safe maximum continuous current per output (Tj <= 125 C; Rds 120 mohm hot max (P09); K/W from model; base board load 2.6 W): budget = 125 - 85 - base rise. h=10: 40-14 = 26 K / 24.3-29.4 K/W = 0.9-1.07 W -> 2.7-3.0 A. h=5: 12.7 K / 30.5-37.6 = 0.34-0.42 W -> 1.7-1.9 A. h=3: 0 at 85 C air; at 70 C air 10 K/(38-46) = 0.22-0.26 W -> 1.4-1.5 A. Outputs by position: Q1-Q4 24.0-24.5 K/W, Q5 25, Q7 27, Q8 29 (h 10). All 8 on at 1 W each: 79-106 K above air at h 10 (not a real case). The header pin / socket limit is not the board's and not verified (UNVERIFIED: ~3 A for a 2.54 mm pin).

## 4. Driver thermal design (4 layers)
- Copper per driver: F 84-99.6, In2 103.6-108.2, B 95-108 mm2 (VERIFIED c1). 35 um-equivalent (inner 17.5 um assumed): F ~90 + In2 105 x 0.5 + B 105 = ~248 mm2 vs ~298 on rev 0.10 (B06: 15.2 um inner there too, but 3 inner layers). Vias per drain net 35-42, 24-26 in the tab; ~25 holes of 0.3 mm = 1.8 mm2 open hole in a 37 mm2 pad (4.8 %).
- Vias in pads / fill: 1423 vias, all 0.6/0.3; B03 counted 664 inside pads of the same net (404 in Q1-Q8 tabs); B04 counted 730 touching SMD pads (373 in TO-252). Vias are tented on the mask except via-in-pad openings (B04), so under the DPAK tabs the 0.3 mm holes are open on the top side and tented on the bottom. README "Before ordering 9" and line 37 say "order epoxy-filled and capped"; no order record or JLC notes exist in the repo, and the gbrjob and drill files carry no fill information (VERIFIED: gbrjob has no such field). JLC treats epoxy fill as free only at 6+ layers (B03 web check). So whether the order used it is UNKNOWN: read the JLC order confirmation. INFERRED sizing of the risk: open holes 25 x 0.113 mm3 = 2.8 mm3 per tab vs ~2 mm3 of solder from the 4 paste windows (33.5 mm2 x 0.12 mm stencil x ~50 % metal, stencil thickness UNVERIFIED): wicking can starve or void the tab joint. Effect: tab Rth up, DPAK lifts or voids; check with X-ray/thermal camera.
- Model estimate for injector duty: see Summary 5 and section 3 table. 1.2 A, 80 % duty, 0.12 ohm hot = 0.138 W conduction; clamp (driver's own, 15.3 mJ at 20 mH, repo sim_inj_clamp) = 0.92 W at 7200 rpm sequential (60 shots/s per injector) -> 1.06 W; at 8 mH 0.37 W -> 0.51 W.
- Missing 220 ohm input resistors (Q1-Q8 inputs: U11.3-10 wired directly; nets /Outputs/*_IN = Qn.1 + R19-26 10k pull-down + U11 pin; VERIFIED pcb_nets). What ST says (datasheet C155605 VND7NV04, Doc ID 7383 Rev 4): Table 2 p.7: IIN +-20 mA; RIN MIN "minimum input series impedance" 150 ohm; Table 4: VINCL 6/6.8/8 V at IIN 1 mA, -1.0..-0.3 V at -1 mA; IISS 100-150 uA; Igf fault sink 15 mA at Tj = Tjsh; switching and Eas test conditions all use Rgen = RIN MIN = 150 ohm (tr 0.47-1.5 us, Eas 200 mJ). Section 3 (p.10): input is "electrically connected to the gate through a low impedance path"; on over-temperature the device sinks Igf through the input pin: "If driven from a low impedance source, this current may be used to warn the control circuit"; "no requirement is put on the current capability of the input pin driver except IISS". ST gives no mechanism for the 150 ohm; the repo audit says the same (rev0.10_design_audit "ST does not say what happens below 150 ohm"). INFERRED when it bites: the series R limits IIN when the input pin is pushed beyond its internal clamp (above ~6.8 V or below -1 V) or by ESD/transients through a stiff driver, and it damps the gate edge. With U11 at 5 V (output ~20 ohm, 0.55 V drop at 24 mA, repo) IIN is ~0.1 mA and the 15 mA Igf is within U11's 24 mA drive, so ordinary injector duty cannot reach 20 mA. Edge: without RIN turn-off is faster than the datasheet figures (tf 0.35 us at 150 ohm), clamp events and EMI are outside what ST characterised. Bite scenarios (INFERRED): ESD/transient on drain output coupling to gate when U11 is high-Z or driving low (20 ohm sinks the clamp's gate current), a >6.8 V event on the +5V rail (U11 VCCB 5.5 V max) etc. Severity: medium/low, unquantified.
- Rework practicality: pin 1 (2.2 x 1.2 mm pad, lower-left lead) leaves on a short F.Cu track that runs straight to the gate node; crop work/B18.../crop_q123_Fcu.png. Cut the track 1-2 mm from the pad with a blade, scrape mask each side, bridge with a 220 ohm 0402/0603 (8 sites); the tracks are 0.2-0.3 mm: fragile, use 0402 or a bent-lead resistor and glue. Q pin 1 is on the tab side-lead; do it before power. Tell JLC nothing; not required to power-up. Alternative with no rework: keep, measure at stage 6 (scope gate and drain at 12-14 ohm and a relay coil).

## 5. Decoupling, crystal, analog vs rev 0.10 (VERIFIED c4.py, pcb_net_routing)
- U1 VDD pin to nearest 100 nF pad distance: pin 6 4.6, 100 3.5, 11 5.6, 19 3.7, 28 7.8, 50 2.7, 75 3.6 mm; VDDA pins 21/22 9.2-9.6 mm from C11/C12 at FB1: IDENTICAL to rev 0.10 (0.0 mm difference, all pins) and to B07's weaknesses (pins 11/19/28 share one cap; VDDA caps far).
- Crystal Y1: HSE_IN 12.6 mm vs 12.1 (cur), HSE_OUT 15.3 + 1.4 B.Cu vs 14.8 + 1.4: same. Y101 wideband: WB_OSC_IN 5.2, WB_OSC_OUT 7.2 mm all F.Cu (rev 0.10: 2.0 F + 7.45 B.Cu, so the ordered one is slightly better).
- Analog inputs/wideband: same placement; In1 under U105 only 81 %, U102 83 %.
- Different (weaker) on ord: (a) the 3V3 plane is on In2, with the stack 0.21/1.065/0.21 mm, vs In4 on rev 0.10: equal inter-plane spacing (~1.1-1.2 mm), so no change in HF; (b) buck: C71 100 nF absent, C17/C18 4.3-7.8 mm from VIN (pad), SW node unchanged. (c) The 100 nF/10 uF counts are the same.

## 6. Rev 0.9 vs rev 0.10 differences that make 0.9 weaker (from B03 delta, re-verified where noted)
| Item | Ord 0.9 | Cur 0.10 | Effect |
|---|---|---|---|
| F1 | nSMD050-33V 1206 0.5 A hold, 1.0 A trip, R 0.15-0.7 ohm (datasheet C70077 table II, VERIFIED) | BSMD1812-110 1.1 A | hot trip / drop; P16 INFERRED 0.34 A @60 C, 0.24 A @85 C vs 0.25-0.6 A load |
| L1 | CMI322513U2R2KT 1210 2.2 uH 500 mA 300 mohm | MWSA0503S | at 0.45-0.6 A at/above rating; 0.3 ohm x 0.5 A = 0.15 V |
| Clamp | none: no D42-D49 | ES1D + 1.5SMC16A per injector | driver clamp takes all turn-off energy (section 3/Summary 5) |
| Input R | none | 220 ohm R152-159 | section 4 |
| Buck input | no C71 100 nF | C71 present | switching spikes, EMI, VIN margin |
| Battery sense | R11.1 on +12V after D7/F1 | on VBAT_IN | VBATT reads 0.4-0.8 V low, load dependent |
| CEL | Q13 via U12.6 (DRV_EN) | direct from PE4 | no lamp on fatal error |
| Cranking | D7 0.4 V + F1 (up to 0.7 ohm) + L1 0.3 ohm | 0.25 ohm + 29 mohm | at 6 V battery and 0.6 A U2 Vin ~4.8-5.2 V (INFERRED; P05: dropout starts 5.4-5.6 V) -> +5V sags to ~4.5-4.9 V vs 4.8-5.0 V on rev 0.10 |
| microSD, flex/N2O RC, SD pull-ups | absent | added | feature loss, not weakness |
| 4 layers | In1 GND, In2 3V3 | 6 layers | less heat spreading; B.Cu signals reference 3V3 plane |

## 7. Known weaknesses of the ordered daughterboard (consequence / bench test / rework)
| # | Weakness | Consequence | Bench test | Rework |
|---|---|---|---|---|
| W1 | F1 0.5 A hold PTC + L1 500 mA on the logic supply | hot nuisance trip, brown-out in crank (+5V < 4.8 V), L1 overheat | bench supply 6/8/13.8 V with current meter; measure V across F1, L1 and D7 at idle and in USB+TunerStudio; heat gun/hot-soak to 70 C; watch +5V at 6 V | swap F1 for a 1206 1.1 A PTC (e.g. 1206L110/33NR C48985884, P16), L1 for a >= 1 A 1210 or 0 ohm link; both fit the pads. Hand-rework with iron, no hot air |
| W2 | No injector clamp network | VND7NV04 own clamp (VCLTH 36 V, 45 V typ) takes 15 mJ/shot at 20 mH: +80-86 K above air at 7200 rpm; 8 mH: +46-50 K | measure injector L with LCR; dummy 12-14 ohm + relay coil/injector, thermocouple on tab, 1 h at 6000 rpm equivalent; scope drain clamp level | external TVS (SMCJ16A/1.5KE16-class) from OUT_INJx to VBAT_IN at the harness (wired option); on 1989-93 mb D3/D4 SMCJ30A exist. Otherwise limit sustained rpm |
| W3 | No 220 ohm at Q1-Q8 inputs | outside ST's rating (RIN MIN 150 ohm); consequence unquantified, low in normal drive | scope gate and drain, check Igf case by heating a driver (short tab thermal shutdown with 1 ohm load for 1 s) while watching U11 | cut + 220 ohm 0402 bridge at each pin 1 (delicate, 8 sites, 0.2-0.3 mm track) or accept |
| W4 | Via-in-pad under DPAK tabs (25 open 0.3 mm holes per tab) with fill status unknown | solder wicking: voids, lifted tab, Rth up, early thermal shutdown | read JLC order confirmation; X-ray/ultrasound or side view of tab fillets; thermal camera at 1 A per driver comparing the 8 | reflow with extra paste/solder wire around tab edges; if fill was not ordered nothing can be done to the bottom side |
| W5 | Battery sense after D7+F1 | VBATT reads low by 0.4-0.8 V, worse under load; cold-start enrichment skew | compare TunerStudio vs DMM at 9/12/14 V | R11.1 to VBAT_IN (wire to D7 pad 2/J1.1), or TunerStudio offset |
| W6 | CEL behind shared driver enable | no lamp if firmware dead or DRV_EN low | pull DRV_EN high and watch CEL | cut U12.6 -> Q13 gate, wire PE4 (U1.3); tie U12.18 to GND |
| W7 | Buck input: no C71, bulk caps 4.3-7.8 mm from VIN | switching spikes on VIN (abs max 44 V; D12 Vc 53 V in dump), EMI | scope VIN at the pin, 8-36 V | 100 nF 50 V 0603 across U2 pins 2/GND by hand |
| W8 | Heater FET Q101 no vias/no inner copper | warm-up +20-25 K only; fine | monitor case temp during warm-up | none needed |
| W9 | Plane/stack: 3V3 plane absent under strip; B.Cu signals reference 3V3 plane | none observed for USB FS/CAN/HSE | USB enumeration, CAN loopback | none |
| W10 | Decoupling/VDDA/crystal geometry (same as rev 0.10, B07) | ADC noise, marginal HSE start | scope VDDA, HSE start; ADC noise histogram | 100 nF at VDDA by hand, optional |
| W11 | Header pin (0.64 mm) is the real output ceiling (board copper is not) | injector 1-2.4 A pair on one pin | millivolt drop across the socket at 2 A | none |
| W12 | OUT_TACH direct to 2I on 1989-95 (B03) | tach conflict with igniter | set tach none first | cut 2I track |

## Sources actually read
the review brief; kb/boards B01, B03, B04, B06, B07 (cited); kb/parts P05, P09, P16 (cited); evidence/ord_db: drc_kicad9.json, erc_kicad9.json, pcb_nets.txt, pcb_pads.csv, pcb_footprints.csv, pcb_net_routing.csv, pcb_stats.json, gerbers/*.gbrjob, layers/F_Cu.png; repo/ordered-boards/2026-11/daughterboard/miata_ecu_daughter.kicad_pcb (pcbnew geometry dump, copied to work dir), daughterboard/README.md (lines 15-38, 260-321), repo/firmware/tools/board_thermal.py (run on the ordered board with a venv site-packages path; losses() 'rev09' case); datasheets/txt: C155605 VND7NV04 (Table 2, Table 4, section 3), C2649436 VND14NV04 (Rds, Rth), C70077 nSMD050-33V (table II), C70960 (rating only from LCSC title), C8678 SS34, LMR14020 datasheet (grep).

## Not checked
- Actual JLC order options (fill, copper weight, finish): not in repo; inner 0.5 oz and stack thicknesses are JLC defaults from memory.
- IPC-2152 charts (used 2221 conservative).
- Mechanism of the 150 ohm rule: no ST document explaining it was found; no app note read.
- Real injector inductance/current, real case airflow (h) and cabin temperature.
- Header pin / socket current rating (UNVERIFIED).
- Paste stencil thickness (assumed 0.12 mm) and paste aperture-vs-via overlap from the paste gerber.
- Physical rework feasibility (no board in hand).
