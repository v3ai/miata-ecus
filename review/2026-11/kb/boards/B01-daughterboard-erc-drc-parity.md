# B01 - Daughterboard: triage of KiCad 9 DRC / ERC / schematic parity (cur_db rev 0.10, ord_db rev 0.9)

STATUS: COMPLETE (2026-11-16)

## Summary
1. Schematic vs PCB connectivity, compared as partitions of (ref,pad) keys ignoring net names (work/.../parity.py): cur_db 338 parts, 1078 pins, 284 groups on each side, ZERO groups differ; ord_db 310 parts, 1015 pins, 269 groups, ZERO differ. The repo claim "0 differences" is TRUE for both. VERIFIED (computed).
2. All 54 KiCad "net_conflict" (cur_db) and 57 (ord_db) are one pattern: "Pad missing net given by schematic (unconnected-(REF-PIN-PadN))". Each is a single-pin no-connect in the schematic (pin carries a no-connect flag) and a pad with no net on the PCB. Name difference only; connectivity identical. Real NC pins, not errors. (U1 21 pins, U102 17, U12 2, U13 2, U14/U3 3 each, U6/U7 2 each, J3/J102 SWO.) cur 54 = ord 57 minus 3 pins that were used in the ordered board.
3. The 6 footprint_symbol_mismatch: J3, J102 (Tag-Connect pads, no part) and H1-H4 (M3 holes): footprint has exclude_from_bom + exclude_from_pos set, symbol does not. Benign: it is why they are absent from the JLC BOM/CPL (correct). Same in ord_db.
4. DRC 495 (cur) / 474 (ord): 199/199 lib_footprint_issues = tool artefact (KiCad 9 run without the stock footprint libraries; footprints are embedded in the PCB; the counts per library match the repo's own report). 125 silk_overlap + 70 silk_over_copper = cosmetic (reference text on lines / clipped by mask; JLC trims silk on pads). 101 courtyards_overlap = REAL as a KiCad rule but harmless for JLC (see below). 0 unconnected, 0 clearance / hole / mask-bridge / edge violations of any kind (severity-all run). The repo's own fab_drc_report.txt lists exactly the same counts (so it is not a KiCad 7 vs 9 artefact either; the repo already documents the overlaps in VERIFICATION.md lines 541, 590).
5. ERC 991 (cur) / 920 (ord): 646 + 340 warnings = missing symbol/footprint libraries (artefact, all of them "current configuration does not include library X"). The only 5 ERC ERRORS are power_pin_not_driven on J3.5 (GND), U1.22 (VDDA / +3V3A), U2.2 (VIN / +12V_F), U4.3 (VI / +5V), U3.8 (+12V): the schematic has no PWR_FLAG anywhere, so power nets driven through passives (ferrite, inductor, fuse, GND) have no POWER_OUT pin. Artefact; each net does have a real source. No pin-conflict, no duplicate reference, no dangling label, no unconnected-pin (every NC pin carries a flag), no undriven-input error in ERC.
6. My own ERC-like pass (own_erc.py): no multi-driver nets, no output-on-rail, no single-pin real-named nets, no shorted parts, no passive with both pins on one net. Unused buffer inputs are tied: U12 B1/B4 (pins 21,18) and U13 5A/6A (pins 11,13) to GND, DIR on U12/U11 as designed. Open-collector comparator outputs VR1_OUT/VR2_OUT have pull-ups (R55/R77, R60/R78).
7. Courtyard overlaps: 101 pairs (cur), 91 (ord), all top side, all small passives/diodes/SOT. Exact pad-to-pad gap (shapely on true pad outlines) minimum 0.200 mm (0805/0805 R51/R52 etc.), most 0.2-0.3 mm; against JLC spacing table in repo/scripts/jlc_spacing.py (0.18 for 0402/0603/0805 pairs, 0.2 SOT vs small, 0.25 1206 vs small, 0.4 SOP) there are 0 violations, margin as low as 0.006 mm (rule met exactly). Body-to-body (F.Fab bbox, approximate) gaps are 0 to 0.1 mm for a few pairs.
8. Conclusion: nothing in the KiCad 9 DRC/ERC/parity output is a real electrical error. Notable positives: 0 clearance violations, parity exact, no floating inputs.

## Parity detail (cur_db, files in work dir: cur_db_parity.txt / .json, ord_db_parity.txt / .json)
- Method: key=(ref, pad number); duplicate-numbered pads (tabs, thermal pads) merged (all same-numbered pads sit on one net: 0 conflicts); schematic partition from sch_netlist.xml, PCB partition from pcb_pads.csv; sets of frozensets compared. Single-pin nets on both sides counted as singletons. Also compared parts, values, footprints and LCSC field: 0 mismatches.
- Names: 230 of 284 groups identical names (hierarchical names like /Inputs/KN_N match on both sides, so hierarchical naming is not a source of conflicts); the 54 others differ only as `unconnected-(...)` vs no net.
- ord_db: 269 groups equal, 212 same name, 57 differ (all unconnected-vs-no-net).
- Pins on the 54: U1 PA0 23, PA9 68, PA10 69, PA15 77, PB11 48, PC0 15, PC1 16, PC2 17, PC3 18, PC10 78, PC11 79, PC12 80, PC15 9, PD0-PD4 81-85, PD14 61, PE14 45, PE15 46; U102 PA1 11, PA4 14, PA5 15, PA7 17, PA8 29, PA15 38, PB1 19, PB3 39, PB4 40, PB11 22, PB12-15 25-28, PC13-15 2-4; U12 A1 3, A4 6; U13 5Y 10, 6Y 12; U14 and U3 NC 2,6 and PG 4; U6, U7 NC 1,8; J3/J102 SWO 6.
- Of these, U1 PD0/PD1 (CAN pins) etc. are simply unused; U14/U3 PG (open-collector power-good) left open by design.

## Not-driven power pins (ERC errors) check
Nets: GND (J3.5), +3V3A (U1.22 via FB1 from +3V3), +12V_F (U2.2 via L1 from +12V), +5V (U4.3, buck output via L2), +12V (U3.8; reported once per net, U14.8 same net). No PWR_FLAG symbols. Fix is cosmetic: add PWR_FLAG. +5V is made by buck U2 (switch node via L2); U14/U3 ADJ pins on +5V are a tracking-regulator reference (not checked in detail; other audit owns).

## Courtyards (table: work/.../cur_court.json, ord_court.json)
Worst by body gap (F.Fab bbox, approximate; crude): D41/U101 0.0, D37/D36 0.0 (both SOT-23 BAT54S side by side, pad gap 0.5), D40/C105 0.0, U13/C66 0.03, C104/R109 0.05 (pad gap 0.14 by crude calc, exact check >= 0.2), D25/D26 0.05, U7/U6 0.08 (TC4427 SOIC-8 pair, pad gap 0.67). Whether JLC places them: JLC recommended spacing (as encoded in repo/scripts/jlc_spacing.py, taken from the JLC help article; I did not re-fetch the article) is met on pad faces for all 101 pairs. Bodies touching a neighbour's body cannot be excluded for D37/D36 and D41/U101 without 3D models: UNVERIFIED, low risk.
Caveat: my first, crude pad-gap numbers (rotated-rectangle approximation, 0.125 mm for R139/D36) were wrong and are discarded; exact outlines give >= 0.2.

## Sources actually read
the review brief; evidence/cur_db and ord_db: drc_kicad9.json, erc_kicad9.json, fab_drc_report.txt, sch_netlist.xml, pcb_pads.csv, pcb_nets.txt, pcb_footprints.csv, fab BOM/CPL; repo VERIFICATION.md (DRC lines), repo/scripts/jlc_spacing.py, design.py line 169; repo PCB files copied to work dir (cur.kicad_pcb, ord.kicad_pcb).
Scripts: parity.py, own_erc.py, court.py, dump_pads.py, exact.py, spacing.py in work/B01-daughterboard-erc-drc-parity/.

## Not checked
- JLC's current spacing article not re-fetched (rules taken from the repo script).
- Silk overlaps/clipping not reviewed individually (cosmetic classes; 48 are reference designators clipped by mask).
- 3D body overlaps (no models).
- Power architecture (TLS115 tracking regulators) left to other audits.
