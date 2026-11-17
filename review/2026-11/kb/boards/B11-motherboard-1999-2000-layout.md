# B11 - 1999-2000 (NB1) motherboard rev 0.9: layout, circuit and mechanical review

STATUS: complete (audit run 2, 2026-11-16). Tags: VERIFIED = read/computed today from files; INFERRED = reasoned from verified numbers; UNVERIFIED = memory/secondary.

## Summary
1. The outline (notched NA case, 154.0 x 161.5), the four M4 holes and the header position are the NA placeholder (mb_na6.py:18-52, mb_nb1.py:HDR_1A). The only open design for this car in ext/ is Hellen NB1 (ext/hellen-miata-NB1/hellen64_NB1.kicad_pcb): rounded rectangle 154.0 x 159.0 R7, SIX holes (5.0 mm drill, 7.0 pad), header 1A at (15.99, 21.42). Numeric comparison below. Same outline is used by Hellen NA6-94 and NB2 files (identical Edge.Cuts).
2. CAVEAT that matters: Hellen NB1 does NOT use the Miata case. Hellen issue #3 "What PCB outline do we use?" (2021-07): "2000 camry looks like the winner... looks to match NB1/NB2 OEM style so brackets might align", "2000 camry case has arrived it totally works for us ... two not one PCB to case mount and different location". Hellen sells boards in a powder-coated Camry case (Hellen-One-Platform wiki). So their holes prove the Camry-case posts, not the customer's stock Miata case posts. Real stock case still has to be measured. UNVERIFIED equivalence.
3. Header: Hellen NB1 uses the same TE 178780-1 (76 pos) as this board (footprint hellen-one-common:178780-1, 76 pads, ref P2). Every one of the 64 used pad offsets and the four 3.5 mm pegs of our ecu_mb:TE_178780-1_76P_NB1 are identical to Hellen's (0 differences, 4 decimals). But Hellen chose it because the Camry case window is wide (issue #3: "wide 122 or 125 connector OEM so we would be able to fit 76 pin"; "76 connector own width 130 mm"). The stock Miata NB1 header is the 64-pos 176122-6 (pad span 101.3 mm in the ordered board vs 122.0 mm for the 76-pos), i.e. about 20.7 mm narrower: whether the stock case window passes the 76-pos housing is unknown (risk).
4. Ground pour: computed two-layer GND network (zones refilled, 0.25 mm raster, 1 oz, 0.5 mOhm/sq, via 1.5 mOhm): all 52 GND pads are one copper component; R(harness grounds 3A/3B/3C/3F -> the 20 JD1 ground pins) = 0.44 mOhm; to JD2 grounds, MAP U2.2, USB shell, mounting holes 0.37-0.39 mOhm. At 8 A return that is about 3.5 mV. Model is a lower bound (point sources, no thermal-spoke limit) but margin is 10x+. DRC "starved_thermal" x3 (JD1.39, J5.16, J5.18): pads are PTH so B.Cu zone also reaches them; zero unconnected pads.
5. Circuit parts checked and correct: D1 (SS34, K=IAC_12V/3O, A=OUT_IACV/3M) is directly across the idle coil, polarity right, independent of F2; D5 same; F2 2 A PTC in series with 3O; VICS (3Q) on OUT_MAINRLY ZXMS6004FF (EAS 90 mJ, clamp 60-70 V) needs no external diode; 1U on the VVT driver; knock 2F straight to JD2.3 and J5.6.
6. Findings of substance: socket C124412 is rated 1 A per contact (LCSC) while the LSU heater (3 A hold PTC) returns through only two socket pins (+2 ground); F2 hold derates to 0.80 A at 85 C; if the Hellen outline is adopted J2 and J4 fall on/over the new bottom edge.

## 1. Mechanical comparison (numbers; board origin = top-left of outline, y down)
Hellen source: `ext/hellen-miata-NB1/hellen64_NB1.kicad_pcb` (last commit 0db8e92 "rev.C gerbers"), extracted with work/B11-motherboard-1999-2000-layout/scripts/hellen_geom.py -> out/hellen_geom.txt. Origin = KiCad (21.0983, 11.7053) (Edge line centres; bbox incl. 0.1 mm line width 154.2 x 159.2). VERIFIED.
Ours: repo/scripts/mb_na6.py:14-52 (W,H,OUTLINE,CASE_HOLES), mb_nb1.py:6-10,HDR_1A; evidence/cur_mb9900 (pcb origin 100,50).

| item | this board rev 0.9 | Hellen NB1 | delta |
|---|---|---|---|
| size | 154.0 x 161.5 | 154.0 x 159.0 | height -2.5 |
| shape | NA notched, 3 mm / 6 mm notch arcs | plain rect, R7.0 on all 4 corners | different |
| holes | 4: (4,84) (150,84) (4,143) (150,143), drill 4.5, pad 7 (H1/H2 at y 7.3 removed) | 6: (5.0,5.1) (149.0,5.1) (5.0,87.1) (148.95,87.1) (5.0,153.9) (149.0,153.9), drill 5.0, pad 7.0 | x +1.0/-1.0; y 84->87.1 (+3.1), 143->153.9 (+10.9); 2 extra top holes |
| header 1A | (16.00, 18.13) | (15.99, 21.42) | y +3.29 |
| header 1B row | y 13.63 | y 16.92 | +3.29 |
| header span x | 16.0 .. 138.0 centred (77.0) | 15.99 .. 137.99, centre 77.0 (= board centre; issue #3: centred within 0.0375 mm) | same |
| header pegs | 3.5 mm at 1A + (-0.65,-10.20), 4x | same | 0 |

Holes relative to header pad 1A: Hellen middle holes y +65.68, ours +65.87 (0.2 mm apart), bottom holes Hellen +132.48 vs ours +124.87 (7.6 mm apart).
Hellen file quirks: Edge.Cuts circle for the bottom right hole is at y 164.8053 while the pad J14 is at 165.6053 (0.8 mm; issue #18 "Board mount hole", fixed 2021-10-26 per comment "confirmed location fixed"); the pad position is the one that matches J13, use 153.9. Middle right circle is r 2.25 (4.5 mm) while the pad drill is 5.0.
Corrected dimensions IF the customer case equals the Hellen/Camry case: OUTLINE 154.0 x 159.0 R7; CASE_HOLES = {(5.0,5.1),(149.0,5.1),(5.0,87.1),(149.0,87.1),(5.0,153.9),(149.0,153.9)}, 5.0 mm drill (M4); HDR_1A = (15.99, 21.42). Check I ran with existing part positions unchanged: no pad within 3.5+0.5 mm of any new hole; with J1 moved +3.29 in y nothing collides; pads that leave the 159.0 outline: J2.(pads at y 159.1, x 20.6 and 28.4) and J4 shield pads (y 158.68, x 75.7 and 84.3) -> J2 and J4 must move up at least 2.5 mm. Daughterboard (14.5,42 .. 139.5,118) is clear of all six holes.
Ordered boards: ord_mb9900 (rev 0.7) has the same placeholder outline and a 64-pos 176122-6 header at 1A (26.35, 18.13) (span 101.3 mm): same exposure.
Supporting issue evidence (work/B11-.../web/*.json, GitHub issues of rusEFI hellen-NB1-issues #3, #18 and hellen-NB2-issues #25): NB2 "We are using the exact same case as NB1... the NB1 perfectly fits the hole" (2021-12-15); "2000 miata OEM case looks like NB2 case with 64 pin connector; does NOT look like NA6 or Frankenso case" (issue #3 body).

## 2. Header part comparison
- Hellen NB1: TE 178780-1, 76 pos (22 | 12 | 16 | 26), the 12-pos bay carries Hellen's own "options port" 4A-4L (wideband, flex, boost, VVT). The bay is unused on our board. Hellen BOM lists no LCSC for P2 (hand fitted).
- This board: same part and same footprint geometry. Ordered rev 0.7: TE 176122-6 (64 pos, 22+16+26), the car's own part per README.
- Considerations: the 12-pos bay adds 20.7 mm of housing; benefit = TE 178780-1 stock at distributors (repo research); cost = case window risk. Hellen's choice was driven by a wider case, so it is not evidence that the Miata case takes it.
- repo/motherboards/1999-2000/README.md Rev 0.8 line says the 178780-1 comes "with this car's four plugs on it": the car has three plugs (22/16/26); doc slip.

## 3. Circuit review (every non-connector part)
| ref | what | check |
|---|---|---|
| F1 3 A PTC 2920 (VBAT_IN -> HTR_PWR -> J2.8) | LSU heater supply | OK. Track 1.0 mm both layers (12.5+11.2 mm). IPC-2221 external: 1.0 mm, 1 oz carries 2.4 A at +10 K, 3 A at about +17 K. Return LSU_HTR_N 1.0 mm, 135 mm total length (0.066 Ohm, 0.2 V at 3 A) |
| F2 2 A PTC 1812 (VBAT_IN -> 3O) | idle valve +12 V | Datasheet C46641168 derating table: hold 2.00 A at 25 C, 1.45 A at 60 C, 1.09 A at 70 C, 0.80 A at 85 C. Idle valve current not known (coil resistance UNVERIFIED); at 100 % duty and 8-10 Ohm it is 1.4-1.8 A, above 0.8 A at 85 C. Mostly a short-circuit guard; low risk |
| D1 SS34 | idle freewheel | Netlist: D1 pin1 K = IAC_12V (3O), pin2 A = OUT_IACV (3M). Directly across the valve coil, so independent of F2 state. Orientation correct (KiCad Device:D_Schottky pin1=K). VERIFIED in sch_netlist.xml. Placed under the daughterboard at JD1.31 |
| D5 SS34, F4 1.1 A, R35 4.7k, R36 10k | AUX boost valve, flex, N2O | correct: D5 K=AUX_VBAT A=OUT_BOOST |
| 1O OUT_ALT | alternator field PWM | JD1.40 + J5.4 parallel; ships off (documented) |
| 3Q VICS on OUT_MAINRLY | ZXMS6004FF low side on daughterboard | Datasheet: clamp 60-70 V, EAS 90 mJ; a VICS coil (35 Ohm, 50 mH as in repo sim) stores 0.5*0.05*0.4^2 = 4 mJ, 22x margin. Firmware has no VICS strategy so it stays off (firmware README:248, documented) |
| 1U front O2 heater on OUT_VVT | low side, DC | Hellen routes 1U via jumper R32 to a dedicated OUT_O2H; ours uses the VVT driver (VND7NV04, VERIFICATION notes cold inrush 4.6 A sim vs 6 A min limit). No diode (resistive). OK |
| 2F knock | IN_KNOCK -> JD2.3 and J5.6 | no part on the motherboard; daughterboard has R138 2.2k + amp. A knock sensor on AUX J5.6 would be in parallel with the stock one (note) |
| C1 1u, C2 10n, C3 470p | MAP supply/output | C1/C2 at (143.6,140.6)/(143.6,136.6) local, U2 at (124,142): about 20 mm from the sensor, acceptable. C3 at the sensor end |
| R1 120, R6 0R | CAN termination | fine |
| R20-R22 | NOT FITTED 12 V pull-ups | fine |
| U4 USBLC6, R2/R3 5.1k, J4 | USB | see below |
Pin map spot check against Hellen NB1 netlist (hellen64_NB1.xml, P2 pads): 3M=OUT_IDLE(+3 diodes), 3O=+12V_RAW, 3Q=OUT_VICS, 2K=OUT_TACH, 2F=IN_KNOCK_RAW, 2I=+5VAS, 2B IAT, 2D VSS, 2E CLT, 2H cam, 2J crank, 2L MAF, 3E TPS, grounds 3A/3C/3B/3F: all agree with HARNESS in mb_nb1.py. VERIFIED.

## 4. Layout
- Widths (pcb_net_routing.csv + nets.py): VBAT_IN 1.2 mm trunk (221 mm of 1.2 mm F+B, plus 50 mm at 0.6 mm), IAC_12V 0.8, HTR_PWR 1.0, LSU_HTR_N 1.0, AUX_VBAT 0.5 (F4 1.1 A hold: 0.5 mm good for about 1.95 A at +20 K), OUT_INJ 0.6, OUT_IACV 0.6/0.8, OUT_VVT 0.6, OUT_FP/FAN/MAINRLY 0.5, OUT_IGN 0.4. No under-sized power track found for the stated currents. Worst case all loads on VBAT_IN (3 + 2 + 1.1 + 1 A) on a 1.2 mm trunk would be about +85 K by IPC-2221 on one layer, but the trunk is routed on both layers and the worst case is not simultaneous (INFERRED, low).
- Routing is autorouted and long: IN_KNOCK 213 mm, IN_MAP 135 mm, OUT_ALT 246 mm, IN_CLT 136 mm, USB_DP 62.8 mm. Parallel runs within 0.6 mm edge gap (xtalk.py): IN_KNOCK next to OUT_VVT 34.7 mm (heater DC, benign), IN_MAP next to OUT_ALT 39.8 mm (alt PWM off by default), IN_CLT next to OUT_MAINRLY 35.4 mm (VICS rarely switched). A 0.2 mm 135 mm MAP trace driven by the sensor through 470 pF at its end; coupling estimate from 14 V edge through about 1.2 pF over 470 pF = about 36 mV worst-case spike (INFERRED), under 1 % of 5 V; low.
- USB: DP 62.8 mm, DM 58.5 mm (skew 4.3 mm), full speed 12 Mbit/s, no impedance control needed at that speed; U4 is flow-through (pins 1/6 and 3/4 both on the line); VBUS runs 20.5 mm alongside DP. Checked, acceptable.
- MAP: U2 lies flat at the right of the board, 90 mm from JD2.5; fine.
- DRC (evidence/cur_mb9900/drc_kicad9.rpt): 46 findings, 0 unconnected pads; 44 are net_conflict from unnamed NC harness pads, 3 starved_thermal on PTH GND pads (connected through the other layer), silk overlaps only.
- Sockets: LCSC C124412 B-2200S40P-A120 live lookup: 'Current Rating': '1A' per contact (tools/lcsc.py). Heater return LSU_HTR_N uses JD2.37/38 (2 pins), 3 A hold / 2.3 A rms cold = 1.15-1.5 A per pin, ground return JD2.39/40 likewise; OUT_VVT (O2 heater DC) uses single pin JD1.34; injectors and idle valve one pin each. 1 A is a nominal contact rating (typical contact resistance 10-20 mOhm so I^2R small), so low-medium; the Wurth 61304011821 recommended in VERIFICATION is rated higher (UNVERIFIED, from memory 3 A).

## Sources actually read
- the review brief; repo/motherboards/1999-2000/README.md; repo/scripts/mb_common.py, mb_nb1.py, mb_later.py, mb_na6.py (outline/holes); mb_route.py not needed beyond width table; repo/research/pinouts_9605.md (header notes).
- kb/interconnect.md cur_mb9900 sections; evidence/cur_mb9900: pcb_nets.txt, pcb_pads.csv, pcb_footprints.csv, pcb_net_routing.csv, pcb_stats.json, drc_kicad9.rpt, sch_netlist.xml, fab_drc_report.txt; evidence/ord_mb9900 pcb_pads.csv.
- ext/hellen-miata-NB1 (pcb, xml, kicad_sym, gerber csv), ext/hellen-miata-NA6/NB2 pcb (same outline); GitHub issue/comment JSON in work/.../web (hellen-NB1-issues #3, #18; NB2 #25; NA6 #26); wiki pages Hellen-NB1, Hellen-One-Platform, OEM-connectors in work/.../web.
- datasheets/txt: C46641168 (SMD1812-200-30 derating table), C95063 ZXMS6004FF (EAS, clamp); tools/lcsc.py C124412.
- Scripts: work/B11-.../scripts/hellen_geom.py, nets.py, xtalk.py, gnd1.py/gnd2.py (ground resistance model).

## Not checked
- The real stock Miata NB1 case (post positions, connector window width): no source in the workspace; Camry-case equivalence unverified.
- IAC valve and front HO2S heater resistance/current (no FSM in workspace).
- 3-D clearance of parts against the case; JLC CPL rotations; whether Hellen NB2/NA6 hole sets differ (only the shared Edge.Cuts compared).
- Full-copper-field analysis of EMI; ground model is a first-order raster model (+/- 2x).
