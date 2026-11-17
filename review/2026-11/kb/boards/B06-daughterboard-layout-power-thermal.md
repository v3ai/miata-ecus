# B06 - Current daughterboard (rev 0.10, 6-layer) layout review: power, current-carrying copper, thermal

Status: COMPLETE (scratch: work/B06-daughterboard-layout-power-thermal/, scripts b01..b08, geom.json from pcbnew; repo thermal reruns in repo_thermal_runs*.txt).
Stackup (VERIFIED from board): F.Cu 35um / In1 GND plane / In2 + In3 signal+GND pours (15.2um) / In4 +3V3 plane / B.Cu 35um; 1349 vias, all 0.6/0.3 through vias.

## Summary
1. Injector/valve drain path (tab -> J1 pin): VERIFIED solid. Each drain is a 6.0-6.9 mm wide column on F/In2/In3/B joined to the J1 pad (100% ring contact, 89% for INJ3) along ~5 mm; R ~0.1-0.2 mOhm, dT ~0. No bottleneck at 1.2 A (2.4 A pair case also fine). The weak link is the single 0.64 mm header pin per output, not the board.
2. Ground return: source pad of each driver (2.2x1.2 mm) has 1 via inside + 4-11 more within the local F.Cu island, then In1 (single connected 8383 mm2 plane, 88% cover; 95-98% under MCU/buck) to 17 J1 GND pins, each tied to In1 100%. Fine. Q8 source sits in the 2914 mm2 main pour.
3. In1 plane integrity (VERIFIED): one component, no slots. Only voids: 8 x 24 mm2 (5.1x5.1 mm) under each DPAK tab via-field plus 11-12 mm2 ones; driver strip cover 71%. Necks between the tab voids 2.5 mm; In2/In3/F/B GND pours also parallel the return. No problem.
4. +3V3 plane In4: 82% cover, one component but fragments below 2 mm neck width (low current, fine); under the driver strip 66%.
5. Buck hot loop: C17/C18 (2x10u/50V) pads are 5-7 mm from U2 VIN (pins 2/3 at x=11.7); C71 100n is 2.2 mm away with 1 GND via at 0.28 mm; SW pin 8 -> D9 pad 1 3.4 mm; D9 anode GND pad has 2 vias within 1 mm; In1 solid GND 0.1 mm under F.Cu everywhere (BUCK_SW has no copper on any inner layer). Loop is small (F.Cu to In1 return) - good. SW node F.Cu copper 19.6 mm2, 0.8 mm track 6.2 mm to L2: acceptable; FB (0.2 mm, 8.6 mm) is 3.5 mm from SW and 5.5 mm from BOOT: good. L2 sits 9 mm from the IC (acceptable). Cin is 2x10u only for a 2 A 40 V converter; fine at 0.4-0.6 A.
6. Input protection placement: D6 SMCJ30A at J1 side, D7 SS34 reverse diode, F1 PTC, D12 SMAJ33A: order is correct, all within 12 mm of J1 pins 1/2.
7. Repo thermal model reproduces (h=10: board 31 C, drivers 41, TVS 52, MCU 40 C, 5.9 W). Board mean rise is essentially P/(2*A*h) with A=0.0095 m2, i.e. dominated by h. h=10 per face is a free-air figure; in a closed metal case h per face is likelier 3-6. See findings.
8. Total dissipation (INFERRED, own sum, close to repo): idle ~3.1 W, cruise 3000 rpm ~3.9 W, sustained 7200 rpm 20 mH ~6.0 W. Base load (MCU .33, buck .5, LDO .43, trackers .72 at assumed 35/50 mA, D7 .14, WB/CAN ~.4) ~3 W dominates at idle.
9. Temperature-limited parts: see table below. PTC F1 derating (datasheet) is the tightest: 0.52 A hold at 85 C.

## Drain copper and via counts (measured, replaces README's 84-100 / 95-108 / 34-42)
| Driver | F.Cu mm2 | In2=In3 mm2 | B.Cu mm2 | vias on net | in tab pad (37.1 mm2) |
|---|---|---|---|---|---|
| Q1 INJ1 | 94.1 | 107.4 | 107.4 | 41 | 25 |
| Q2 INJ2 | 95.6 | 107.6 | 107.6 | 41 | 25 |
| Q3 INJ3 | 93.6 | 105.9 | 105.9 | 41 | 25 |
| Q4 INJ4 | 100.2 | 108.4 | 108.4 | 45 | 25 |
| Q5 IACV | 97.0 | 106.3 | 106.3 | 41 | 25 |
| Q6 VVT | 96.7 | 105.2 | 105.2 | 41 | 25 |
| Q7 BOOST | 98.9 | 107.5 | 107.5 | 41 | 25 |
| Q8 ALT | 101.6 | 109.9 | 109.9 | 41 | 25 |
README says F.Cu 84-100, inner/B 95-108, 34-42 vias: stale by a few percent (3-4 vias per net lie outside the column), claims essentially right. Effective (35 um-equivalent) copper per driver ~ 98 + 0.434*2*107 + 107 = ~298 mm2.
Clamp TVS (D46-D49): K-side F/In2/In3/B = 37/52/52/31 (D46), 39/53/53/50, 35/52/52/42, 36/53/53/24 mm2; A (VBAT_IN) side 24-31 / 33-35 / 33-35 / 21-33. Vias per pad: in pad 1-3, in zone 3-8 (D48 K only 4, D49 A only 3; D49 pads have 1 via each in the pad). README "176-196 mm2 effective" holds as K+A sum, ~mixed definition. Spread of via counts is uneven but thermal effect minor (the model gives D46 51 / D48 52 C).
Other heat sinks: U2 EP 6.9 mm2 2 vias; U3 EP 3 vias; U14 EP 1 via (all to GND planes, fine); **U4 LDO tab (+3V3, 7.4 mm2) has 1 via and a 2.9 mm2 F.Cu island; heat goes only into In4 (15 um)**; Q101 heater FET drain (LSU_HTR_N) 48 mm2 F.Cu island, 0 vias, no inner copper.

## Current paths, resistance, rise (own calc; IPC-2221 external I=k dT^0.44 A^0.725, k=0.048; IPC-2152 gives lower rise with planes so these are conservative)
| Path | Geometry (VERIFIED) | I | R | dT |
|---|---|---|---|---|
| INJn drain, tab to J1 pin | 4-layer pour 6-6.9 mm wide, ~5 mm | 1.2 A (2.4 A paired) | ~0.15 mOhm | ~0 |
| INJ source to J1 GND | via(s) 1.4 mOhm each (0.3 drill, 18 um plating, 1.6 mm) x 5-12, In1 plane, 17 pins | 1.2 A per driver | <3 mOhm | ~0 |
| Heater LSU_HTR_N / HTR_GND | 1.0 mm F.Cu (+B.Cu 2.5 mm) to J2 pins 37/38 and 39/40 | 2.0 A (warm-up 2.3 A rms) | ~25 mOhm per 50 mm | 6.6 C IPC-2221 (matches repo 6.7) |
| VBAT_IN (clamp return, J1.1/2) | 0.25-1.0 mm tracks + In2 pour | pulses 0.2 A | - | <8 C (repo 7.2 worst, 0.57 A on In2 1.0 mm 15 um, plausible; transient only) |
| Battery logic path D7-F1-L1-U2 | 0.8 mm F.Cu | 0.3-0.55 A real (repo test 1.1 A) | - | <3 C |
| +5V | 0.5 mm F.Cu | 0.64 A | - | 1.6 C |
Heater: VND14NV04 0.07 Ohm max (hot ~0.14) x 2.3 A rms warm-up = 0.4-0.7 W for ~14 s on 48 mm2 of F.Cu, ~60 C/W => +25-45 C: acceptable, steady state 0.04 W.

## Dissipation and temperature (independent estimate)
| Case | W (own) | repo | board mean rise at h=10 (repo; no pins/pins) | at h=5 (my closed-case guess; no pins/pins, repo script rerun) |
|---|---|---|---|---|
| idle 800 rpm | 3.1 | not tabulated | ~16 / 12 | ~33 / 21 (scaled) |
| cruise 3000 rpm | 3.9 | not tabulated | ~21 / 15 | ~41 / 26 |
| 7200 rpm sustained sequential 20 mH | 6.0 | 5.9 | 31 / 23 (reproduced) | 63 / 41, MCU junction +71 / +51, TVS +83 / +61, drivers +72 / +47, LDO +76 / +56 |
| 1989-93 paired, batch | 8.6 | 8.6 | 46 | h=5 not run; h=3: 151 C mean, TVS +220 |
Closed-case h per face: gap conduction k/delta = 0.026/0.015 = 1.7, radiation to bare metal case (eps_eff ~0.2) ~1.3, so 3-5 W/m2K (UNVERIFIED, assumption). Case-to-cabin under carpet: assume ~0.12 m2 shell, effective ~3-4 W/m2K => 0.3-0.4 W/K, adds 10 K (idle), 13 K (cruise), 19 K (7200) above cabin (UNVERIFIED, case size/mounting unknown; B13 owns case). The repo's "air around the board" excludes this step and its h=10 is a free-air value. Resulting limit for MCU (105 C junction) at sustained 7200: air-around-board <= 54 C (pins path) or 34 C (no pins) vs repo's 65-73 C; i.e. repo optimistic by ~11-31 K in allowable air, plus another 15-20 K case rise to cabin. At idle/cruise the board is far from limits (MCU junction ~ cabin + 40-60 K).
Where the repo is pessimistic: counts no part-body surface (+10-20% area), no conduction through the 4 M3 standoffs / case; E_tvs scaled to 20 mH (8 mH quoted by owner as plausible: clamp heat 40%); 0.8 duty; sustained 7200 rpm for hours is a track-only case (board time constant tens of minutes).
Repo uses TLS115B0EJ RthJC 10 C/W; datasheet (C3743696 p.8 Table 3, VERIFIED) says 18 K/W typ junction-case: +0.3 W x 8 K = +2.4 K, negligible. Tracker load 35/50 mA is assumed: at the 150 mA rating U14 would dissipate (13.5-5)x0.15 = 1.3 W in a DSO-8 EP with 1 via in its pad.

## Temperature-limited parts near heat sources
| Part | Limit | Nearest heat | Note |
|---|---|---|---|
| F1 BSMD1812-110 PTC | hold 1.10 A@25, 0.71@60, 0.66@70, 0.52@85 C (datasheet C883150 derating table, VERIFIED); operating -40..85 | D6 8.7 mm, D7 8.7 mm, L1 9 mm | real draw 0.4-0.55 A (cranking 8 V ~0.45 A per repo) vs 0.52 A at 85 C: thin margin when air >70 C, F1 also derates from its own 0.25 Ohm self-heat |
| J4 microSD socket | -20..+85 C (repo) | Q8 17 mm, Q7 19.7 mm (ALT/BOOST drivers, light duty); TVSs 33 mm | not the hottest zone; limit is cabin+case air |
| Y1 8 MHz (MCU) | typ -40..85 | U4 LDO 10 mm, U1 16 mm | LDO +44..+76 C junction: crystal sees ~mean board temp |
| Y101 (wideband) | same | U102 10 mm, Q101 17 mm | fine |
| U1 STM32F407VGT6 | 105 C junction (85 C grade) | itself 0.33 W | tightest IC |
| U4 LDL1117S33R | Tj 125 C | 0.43 W, 1 via in tab | weakest heat path of the regulators |
| U105 AD8628 / U103 REF3033 (analog) | 125 C parts, drift | Q101 8.5 mm / 20 mm | warm-up heater dissipation 0.5 W near the pump-current amp: minor offset drift |
| Electrolytics | none on board | - | polymer/ceramic only |
| Clamp TVS 1.5SMC16A | 150 C (known) | self | 4 pads vias per above |

## Findings not promoted to the top list
- Drain/tab claims in README essentially correct (table above).
- Open 0.3 mm vias in 25 positions per DPAK tab: README line 75 and 371 already require epoxy-filled+capped order (documented).
- No separate slot/void problems; In1 solid.

## Sources actually read
evidence/cur_db/fab_track_current.txt, pcb_nets.txt, geometry via pcbnew export (work/.../geom.json); repo/firmware/tools/board_thermal.py (read, rerun at h=10/5/3 with and without --pins using a cairosvg rsvg-convert shim in work/.../bin), VERIFICATION.md 790-835 and 1105, daughterboard/README.md 36-75, 370; datasheets/txt/C883150_BSMD1812-110-33V.txt (derating table), C3743696_TLS115B0EJ.txt (Table 3), C155605_VND7NV04TR-E.txt (Rthj-case 2.1). IPC-2221 formula computed by hand.

## Not checked
IPC-2152 charts (used IPC-2221 as conservative bound); STM32 crystal/LDL1117/microSD datasheet limits not re-read (microSD -20/+85 taken from review brief/README); actual ECU case size/mounting/carpet cover (assumed); injector inductance/current; motherboards' current paths (other audits); ordered rev 0.9 board.
