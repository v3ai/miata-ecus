# B10 - 1996-97 motherboard (rev 0.9, current) - layout and circuit review

Board: `cur_mb9697` = `repo/motherboards/1996-97/miata_mb_9697.kicad_pcb` (2 layers, 154.0 x 161.5 mm, KiCad origin (100,50); coordinates below are board coordinates = file minus (100,50)).

## Summary
1. MECHANICAL (main result): the placeholder outline/holes are NOT the 1996-97 ones. They are the 1989-95 notched NA outline taken from the OLD Hellen NA6 rev-b board (`ext/hellen-miata-NA6/old/hellen64_miataNA6_94.kicad_pcb`). rusEFI's Hellen NA8-96 board (rusefi/hellen-miata-NA8, commit b2b0948) uses a different outline: 154.0 x 159.0 mm rectangle with 7 mm corner radii and SIX mounting holes. Derived dimensions below (VERIFIED from the KiCad file, "real case" itself INFERRED).
2. Header: TE 178780-1 x position matches Hellen to 0.01 mm (1A at x=15.99 vs 16.00); y differs: Hellen 1A (lower row) at y=21.42, repo 18.13 -> move 3.29 mm down.
3. Ground: pour is fully connected on both layers (0 islands in GND net, DRC agrees). Computed resistance, all 5 harness ground pins to all 25 daughterboard GND pins: 0.33 mOhm; any single harness pin to all JD pins 0.66-0.93 mOhm; to the worst single JD pin 1.5 mOhm; to USB-C GND 1.3 mOhm, J5 GND 1.7 mOhm. Excellent (checked, correct).
4. Track widths vs current are adequate for injectors (0.6 mm, 72 mOhm, ~1 A), IACV, relay coils, ignition logic. Widest concern: VBAT_IN trunk from 4B is only 0.6 mm x ~80 mm (90 mOhm to JD1.1) and carries ECU supply plus LSU heater current (<=3 A through F1): low/medium risk, see below.
5. O2 heater: 3M -> OUT_VVT -> JD1.34 -> daughterboard VND7NV04 low side (Ilim 6/9/12 A min/typ/max, datasheet C155605 line 404). Stock front HO2S heater is about 13 ohm cold (1994/95 Mazda spec, secondary source) so about 1.1 A at 14.4 V: 0.6 mm / 41 mOhm trace is fine; no freewheel diode needed (resistive, correct that D2 is omitted).
6. Freewheel diodes D1 (IACV to VBAT_IN) and D5 (BOOST to AUX_VBAT) have the correct polarity (pad1 = cathode on VBAT/AUX_VBAT, pad2 = anode on the driver output): checked, correct.

## Mechanical: Hellen NA8-96 vs this placeholder (VERIFIED from files, origin = top-left of outline)
Source: `work/.../ext_dl/hellen-miata-NA8/hellen64_NA8_96.kicad_pcb` (cloned from github rusefi/hellen-miata-NA8, last commit b2b0948 2023-04-11 "modern approach"; script `scripts/hellen_geom.py`). Outline file coords x 21.098..175.098, y 11.705..170.705, Edge.Cuts lines w=0.1 plus r=7 corner arcs.

| item | Hellen NA8-96 (real) | repo placeholder |
|---|---|---|
| outline | 154.0 x 159.0 rectangle, corner R7, no notches | 154.0 x 161.5 NA notched outline (R6/R3 notches, top edge only 129 mm wide at y<3.5) |
| holes | 6: (5.0,5.1) (149.0,5.1) (5.0,87.1) (148.95,87.1) (5.0,153.9) (149.0,153.1) | 4: (4,84) (150,84) (4,143) (150,143) |
| hole drill/pad | 5.0 mm / 7 mm pad (MountingHole_4.5mm_Pad lib part, drill 5.0) | 4.5 / 7 |
| header 1A pad | (15.99, 21.42) lower row; upper row y 16.92 | (16.0, 18.13); upper row 13.63 |
| header mount holes | x 15.34..138.64 (3.5 mm), y 11.2 | x 15.35..138.65, y 7.93 |
| header body (courtyard/silk bbox) | x 11.77..142.25, y -4.27..22.3 | x 11.45..142.6, y -7.9..19.8 |

Deltas: hole (4,84)->(5.0,87.1) (+1.0,+3.1); (150,84)->(148.95,87.1) (-1.05,+3.1); (4,143)->(5.0,153.9) (+1.0,+10.9); (150,143)->(149.0,153.1) (-1.0,+10.1); two top holes (5.0,5.1),(149.0,5.1) are missing in the placeholder (the code even removes H1/H2). Board height 2.5 mm too tall. Bottom features that then need moving: J2 JST courtyard reaches y=162 (>159), USB-C J4 at y=157.6 and its shell would overhang. Hole drill in repo is 4.5 vs 5.0 (M4 passes both).
Confidence: the numbers are VERIFIED; that they fit the real 96-97 case is INFERRED (Hellen NA8-96 is a sold, "somewhat abandoned" board; its own wiki does not state case dimensions). Caveat: Hellen's modern NA6_94 and NB1 files carry the identical outline and holes (the NA6_94 file is a clone, `step2_copy_hellen64_na6.sh`), so the same outline may be a common Hellen "fits all" design, which is evidence it clears several cases rather than proof it is the case outline. No dimension drawing of the Mazda case found. Treat as best available; the owner should still measure a real case before ordering.
Header width: 76-pos housing about 130.5-131 mm (footprints), 123.3 mm between outer mounting holes, inside a 154 mm board leaves 11.5 mm per side; Hellen proves that arrangement; the case opening itself not found (not verified). The placeholder notched top edge (129 mm wide) is narrower than the housing (131 mm): about 1 mm per side overlap, README already flags it; moot with the Hellen outline.

## Layout checks
Ground resistance method: rasterised F/B zone fills + tracks + pads at 0.33 mm, 1 oz (0.49 mOhm/sq, assumed JLC default), vias 1.5 mOhm, solved as resistor mesh (scripts/dump_mask.py, solve_res.py). Results in summary. All GND pads in one component. DRC (KiCad 9) shows one starved thermal (J-pad, 1 spoke).
Track widths (pcb_net_routing.csv): INJ1-4 0.6 mm; IACV 0.6; VVT 0.6; FAN/AC/FP/LS7 0.5; CEL/TACH/IGN 0.4; BOOST 0.8; HTR_PWR and LSU_HTR_N 1.0; VBAT_IN 0.6 (trunk) and 1.2; AUX_VBAT 0.5 (F4 1.1 A hold). IPC-2221 external 1 oz: 0.6 mm about 1.6 A for +10 K, 1.0 mm about 2.3 A, 1.2 mm 2.7 A.
Path resistances (computed, mOhm): 4B->JD1.1 90; INJ1 72, INJ4 62; IACV 42; VVT 41; FP 36; FAN 60; LSU_HTR_N J2.2->JD2.37 66 (100 mm route); HTR_PWR about 12 (estimate). Heater loop (4B -> F1 -> sensor -> JD2 low side) <= about 0.3 ohm, i.e. under 1 V at 3 A: acceptable.
VBAT_IN: the first 80 mm after 4B are 0.6 mm; through it flows ECU supply (about 0.5-1 A, UNVERIFIED) + heater (peak 3 A, fused at 3 A hold). At 3.5 A IPC suggests about 55 K rise steady state (short warm-up only). Low/medium; fix: 1.2 mm on that trunk.

## Circuit (every non-connector part)
C1 1u / C2 10n on V5_SENS (MAP supply decoupling), C3 470p on IN_MAP (RC with divider), D1 SS34 IACV flyback to VBAT_IN, D5 SS34 boost-valve flyback to AUX_VBAT, F1 3 A PTC LSU heater, F4 1.1 A PTC AUX 12 V, R1 120 + R6 0R CAN termination (R6 removable), R2/R3 5.1k USB-C CC, R20-22 4.7k NF 12 V pull-up options on SW1-3, R35 4.7k flex pull-up to V5_EXT, R36 10k nitrous pull-down, U4 USBLC6-2SC6 USB ESD (pins 1/6 DP, 3/4 DM, 5 VBUS: correct per ST), U2 MPX5700AP. Nothing found wrong in function. Fuel pump (1U OUT_FP) and fan/AC/LS7 (1A,1G,1B) and CEL (1E) are low-side relay-coil/lamp outputs straight from VND7NV04-class drivers, no flyback on the motherboard: relay coils in stock Mazda relays are driven the same way by the stock ECU with internal clamp; the daughterboard drivers clamp at 40-55 V (design.py:332-341). INFERRED fine.
Unconnected harness cavities (44, list in the 1996-97 README): car consequences per kb/pinouts/PIN-9697 (no OBD-II scan/readiness via 1D, EGR, purge, PRC, rear heater 4Z, PS and brake switches, headlight/AC-control lines, battery backup 4I): no engine-damage item, driveability/emissions only; owned by the pinout audit.

## Sources actually read
the review brief; repo 1996-97 README; scripts mb_na96.py, mb_na6.py (outline, holes), mb_common.py protection_place; evidence/cur_mb9697 pcb_net_routing, pcb_stats, drc rpt; kb/interconnect.md sections; kb/pinouts/PIN-9697; hellen NA8-96, NA6_94, NB1 KiCad files (pcbnew); ext NA6 old board; datasheets/txt/C155605_VND7NV04TR-E.txt line 404; manualslib/autorepairshq search result for Miata HO2S heater about 13 ohm at 20 C (secondary).

## Not checked
Real Mazda case drawing/opening (none found); header housing vs case opening; JLC copper weight (1 oz assumed); heater inrush current of the real stock sensor; whether Hellen board has actually been fitted in a 96-97 case by users (no issue tracker read); thermal effects on traces by simulation; motherboard routing around the new outline (needs full reroute).
