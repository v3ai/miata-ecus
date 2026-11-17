# B04 - Fabrication and assembly outputs of the daughterboard (cur_db rev 0.10, ord_db rev 0.9)

Status: COMPLETE (2026-11-16). Scripts and extracts: `work/B04-fab-outputs-daughterboard/` (scripts/bomcpl.py, g1_stats.py, g2_outline_drill.py, maskpaste.py, vip2.py, origin.py; cur/ and ord/ hold the copied boards and pcb.json dumps).

## Summary

1. Gerber/drill set for rev 0.10 is complete and internally consistent (VERIFIED): 18 files in the zip, six copper layers named F_Cu.gtl, In1..In4 (.g2..g5), B_Cu.gbl, correct FileFunction L1..L6 in the headers, closed outline (4 lines + 4 R2 arcs, 125.0 x 76.0 mm), PTH 1429 holes and NPTH 10 holes equal the PCB exactly (0 missing, 0 extra).
2. BOM, CPL and PCB agree exactly (VERIFIED): 330 SMD footprints, each once in BOM and CPL, all Top, no DNP, no through-hole, no bottom parts; CPL X/Y equal the KiCad 9 position file (Y negated = gerber frame); same for ord_db (302 parts).
3. BIGGEST ISSUE: via-in-pad is not limited to the DPAK tabs and clamp TVSs, which the README (Before ordering 9) names. 719 of 1349 via holes touch an SMD pad; about 300 sit in pads of 0402/0603/0805 passives, SOT-23, SOIC, TSSOP, LEDs, RN arrays, microSD (VERIFIED by geometry). Open 0.3 mm vias there wick solder. The repo's mitigation (epoxy filled and capped) is JLC's stated default only for 6-layer and above, so the rev 0.10 order is probably fine if left on default, but the order summary must be checked. The README wording should be widened to "all vias".
4. ORDERED rev 0.9 (4-layer): same pattern (730 via holes touching SMD pads, 373 in TO-252 pads). For 4-layer, filling is not the default (INFERRED from JLC wording "default for 6-layer and above"). If the order used the default tented/plain vias, the 8 injector-driver tabs are exposed to solder wicking (voids, thermal performance below the modelled value). Cannot be reworked; check the order record and inspect.
5. Rotations: the CPL applies +180 (SOT-23*, SOT-223*, TO-252), +270 (SOIC, PG-DSO, TSSOP, LQFP), +90 (R_Array_Convex), 0 for everything else. These match the widely used community tables for SOT-223, SOIC, TSSOP, LQFP, R_Array; they DISAGREE for SOT-23 (an older community table has -90 for ^SOT-23) and have no entry for TO-252, PG-DSO-8, microSD, TS-1187A. Repo derived them from JLC's preview of rev 0.5. Not confirmable here; list below.
6. Order options needed: 6 layers, 1.6 mm, 1 oz outer / 0.5 oz inner (JLC default), ENIG or OSP (HASL is not available at 6 layers per JLC capability page), via covering = epoxy filled and capped (default at 6 layers), min via 0.3/0.6 OK, no impedance control, no edge plating.
7. Economic assembly: by JLC's published limits the board qualifies (6 layers supported, 1.6 mm, top-side placement only, 125 x 76 mm, 2-50 pcs). 38 extended + 7 preferred-extended + 48 basic BOM lines. Extended-part loading fee applies to the 38 non-preferred lines (fee amount UNVERIFIED, I recall $3 each).
8. Paste: thermal pads are windowed (4 apertures of 3.05 x 2.75 on each 6.4 x 5.8 TO-252 tab; 4 windows on each exposed pad of U2, U3, U14); no B paste file content (empty, correct, no bottom SMD).
9. Mask: openings equal pad size (expansion 0, JLC applies 1:1), vias are tented (no mask flash at any via centre in rev 0.10); vias in pads sit inside the pad opening so their holes are open to the mask unless filled (see 3).
10. Nothing found that would block ordering. Findings are risks/doc items; no confirmed error.

## 1. Gerber set and naming (cur_db)

| item | result | tag |
|---|---|---|
| Files in zip | F_Cu.gtl, In1_Cu.g2, In2_Cu.g3, In3_Cu.g4, In4_Cu.g5, B_Cu.gbl, F/B_Mask .gts/.gbs, F/B_Silkscreen .gto/.gbo, F/B_Paste .gtp/.gbp, Edge_Cuts.gm1, PTH.drl, NPTH.drl, 2 drill maps (.gbr), .gbrjob; zip == evidence copy | VERIFIED (zipcheck.py) |
| Layer order | gerbonara autodetect orders copper top, inner_2..inner_5, bottom = F, In1, In2, In3, In4, B; file headers say `TF.FileFunction,Copper,L2..L5,Inr` | VERIFIED |
| JLC naming rule | JLC naming table lists G2L/G3L for inner layers of a 4-layer board and says it "understands KiCAD's gerber naming patterns", suggesting Protel file names; ordered 4-layer used .g2/.g3. For 6 layers .g2-.g5 is the same scheme extended. JLC page gives no explicit 6-layer table or ordering rule | INFERRED (JLC help "Suggested Naming Patterns", fetched) |
| Drill | PTH 1429 = 1349 vias (0.30) + 80 header holes (1.00, J1/J2); NPTH 10 = 4 x 3.2 mounting + 6 x 0.991 Tag-Connect locating holes; all match the PCB hole by hole; closest hole to outline 1.35 mm | VERIFIED (g2_outline_drill.py) |
| Outline | closed loop, 8 segments, 0.1 mm line; gerber bbox 99.95..225.05 x 49.95..126.05 | VERIFIED |
| Extras | the two `-drl_map.gbr` and `.gbrjob` in the zip are harmless in my experience (UNVERIFIED that JLC ignores them) | UNVERIFIED |
| Copper limits | via 0.6/0.3, header hole 1.0; JLC 6-layer minimums 0.15 hole / 0.25 via, 0.09 mm track/space (capabilities page) | VERIFIED |

## 2. BOM / CPL / PCB

- bom has columns Comment, Designator, Footprint, LCSC Part # (JLC format); 92 lines, 330 designators, no duplicates; cpl 330 rows; set(BOM)=set(CPL)=set(SMD footprints in pcb_footprints.csv). `smd not in cpl`: none; `cpl refs not smd`: none; DNP: none; THT/other excluded: J1, J2 (bottom headers, self-order), H1-H4, J3, J102 (Tag-Connect pads). (bomcpl.py)
- LCSC codes vs kb/parts_manifest: each BOM line is in the manifest with the same refs; footprint vs actual package consistent (e.g. C12345 = STM32F407VGT6 LQFP-100, real; U3/U14 TLS115B0EJ DSO-8; Q9-Q19 ZXMS6004FFTA is "SOT-23F" mapped to KiCad SOT-23, U4 LDL1117S33R "SOT-223-4" mapped to SOT-223-3_TabPin2 - pad geometry fit not checked here).
- Coordinates: CPL Mid X/Y equals pos file PosX/PosY for all 330 rows (difference <0.001 mm), units mm with suffix, Y negative (KiCad y-down, negated = gerbers' y-up, no aux origin). VERIFIED. Gerbers are in the same absolute frame (bbox x 100..225, y -126..-50).
- Low JLC stock (2026-11-15, manifest): U10/U106 TCAN1042VDRQ1 257, U3/U14 TLS115B0EJ 556, Q101 1902 (C2649436), D46-49 1.5SMC16A 1709 (README says 2709 on 11-15, manifest shows 1709; minor), U101 MCP6004 1761, U13 74HCT04 3583. Fine for prototype quantities.

## 3. Mask, paste, silk

- Mask: F.Mask flashes 1090 = F.Mask pads in PCB; B.Mask 96 = pads; mask expansion 0 (JLC applies 1:1 per capabilities page); no mask flash at any via centre (tented): VERIFIED. Silk: exported with --subtract-soldermask (export.sh), so silk is clipped off pad openings; KiCad 9 DRC still lists 70 silk_over_copper warnings (cosmetic).
- Paste: 1030 apertures = F.Paste pads. Thermal pads windowed: TO-252 tab 6.4x5.8 mm has 4 x (3.05 x 2.75) windows (about 90 % coverage, KiCad stock footprint); U2, U3, U14 exposed pads each 4 windows; SOT-223 tabs single aperture. B_Paste empty (no bottom SMD). VERIFIED (maskpaste.py).
- Via in pad (maskpaste/vip2.py): hole circles touching SMD pad copper, rev 0.10 / rev 0.9: TO-252 406 / 413; D_SMC 18 / 2; SOT-223 8 / 7; PG-DSO/SOIC-EP 17 / 18; passives C/R 0402-1206 about 150 / 175; SOT-23 19 / 26; SOIC-8 20 / 14; SOD diodes ~19; others small. About 300 of the 719 are in non-thermal pads and hole centre is inside the pad copper for ~630 of them.
- Via-in-pad on 0.5 mm LQFP pins: holes touch pads only at 0.1 overlap (U1 pins 21/22, U102) - these are via annulus clipping, hole barely overlaps; inspect.

## 4. Rotations (CPL = KiCad rotation + family offset, JLC_ROT in repo/scripts/order_bom.py:217)

Offsets seen in CPL (per footprint family) and how they compare to community tables (matthewlai/JLCKicadTools cpl_rotations_db.csv fetched; Bouni kicad-jlcpcb-tools DB not retrievable, only its docs; no official JLC table exists):

| family (refs) | CPL offset | community table | status |
|---|---|---|---|
| SOT-223 Q20, SOT-223-3_TabPin2 U4 | +180 | ^SOT-223 180 | agrees; confirmed in JLC preview rev 0.5 per repo (UNVERIFIED by me) |
| SOT-23 x20 (Q9-Q19, D15-D18, D35-D37, U15, U103 ...) | +180 | ^SOT-23 -90 (older table) | DISAGREES with that table; repo says seen in preview. Polarised, 20 parts. Needs JLC preview |
| SOT-23-5 U8, U105 | +180 | ^SOT-23 -90 | same; repo says seen |
| TO-252-2 x9 (Q1-Q8, Q101) | +180 | no entry | repo says seen; DPAK pin1 and tab; origin offset 0.84 mm vs pad bbox centre not corrected. Needs preview |
| SOIC-8 x6, SOIC-8-1EP U2 | +270 | ^SOIC- 270 | agrees |
| Infineon_PG-DSO-8-27 U3, U14 | +270 | no entry | assumed by analogy to SOIC. Needs preview |
| TSSOP-14/24 U11-U13, U101 | +270 | ^TSSOP- 270 | agrees (repo: "rows/columns seen swapped") |
| LQFP-100 U1, LQFP-48 U102 | +270 | ^LQFP- 270 | agrees |
| R_Array_Convex_4x0603 RN1-3 | +90 | ^R_Array_Convex_ 90 | agrees |
| D_SMA, D_SMC, D_SOD-123, D_SOD-323, LED_0603 | 0 | no entry | repo: seen for SMA/SMC/SOD/LED in rev 0.5; the 1.5SMC16A clamp TVSs D46-D49, new in 0.10 and README says never checked. LED polarity mark differs by LCSC part (KT-0603x) - UNVERIFIED |
| SW TS-1187A SW1, SW2 | 0 | no entry | 4 corner pads, 90 deg error would change which pins are the switch contact pair; low risk |
| microSD J4 Molex 47219-2001 | 0 | no entry | new in 0.10, origin is 0.55 mm from the pad bbox centre, no JLC_OFFSET entry; needs preview |
| chip R/C/L/ferrite/fuse/crystal, Sunlord inductors | 0 | none needed | symmetric / non-polar |

List to confirm in the JLC 3D preview: all SOT-23 (20), SOT-23-5 (2), TO-252 (9), PG-DSO-8 (2), D46-D49, LEDs (8), J4, SW1/2, and one each of the SOT-223s.

## 5. Order options for JLCPCB (rev 0.10)

6 layer; 125.0 x 76.0 mm; 1.6 mm; outer 1 oz, inner 0.5 oz (default, matches track_current.py assumption); finish ENIG (HASL not offered at 6 layers; OSP possible, ENIG recommended for the 0.5 mm LQFP-100); via covering epoxy filled and capped (6-layer default; set explicitly); no impedance control; remove JLC order-number mark/ allow "special" placement of marker; assembly: SMT top side, 330 parts, let JLC add rails/fiducials (board has none, README item 7), economic assembly possible (see summary 7), THT parts hand-fitted.

## 6. Ordered rev 0.9 (ord_db)

Same checks: BOM = CPL = 302 SMD footprints, no duplicates, no THT; rotation table identical in logic; gerbers 16 files in zip; 4 layers, 1423 vias 0.6/0.3. Via-in-pad as above (733 via holes touching pads, 373 in TO-252). In rev 0.9 the 2 vias have mask flashes at their centres (one or two vias open on mask; check). For a 4-layer board JLC's epoxy fill is not default, so ask whether it was selected (README of the ordered design says to order epoxy filled and capped). Cannot be fixed in fabrication; if open, vias in the tabs will wick during reflow, expect voided tabs.

## Sources actually read

repo/scripts/order_bom.py (rotation, offset code), export.sh, daughter_release.sh; repo/daughterboard/README.md (Before ordering, copper); evidence/cur_db and ord_db: gerbers, gbrjob, fab_*_bom/cpl, pcb_pos_kicad9.csv, pcb_footprints.csv, PCB copies dumped with pcbnew; kb/parts_manifest.md/json; JLC pages (via search/page fetch): capabilities (pcb-capabilities), Suggested Naming Patterns, assembly capabilities summaries; community: matthewlai JLCKicadTools cpl_rotations_db.csv, Bouni kicad-jlcpcb-tools CORRECTIONS.md.

## Not checked

- JLC 3D/placement preview (cannot be run here): every rotation above is unconfirmed beyond the repo's claim.
- Exact economic assembly constraints and extended-part fee (summary text from search only); current Bouni rotation DB.
- jlc_spacing.py / jlc_fab_check.py not re-run; mask bridge on 0.5 mm LQFP not recomputed.
- What options were selected on the actual rev 0.9 order.
