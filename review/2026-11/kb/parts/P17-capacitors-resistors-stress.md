# P17 - Capacitors and resistors: stress, derating, tolerance, extended-vs-basic

STATUS: complete (economical pass). Scripts and join table: work/P17-capacitors-resistors-stress/ (join.py -> join.csv, chk.py). Tags VERIFIED / INFERRED / UNVERIFIED per review brief section 5.

## Summary
1. HEADLINE ERROR (VERIFIED): R110 (wideband pump-current sense resistor, nets LSU_RT-LSU_IP, value "62") is placed with LCSC C25341 = 1206W4F620LT5E = **0.62 ohm**, not 62 ohm. Same on CURRENT rev 0.10 and ORDERED rev 0.9 (fab BOM line "62,R110,R_1206_3216Metric,C25341"). Wideband current measurement would be 100x too small. Fix: C17971 1206W4F620JT5E (62 ohm, 1206, extended, $0.0053@1).
2. Script check of all 551 C/R/RN lines on 11 boards: capacitance / resistance in the live LCSC description equals the schematic value for every line except R110 (chk.py). The "R28/R20 mismatch" lines are only text-value strings on motherboards (0 ohm / 4.7k parts correct).
3. Capacitor voltage ratings: all rail caps >=50 V on the +12V / +12V_F nodes (clamped about 39 V by D12), 25 V on +5V bulk, 16 V on 3.3 V / 5 V / divided nodes (>=3x). One exception on a harness node: C102 (100n 16 V X7R 0402) sits directly on the LSU_UN wire (14.4 V when shorted to the heater feed = 90 % of rating; 24 V jump start = 150 %).
4. Resistor power: nothing exceeds 50 % in normal use. Sustained-fault outliers: motherboard R20-R22 (4.7k 0603 to VBAT_IN, 122 % at 24 V jump start, switch closed), R15-R18 (100 ohm 1206, 85 % of 250 mW into a short to GND, about 100 % derated at 85 C). R144-R147 3.3k 1206 are fine (70 % at 24 V).
5. C0G where needed: HSE load caps C13/C14 (C1663 C0G) and WB crystal C119/C120 (C1562 C0G): correct. Everything else X7R / X5R, acceptable. No Y5V anywhere.
6. DC-bias: the Samsung datasheets on file (4986-line catalogue) have NO DC-bias curves and Samsung's online tool returned HTTP 500; so effective capacitance numbers stay INFERRED/UNVERIFIED (see table). Other notes (P05, P07, P08) reach the same conclusion.
7. Precision: buck feedback 68k/12k 1 % 100 ppm: Vout = 0.75 x (1+68/12) = 5.00 V nominal (INFERRED, LMR14020 Vref 0.75 V recalled from P05; see P05). Battery sense 33k/6.8k 1 %: ratio error up to about +-1.3 %, adequate. All wideband resistors are 1 % thick film, identical to mck1117 BOM (ext/wideband-mck1117 rev C BOM) so no regression vs reference. Resistor tolerance codes: Uniroyal 'F' = 1 %, ND = 'J' in the value field means 10^-1 multiplier (datasheet C25341 txt line 51: J=10^-1 K=10^-2 L=10^-3), which is exactly how the R110 error happened.
8. Extended-part count: passives that are EXTENDED: C17969 (47R 1206), C25341 (620 mR 1206, wrong), C26032 (3.3k 1206), C106862 (33n 0402) = 4 non-preferred; plus 4 "preferred extended": C23221 62k, C25771 27k, C25917 6.8k, C36871 68k. Only ONE can be removed cleanly: C26032 -> 1206 4.7k C17936 BASIC (needs the owner's check of pull-down timing). After the R110 fix, extended passives stay 8 (C17971 replaces C25341).

## Method
join.py: parts_manifest.json lines (board, refs, LCSC) x pcb_pads.csv nets x manifest part data -> join.csv. chk.py: value vs LCSC description. Worst-case node voltages: VBAT_IN/+12V node 14.4 V normal, 24 V jump, TVS-limited ~36-39 V suppressed dump (P06); +5V / +3V3 rails; harness-facing nodes up to 14.4 / 24 V when shorted.

## Distinct parts used (current daughterboard; ordered identical except where noted)
Caps: C14663 100n 50V X7R 0603; C1525 100n 16V X7R 0402 (23); C15195 10n 50V 0402 (12); C57112 10n 50V 0603; C1523 1n 50V; C46653 1n 50V 0805; C52923 1u 25V X5R 0402; C15849 1u 50V X5R 0603; C23630 2.2u 16V X5R 0603 (VCAP); C19666 4.7u 16V X5R; C15850 10u 25V X5R 0805 (+5V, +3V3); C13585 10u 50V X5R 1206 (C16-C18); C15008 100u 6.3V X5R 1206 (C63, C68 on +3V3); C1603 220p; C106862 33n; C1562/C1663 33p C0G.
Resistors: Uniroyal 0402 (62.5 mW, 50 V), 0603 (100 mW, 75 V), 0805 (125 mW, 150 V), 1206 (250 mW, 200 V), all 1 %, 100 ppm except the sub-ohm / low-value codes (R7 1R 400 ppm, R110 800 ppm). Derating: full power to 70 C ambient, then linear (datasheet section 9, C25341 txt line 276-280): about 82 % at 85 C (INFERRED from linear to 155 C).
RN1-RN3: C29718 4D03WGJ0103T5E 4x10k 0603x4 +-5 %, 62.5 mW/element, 8 pins. Pin map (VERIFIED pcb_pads): RN1 pads 1-4 = IGN1..4_CTL, 5-8 GND; RN2 1-4 = FP_G, MAINRLY_G, AC_G, FAN_G, 5-8 GND; RN3 1-3 = CEL_G, TACH_G, LS7_G, pad 4 GND (unused element tied to ground with its pair, pads 4-8 GND). Convention pad n pairs with 9-n (element i = pad i / pad 9-i) as used in design.py `ign_pd`; consistent with a standard 4-resistor isolated array where 1-8, 2-7, 3-6, 4-5 pair (UNVERIFIED against the Uniroyal 4D03 drawing; not opened). Dissipation 3.3 V^2/10k = 1 mW. OK.

## Stress table (selected)
| Ref | Part | Node | Worst case | Result |
|---|---|---|---|---|
| R110 | C25341 620 mR | LSU_IP/RT | wrong value | ERROR (critical) |
| R20-22 (mb, all years) | 4.7k 0603 100 mW | VBAT_IN to IN_SWx | 14.4 V: 44 mW (44 %, 54 % at 85 C); 24 V: 122 mW; 35 V 260 mW (ms) | LOW/MEDIUM, switch closed |
| R37 (mb 89-95, optional) | 1k 2512 1 W self-order | VBAT_IN to OUT_TACH | 14.4 V 207 mW; 24 V 576 mW | OK |
| R15-18 | 100R 1206 | TC4427 5 V to short to GND | (5-0.4)^2/100 = 212 mW = 85 % | OK at 25 C; about 103 % of derated at 85 C |
| R144-147 | 3.3k 1206 | OUT_IGNx | 14.4 V 63 mW; 24 V 175 mW (70 %) | OK |
| R61/R63 | 4.7k 0603 | IN_HALLx to clamp | 24 V: (24-3.6)^2/4.7k = 88 mW | 88 % of rating, 107 % derated at 85 C (jump start + shorted wire only) |
| R62/R64 | 1k 0603 | pull-up behind D35 | diode blocks short to battery (design.py 434-437) | OK |
| R108 | 47R 1206 | LSU_RT | short to 14.4 V 2.3 W | sacrificial (documented) |
| C16-18 | 10u 50V X5R 1206 | +12V, +12V_F | 14.4 V normal, up to ~39 V clamp | OK rated; effective C at 14.4 V about 50-60 % (UNVERIFIED), at 36 V maybe 20-30 % |
| C22,23,26,59 | 10u 25V X5R 0805 | +5V | 5 V = 20 % of rating | effective about 60-75 % (UNVERIFIED) |
| C63,C68 | 100u 6.3V X5R 1206 | +3V3 | 52 % of rating | effective about 40-60 % (UNVERIFIED, P08) |
| C9,C10 | 2.2u 16V X5R | VCAP 1.2 V | negligible bias; -15 % X5R temp, -10 % tol | 1.6 uF worst case, F407 needs 1-2.2 uF OK (INFERRED) |
| C102 | 100n 16V 0402 | LSU_UN to WB_ESR | wire to heater feed 14.4 V (24 V jump) | 90 % / 150 % of rating: risk |
| C104 | 1u 25V | WB_VMS | at most ~14.4 V after F2 | OK |
| C28,29 | 100n 16V | divider outputs | <=4.1 V at 24 V | OK |
| C103 | 33n 50V X7R | pump filter | <5 V | OK; X7R +-10 % acceptable in 482 Hz filter |

## Precision-critical positions
| Function | Parts | Assessment |
|---|---|---|
| Buck FB | R9 68k, R10 12k, 1 %, 100 ppm | worst-case Vout about +-1.3 % from resistors alone, plus Vref tolerance (P05) OK |
| Battery sense | R11/R12 33k/6.8k, R13/R14; WB R120/R121 100k/10k | +-1.3 % ratio; good enough for engine corrections |
| Thermistor pull-ups | R33, R36 2.7k 1 % 100 ppm to V5_EXT | about 0.3 C equivalent; OK |
| Wideband gain/ref | R101/R102 1k/1k 1 % (Vm ref 1.65 V) , R111/R112 10k, R115/R117 100k, R131/R132 68k, R133/R134 10k, R124 3.3k, R104/R103 10k, R105/R107 27k | identical values and 1 % grade as mck1117 rev C BOM (VERIFIED file). Matching pairs 1 % unmatched, same as reference |
| Pump sense | R110 | WRONG PART |

## Extended-to-basic table (price at qty 30-100 from live tools/lcsc.py today)
| Ref | Now | Library | Basic alternative | Notes |
|---|---|---|---|---|
| R144-147 | C26032 3.3k 1206 $0.0036 | ext | C17936 1206W4F4701T5E 4.7k 1206, BASIC, stock 2.08 M, $0.0059@1000 / $0.0077@1; or C26010 3.3k 0805 BASIC but 125 mW fails 175 mW at 24 V | pull-down slows 1.4x: owner to confirm spark-end pull-down timing; removes 1 distinct extended part, 4 placements |
| R108 | C17969 47R 1206 | ext | C23182 47R 0603 BASIC (100 mW) | R108 is sacrificial in a short to battery either way; 0603 changes footprint (layout change) - not recommended without care |
| R110 | C25341 | ext | none basic; use C17971 1206 62R ext | fix, not a saving |
| R114 | C23221 62k 0603 (pref. ext) | ext | C23231 68k 0603 BASIC | changes Nernst pull-up current by 9 %; mck1117 uses 62k; affects wideband analog: UNVERIFIED, not recommended |
| R12/R14 | C25917 6.8k 0402 (pref. ext) | ext | 47k/10k basic (C25792/C25744) with new firmware divider | R116 also uses 6.8k so part count not reduced; skip |
| R105,R107 | C25771 27k | pref. ext | 22k C25768 basic | changes Nernst buffer gain; no |
| R131,R132 | C36871 68k | pref. ext | none | no |
| C103 | C106862 33n 0402 | ext | none basic 33n; 0603 33n not basic | keep |
Net: 1 distinct extended removed (C26032) with caveat; preferred-extended parts are likely fee-exempt at JLC (UNVERIFIED, from memory).

## Differences, ORDERED boards
Daughterboard rev 0.9 has the same C25341 R110 error (VERIFIED fab BOM). Hand-rework before first power: replace R110 1206 with a 62 ohm 1206 (or two 33R... any 62 R 1 %). Ordered boards have no R152-R159 (220R) and fewer 100n (22 vs 23); motherboards 1989-93 rev 0.11 add R23-R26 0R 0805 injector links. Nothing else in the passive set differs electrically.

## Sources actually read
evidence/*/pcb_pads.csv, pcb_footprints.csv, pcb_nets.txt, fab BOMs; kb/parts_manifest.json; repo/scripts/design.py 296-330 and 430-440, wideband.py 33-35 and 153; repo/VERIFICATION.md 265-280; datasheets/txt/C25341_1206W4F620LT5E.txt (lines 51, 276-280); Samsung CL31 catalogue text (no bias curves); ext/wideband-mck1117 rev C BOM; kb/parts/P05, P06, P07, P08; live tools/lcsc.py for C25341, C17969, C22936, C23092, C23222, C17971, C17936, C23182, C26010.

## Not checked
Samsung/Yageo DC-bias curves (not in files; web tool 500); RN 4D03 package drawing; 0603 vs 0402 land patterns of passives (footprints are stock KiCad); per-rev differences of every 100n; rated pulse (surge) limits of resistors; JLC extended-fee exemption rules.
