# R01 - rusEFI hardware family: boards rusEFI designed, and the circuit choices they converged on

Date of work: 2026-11-16. Tags: VERIFIED = read today in the primary source named; INFERRED = reasoning shown; UNVERIFIED = memory / single post.
Scratch: work/R01-rusefi-hardware-family/ (module schematic PDFs/txt in modsch/, downloaded wiki/shop/issue pages in dl/, NA6 git history clone in git/NA6-hist).

## Summary

1. rusEFI's own Miata plug-ins (Hellen64 NA6 rev A-D, NB1 rev A-C, NA8-96 rev A, NB2 rev C-F) are all **2-layer, 1.6 mm** boards, built from "hellen-one" modules (power, mcu144, output, ign8, input, dinput4, knock, wbo, can, sd) and patched per board with `bom_replace_*.csv` (JLC stock substitutions). VERIFIED (kicad_pcb layer tables; ext/hellen-miata-*/bom_replace*).
2. Injector drivers: module default AUIPS2041LTR (SOT-223, 1.4 A, self-clamping, no external clamp) but **every Miata BOM replaces it with ZXMS6005SGTA** (SOT-223, self-protected 60 V, JLC ext. 18 pcs, USD 1.17 @1 / 0.74 @100). AUIPS2041LTR has stock 0 at JLC today. The replacement is a JLC-availability driven change (INFERRED: early revs list Q305-Q312 as "non-JLC components", rev C onward lists ZXMS6005; NB2 issue #38 validates NCV8440 as another alternative).
3. Current uaEFI (rev F3, Sept 2026) has moved to **VNLD5090/VNLD5160 dual low-side drivers on every low-side output**, 4 layers, and **STM32F407VGT6 (same MCU as this project)** as a cost reduction; it added series resistors in front of the driver inputs (rev F, July 2026) after injector-driver failures - ST says the same 150 ohm minimum that this project's 220 ohm resistors satisfy (and the ordered rev 0.9 daughterboard lacks).
4. Field failures that shaped rusEFI circuits: (a) NA6 H64b bricked when the TPS 5 V pin was shorted: **no protection on any +5 V sensor output** -> TLS115D0 tracking regulator on every board (rev C+); (b) NB2/Frankenso/NB1 **alternator-control / tach TC4427 outputs killed MCU pins** (rail-steering diodes failed, 8-10 ohm to ground) -> 100 ohm series + Schottky on output module 0.3 (Nov 2021); (c) NB1 alternator misbehaviour -> R23 1 k removed; (d) weak ULN2003 low sides and ignition outputs had no current limit (2024) -> VNLD everywhere in uaEFI; (e) level-shifter (SN74LVC4245) as smart-coil driver questioned (50 mA) -> LXH8T245 in uaEFI rev E.
5. rusEFI **does not currently sell or stock any Miata Hellen board** ("we do not fabricate or stock those but can help with bulk orders"; NB2 and NA96 wiki pages say "somewhat abandoned"). Shop sells uaEFI (from USD 275), a uaEFI NA6 adapter "definitely has issues", Superseal adapters (USD 50), NC adapter. So the rusEFI-made, Miata-specific competitor is open-source only.
6. Statements in `repo/research/other_miata_pnp_boards.md` checked: three are wrong or incomplete (suffix-7 STM32 claim wrong; AUIPS2041L is not what the Miata boards fit; uaEFI MCU stale). See section 7.

## 1. hellen-one module system (ext/hellen-one @5076e80, 2026-10-30)

All data: ext/hellen-one/modules/<m>/<ver>/*-BOM.csv (VERIFIED, read today).

| Function | Module (ver) | Parts / topology |
|---|---|---|
| Main power 12 V | power12 0.2 / power_12and5V 0.3 | polyfuse SMD1206P050TF/24 (0.5 A hold, 24 V) F410; **SMCJ30A** TVS D418 (SMC); B5819W Schottky D416/417; 1N4148WS steering; PSM712-LF dual TVS D411; 2x47u; MIC5205-3.3 LDO; 0.3 adds TLS115 (5 V sensor tracker) U411 and LEDs |
| 5 V buck | power5 0.2 | LMR14020 (BOM replaced by LMR14030 in Miata boards), 2.2uH (L420)+10uH (L421), SS34, **P6SMB6.8CA** on 5 V |
| Processor | mcu144 0.6 / mega-mcu144 / mega-mcu100 0.3 / mcu 0.7 | module default STM32F767ZI (LQFP144); mega-mcu100 default STM32F429VIT6 (LQFP100); Miata boards replace with F407 (see table 2). Sensor 5 V from module has polyfuse only (hellen-one#119, NB1#32 "polyfuses are only so good") |
| Low-side outputs | output 0.3 | 8x AUIPS2041LTR (SOT-223) injectors, no external clamp or flyback; 10u x10 bulk; ULN2003AD x2 for weak low sides (deprecated 2024: "would not survive short to +12 V", hellen-one#360); TC4427 + RZ7899 (ignition-style push-pull / alternator); 2 PJM2319PSA P-FETs: Q313 reverse-battery switch + Q314 gated by PSM712 (7 V/12 V) overvoltage kill; F300 polyfuse 0.5 A/24 V in V12P; 100 ohm series R312/R316 (0805) + B5819W on TC4427 outputs (added 2021-11-26, commit 520bed0) |
| Ignition | ign8 0.2 | SN74LVC4245APW 8-bit level shifter + 10 ohm series (R461-469). No on-module driver: board outputs 5 V logic to stock igniter/smart coil. uaEFI adds ISL9V3040D3ST IGBTs as an option |
| Analog inputs | input 0.1 | 4.7k series, 1n/10n/100n, SRV05-4 (4-ch TVS, SOT23-6) x6, P6SMB6.8CA, 680k/10k dividers |
| Digital/hall inputs | dinput4 0.1 | 74HC2G17 (SN74LVC2G17 in Miata BOM) Schmitt, 680k pull / 10k, 1n |
| VR | vr-max9924 0.3 / vr-discrete 0.5 | MAX9924 (MSOP10) + BAT54S; discrete: MAX9142 + MCP6004 + analog switches |
| Knock | knock 0.2 | 2x LMV321 (SOT23-5), passive filters (3.3n/330p/47p/680p), no TPIC8101 |
| Wideband | wbo 0.3 | STM32F042K6 + AD8628 + MCP6004 + REF3033; heater BTS3028 (DPAK) + VNP28N04-E; Miata BOMs: VND14NV04TR-E heater, GS8551 opamp; rusEFI wideband-over-CAN firmware |
| CAN | can 0.1 | TJA1051T/3 + PESD1CAN, 120 ohm |
| SD | sd 0.1 | Molex 47219-2001 microSD (same part as this project's J4), 33k |

Observations: INFERRED from BOMs - the modules use mostly 0603/0402 JLC parts and a flat 2-layer layout; protection is thinner than this project's (no per-injector clamp, no TVS per input except SRV05-4 arrays).

## 2. Per-board table

| Board | MCU | Injectors | Ignition | Inputs | 5 V sensor | Main power | WBO | MAP | Knock | Connector | Layers | Licence | Sold? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Hellen64 NA6 (rev D, 2022-08) | STM32F407ZGT6 LQFP144 (C19156); rev C IGT6 LQFP176 | 8x ZXMS6005SGTA (Q305-312), module default AUIPS2041 | ign8 level shifter, 5 V logic | input 0.1 + dinput4 + Schmitt SN74LVC2G17 | TLS115D0 added rev C (2022-10) after H64b failure | polyfuse 24 V, SMCJ30A, P-FET reverse, 5 A 1206 fuses F1-F3 | on board (wbo 0.3, STM32F042; Q600 VND14NV04) | on board MPX4/MPXH6400A footprint + LPS25HB baro | knock-0.1 module + 3.5 mm audio jack | stock 48-pin (3 headers: Molex-like 178780-1 footprints) + 24-pin options port | 2 | none in repo | not stocked |
| Hellen64 NB1 (rev A-C, 1999-2000) | STM32F407ZGT7 (C1337111, -40..105 C) | 8x ZXMS6005SGTA | same | same | TLS115 | same; rev B added high-side output protection (RC) | on board | LPS22 baro | module | stock 1999-2000 conn. + 12-pin options | 2 | none | not stocked |
| Hellen64 NA8-96 (rev A, 1996-97) | STM32F407ZGT7 | 8x ZXMS6005SGTA | same | same | same | same | on board | - | - | 1996-97 conn. + options port 4A-4L | 2 (INFERRED from 2-layer sister repos; not opened) | none | wiki: "somewhat abandoned" |
| Hellen72 NB2 (rev C-F, 2001-05) | STM32F407IGT6 LQFP176 | 8x ZXMS6005SGTA; NCV8440 validated alt | same | same | TLS115 (NB2#29) | same | on board | external MAP via jumpers or LPS22 baro | module | 94-pin + options, M4x10 case screws, case 89661-3T270 | 2 | none | "somewhat abandoned" |
| uaEFI rev F3 (2026-09) | STM32F407VGT6 (standard), F7 (PRO); LQFP100 | 6x VNLD5090 dual (BOM) / VNLD5160 in INJ6 sheet; Q1 alternatives ZXMS6005/NCV8440 | smart coils via LXH8T245 buffer; optional ISL9V3040D3ST IGBT | 2 VR (MAX9924 + discrete), 3 hall, 9+2 analog | TLS115 | polyfuse + TVS (module) | on board LSU 4.9 | optional MPX4250/MPXH6400 | on board | 5x Molex Mini-Fit Jr (8/18/20/16/6 circuits) | 4 (verified kicad_pcb: F, In1, In2, B) | none stated; Royalty page: GPLv3 | USD 275 base; +50 enclosure, +40 crimp kit, +100 pigtails+WBO cable; "order 3 ship 4"; ships NJ USA ~5 business days |
| uaEFI 121 / super uaEFI | as uaEFI | | | | | | dual LSU | | | 121-pin automotive / Superseal | | | USD 375 / 410 |
| Proteus | STM32F4 (0.3-0.5,0.7) / F767 (0.6) | 16 low-side x 3-4 A | 12x 5 V | 2 VR 6 hall | | | not on board | | yes | TE Ampseal 35+23 | | repo mck1117/proteus: no licence in GitHub metadata | USD 800 (legacy) |
| microRusEFI | F4 (F429VIT6 on mega-mcu100) | 4 high-Z | 4x 5 V | | | | no | | no | single 48-pin | | | USD 475 (legacy); "two injectors per output will burn the board" |
| Huge | | 12 | | | | | dual | | dual | | | | USD 850 |
| Frankenso / Prometheus | not read (wiki pages empty in raw fetch) | | | | | | | | | | | | not checked |

Sources: ext/hellen-miata-*/ (VERIFIED); wiki Hardware/ECU-Comparison/uaEFI/Proteus/microRusEFI pages fetched today (VERIFIED as vendor statements); shop pages shop.rusefi.com/shop (USD, 2026-11-16, single quantity). Where made: JLCPCB PCBA with a small hand-fit set (Proteus wiki: "80 % assembled unit from JLCPCB"; Hellen BOMs carry LCSC numbers) - VERIFIED at wiki/BOM level; shop fulfilment from New Jersey USA (shop page).

Cases: NA6 README "case cover bolts M4/0.7 countersunk Philips 9 mm"; NB2 README "M4 x 10 mm good for NB external case and internal board to case for both NA and NB" (VERIFIED). So rusEFI's Miata boards also sit in the stock case.

## 3. What rusEFI does with fewer / cheaper parts, and where more

| Topic | rusEFI | This project (README) | Comment |
|---|---|---|---|
| Injector drive | ZXMS6005SGTA SOT-223 (about USD 0.74 @100), clamp inside the driver, no external parts | VND7NV04 DPAK (JLC ext.) + ES1D + 1.5SMC16A per injector | rusEFI is cheaper by roughly 2 parts + TVS per channel. Cost of ZXMS6005 (SOT-223 low-Rds not) vs VND7NV04: see R08. rusEFI accepts driver-clamp energy in the driver; this project moved it to a TVS (for thermal reasons) |
| Layers | 2 | 6 (cur) / 4 (ordered) | rusEFI shows a Miata ECU PCB can be 2-layer; NB1#8 asked for 4 layers "available at low cost", andreika objected |
| Reverse battery | P-FET (Q313) switch + TVS gate | see repo; | similar function |
| Input protection | SRV05-4 arrays, 4.7k series | per-input clamp parts | ours heavier |
| 5 V sensor protection | TLS115 added after field failure (all boards) | second TLS115 U14 for harness 5 V | same lesson already adopted |
| Ignition | level shifter 10 ohm, igniter external; TC4427 + 100 ohm + B5819W for alternator/tach | TC4427 + 100 ohm + B5819W | this project already matches post-2021 rusEFI |
| MCU | F407ZG(T7)/IG for Miata; uaEFI VGT6 | F407VGT6 | same as uaEFI standard |
| WBO | STM32F042, rusEFI CAN firmware | STM32F103C8 FOME/mck1117 | |

## 4. Choices that came from field failures (with sources)

All fetched via GitHub API today (VERIFIED as maintainers' statements; root causes partly unproven):
- rusEFI#3559 / hellenNA6_issues#22 (2021-11/12): H64b bricked at install, STM32 module damaged, suspected TPS 5 V (pin 1N) shorted to ground; "There is no circuit protection on any of the +5v outputs"; fix -> hellen-one#119 TLS115D0EJXUMA1 ("cheap and very resilient"), NA6 rev C (2022-10) added protection. Another maintainer: polyfuses "only so good" (NB1#32).
- NB1#25 / NB2#23 / rusEFI#3558 (Nov 2021): MCU pins feeding the 12 V-powered TC4427 died (8-10 ohm to ground, 2-20 ohm to 3.3 V rail) on NB2 and a Frankenso in NB1 Miatas; Hellen had pull-downs but no series resistor and no output RC; OEM Miata ECU uses 1 k series + 100 nF on the alternator wire; fix output-0.3 100 ohm series + Schottky (hellen-one#118, commit 520bed0, 2021-11-26). NB1 rev B/C add that; NB1#29/#30 and NB2#31: R23 (1k) removed due to alternator charging problem (ramps to 17-18 V). Owner's alternator control ships off already; this confirms the risk.
- hellen-one#360/#362 (2024-01): ULN2003 low sides and mega-module ignition outputs have no current limit; fix VNLD for all low sides in uaEFI rev B (Feb 2024), fuse workaround for ignition.
- uaefi#112/#114 (May 2026): "why would blue board injector drivers fail"; maintainer: "datasheet section 3.1, you need a series resistor to protect the mcu" -> rev F series resistor (July 2026); proteus#125 reports VNLD5160 threshold up to 3.5 V is not reachable with 3.3 V GPIO ("expect 5V levels"). Relevant to the VND7NV04 drive (this project drives from 5 V buffer, per README).
- hellen-one#378: SN74LVC4245 as smart-coil gate driver, 50 mA/output, questioned in 2024; uaEFI rev E (2025) uses SN74LXCH8T245 "more current for smart coils".
- Parts-availability driven: hellenNA6_issues#18, #24 (74HC2G17GW shortage), NB1#26/#31/#35/#37, NB2#32/#39/#43 (RZ7899 out of stock), NB2#41 VND7NV04 (C155605) as WBO heater FET - same part as this project's injector driver; JLC stock volatility is a recurring pain.
- hellenNA6_issues#27: flex-fuel dropout traced to firmware, not hardware (closed).

## 6. Implications for this project

1. (cost, medium) Injector driver choice: rusEFI ships ZXMS6005SGTA (USD 0.74 @100 vs AUIPS; JLC ext., stock 18 today - low). It is a SOT-223 with in-chip clamp and no external diode/TVS; this project's VND7NV04+ES1D+1.5SMC16A per channel is about 3 parts more. But the design chose that for thermal margin at 20 mH injectors; rusEFI's field record with ZXMS6005 on Miata is unreported in issues. Confidence medium; compare in R08.
2. (error/risk, high) The ordered rev 0.9 daughterboard lacks the 220 ohm series resistors; rusEFI's uaEFI hit the same failure (injector drivers failed on uaEFI, then series resistor added in rev F, issues #112/#114). Reinforces rework of ordered boards before power-up. Confidence high that the pattern exists; the repo already documents the omission.
3. (doc/ux, medium) Alternator control: rusEFI had two MCU-pin kills and one charging fault on alternator/tach TC4427 outputs. Keep alternator output off by default and keep the 100 ohm + Schottky; consider the OEM 1 k + 100 nF network from NB1#25 for the NB alternator wire.
4. (info) 2-layer Miata plug-ins by rusEFI prove cost floor: but they use fewer protections; use as price benchmark only.
5. (packaging/product, medium) rusEFI does not stock Miata Hellen boards, so the sale of a finished plug-in is not in direct conflict; uaEFI USD 275 + enclosure 50 + crimp 40 + pigtails 100 (USD 465 with everything) is the universal alternative price anchor against USD 399.
6. (supply, low) JLC part availability changes: rusEFI repeatedly substitutes parts (74HC2G17, RZ7899, AUIPS2041 stock 0). Keep alternates.

## 7. Statements in repo/research/other_miata_pnp_boards.md checked against ext/

| Line | Statement | Result |
|---|---|---|
| 14 | Hellen64 1990-95: STM32F407ZGT6 | Correct for NA6 rev D only (bom_replace_hellen64_NA6_94-d.csv:U105). Rev C is F407IGT6 LQFP176 (C33993). NB1 (a-c) and NA8-96 use F407ZGT7 |
| 15 | Hellen72: F407IGT6 | Correct (NB2 e, f) |
| 16 | uaEFI: STM32F429VIT6 | Stale: module default is F429VIT6 (mega-mcu100 BOM) but uaEFI rev F3 BOM replaces it with STM32F407VGT6 ("very cheap"); PRO is F7 per wiki |
| 20-21 | every open STM32 is suffix 6; nobody uses suffix 7 | **Wrong**: Hellen64 NB1 (rev a, b, c) and NA8-96 use STM32F407ZGT7 (JLC C1337111, -40..+105 C, USD 27.80 @1, ext., stock 34) |
| 34 | rusEFI Hellen output module 0.3: AUIPS2041L | Module default is right (output-BOM.csv C113610), but every Miata board BOM replaces it with ZXMS6005SGTA (C174042); AUIPS2041LTR is stock 0 at JLC. The "1.4 A less than two injectors" remark applies to a part not fitted |
| 59 | Hellen64 on-board LSU, 12 V to heater via board connector | Consistent with wiki options port (2D +12 V) |
| 132-134 | BOM file names / commit 5076e80 | Files exist; commit matches ext/hellen-one |
Not re-checked: lines 102, 103 (paired-injector firing; the daughterboard docs depend on it, owned by other audits), line 42 (forum).

## Sources actually read
- ext/hellen-miata-NA6, -NB1, -NB2 (README, bom_replace*, kicad_pcb layer tables, releaseNotes.md, connector-mapping.txt), ext/hellen-one/modules/*/BOM.csv, work/.../modsch/*.pdf (images out03_inj.png, out03_v12prot.png).
- github.com/rusefi/uaefi (changelog.md, bom_replace_uaefi-f3.csv, INJ6/IGN6 sheets, kicad_pcb layer table); rusefi/hellen-miata-NA8 bom; wiki raw pages: Hardware, ECU-Comparison, uaEFI, Proteus, microRusEFI-Manual, Hellen64-Miata-NA6-94, Hellen-NB1, Hellen-NB2, Hellen-NA96, Miata, Royalty.
- GitHub issues: hellenNA6_issues 20, 21, 22, 27; hellen-NB1-issues 8, 15, 25, 29, 30, 32; hellen-NB2-issues 23, 31, 38, 41; andreika-git/hellen-one 118, 119, 360, 362, 378; rusefi/rusefi 3558, 3559; rusefi/uaefi 42, 44, 78, 112, 114; mck1117/proteus 125.
- shop.rusefi.com product pages (uaEFI, nano, uaEFI121, super-uaEFI, Huge, Proteus, microRusEFI), prices as of 2026-11-16.
- tools/lcsc.py live lookups C1337111, C174042, C113610, C2649436, C719073.

## Not checked
- Frankenso and Prometheus (wiki raw pages returned nothing); Proteus/microRusEFI schematic parts (only wiki/issue statements); Hellen NA6 sale price history; PCB outline sizes; ZXMS6005SG datasheet clamp voltage / current limit (download failed); layer count of NA8-96 (not opened); alphax family; hellen NA6 board file connector map vs doc line 102; clones and reseller prices of Hellen boards.
