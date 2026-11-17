# P20 - MAP sensor U2 MPX5700AP (every motherboard), C1-C3, V5_SENS (U3), signal path

## Summary
1. Pinout / mirror check PASSES. Pad 1 (notched lead, Vout) = IN_MAP, 2 = GND, 3 = V5_SENS, 4-6 unconnected, on all 11 boards (VERIFIED, pcb_pads.csv). Orientation is a pure rotation (90 deg) of the NXP top view of case 867B (pin 1 left, leads toward viewer), and equals the footprint of rusEFI Hellen boards' hand-fit MPX4_MAP rotated 180 deg (VERIFIED by coordinates). Residual risk: the 867B drawing's view direction is by third-angle projection inference, so a first-article check with a real sensor (continuity pin 3 vs 5 V, pin 2 vs GND) is still wise before first power.
2. Ordered rev 0.7/0.9/0.11 boards have identical U2/C1-C3 placement, nets and values (VERIFIED ord_mb8993, ord_mb9495, ord_mb9697 pcb_pads.csv/pcb_footprints.csv).
3. Decoupling = NXP Figure 4 exactly: 1 uF + 10 nF on Vs, 470 pF on Vout (C1 C15849, C2 C57112, C3 C1620). OK.
4. Accuracy: datasheet max error +-2.5 % VFSS (VFSS 4.5 V) = +-0.1125 V = +-17.6 kPa over 0-85 C, +-50 % of a 35 kPa idle reading and +-17.6 % at 100 kPa. The absolute offset spec alone (0.184-0.409 V) spans +-17.6 kPa, i.e. the whole budget. Typical error is NOT specified by NXP (UNVERIFIED that it is ~1 %).
5. The sensor is badly sized for an NA Miata: 100 kPa gives only 0.84 V (0.54 V at the ADC), idle 0.43 V. Resolution is fine (0.196 kPa per 12-bit LSB) but absolute accuracy is the weakness.
6. Cost: sensor is $27.49 @30 (JLC extended, stock 155) = the dearest single part. MPX4250AP (+-3.5 kPa) has 0 stock at JLC. The only in-stock analog absolute alternative found at JLC is MPXHZ6400AC6T1 C511770 (SMD, 739 in stock, $10.45 @30, $9.49 @100).
7. NRND claim: conflicting. A search summary of ST pages said the ST Japanese page shows NRND with FXPS7550A4S suggested, the ST English page and estore show Active (I could not fetch st.com myself: UNVERIFIED either way). NXP moving MEMS sensors to ST on 2026-02-02 per NXP JP page (search summary, UNVERIFIED).
8. Hose advice in INSTALL.md is consistent with the 867B drawing (barb OD 4.62-4.93 mm) and AN1513 (1/8 in ID hose per archived 2005 copy, via search summary).
9. Low risk: pad drill 0.8128 mm vs lead width 0.68-0.84 mm (Hellen boards use the same; Hellen's ibom 867B footprint uses 1.1 mm).

## Datasheet digest (datasheets/C90152_MPX5700AP.pdf = NXP Rev 10, 10/2012; also current ST-branded 2026 copy exists but not fetchable here)
- Function: integrated absolute MAP sensor, 15-700 kPa, ratiometric. Vout = Vs*(0.0012858*P + 0.04) +-Error, Vs 5.0 (p.3 Fig 2).
- Table 1 (Vs 5.0, 25 C): Vs 4.75/5.0/5.25 V; Io 7 typ 10 max mA; Voff absolute (0-85C) 0.184..0.409 V; VFSO 4.587/4.7/4.813; VFSS 4.5 V typ; accuracy +-2.5 %VFSS (0-85 C); sensitivity 6.4 mV/kPa; response 1 ms; Io+ at full scale 0.1 mA typ; warm-up 20 ms.
- Table 2 abs max: P1max 2800 kPa; Tstg and TA -40..+125 C. NO Vs absolute maximum is given. Accuracy only specified 0-85 C (no multiplier for -40/+125, unlike MPX4250A which has x3).
- Pins (case 867B-04 p.8 Style 1): 1 Vout, 2 GND, 3 VCC, 4 V1, 5 V2, 6 VEX; Fig 1: pins 4,5,6 are no connects.
- Recommended circuit (Fig 4): 1.0 uF and 0.01 uF Vs to GND, 470 pF Vout to GND.
- Package (p.7, 867B-04): lead pitch 2.54, lead width 0.68-0.84, thickness 0.36-0.41, hole spacing 23.11 BSC, mounting holes dia 3.89-4.04, barb OD 4.62-4.93, barb length 10.67-11.18, length 29.08-29.85, width 17.40-18.16, leads exposed 5.59-6.10 beyond seating-plane reference, "PIN 1" notch at left lead. Plan view in the drawing: leads at bottom, pin 1 left ... 6 right, barb offset toward pin 6.

## Pinout in the flat, leads-bent attitude (task's high-stakes check)
- 867B drawing is third-angle (ASME Y14.5-1994, p.8 note 2): the seating plane T lies at the left of the side view, i.e. the far side from the viewer of the plan view, so the plan view is seen from the side opposite the seating plane = the top when the part lies on its seating face with leads bent down. Therefore, viewed from above with leads toward the viewer, pin 1 is on the left. (INFERRED from projection convention.)
- Footprint (repo/scripts/mk_map_fp.py): pins at x = -6.35+2.54k, y=16.51 local (pin 1 left, leads toward viewer, body toward -y, barb toward +x = pin 6 side). Matches the drawing.
- Placement: U2 at (224,192) rot 90, top side, all boards. KiCad rot 90 maps local (x,y) -> (y,-x) + origin, giving pad 1 at (240.51,198.35), pad 6 at (240.51,185.65): matches pcb_pads.csv (VERIFIED by computation). Pure rotation, no flip.
- Independent cross-check: ext/hellen-miata-NA6/hellen64_NA6_94.kicad_pcb:3925-3943 (module "MPX4_MAP", pads at x -6.35..+6.35, y 16.51, drill 0.8128, pad1 VOUT/IN_MAP3, 2 GND, 3 +5VA, 4-6 NC) is identical to this repo footprint. Hellen's ibom 867B.kicad_mod has pin 1 at -y, body at +x: rotate 180 deg gives the repo layout. (VERIFIED by reading files.) Hellen NB1/NB2 boards share the footprint.
- Schematic: mb_common.py:66-71 maps {1: IN_MAP, 2: GND, 3: V5_SENS, 4-6 none}; C1/C2 V5_SENS-GND, C3 IN_MAP-GND.

## Pin table U2 (identical on cur_mb8995, cur_mb9697, cur_mb9900, cur_mb0105, ord_mb8993, ord_mb9495, ord_mb9697 (ord 9900/0105 same coordinates per pcb_pads grep))
| pad | net | datasheet | verdict |
|---|---|---|---|
| 1 | IN_MAP (C3.1, JD2.5) | Vout | OK |
| 2 | GND | GND | OK |
| 3 | V5_SENS (C1.1, C2.1, JD2.1) | Vs | OK |
| 4,5,6 | none | no connect | OK |
| mount | none (plated 4.0/3.3) | - | OK |
Daughterboard: JD2.1 -> J2.1 -> U3 (TLS115B0EJ) pin 1 V5_SENS with C25 1 uF; J2.5 IN_MAP -> R29 5.6k -> AN_MAP (R30 10k to GND, D20 BAT54WS to +3V3, C37 10n) -> U1 PA5 (evidence/cur_db/pcb_nets.txt:140,177,218).

## Electrical
- Vs from V5_SENS tracker (P07): 4.815-5.185 V worst case, inside 4.75-5.25. V5_SENS is on the motherboard only (U2, C1, C2) and not on a harness pin (VERIFIED nets), IN_MAP also only goes to the daughterboard: no harness fault can reach the sensor pins; reverse battery / jump start / load dump act on the tracker (P07), not on U2.
- Output load: R29+R30 = 15.6 kOhm, ratio 0.641. Load current = Vout/15.6k: 54 uA at 100 kPa (0.84 V), 27 uA at 35 kPa, 0.30 mA at 700 kPa. It stays below the 0.1 mA typical source current up to Vout 1.56 V = 211 kPa absolute. So the repo's "divider load above typical source current" is moot for a naturally aspirated car and for boost up to ~110 kPa gauge (INFERRED, computed). R29 source impedance with C3 470 p: corner 1/(2pi*5.6k*(470p+10n)) approx 2.7 kHz with C37; fine.
- Thermal: 7-10 mA from 5 V = 50 mW, negligible. Cabin air 85 C is the edge of the accuracy-specified range (0-85 C); above 85 C the NXP MPX5700 sheet gives no accuracy number (MPX4250A multiplies the error by 3 at 125 C, and by 3 at -40 C: Rev 8 Fig 8). The box sits in the car cabin; a -40..0 C cold start is outside the 2.5 % spec.
- Firmware: miata_board.cpp:64-72 sets MT_CUSTOM 0.2 V at 0 kPa, 4.70 V at 700 kPa = datasheet transfer function at 5 V (VERIFIED). Not set: useFixedBaroCorrFromMap (rusefi_config.txt:1242; the option reads MAP at start-up as barometric pressure). 

## Accuracy for speed-density (computed)
VFSS 4.5 V; 2.5 % = 0.1125 V; sensitivity 6.43 mV/kPa (5 V * 0.0012858) => +-17.5 kPa. With a typical VFSS: nothing more specified.
| sensor | range | VFSS | sens. mV/kPa | max err %VFSS | err kPa | at 35 kPa | at 100 kPa | LSB at 12-bit through 0.641 divider |
|---|---|---|---|---|---|---|---|---|
| MPX5700AP | 15-700 | 4.5 | 6.43 | 2.5 | +-17.5 | +-50 % | +-17.5 % | 0.196 kPa |
| MPX4250AP | 20-250 | 4.692 | 20 (5.1 V) | 1.5 | +-3.5 | +-10 % | +-3.5 % | 0.063 kPa |
| MPXH(Z)6400A | 20-400 | 4.6 | 12.1 | 1.5 | +-5.7 | +-16 % | +-5.7 % | 0.104 kPa |
(MPX4250A: Rev 8 Table 2 read from datasheets/extra/MPX4250A_rev8_components-ru.pdf; MPXH6400A Rev 6 Table 3 read from datasheets/extra/MPXH6400A_rev6_components-ru.pdf; both copies are third-party hosts of the NXP PDF, ok for numbers. The HZ variant sold at JLC has its own datasheet which I did not read.)
Fuel effect: at 35 kPa a 1 kPa MAP error is 2.9 % in fuelling; at 100 kPa 1 %. Interpretation: the error is dominated by a fixed offset/span of the individual unit at 25 C (offset spread 0.184-0.409 V = full budget), which a tune on that car absorbs, plus temperature and hysteresis terms (NXP does not split the band: UNVERIFIED that these are about +-1 %VFSS = 4 kPa). A base map shipped for all cars could be ~+-50 % rich/lean at idle for an unlucky unit; closed-loop lambda corrects part (needs +-25 % trim range). A baro-at-key-on correction does not remove a span error at 35 kPa.
Fit to NA Miata: 100 kPa needs only 0.84 V of the 0.2-4.7 V span (12 %); the 700 kPa range is a waste unless boost is intended. Stock-turbo cars would use 250 kPa class.

## Alternatives and market
| part | LCSC | JLC today (stock, @30, @100, type) | notes |
|---|---|---|---|
| MPX5700AP (current) | C90152 | 155, $27.49, n/a (tiers end 30-36), extended, LCSC $27.75 | through-hole, hand fit |
| MPX4250AP | C2802676 | 0, $22.1-23.2, extended | no stock at JLC; Digikey/Mouser not checked; same case & pinout, 1.5 % |
| MPX4115AP | C3259058 | 0 | 15-115 kPa class best matched to NA, no stock |
| MPXHZ6400AC6T1 | C511770 | 739, $10.45, $9.49, extended; LCSC 644 | SMD SSOP-8 with top port; Hellen's NA6 BOM uses this code (U7); pins 2 VS, 3 GND, 4 VOUT, 1,5-8 DNC (Rev 6 Table 1); Vs 4.64-5.36, Io+ max 0.5 mA, Pmax 1600 kPa; hose needs a different arrangement; JLC can place it, saves hand-fit and ~$17 |
| MPXH6400AC6T1 | C2828031 | 0 | SSOP-8 7.4 mm |
| MPX5700DP/GP | C410772 / C2977767 | 194 / 187, $12.84 / $24.6 | differential/gauge, not absolute: not drop-in (DP stock $12.8 but needs 2 ports; ambient-referenced) |
| KP234 | C3239348 | 2, $4.9 | Infineon analog absolute 40-115 kPa SMD, stock 2: unusable |
| digital I2C (BMP/LPS22/MS5611/MPL3115) | e.g. C2827824 | stock but I2C | rusEFI has no external I2C MAP: not an alternative |
Not found in JLC library: any stocked cheap analog-output absolute sensor besides the NXP ones; search of XGZP, MPS20N0040, "pressure sensor absolute" returned nothing in stock (a CFSensor XGZP6886A is advertised by its maker as an MPX5700AP alternative, not stocked at JLC, not read).
What others fit (VERIFIED from ext/ BOMs): Hellen NA6/NB1/NB2: on-board MPXH6400A SSOP (U7, C511770) plus optional hand-fit MPX4_MAP footprint (same pads as this board; BOM line has no LCSC, user supplies MPX4250AP); Speeduino v0.3/0.4 and its Miata NA6 PNP: MPX4250AP (Digikey MPX4250AP-ND, speeduino-hardware BOMs). MSPNP: not checked (UNVERIFIED).

## NRND / supply
- repo VERIFICATION.md:1112 says NRND at ST, LCSC 191 / Mouser 74 on 2026-10-31; today LCSC/JLC stock 155 (VERIFIED, tools/lcsc.py). Web summaries today disagree on the ST status (see summary item 7); I could not confirm. Treat as "unconfirmed, supply thin". Digikey shows 52-week lead time (search summary, UNVERIFIED).

## Hose
- Drawing p.7: barb OD 4.62-4.93 mm, length 10.67-11.18. INSTALL.md:274 "3-4 mm ID, NXP specifies 1/8 in (3 mm) for the 4.9 mm barb": AN1513 (archived 2005) says 1/8 in ID, 1/16 in wall, clamps recommended (search summary of dtsheet.com copy; the repo's link AN1513 was not opened by me). The 4 mm ID figure stretches 23 % over 4.93 mm; 3 mm stretches 64 %: silicone is fine, PVC vacuum hose may split. Statement "the barb is plastic" correct (epoxy case). OK, no change needed beyond adding a clamp/cable tie (already).

## Sources actually read
the review brief; datasheets/C90152_MPX5700AP.pdf text + pages 6-8 images; datasheets/extra/MPXH6400A_rev6_components-ru.pdf and MPX4250A_rev8_components-ru.pdf text; repo/scripts/mk_map_fp.py, mb_common.py:55-72, mb_na6.py:261-266, design.py grep; evidence/*/pcb_pads.csv, pcb_footprints.csv, pcb_nets.txt (cur_mb8995, cur_db); ext/hellen-miata-NA6 pcb 3915-3950, ext/hellen-one ibom-data/867B.kicad_mod; Hellen/Speeduino BOM greps; kb/parts/P07, P12 (cited); firmware miata_board.cpp:60-72; tools/lcsc.py searches; web searches (secondary).

## Not checked
st.com current datasheet / product status (fetch failed); NXP direct download (blocked); MPXHZ6400A (HZ) own datasheet and port dimensions; AN1513 text; layer images around U2 (loop area, copper) not viewed; MSPNP's sensor; Digikey/Mouser price of MPX4250AP; physical lead/hole fit; whether the sensor body clears the case/other parts.
