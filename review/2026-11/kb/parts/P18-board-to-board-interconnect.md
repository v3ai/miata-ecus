# P18 board-to-board interconnect (J1/J2 headers C2977586, JD1/JD2 sockets C124412, HD1-HD4)

## Summary
1. All 80 pins carry the same net on both boards for all 9 motherboard variants (4 current, 5 ordered); the only name mismatches are JD2.39/40 (DB net HTR_GND, MB net GND) and that is intentional (VERIFIED: design.py:113-116, mb_common.py:25, gen_sch2.py:1022): heater FET source returns straight to MB ground.
2. Geometry is a pure translation (+14.5, +42.0) mm for every one of 80 pads in 4 db/mb pairs, no mirror: headers on DB bottom, DB stays right-side-up (VERIFIED, pcb_pads.csv). Mounting holes also offset by the same vector.
3. Ordered rev 0.9 DB J2.24/25 = UART_TX/RX, current DB J2.24/25 = IN_FLEX/IN_N2O; every ordered MB matches ordered DB, every current MB matches current DB, but ordered DB on current MB (or reverse) would cross-wire these 2 pins.
4. Header C2977586 plating is unspecified (Zhouri sheet: "Au or Over Ni"; LCSC Contact Plating '-'); socket C124412 is gold over nickel (sheet). Mixed/unknown plating is the main reliability risk for sub-mA sensor lines.
5. Socket C124412: 65 in stock, extended, $0.57@1/$0.40@30/$0.31@80/$0.26@960; sheet says 3 A, LCSC attribute says 1 A. Header $0.20@1, 2565 stock, extended.
6. Currents per pin are fine except VVT 2.0 A on a single pin (derated limit ~2 A): marginal only at 100 % duty, 85 C.
7. Ground: 23 GND pins + 2 heater-return pins; drop estimate 5-10 mV pulsed, low impact.
8. Stack: header plastic 2.54 + socket 8.5 = 11.04 vs 11 mm standoffs: fine (tolerance +-0.3).
9. Assembly: headers soldered while plugged into MB sockets (jig) -> JLC cannot do it; hand work 160 joints per unit (80 DB + 80 MB sockets).

## Datasheet digests (VERIFIED, page images viewed)
- C2977586 Zhouri PZ2.54-1*N: 2.5 A, 500 VAC, contact R 20 mohm max, -40..+105 C, brass, PBT/PA9T, 0.63 sq pin, plastic 2.54, mating pin 6.0+-0.1, tail 3.0+-0.1, total 11.6, hole 1.02; plating "Au or Over Ni" (ambiguous). Footprint: pad 1.7, drill 1.0 (OK).
- C124412 Ckmtw B-2200S40P-A120: 3 A, 20 mohm max @1 A DC, gold over nickel, brass, 8.5+-0.15 body, tail 3.2+-0.2, pitch 2.54+-0.05 (+-0.2 over span), -40..+105 C. No mating-cycle or retention-force data in either sheet.
- Repo's own VERIFICATION.md:670-675 says sockets were changed from tin to gold for this reason; BOM now C124412 (gold). Header plating not addressed.

## Pin tables
Full tables in kb/interconnect.md (cur_db lines 8-93). J1: 1-2 VBAT_IN, 3 VIGN, 4,5,18,20,21,23,24,26,27,29,30,32,33,35,36,38,39 GND (17), others outputs (INJ1-4 at 19/22/25/28, IACV 31, VVT 34, BOOST 37, ALT 40, IGN 14-17, FP/RLY/AC/FAN/CEL/TACH/LS7 6-12, V5_EXT 13). J2: GND 2,12,18,23,26,29 (6), V5_SENS 1, analog/digital inputs 3-26, CAN 27/28, USB 30-32, LSU 33-36, LSU_HTR_N 37/38, HTR_GND 39/40. Total return pins = 23 GND + 2 HTR_GND = 25.

## Current per pin (inputs from repo/scripts/track_current.py:56-95; derating mine)
| pin(s) | worst current | notes |
|---|---|---|
| VBAT_IN x2 | 0.55 A each (1.1 A F1 hold) + 0.2 A clamp return | ok |
| INJ x4 | 1.2 A (14.4 V/12 ohm) | ok |
| IACV 1.3, VVT 2.0, BOOST 0.6 | single pin each | VVT marginal |
| other outputs | 0.5 A / 0.05 A | ok |
| LSU_HTR_N 37/38, HTR_GND 39/40 | 2 A rms split 2 pins = 1 A/pin; cold peak 2.3 A (VERIFICATION.md) = 1.15 A/pin | ok if contacts share |
| GND (23) | sum at peak: 4 inj 4.8 + IACV 1.3 + VVT 2.0 + boost 0.6 + 6 outputs 3.0 + logic ~0.6 = ~12 A if all simultaneous (not realistic; ~8 A typical worst) | 0.35-0.5 A/pin |
Derating (INFERRED): 3 A rating assumed at ~30 C rise; at 85 C air to stay <=105 C allows ~20 C rise: I = 3*sqrt(20/30)=2.45 A single pin; with loaded neighbours x0.8 = ~1.95 A. Header sheet 2.5 A -> ~1.6 A. So VVT 2.0 A continuous sits at/over the derated limit of the header; 100 % duty of the VVT valve is unlikely (PWM, rusEFI normally <100 %).
Voltage drop: 20 mohm max/pair -> typ 10 mohm; 23 in parallel 0.4-0.9 mohm; 8 A -> 3.5-7 mV; if only half the pins share (uneven) ~10-15 mV = ~12-18 LSB (3.3 V/12 bit) on ADC channels referenced to DB ground, synchronous with injector pulses (INFERRED).

## Stack height (INFERRED from sheets)
DB bottom -> MB top = header plastic 2.54 + socket 8.5 = 11.04 nominal; standoff 11. Tolerance socket +-0.15, standoff ~+-0.1-0.2: from 0.2 mm gap to ~0.3 mm interference (board bow trivial). Pin 6.0 mm inserts fully in the 8.5 mm socket when plastic touches. Screw M3x6 into 11 mm F-F standoff from each side, 1.6 mm boards: 4.4 mm engagement ok. Nothing on MB lies under DB footprint except sockets (checked part coordinates translated into DB frame; J4, J5, U2 are outside DB outline x 99.95-225, y 49.95-126). DB bottom has no parts except J1/J2.

## Assembly / cost
- BOM note: "Solder while plugged into a motherboard's sockets so they come out straight" (fab self-order BOM). So the MB must have sockets fitted first, headers then soldered (80 joints) among SMD parts on DB top (tails protrude 3.0-1.6 = 1.4 mm).
- JLC THT hand-solder pricing (UNVERIFIED, web search results of jlcpcb.com help pages): about $0.05 per joint for pin headers (personalised services page) + ~$3.5 per order labour; MB sockets (80 joints) = ~$4 per unit if JLC does them. JLC cannot do the plugged-in-jig step for DB headers.
- Parts per unit: headers 2x$0.20 + sockets 2x$0.57 (qty 1) = $1.54; at qty 30-80 $0.40/$0.31 sockets.
- Alternatives: (a) direct solder of long pins, no sockets: saves ~$0.8-1.5 and 80 contacts but kills service/swap of the daughterboard, still needs jig; (b) board-to-board mezzanine (e.g. 2x40 0.8-1.27 mm): lower current/pin, more cost, no datasheet read here; (c) single board (what Hellen Miata boards are: one PCB, modules as sub-blocks, INFERRED from ext/hellen-miata-NA6 BOM) removes 160 contacts but loses the universal daughterboard concept.
- Alternate gold header: C2337 BOOMELE 1x40, listed gold, 3 A, 2.5 mm insulation, 6/3 mm pins, $0.16@1, 70081 stock, extended (LCSC listing only; datasheet fetch returned HTML, not read) -> candidate only.

## Sources actually read
kb/interconnect.md tables, evidence/*/pcb_pads.csv, pcb_footprints.csv, fab self-order BOMs, repo/scripts/{design,mb_common,gen_sch2,track_current}.py (grep), datasheets C2977586 and C124412 page 1 (images), lcsc.py today, VERIFICATION.md 660-690, LSU49_bosch.txt, JLC help pages via search snippets.

## Not checked
Real contact plating of delivered C2977586; mating-cycle/retention force; JLC current THT pricing on the live quote; mezzanine alternatives' datasheets; Würth 61304011821 stock; vibration test; Bosch heater cold resistance.
