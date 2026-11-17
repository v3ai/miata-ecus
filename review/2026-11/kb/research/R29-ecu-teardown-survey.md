# R29 - ECU teardown survey: what parts production and aftermarket ECUs actually use

Date of work: 2026-11-16. Tags: VERIFIED = read/seen today in a primary source (file, image, document); INFERRED = reasoning shown; UNVERIFIED = secondary/forum/memory.
Scratch: work/R29-ecu-teardown-survey/ (dl/web = downloaded pages and PDFs, img = photos and crops). Copies of re-checkable files: kb/research/files/R29/ (index in section 8).

## Summary

1. Honest headline: **published teardowns of commercial ECUs with legible chip markings are very scarce.** Not one aftermarket ECU (Link, Haltech, ECUMaster, MaxxECU, AEM, Hondata, Syvecs, ME221/442) has a public board teardown that I could find in about 40 searches/fetches (standard and extended modes). Their internals are known only through published spec sheets (outputs, ratings, temperature range, IP class). What *is* verified at part level: one Mazda 1990 ECU (full reverse-engineered KiCad netlist plus scans), one Mazda 1999 NB1 ECU (photos only, CPU/flash markings), the MegaSquirt V3.0 BOM (manufacturer manual), the rusEFI Hellen modules (see R01), Speeduino (R03), a Saab Trionic 5.5 IC list (Wikipedia, secondary).
2. Mazda 1990 (B63H, PCB 079721-2351): **fully discrete power stage** - 2SD1415 Darlington injector drivers on aluminium case tabs, TO-92/TO-126 pre-drivers, 1E1 rectifier diodes, a 27 V 5 W zener (repo netlist; value "about"), custom Mazda ICs (MP493, MP5273, D151821-0020, D151811-0360), 74HC/4000 logic, uPC177C comparator, film caps (684K100 = 0.68 uF 100 V legible) and radial electrolytics. No multi-channel smart driver anywhere. VERIFIED (netlist + photo crops).
3. Mazda 1999 NB1 (BP5R-18-881, PCB 279721-0044): 160-pin semi-custom QFP CPU (D151806-5740 / SC431421VFM185), Fujitsu 29F200BA flash, two-sided mixed through-hole/SMD board, power transistors on vertical tabs, CPU and flash coated; the board looks varnished. Driver ICs are NOT identified by anyone online. VERIFIED for CPU/flash (author text), power stage UNVERIFIED (not legible).
4. Pattern in every *open or documented* design: injector drivers are **single-channel devices** (discrete logic MOSFET + clamp, or single-channel self-protected MOSFET), never a multi-channel driver IC: Trionic 5.5 = 10 x MTD3055VL (DPAK) UNVERIFIED-secondary; MS2 V3.0 = 2 x IRFIZ34G + IXDI404 gate driver (VERIFIED BOM); rusEFI = ZXMS6005 / AUIPS2041 / now VNLD5090 duals; Speeduino = VNLD5090 duals (R03). Multi-channel ICs (L9842, TLE8104, MC33810) appear only in higher-end designs and are not at JLC (R08).
5. Input protection pattern in cheap designs: series resistor (4.7 k rusEFI; 1 k-10 k MS) + small cap + clamp (SRV05-4 / zener / BAT54S). In low-cost ECUs this is 2-4 parts per input, mostly 0402/0603. No design found uses more than that. (Detail section 4.)
6. Reverse battery / load dump: Mazda 1990 series diode + stud power transistor + zener (inferred from netlist); MS2 V3.0 = 1N4001-class series diodes, 22 V 20 mm MOV, 24 V and 36 V 1 W zeners, 0.5 A polyswitches; rusEFI = P-FET + SMCJ30A + PSM712; Speeduino = 1N5818 + 14D220K MOV + SMBJ40A. ECUMaster EMU Black claims 6-22 V and "immunity to transients according to ISO 7637" with AEC-Q100 grade 2 parts. This project (SMCJ30A + SMAJ33A + B360A + SS34 + polyfuse) is at or above all of them.
7. Enclosure/sealing: EMU Black IP60 CNC aluminium; MaxxECU GEN2 RACE IP68 aluminium with Superseal 1.0; MS3/MS2 DB37 and no sealing; Mazda unsealed aluminium case, board held to case by tab-mounted power devices. The project's stock-case approach matches the Mazda original (unsealed, cabin-mounted) and needs no sealed connector.
8. Conformal coating: only anecdotal (NB1 CPU/flash coating; EMU Black reseller page "protective coating", UNVERIFIED). No shipped low-cost ECU found with documented coating.
9. Where this project spends more: per injector channel ~USD 3 (VND7NV04 + ES1D + 1.5SMC16A + resistors) vs ~USD 0.5-1 for bare logic MOSFET/ZXMS channels in shipped designs (R08 numbers); 6-layer daughterboard; STM32F103 + LSU wideband on board (a feature, not a protection cost). Where it spends less: no potting, no sealed connector, no per-input TVS on the daughterboard.
10. Gaps: no Haltech/Link/EMU/MaxxECU/AEM/Syvecs internal photos found; FCC-ID route yielded nothing (these ECUs have no radio, searches in dl/fcc_search_*.html returned only wireless products). See "Not checked".

## 1. This project's own parts (baseline, evidence/cur_db/sch_bom_grouped.csv, VERIFIED)

- Injector/aux low-side: Q1-Q8 VND7NV04TR-E (TO-252), Q101 VND14NV04, Q9-Q19 ZXMS6004FFTA (SOT-23) for relays/ignition pull-downs; ignition: 2 x TC4427 + 74HCT04 + ZXMS6004FF; R152-R159 220 ohm series on gate inputs (cur_db only).
- Per injector channel: VND7NV04 + 220 R + ES1D + 1.5SMC16A (D42-D45 ES1D x4, D46-D49 1.5SMC16A x4 present, i.e. clamps on four channels) + 10 k pull-down.
- Protection: SMCJ30A (D6), SMAJ33A (D12), B360A (D9), SS34 (D7), BSMD1812-110-33V polyfuse (F1), nSMD010 (F2), 8 x B5819W, BAT54S/WS ~17 pcs.
- Supply: LMR14020 buck, 2 x TLS115B0EJ (sensor 5 V tracker), LDL1117S33R 3.3 V, TL431, REF3033.
- Count: 8 x B5819W + 11 BAT54WS + 6 BAT54S + 5 1N4148WS = ~30 small diodes on the daughterboard; 100 pcs of 0402 100 n etc. Ceramic caps only (no electrolytics): 100 u 1206 x2.

## 2. Factory ECUs

### 2.1 Mazda 1990 NA6 ECU, ECU version B63H, PCB 079721-2351 (reverse engineered by a third party)
Source: github.com/jawamustang/079721-2351 (cloned shallow: work/.../dl/mazda_b63h_079721-2351; commit 3bfff0d, 2020-06-08; scans top_scan.png, bottom_scan.png; KiCad netlist 079721-2351.xml). Netlist values are the author's identification (UNVERIFIED as to correctness; consistent with photo silk). I looked at crops img/b63h_crop_inj.png and b63h_crop_psu.png.

| Function | Part per netlist | Legible in my crop? |
|---|---|---|
| Injector drivers T712/T722 | 2SD1415 (NPN Darlington power, TO-220F style), bolted to case via screw, two channels (2U = injectors 1,3; 2V = 2,4) | silk "T712/T722" and bolted tabs visible; type marking NOT legible -> netlist only |
| Injector pre-drivers T711/T721 | 2SC2001-type TO-92, R712/R713 etc., C711/C721 film | caps legible: "684K100" (0.68 uF, 100 V, J tol marking) VERIFIED |
| Ignition pre-drivers | CE1A3Q (TO-126) T751/T761/T812/T842 | netlist only |
| Regulator | T1 2SB1015B (PNP pass) + D5 6.2 V zener + IC1 "HC244" bolted block | "HC244 9L17" on package legible VERIFIED (it is a package label of a block/hybrid, function unclear; INFERRED part of PSU) |
| Stud-mounted power part T001 on case | silk T001, clamped with screw to the aluminium case: thermal path = case | VERIFIED visually |
| Reverse battery | large axial diode D001/D00x (marking "SR..." partly legible) in series | partly legible; INFERRED series reverse diode |
| Load dump | D2 "about 27 V 5 W" zener (netlist note), series R001 | UNVERIFIED value |
| Processor | custom Mazda D151801/D151811/D151821 ICs, MP493, MP5273 (Mazda ASICs), B63H.asm ROM listing in repo | netlist |
| Logic/analog | 4069UBP, 4071BP, uPC177C quad comparator, DIS157 photocoupler | netlist + datasheets in repo |
| Caps | film 684K100 x2, radial electrolytics 33 uF 35 V, 47 uF 35 V, 220 uF 10 V, 3.3 uF tantalum 16 V x4, many disc ceramics | radial electrolytics (blue sleeves, "9L17" date code era, 1990s) visible; film caps legible |

Observations: 100 % through-hole discrete power stage, axial resistors, single-sided heat path through case. The pin-for-pin load per channel is one Darlington + 2-3 small parts. VERIFIED visually: electrolytic caps next to the regulator block are the age-failure suspects (R16 note: miata.net thread titles about leaking capacitors, UNVERIFIED).

### 2.2 Mazda 1999 NB1 ECU BP5R-18-881 (PCB 279721-0044)
Source: https://www.vkmotorsports.com/blog/2019/05/22/ecu-research-bp5r.html (photos downloaded: img/bp5r_front_1.jpeg, bp5r_back.jpeg; kb/research/files/R29/).
- VERIFIED (author text): CPU D151806-5740 / SC431421VFM185 / SSAU9945A, 160 pins (guessed MC68HC16Y1 family); flash Fujitsu 29F200BA-90 (IC600, 44 pin); IC400 11U19 MG8461 (44 pin, unknown); CPU and flash coated in a compound.
- VERIFIED (my view of photos): board number legible "279721-0044" on the top side; green solder mask, mixed THT/SMD both sides; 160-pin QFP CPU and TSOP flash top; about ten tab-mounted (TO-220/DPAK-style) power devices and two vertical SIP blocks on the left, near the connector (the heat path goes to the case through tabs/bracket: bracket with "14" casting number visible); axial resistors on the bottom; large radial electrolytics (4 visible, plus several small); fine-pitch SOIC ICs of unreadable marking. Driver IC types: NOT identifiable from image resolution (1058 px wide). So: injector drivers, ignition pre-drivers, regulator type = UNVERIFIED/unknown.

### 2.3 Other factory ECUs (context, secondary)
- Saab Trionic 5.5 (Wikipedia IC list, secondary: https://en.wikipedia.org/wiki/Trionic_T5.5, saved dl/web/t55.txt): MC68332 MCU, L4937 dual regulator, L9842 octal power driver, CA3262E quad 700 mA driver (ignition trigger), **10 x MTD3055VL DPAK logic MOSFETs** (4 injectors, 2 purge, O2 heater, vacuum pump, IAC) and 3 x MTP3055V TO-220 (boost). UNVERIFIED (secondary list, no photos).
- Magneti Marelli IAW 4AC.A3 and Bosch DCU17 teardowns exist on electronics360 (search snippet: ST10F269 + L9113 PMIC; many ICs from 1997) but the site returned HTTP 403, so nothing beyond the snippet. UNVERIFIED.
- EEVblog thread on Sagem-Lucas GEMS and a "potted 1993 Dodge ECU" thread exist (not read in depth).
- ECU capacitor failure generalities: leaking electrolytics in 1990s Japanese ECUs (Mazda 929, Lexus, 3000GT wikis; no Miata-specific recap guide with part numbers found). Lexus forum warns rebuild caps are often wrong type. UNVERIFIED (forum).

## 3. Aftermarket ECUs

| Product | What is publicly known | Source / tag |
|---|---|---|
| ECUMaster EMU Black | Operating 6-22 V, "immunity to transients according to ISO 7637", **AEC-Q100 grade 2 (-40..+105 C)**, 5 A fuse (ign) + 15 A fuse (batt) as installer-fitted, IP60 CNC aluminium, 150x72x31 mm, 390 g, 6 injector outs, 6 aux 5 A "protected" low-side, full bridge 7 A, 9 analog inputs "protected", built-in LSU 4.2/4.9 controller, connectors Sicma FCI 211PC249S8033 (24-way) + custom black, 4-layer PCB, mostly SMD, protective coating (reseller, UNVERIFIED) | Manual v1.4 p.3-4 (kb/research/files/R29/emu_black_manual.pdf/.txt) VERIFIED; reseller tegiwa.com UNVERIFIED |
| MaxxECU GEN2 RACE | injector (peak/hold) 10 A peak / 5 A continuous, flyback 30 V with automatic regulation, PWM over-current, overload, short-circuit protection; aux 3-5 A protected; IP68 black aluminium case, Superseal 1.0 connectors | MaxxECU quickguide (dl/web/maxx.txt lines 61-64, 144-157) VERIFIED as spec claims; chips unknown |
| Link G4X | "8 x high current injector drives (suits high impedance)", 8 ignition channels, one MCU across range; plug-ins derived from XtremeX; Link forum: pinout/PCB not released | demon-tweeks spec sheet, Link forum search results UNVERIFIED |
| Haltech Elite / Nexus | injector driver failures reported (E8, Elite); no chips named; pin touching alu housing case reported | forums.haltech.com search results UNVERIFIED |
| MS3Pro / MS3X (MegaSquirt) | V3.57 mainboard: 2 injector outputs each up to 14 A, MS3X 8 x 5 A; ignition via BIP373 on Q16 (30115 marking) | msextra V3.57 hardware manual 1.5, ms3v357.txt lines 1471-1474, 585, 3088 VERIFIED |
| MS2 V3.0 (full BOM) | see 3.1 | msextra MS2V30_Hardware-3.4.pdf p.197-200 VERIFIED |
| ME221 / ME442 | board only; high-impedance injectors only; Gen2 "drive stock hardware"; no internals found | install guide search snippet UNVERIFIED |
| AEM, Hondata, Syvecs | nothing found (Hondata injector driver is an external 4-ch box; S300 socketing page lists IC3/IC4 only) | UNVERIFIED |
| rusEFI Hellen / uaEFI, Speeduino | see R01, R03, R08 (all verified there) | cross-ref |

### 3.1 MegaSquirt V3.0 bill of materials (VERIFIED, ms2v30.pdf p.197-200, "MS2V3.0 Hardware Guide" 2015-07-09, James Murray; copy in files/R29)
- Injector stage: Q1, Q5 IRFIZ34G (N-MOSFET 60 V 20 A, TO-220FP), U4 IXDI404PI dual 4 A low-side gate driver (DIP-8), Q9/Q12 TIP125 PNP Darlington (active flyback "D5,D7 FR302 3 A fast diodes"), R37/R38 0.05 ohm 20 W TO-220 current limit resistors (for low-z), Q2/Q4 ZTX450, Q22/Q23 ZTX553, Q3/Q11 PNP 6 A 100 V.
- Ignition: Q16 BIP373 (Bosch, TO-220) with mica; R43 0.010 ohm sense.
- Regulator: U5 LM2937ET-5.0 (LDO, TO-220).
- Protection: MOV1 22 V 20 mm ZNR 2000 A at input; D1-3, D9-11 1N4001 (7 pcs); D12 24 V 1 W zener, D13 12 V zener, D6/D20/D21 36 V 1 W zeners, D4/D8 22 V 1 W zeners, D17/D18 1N5819 Schottky, F1/F2 polyswitch RXE050 0.5 A, L1/L2 1 uH chokes.
- Caps: 10 x 0.1 uF 50 V X7R radial, tantalum 22 uF 25 V x2 and 4.7 uF 25 V x2 (no aluminium electrolytic), film absent.
- Comms: U6 MAX232-type RS232 driver, U7 dual op-amp, DB9 + DB37 connectors, gold sockets for the CPU card.
- Total protection parts: about 20 discrete protection parts for the whole board (MOV, 7 x 1N4001, ~8 zeners, 2 Schottky, 2 polyswitch). Per output: one gate driver channel + MOSFET + flyback; per input: R + C (+ zener on ignition input).

## 4. Patterns

| Item | Observed (source) |
|---|---|
| Injector driver | single-channel: discrete Darlington (Mazda 1990), DPAK logic MOSFET (Trionic UNVERIFIED), IRFIZ34G + gate driver IC (MS2), ZXMS6005 / AUIPS2041 single (rusEFI Hellen), VNLD5090 dual (Speeduino, uaEFI), NCV-class (this project). Multi-channel ICs (L9842, TLE8104/8110, MC33810, TLE8888) used only in expensive designs, none stocked at JLC |
| Ignition stage | 5 V push-pull TC4427/74HC buffer driving stock igniter (Mazda NA, rusEFI, this project); BIP373 or IGBT (EcoSPARK) in MS; CA3262E in Trionic |
| Regulator | LDO linear (L4937, LM2937, 2SB1015 pass) in 1990s; buck + LDO + tracker in rusEFI/this project |
| Input protection | R (1 k-10 k) + C + clamp; MS inputs R+C only (no TVS), rusEFI SRV05-4 + 4.7 k per analog input |
| Reverse battery | series Schottky/diode (Mazda, MS, Speeduino), P-FET (rusEFI output module) |
| Load dump | zener/MOV/TVS (Mazda 27 V zener UNVERIFIED value, MS 22 V MOV + 24/36 V zeners, rusEFI SMCJ30A, Speeduino SMBJ40A + 14D220K, EMU Black "ISO 7637" claim) |
| Thermal | Mazda: power parts on case tabs; MS: TO-220 on heatsink bar/case with mica; EMU Black / MaxxECU: CNC aluminium case; rusEFI/this project: copper only (SOT-223/DPAK on pour) |
| Sensor 5 V | EMU/MS: fused/protected; rusEFI: TLS115 tracker after failures; Speeduino: polyfuse (one failure report) |
| Coating | NB1 coating on CPU/flash (VERIFIED author text); EMU Black coating (reseller UNVERIFIED); none documented elsewhere |

## 5. Minimal robust BOM per shipped products (INFERRED from sections 2-4)
- Supply: series diode or P-FET, one bidirectional/unidirectional TVS 30-36 V (SMCJ30A class), polyfuse or fuse, buck or LDO, 3.3 V LDO. (Matches this project.)
- Per injector: one logic-level, self-protecting MOSFET (single or dual), with on-chip clamp; no external TVS needed when the device has ~42-55 V active clamp (ZXMS/NCV/VND); series gate R 150-220 ohm only if the part is an OMNIFET II.
- Per aux output: same, SOT-23/223 class.
- Ignition: logic buffer to stock igniter; coil drivers only if IGBT coils.
- Per analog input: R + C (+ BAT54S / dual-diode clamp).
- Hardware count in rusEFI Hellen NA6: ~19 outputs all on ZXMS6005 (R08), so ~USD 7 for all low sides vs this project USD 19-22.

## 6. Implications for this project (goals in review brief section 1)

1. (goal 3/5, cost) Every shipped/open design surveyed uses single or dual 0.4-1.2 USD drivers; none relies on an expensive intelligent driver and none adds per-channel TVS when the driver self-clamps. This supports R08's recommended replacement (NCV8401B / NCV8403A) and suggests dropping the per-channel 1.5SMC16A + ES1D (4 x ~0.3 = about 1.2 USD/board) if the chosen driver's active clamp and avalanche energy are validated for the real injector inductance. Evidence: Hellen modules rely on AUIPS/ZXMS self-clamp without external clamp (hellen-one output module BOM per R01); confidence medium (injector inductance unknown, repo documented).
2. (goal 1, errors) Nothing in the survey contradicts the project's protection set; it is richer than MS2 V3.0 and Speeduino. Reverse-battery + 30 V TVS + polyfuse is the common denominator. No change; info.
3. (goal 4, UX, documentation) NB-era stock ECUs have coating on CPU/flash and electrolytic caps that age; the project's all-ceramic daughterboard (no electrolytics) removes the commonest age failure. Worth stating in the product page (reliability claim) - confidence medium, since failure statistics for Miata ECUs are anecdotal.
4. (goal 6, packaging) Stock case reuse mirrors factory unsealed aluminium; EMU Black IP60 and MaxxECU IP68 show sealed alu cases are the aftermarket norm, but only for engine-bay use. No sealed connector needed for cabin install. Also, the factory design uses the case as heat sink via tab-mounted power devices; this project uses copper only (R08 thermal model).
5. (goal 3) Trionic and Mazda factory designs use 10 x DPAK MOSFETs etc. without smart features; so smart FET features (current limit) are a luxury, not required by production practice. Option: for the 11 ZXMS6004FF relay/ignition drivers keep as is (cheap). Confidence low-medium.
6. (goal 1/doc) No evidence found for what the NB driver stage looks like; therefore do not claim "NB-compatible output stage" based on teardown; document drive levels from the FSM instead (R17-R19).
7. (goal 2) No removal candidate emerges from this survey beyond item 1.

## 7. Findings candidates
(see structured output; the rest here)
- Haltech/Link: drivers fail in the field (shorts, fuel fire), repaired by factory; supports keeping short-circuit-protected drivers (info).
- EMU Black claims AEC-Q100 grade 2 parts: if the owner markets "automotive-grade", the project's JLC parts are mostly commercial/industrial grade (not checked part by part).

## 8. Files saved (kb/research/files/R29/)
- emu_black_manual.pdf/.txt (Ecumaster EMU Black manual v1.4)
- ms2v30.pdf (MS2 V3.0 hardware guide with BOM p.197-200), ms3v357.pdf (MS3 V3.57 hardware 1.5)
- bp5r_front_1.jpeg, bp5r_back.jpeg (NB1 ECU photos, (c) vkmotorsports.com, kept for reference)
- 1990 ECU repo cloned at work/R29-ecu-teardown-survey/dl/mazda_b63h_079721-2351 (3rd-party data, untrusted)

## Sources actually read
- github.com/jawamustang/079721-2351 (README, netlist xml, "mazda ecu technical data.txt", scans)
- https://www.vkmotorsports.com/blog/2019/05/22/ecu-research-bp5r.html and 2 photos
- https://www.ecumaster.com/files/EMU_BLACK/EMU_BLACK_manual.pdf
- https://www.maxxecu.com/files/Documentation/Manuals/MaxxECU%20GEN2%20RACE%20quickguide%20and%20wiring-en.pdf
- http://www.msextra.com/doc/pdf/MS2V30_Hardware-3.4.pdf, MS3baseV357_Hardware-1.5.pdf
- https://en.wikipedia.org/wiki/Trionic_T5.5
- Web search result lists (not pages): tegiwa EMU Black, Link forums, Haltech forums, Hondata forums, electronics360 teardowns (403), eevblog.
- Local: the review brief, evidence/cur_db/sch_bom_grouped.csv, kb/research R01, R03, R08, R16-R19, R24, R25.

## Not checked
- Any Haltech, Link, EMU, MaxxECU, AEM, Syvecs, ME221/442 internal photo (none found; FCC route empty).
- Part markings on NB ECU power transistors (photo resolution too low; the author's higher-resolution figures 5-7 not viewed beyond text).
- Magneti Marelli / Bosch teardown articles (HTTP 403).
- MS3Pro EVO BOM (manual download blocked: HTML shell).
- Capacitor part numbers/types specific to Miata ECUs.
- Miata 94-97 and 2001-05 ECU internals.
