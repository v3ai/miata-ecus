# P13 - Digital and trigger inputs (hall crank/cam, 12 V switch inputs, flex / nitrous, VR conditioner U9)

STATUS: complete (partial; see "Not checked").

## Summary
1. No wiring / pinout / polarity error found in this scope on CURRENT (rev 0.10) or ORDERED (rev 0.9) boards. U9 LM2903DR pads 1-8, D35 BAT54A, D15-18/D36/D37 BAT54S, 1N4148WS clamps, PE7-PE13 / PC6 / PC7 pin numbers all verified (PCB pads, design.py, TI/onsemi/JSMSEMI datasheets).
2. Hall inputs: 1k pull-up (from V5_EXT through one cathode of D35) + 4.7k series + 1n + 1N4148WS clamp to +3V3. Pin high level is clamped to about 3.85 V, low level = sensor Vol. Edge delay 3-7 us vs 208 us tooth period at 4.8 kHz: negligible (about 0.15 deg skew rising/falling at 8000 rpm).
3. Weakest point: 1k pull-up needs the sensor to sink about 4.7 mA with Vol below 0.99 V (ST VIH/VIL CMOS limits). Sensor sink data not found (UNVERIFIED for NA CAS and NB crank/cam); Hellen uses 4.7k.
4. 12 V switch inputs (22k/10k): guaranteed-high needs about 7.4 V at the harness (0.7 VDD = 2.31 V x 3.2); at 6 V cranking the pin sees 1.875 V (only above the by-design 1.785 V). Guaranteed low <= 3.17 V. Low severity (these signals are not cranking-critical).
5. Fault survival is fine except stacked abnormal cases: R61/R63 4.7k 0603 = 86 mW at 24 V (limit about 82 mW at 85 C), 206 mW at 35 V; D35 reverse stress 30 V = its absolute maximum in a short to a 35 V load-dumped battery.
6. VR stage works as designed: hysteresis 29 mV with a sensor attached (295 mV with nothing attached), thresholds about +-15 mV, common mode 1.65 V (limit Vcc-1.5 = 3.5 V; Vcc-2 = 3.0 V hot).
7. VR conditioner (U9 + 26 passives, 27 parts) is removable without affecting any supported car: about $0.22 BOM per unit at qty 50 plus one extended-part fee (C7549, $3 per order, unique to U9) and 27 placements; frees J5 pins 7-10 and PE12/PE13. Keep only if "custom VR trigger wheel" is a sold feature.
8. Ordered rev 0.9 daughterboard: identical hall / SW / VR circuits; R139/R140 + D36/D37 are the UART series resistors / clamps there (no flex / N2O inputs).

## 1. Parts (CURRENT db rev 0.10; ordered rev 0.9 identical except R139/R140/D36/D37/C72/C73)
Source: repo/scripts/design.py lines 402-507; evidence/cur_db and ord_db pcb_pads.csv (work/P13-.../cmp.py output).
| Function | Parts |
|---|---|
| Hall 1/2 | R62/R64 1k 0603 (C21190) pull-up from V5_H1/V5_H2; R61/R63 4.7k 0603 (C23162) series; C51/C52 1n 0402; D13/D14 1N4148WS (C2128) pad1 (cathode) +3V3, pad2 (anode) HALL; D35 BAT54A (C916423, JSMSEMI) pads 1,2 = cathodes V5_H1/V5_H2, pad 3 = common anode V5_EXT |
| SW1-3 | R65/67/69 22k, R66/68/70 10k (0402), C53-55 10n, D27-29 1N4148WS to +3V3 |
| Flex / N2O | R139/R140 10k 0603 series, D36/D37 BAT54S (pad1 GND, pad2 +3V3, pad3 node), C72 1n, C73 10n; motherboard R35 4.7k V5_EXT->IN_FLEX, R36 10k IN_N2O->GND |
| VR | U9 LM2903DR; R51-54/56-59 5.1k 0805; R55/R60 10k; C48/C49 1n 0805; C50 100n; D15-18 BAT54S; R73-76 100k; R77/78 1M; R79/80 10k; C60 100n |
Motherboards (all four current): R20/R21/R22 4.7k VBAT_IN->IN_SW1/2/3 NOT FITTED (JLC BOM blank), R35, R36 fitted; 1989-95 also R27/R28/R29 (AUX1 analog, other audit). Harness: 89-95 SW1 1M (VSS), SW2 1Q (A/C pressure), SW3 1V (clutch); hall 2E/2G; 96-97 4F/4G (CAS), SW 1M/1K/1L; NB1 2J crank, 2H cam, SW 2D/1P/3I; NB2 3Y/3V.

## 2. Datasheet digests
LM2903DR (TI SLCS005X, datasheets/txt/C7549_LM2903DR.txt): Vcc max 36 V; VID +-36 V; input voltage -0.3..36 V; output 36 V; Tj 150 C; theta-JA SOIC-8 about 97-130 C/W (D pkg, not extracted for this variant). LM2903 electrical (Vcc 5 V): VIO 2 typ / 7 max 25 C, 15 max -40..125 C; IIO 5/50 nA (200 hot); IIB -25/-250 nA (-500 hot); VICR 0..Vcc-1.5 (Vcc-2 over temp); VOL 150/400 mV @4 mA, 700 mV hot; IOL >= 6 mA; ICC 0.8/1 mA; response 1.3 us (100 mV step, 5 mV overdrive). Pin table SOIC-8: 1 1OUT, 2 1IN-, 3 1IN+, 4 GND, 5 2IN+, 6 2IN-, 7 2OUT, 8 VCC. No decoupling requirement stated; C50 100n fitted.
BAT54S onsemi (C19726): VR 30 V, IF 200 mA, VF 0.29-0.32 V @1 mA, 0.35-0.40 @10 mA, 0.8 max @100 mA; SOT-23 pin 1 anode, 2 cathode, 3 cathode/anode (series pair). BAT54A JSMSEMI (C916423, p.1 picture): cathodes 1 and 2, common anode 3, VR 30 V, IF 200 mA, IFSM 600 mA. 1N4148WS (C2128): 100 V, 150 mA, SOD-323 pin 1 cathode.
STM32F407 (DS8626 Table 48): VIL max 0.3 VDD (0.99 V) [tested] / 0.3VDD-0.04 [design]; VIH min 0.7 VDD (2.31 V) [tested] / 0.45VDD+0.3 = 1.785 V [design]; FT pins 5.5 V max, leakage 3 uA at 5 V.

## 3. Usage audit
### 3a/b. Pin tables (VERIFIED: pcb_pads.csv cur_db and ord_db, design.py 402-452, sch pin names)
U9: 1 VR2_OUT (1OUT OK), 2 VR2_INN (1IN- OK), 3 VR2_INP (1IN+ OK), 4 GND OK, 5 VR1_INP (2IN+ OK), 6 VR1_INN (2IN- OK), 7 VR1_OUT (2OUT OK), 8 +5V OK. Footprint SOIC-8 3.9x4.9 P1.27: pads 1.95x0.6 mm, 4.95 mm centre span, pin 1 at (164.525,110.395) = pad 1: matches standard land pattern. Placement dense (DRC only courtyard overlaps, no electrical items in scope).
D35 BAT54A: pad3 = V5_EXT (common anode, OK), pads 1/2 = V5_H1/V5_H2 cathodes through R62/R64: a wire shorted to battery reverse-biases D35: OK.
D15-18, D36, D37 BAT54S: pad1 GND (anode of lower diode), pad2 +5V (D36/D37: +3V3) cathode of upper diode, pad3 node: clamps node to -Vf .. rail+Vf: OK.
D13/D14/D27-29 1N4148WS: pad1 (cathode) +3V3, pad2 (anode) signal: clamps above 3.3+Vf: OK.
VR polarity: harness N -> R51/R52 -> IN+ ; harness P -> R53/R54 -> IN-; output high when N above P (R77 1M OUT->IN+ positive feedback: OK). Header: J5.7 VR1_P, J5.8 VR1_N, J5.9 VR2_P, J5.10 VR2_N; JD2 19-22 match J2 19-22 (interconnect.md).
MCU: LQFP100 pin 38 PE7 HALL1, 39 PE8 HALL2, 40-42 PE9-11 SW1-3, 43 PE12 VR2_OUT, 44 PE13 VR1_OUT, 63 PC6 FLEX, 64 PC7 N2O (design.py 152-158; F407 pin numbers consistent). EXTI line 7 shared PE7/PC7: PC7 polled (documented).
### 3c. Stress / thresholds (computed, work/.../calc.py)
- Hall, wire shorted to battery: via R61 4.7k into the clamp: 2.2 mA at 14.4 V (24 mW), 4.3 mA / 86 mW at 24 V, 6.6 mA / 206 mW at 35 V. 0603 4.7k rated 100 mW at 70 C, about 82 mW at 85 C (linear to 0 at 155 C, INFERRED from the Uniroyal rating on LCSC). Pull-up path blocked by D35: reverse 14.4-5 = 9.4 V, 24 V -> 19 V, 35 V -> 30 V (= limit).
- Hall, normal: high level = clamp = 3.3 + Vf(1N4148WS, 0.2 mA) = about 3.85 V (> VIH 2.31); 0.19 mA per channel into +3V3 whenever high. Low: pull-up current (5-0.3)/1k = 4.7 mA through sensor; MCU needs Vol < 0.99 V.
- Hall timing: tau 4.8 us (fall) / 3.3 us (rise to 2.31 V) vs 208 us tooth at 4.8 kHz (36 teeth x 8000/60; tooth count UNVERIFIED, from memory) and 3.7 ms at 267 Hz (NA CAS 4 slits per cam rev). OK.
- SW inputs: divider 10/32; pin = 1.875 V at 6 V, 2.31 V at 7.4 V, 2.81 V at 9 V, clamped about 3.85 V above 12.3 V. 12 V: 0.37 mA through D27; 24 V: 18 mW in 22k; 35 V: 44 mW (0402 62.5 mW OK). Filter 22k||10k x 10 nF = 69 us: fine for VSS (about 170 Hz max) .
- Flex / N2O: 10k + 1n = 10 us (flex 50-150 Hz): OK; N2O 100 us. Flex: pull-up 4.7k to 5 V -> pin sits at about 3.6 V (clamp), 0.14 mA continuous; shorted to 14.4 V: 1.1 mA into +3V3 and about 2 mA back through R35 into V5_EXT (small).
- VR: hysteresis 28.6 mV (Rc 100 ohm) / 29.8 mV (1k) / 34.7 mV (5k); 295 mV open. VR amplitude: 100 V peak -> about 4.6 mA loop current through 20.4k, 108 mW peak in each 5.1k 0805 (125 mW at 70 C): brief pulses only; clamp current into +5V rail. Negative clamp holds -0.30..-0.37 V vs the -0.3 V input limit (marginal, current limited by 5.1k, not a failure).
### 3d. Required externals
LM2903: open-collector output pull-ups R55/R60 present (10k to +3V3; output max 36 V so mixed 3.3 V logic is fine); +5V decoupling C50. Unused pins: none.
### 3e. References
ext/hellen-miata-NB2 netlist: IN_CAM has a 4.7k (R3, pull-up to 5 V) and routes through the Hellen "input" module (4.7k arrays, 1n/10n, SRV05-4 TVS, 680k/10k). The Hellen dinput4 module uses 74HC2G17 Schmitt buffers. This design is simpler (diode clamps, no Schmitt); it relies on MCU hysteresis (0.1 VDD).

## 4. Real-world sensor behaviour (mostly UNVERIFIED)
- NA 1990-93 CAS: optical, two slit rings (4 = crank angle, 2 = cam) per community tuning guides (diyautotune search result); miata.net pinout sheet reads "Cam Angle Sensor - 5 volts (key on)" (search snippet only, UNVERIFIED), which fits the repo's 5 V sensor reference on 2K; output assumed open collector (repo research pinouts_9605.md 'high' confidence, Hellen fits 4.7k pull-up).
- 1996-97 CAS and NB crank (BP4W-18-221) / cam: 3-wire Hall, 12 V fed, open collector (repo research; not independently verified; sink capability not found).
- Switch polarities (VSS, A/C, clutch): not verified; repo leaves the 12 V pull-up options R20-R22 unfitted: a signal that switches to ground reads permanently low until the owner fits the pull-up (UX item: needs a per-year decision).

## 5. Cost / removal
VR conditioner BOM at qty 50 (live lookup 2026-11-16): U9 C7549 $0.073 (EXTENDED, unique to U9), D15-18 4 x $0.0145 (C19726 remains needed for D36/D37 so no extended-part saving), R51-54/56-59 8 x $0.0055, R55/R60 2 x $0.002, R73-76 4 x $0.001, R77/78 2 x $0.0012, R79/80 2 x $0.0015, C48/C49 2 x $0.0082, C50 $0.01, C60 $0.004: sum about $0.22, plus about $3 extended-part fee per order, 27 placements, and about 15 x 12 mm of board next to the inputs. No supported Miata has a VR sensor (repo research and pinout files); the harness pins VR1/VR2 appear only on the AUX header J5 7-10.
Alternates (datasheets NOT read, so not recommended): LM2903DR2G onsemi C57474 (extended, -40..105 C, $0.057 at 50); LM393DR2G C7955 is BASIC but 0..70 C (below the 85 C cabin requirement). Saving is under $0.02, not worth a datasheet review.
Free removals elsewhere in scope: none (each clamp / filter has a documented reason).

## Sources actually read
design.py 395-515; mb_common.py 55-160; mb_na6/na8/na96/nb1 harness maps; evidence cur_db/ord_db pcb_pads, footprints, drc rpt, cur_mb* pcb_nets; kb/interconnect.md; datasheets C7549 (pp. electrical, pin), C19726, C916423 (p.1 image), STM32F407 Table 48; lcsc.py lookups (C7549, C19726, C916423, C2128 and resistors/caps); ext hellen-miata-NB2 netlist, hellen input / dinput4 BOMs; one web search (NA CAS).

## Not checked
Real sensor datasheets (BP4W hall, NA optical CAS output stage); switch polarities per year; layer-image review (loop area, decoupling distance of C50/U9); ngspice transient of the VR stage; the +3V3 / +5V rails' ability to absorb clamp current (other audits: P05/P08); onsemi / ST LM2903 alternates.
