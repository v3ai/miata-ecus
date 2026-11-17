# P22 small parts and hardware (LEDs, buttons, ferrite, crystals, inductors, arrays, headers, Tag-Connect, hardware)

Status: complete for the scope below (see "Not checked"). Tags: VERIFIED / INFERRED / UNVERIFIED per review brief section 5.

## Summary
1. No wrong pinout, polarity or footprint found in this scope. Checked correct: L1 and L2 land patterns, SW1/SW2 land pattern, Y1/Y101 pads, FB1 net (VDDA, pin 22), RN array pairing, TC2030 pad nets, 4 standoff positions.
2. L1 (cjiang FXL0530-2R2-M, C177247): land pattern equals the maker's recommended pattern (2.2 gap / 6.0 outer / 2.5 wide, pads 1.9 x 2.5 on PCB). The repo "could not load maker drawing" but the LCSC PDF text has it. Isat 5.6 min / 7.5 typ, Irms 6.4 min / 7.0 typ, DCR 29 mohm max, "125 C maximum total temperature". The maker's own caution list excludes "Transportation equipment (automobiles...)" and LCSC says "Consumer grade".
3. L2 (Sunlord MWSA0603S-100MT, C132141): footprint L_Sunlord_MWSA0603S equals the Sunlord table (I 2.35, J 3.7, H 3.5). Isat typ 5.2 A (30 % drop), Irms typ 4.5 A, DCR 68 mohm max, -40..+125 C incl. self heating. LCSC states "4.5A 5.5A" (not the sheet's 5.2). Isat is "typ" only: no guaranteed minimum; LMR14020 peak limit 3.8 A max leaves about 1.4 A (27 %) margin at 25 C.
4. Crystals: YXC X50328MSB2GI (C115962, JLC BASIC, stock 500k): CL 20 pF, ESR 80 ohm max (8-16 MHz), C0 5 pF max, drive 10-300 uW, -40..+85 C. Gm_crit = 4*ESR*(2*pi*f)^2*(C0+CL)^2 = 0.505 mA/V worst case versus STM32F407 Gmcritmax 1 mA/V (DS Table 32) and Gm 5 mA/V min: OK. Land pattern: maker 1.7 x 2.4 pads, 2.0 gap; board uses 2.0 x 2.4 pads on 3.7 centres (gap 1.7): fine.
5. Hand-fitted per ECU: about 260-290 solder joints (see table), roughly 60-90 minutes plus mechanical assembly (INFERRED, 15-20 s per joint including handling).
6. Main cost/simplification items: current J5 2x10 box header is named On Shore 302-S201 with no LCSC code; BOOMELE C3405 (2x10, 3A, stock 42.6k, $0.146@1 / $0.072@2000) is the same series as the C3406 used on the ordered boards. Ferrite FB1 could be the JLC BASIC BLM18PG121SN1D (C14709). LED yellow/green/blue are EXTENDED (red is BASIC).
7. Ordered boards: motherboards carry a 2x8 (16-pin) IDC header C3406 (JLC description wrongly says "2x5") and daughterboard L1 = FH CMI322513U2R2KT (500 mA, 300 mohm, 1210). Both consistent with their own rev.

## 1. Identity (kb/parts_manifest.md + live lcsc.py 2026-11-16)
| Ref | LCSC | MPN | Library | JLC stock | Price |
|---|---|---|---|---|---|
| D1,D5,D102 green | C12624 | KT-0603G | EXT | 221k | 0.0119@1 |
| D2,D103 blue | C2288 | KT-0603B | EXT | 60.9k | 0.0106 |
| D3 yellow | C2287 | KT-0603Y | EXT | 57.8k | 0.0106 |
| D4,D101 red | C2286 | KT-0603R | BASIC | 5.6M | 0.0077 |
| SW1,SW2 | C318884 | TS-1187A-B-A-B | BASIC | 841k | 0.0215 |
| FB1 | C80165 | BLM18PG221SN1D | EXT | 190k | 0.0149 |
| Y1,Y101 | C115962 | X50328MSB2GI | BASIC | 500k | 0.246@1 / 0.183@100 |
| L1 | C177247 | FXL0530-2R2-M | EXT | 49.7k | 0.1537@1 / 0.1208@50 |
| L2 | C132141 | MWSA0603S-100MT | EXT | 23.1k | 0.0948 / 0.0784@20 |
| RN1-3 | C29718 | 4D03WGJ0103T5E | BASIC | 1.03M | 0.0075 |
| J1,J2 (DB) | C2977586 | ZHOURI 2.54-1*40 | EXT | 2.6k | 0.205 |
| JD1,JD2 (MB) | C124412 | B-2200S40P-A120 | EXT | **65** (JLC and LCSC) | 0.571 |
| JP 1x3 | C49257 | BOOMELE 1x3 | EXT | 217k | 0.029 |
| shunt | C5305 | BOOMELE | EXT | 734k | 0.0099 |
| J5 ordered | C3406 | BOOMELE 2x8 | EXT | 50.8k | 0.127 |
All codes are the described parts (descriptions match). J3/J102 TC2030, J5 (current), JP4/JP5, R37 (2512), standoffs, screws, nuts have no LCSC code (self-order).

## 2. Datasheet digests
### LEDs KT-0603 (Hubei Kento, datasheets/C12624 etc.)
Abs max (G/B): IF 30 mA (Y/R 25 mA), IFP 60 mA, VR 5 V, Pd 100 mW, -40..+85 C. VF: green/blue 2.6 min - 3.1 max at 5 mA; yellow 1.8-2.4 at 10 mA; red 1.8-2.4 at 20 mA. Iv green 210-430 mcd at 5 mA. Package 1.6 x 0.8 x 0.6, recommended pad 0.7 x 0.7, gap 0.7 (board pads 0.875 x 0.95, centres 1.575 apart, KiCad std).
Usage: R2-R6 1 kohm from 3.3 V (GPIO high or +3V3). Green/blue: (3.3 - ~2.8)/1k ~ 0.3-0.7 mA (VF is at 5 mA, lower at low current; INFERRED), red/yellow (3.3-2.0)/1k ~ 1.3 mA. Safe; green/blue will be dimmer per mA but 430 mcd class at 5 mA gives indicator brightness at 0.5 mA. Not a defect; colours will look unequal. Polarity: KiCad LED_0603 pad 1 = cathode (UNVERIFIED, from memory of the KiCad library; library file not on disk); design has pad 1 = GND, pad 2 = net (design.py:195, pcb_pads.csv D1 pad1 GND). Cathode marking is the green mark on the notch end (datasheet p.2). JLC rotation not checked in preview (documented open item).
### Buttons TS-1187A-B-A-B (XKB)
Rating 50 mA / 12 V DC, contact resistance 100 mohm max, 100 000 cycles per LCSC, -30..+85 C, force 160 gf (B). Land pattern (datasheet): pads 1.0 x 0.75, x-centres 6.0, y-centres 3.75 (7.0 / 5.0 outer/inner in x; 4.5 / 3.0 in y). Board pads: 1.0 x 0.75 at x 216.5/222.5 (6.0), y 101.725/105.475 (3.75): exact. Terminals A/B shorted internally, C/D shorted: SW1 +3V3 vs BOOT0 (with R1 10k to GND: 0.33 mA), SW2 NRST vs GND (C15 100n): fine at 3.3 V. Lower temperature -30 C vs board -40 C. Note NA/NB case lids hide the buttons (UX, other audits).
### Ferrite BLM18PG221SN1D (Murata JENF243A, datasheets/C80165)
220 ohm +-25 % at 100 MHz, rated 1400 mA at 85 C / 1000 mA at 125 C, DCR 0.10 initial / 0.14 ohm max after test. Use: FB1 +3V3 -> +3V3A feeds U1 pins 21 (VREF+) and 22 (VDDA) plus C11 1u, C12 100n (pcb_nets.txt:21). Load is a few mA: drop < 1 mV, no issue. Pin numbering of the STM32 (VREF+ 21, VDDA 22) as in the net list. Alternative: BLM18PG121SN1D (same sheet: 120 ohm, 2000 mA at 85 C, DCR 0.05/0.10) is JLC BASIC C14709 ($0.014@1, $0.0072@top, stock 1.55M).
### Crystal X50328MSB2GI (YXC YSX530GA, image-only PDF, viewed)
5.0 x 3.2 x 1.2, 8 MHz, CL 20 pF, tolerance +-10/+-20 ppm, temp +-20 ppm, -40..+85 C, C0 5 pF max, DL 10-300 uW (100 typ), ESR 80 ohm max (8-16 MHz), aging 3 ppm/yr. Pads #1/#2 (no polarity). Load caps C13/C14, C119/C120 33 pF C0G/NP0: CL = 33/2 + Cstray = 16.5 + 3-5 pF = 19.5-21.5 pF (INFERRED, Cstray assumed), centred on 20 pF. Drive level not evaluated against STM32 (low-drive internal inverter, typical OK). F103 (Y101) uses the same part as FOME wideband.
### Inductors: see items 2 and 3 above; L1 table row (cjiang p.~20) FXL0530-2R2-M 2.2 uH +-20 % at 100 kHz, 29 mohm, Isat 5.6/7.5, Irms 6.4/7.0 A, SRF 25 MHz min, withstand V 30 V. Sunlord MWSA0503S-2R2MT (C408408; JLC EXT, stock 9.8k, $0.1303@1 / $0.1028@50) : 29 mohm max, Isat 7.0 typ, Irms 7.0 typ, same 5.2x5.4 body and identical land (I 1.9 / J 2.2 / H 2.5), -40..+125 C (datasheets/extra/MWSA_chipdip.pdf, Revised 2018/11/30). The repo avoided it because LCSC's page was "not found" on 2026-11-13; JLC still lists it today.
Use of L1: +12V -> +12V_F input filter into LMR14020 (draw ~0.15 A at 12 V, ~0.45 A at 8 V cranking, up to the F1 1.1 A hold): DCR drop 29 mohm x 1 A = 29 mV, P = 29 mW, no saturation issue. Orientation: no polarity. Voltage: inductors see load-dump-suppressed 35 V only through the TVS clamp; not an inductor limit.
Use of L2: buck inductor 10 uH, LMR14020 (5 V, 2 A, peak limit 3.8 A max): ripple small; Isat typ 5.2 A, hot derating unknown.
### Resistor array 4D03WGJ0103T5E (Uniroyal JLC-01-015)
4D03 convex 4-element, 3.2 x 1.6 body, 0.8 mm pitch; 1/16 W each (62.5 mW), working 50 V, overload 100 V, withstand 300 V, +-5 % (J), +-200 ppm. Circuit: element i joins pin i and pin 9-i (1-8, 2-7, 3-6, 4-5). Use: RN2 pins 1-4 gate nets, 5-8 GND (RN2: FP_G, MAINRLY_G, AC_G, FAN_G; RN3 CEL_G, TACH_G, LS7_G, pin 4 and 5 both GND = unused element shorted GND-GND, harmless; RN1 IGN_CTL 1-4, 5-8 GND). Currents < 1 mA, voltage <= 5 V: OK. Footprint pads 0.8 pitch x 0.4/0.5: ok.
### Generic family sheets (for other audits)
- Uniroyal thick film (0603WAF.. 0805W8F.. 1206W4F..., datasheet Feb 2019 V.3): 0603 1/10 W at 70 C, max working 75 V, overload 150 V, withstand 300 V; 0805 1/8 W (0 ohm 1/4 W class), 150 V / 300 V; 1206 1/4 W, 200 V / 400 V; 2512 1 W, 200 V / 500 V. Jumper (0 ohm) < 50 mohm, rated 1 A (0402/0603), 2 A (0805-2512), max overload 2 / 5 / 10 A. Range -55..+155 C. Tolerance code F = +-1 %, J = +-5 %. TCR +-100 ppm (+-200 for arrays, +-400 for 1 ohm 0603 C22936, +-800 for 0 ohm 0805).
- Samsung CL series (catalogue, 4986 lines, datasheets/txt/C1525...): temp char A = X5R -55..+85 C +-15 %, B = X7R -55..+125 C +-15 %, C = C0G; 1005/1608 parts used: CL05B104KO5NNNC 100n 16 V X7R 0402; CL10A475KO8NNNC 4.7u 16 V X5R; CL10A225KO8NNNC 2.2u 16 V X5R; CL10A105KB8NNNC 1u 50 V X5R; CL31A106KBHNNNE 10u 50 V X5R 1206; CL10C330JB8NNNC 33p 50 V C0G +-5 %. DC-bias curves are not in the catalogue text and were not read.
- Yageo CC0603KRX7R9BB104 100n 50 V X7R, FH 0603B xxx K 50 V X7R +-10 %.
- Voltage check (script work/P22.../capv.py on pcb_pads.csv): all 16 V parts (C1525, C19666, C23630, C52923) sit on nets of <= 5 V (+3V3, +5V, VCAP, WB_VDDA, AN_VBATT/AN_VIGN which are clamped to ~3.6 V by design); 50 V parts on +12V_F / DAMP. No overvoltage on any MLCC in the scope.
- X5R parts (85 C limit) are used on the 12 V input/buck (C16-C18 10u 1206, C11/C24/C25/C45/C61/C62 1u), +3V3/+5V bulk, VCAP: above 85 C they are outside tolerance (see finding).

## 3. Usage audit
### 3a pin tables
| Part | Pad -> net | Function | Result |
|---|---|---|---|
| D1 (RUN) | 1 GND (K), 2 LED_RUN_A | pad1 cathode | OK (pcb_pads.csv:182-183) |
| D4 | 1 GND, 2 LED_ERR_A | | OK |
| D5 | 1 GND, 2 PWR_LED_A (R6 1k from +3V3) | | OK |
| SW1 | 1 +3V3 (both pads), 2 BOOT0 | | OK; R1 10k pulldown |
| SW2 | 1 NRST, 2 GND | | OK |
| FB1 | 1 +3V3, 2 +3V3A | | OK |
| Y1 | 1 HSE_IN (U1.12) , 2 HSE_OUT (U1.13) | | OK (pcb_nets.txt) |
| Y101 | 1 WB_OSC_IN (U102.5), 2 WB_OSC_OUT (U102.6) | | OK |
| L1 | 1 +12V, 2 +12V_F | | OK |
| L2 | 1 BUCK_SW, 2 +5V | | OK |
| J3 TC2030 | 1 +3V3, 2 SWDIO, 3 NRST, 4 SWCLK, 5 GND, 6 nc | TC2030 ARM pinout 1 VTref 2 SWDIO 3 nRESET 4 SWCLK 5 GND 6 SWO (UNVERIFIED, from memory; Tag-Connect doc not fetched) | matches |
| J102 (bottom) | same on WB_SWDIO, WB_NRST, WB_SWCLK | hole pattern identical; mirrored on bottom as a 180 deg rotation, relative position of pin 1/2 to the single hole preserved (INFERRED from coordinates) | consistent with J3 |
### 3b footprints
All matches described above (L1, L2, SW, crystal, LED, RN).
Mounting: daughterboard H1-H4 3.2 mm NPTH at 104.5/220.5 x 54.5/121.5 (116 x 67 mm spacing); motherboard HD1-HD4 at 119/235 x 96.5/163.5 (116 x 67 spacing, cur_mb8995 pcb_footprints.csv). Same spacing: OK. Stack height: socket 8.5 +-0.15 (Ckmtw drawing) + header plastic 3.0 +-0.1 (ZHOURI drawing; pin 6.0 mating, 11.6 total) = 11.5 mm versus F-F standoff 11 mm: the header body will sit about 0.5 mm above the socket top, pins engage about 5.5 of 6 mm (INFERRED). Works; a 12 mm standoff would NOT.
### 3c stress
LEDs: 1.3 mA max (3.3 V/1k) vs 25-30 mA: no stress. Buttons: 3.3 V, < 1 mA vs 12 V 50 mA. Ferrite: < 10 mA vs 1 A. L1: 14.4 V / ~1 A max. 24 V jump start: all parts see only rail voltages behind the TVS/PTC. Reverse battery: L1 is behind D7 (SS34)? Not analysed (power audit). Temperature: SW -30..+85 C, LEDs -40..+85 C, crystal -40..+85 C are all rated 85 C maximum; with 85 C cabin air plus self heating inside the stock case the board runs above these (INFERRED), same issue as the documented microSD socket.
Header current: J1/J2 pins (ZHOURI) 2.5 A per pin; Ckmtw socket drawing says "Current Rate 3 Amp" (LCSC text "1A" is the 1 A contact-resistance test current). VBAT_IN uses 2 pins (J1.1/J1.2, 5-6 A capacity), heater return 2+2 pins, GND 23 pins: ok vs P04 heater figure 4.5 A peak / 2.2 A RMS. 1x3 headers 3 A, box header C3406 1 A (ordered 2x8, AUX_VBAT 3 pins into F4-protected 1.1 A).
### 3d external parts
Crystal load caps present and in range. VDDA: C11 1u + C12 100n after ferrite present; VCAP C9/C10 2.2u (X5R 16 V, VCAP at 1.2 V) present. BOOT0 pull-down R1 present. NRST C15 100n.
### 3e reference compare
Not repeated: crystals/VDDA were taken from AN2867 per repo comment; no deviations seen.

## 4. Cost and simplification
- R37 (2512 1k 1 W, Yageo RC2512JK-071KL, self-order, optional, only fitted after a COP conversion): 0.2 W at 14.4 V, 0.58 W at 24 V, ~1.2 W at 35 V for the load-dump pulse. A JLC-placeable equal exists: Uniroyal 25121WF1001T4E C54315, EXT, $0.034@1, stock 55k (1 W, 200 V, +-1 %). Only matters if the part is fitted by default.
- 0 ohm links R28/R30 (0805, C17477 BASIC, rated 2 A): "not fitted" options, R29 fitted. Fine.
- J5 2x10: use BOOMELE C3405 (or same as ordered C3406's series).
- FB1: BLM18PG121SN1D C14709 basic (saves one extended-part setup fee, UNVERIFIED assumed ~$3 per distinct extended part per order). Unit saving < $0.01.
- LEDs: only red is BASIC (KT-0603R C2286; white KT-0603W C2290 basic); green/blue/yellow are extended. Making all status LEDs red (or red+white) would remove 3 extended part types per order; UX cost only.
- Four LEDs + 4 resistors are not needed electrically: they are diagnostics. Remove-for-free candidates are not recommended (cheap, useful).
- L1 input filter: could be a cheaper 1210 inductor of >= 1.5 A; saving ~$0.05; not worth risk.
- Ordered rev: L1 CMI322513U2R2KT 500 mA is at the limit of the 0.5 A PTC hold when the buck draws about 0.45 A at 8 V cranking; Irms rating 500 mA (LCSC description) with DCR 0.3 ohm: 75 mW at 0.5 A. Acceptable, small margin; no board change possible by hand without desoldering (can swap by hand later).

## 5. Hand-fitted items and time per ECU (INFERRED, 15-20 s per through-hole joint, 1989-95 motherboard)
| Item | Joints |
|---|---|
| J1, J2 1x40 headers on daughterboard (bottom, soldered while plugged) | 80 |
| JD1, JD2 sockets on motherboard | 80 |
| Harness header J1 (48 pins 1989-95; 76 / 72 on later) | 48-76 |
| JP1-3,6 (1x3) + JP4,JP5 (1x2) | 16 |
| J5 box header | 20 |
| U2 MAP sensor (6 leads, 2 M3 screws + nuts) | 6 |
| J2 JST wideband (8 pins) | 8 |
| total joints | about 258-290 |
Mechanical: 4 standoffs, 8 M3x6, 2 M3x10, 2 nuts, 6 shunts. Estimate 60-90 min per ECU (soldering 70-100 min at the high end), plus test.
Risk note: JP1/JP2 (INJ3/INJ4 pair/seq), JP3, JP6 are open-top shunts on 2.54 mm pins inside a car; a lost shunt leaves a harness injector wire unconnected (JP1 pin 3 = HARN_2Y; mb_na6.py:138-146). Shunts have no retention (UNVERIFIED vibration behaviour).

## Sources actually read
the review brief; kb/parts_manifest.md; datasheets C177247 (cjiang FXL, p.4-5 dimensions, table FXL0530), extra/MWSA_chipdip.pdf (text), C12624/C2288/C2287/C2286 text and page 2 image, C318884 page image, C80165 text, C115962 page image, C12345 Table 32, C29718 text, C25804 text (sections 6-7), C124412 page image, C2977586 text, C3406 text; repo/scripts/design.py 170-236, 280-314, mb_na6.py 138-232, order_bom.py 19-50; evidence/cur_db pcb_pads.csv, pcb_footprints.csv, pcb_nets.txt; evidence/cur_mb8995, ord_mb8993 footprints/pads; live lcsc.py lookups listed above.

## Not checked
- Tag-Connect official pinout and footprint dimensions (not fetched).
- Samsung DC-bias derating curves (not in catalogue text) and X7R alternatives for the 10u 50 V 1206 (no hit in first search).
- On Shore 302-S201 datasheet (no LCSC copy; pin-count meaning of "S201" from memory).
- JLC placement rotation of polarised parts (LEDs).
- Layer images around L1/L2/Y1 (loop areas), not viewed (not checked).
- Reverse-battery / load-dump path on L1 (power audits).
