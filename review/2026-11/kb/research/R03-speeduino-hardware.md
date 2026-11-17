# R03 - Speeduino hardware, especially the Miata plug-in boards

Status: finished 2026-11-16 (partial; see "Not checked").

## Summary (10 lines)

1. The official Speeduino NA6 PNP v1.3 (1989-95, 48-pin) is an Arduino Mega 2560 on a 2-layer-class carrier with 4 x VNLD5090 dual low-side drivers, 2 x TC4424A ignition buffers, 1 x VN5160S fuel-pump high-side, MC33814 (5 V supply/relay function), SP720 ADC clamp array, MPX4250 + KP234 (baro). VERIFIED from BOM/netlist (files below).
2. No knock, no sequential-capable cam/VR conditioning beyond RC+pullup, no CAN, no wideband controller, no alternator/VVT. Wideband = outside 0-5 V controller into the stock O2 wire (wiki, VERIFIED).
3. Official store does not sell a Miata PNP (speeduino.com/shop shows only Dropbear V2 $420, v0.4 PCB $10, kit $145, 2.5 bar MAP $40; fetched today). Miata units come from resellers: SpeedyEFI NA6 kit $449-489, NA8 kit $399 (out of stock); Alex Engineering NA/NB/NBfl EUR 325 (+EUR 70 optional LSU 4.9 CJ125 controller, +EUR 20 Bluetooth).
4. Direct price comparison: this project's $399 with LSU 4.9 on board and rusEFI is at or below the Speeduino PNP price points, and well below the MS3Pro class ($830-1,350).
5. Field complaints: fuel-pump driver killed when the ST_SIG fuse was not pulled (install trap); dead 5 V supply (MC33814 area) giving no prime without USB; unexplained instability >5000 rpm in full-sequential, finally traced by one vendor to noisy unshielded Hall CKP/CMP wiring and fixed with a Schmitt-trigger input board.
6. Lessons already visible in revisions: v1.3 (2023) added a 40 V TVS on the supply (SMBJ40A), 100 V Schottky flyback diodes on idle/boost/fan outputs, and a baro sensor; v1.0-1.2 had none of these.
7. Repo statements about Speeduino in other_miata_pnp_boards.md: all that I could check were correct; two wording/precision points listed below.
8. Speeduino hardware is CERN-OHL-S (strong reciprocal); this project is MIT: do not copy Speeduino circuit files.

## 1. Official NA6 PNP v1.3 (files: ext/speeduino-hardware/PNPs/Miata NA6/Latest/; work/R03-speeduino-hardware/na6/v13/)

Latest upstream change: git history of PNPs: "NA6 PNP v1.3 files" 2023-05-22; end plates 2024-10-08 (VERIFIED, api.github.com commits for path PNPs, fetched today).

| Block | What it is | Source |
|---|---|---|
| MCU | Arduino Mega 2560 plugged on 4 headers (XA1), Mega's own USB | BOM XA1; nets VERIFIED |
| Injectors | 2 x VNLD5090-E (U2: INJ1,INJ2; U4: INJ3,INJ4), input 1k series (R5,R6,R17,R18). No external clamp: only 1N4448 + LED + 2.4k indicator chain to +12V. Clamp = the chip's own: 41/46/52 V min/typ/max (VIN=5 V, ID=1.6 A) per third-party copies of the VNLD5090-E datasheet (search summary; UNVERIFIED for ST primary) | NA6_v1.3_nets.txt (INJ-n-OUT), BOM |
| Ignition | 2 x TC4424A (U3: IGN1, IGN2 to stock connector J1.4/J1.28 via 2.4k; U10: IGN3, IGN4 to header J6 only, not on stock connector) = logic-level 5 V igniter drive, no coil driver on board | nets |
| Idle / boost / fan / tach | VNLD5090 U7 (idle J1.23 with D15 100 V SMB flyback; boost J1.47 with D16), U9 (fan J1.33 with D17; tach via jumper JP1 to J1.16, 100k pull-up to 12 V). Flyback diode NBRS2H100T3G added in v1.3 | nets, BOM v1.2 vs v1.3 diff |
| Fuel pump | VN5160S-E (U8) on stock "ST_SIG" pin J1.2; wiki says fuse must be removed before power-up (fuse removal trips the smart FET) | nets; wiki MX5_PNP.md |
| Inputs | SP720ABTG 14-ch diode array (U6) on ADC lines, each with 470R + 0.22uF (TPS, CLT, IAT, O2, battery, MAP...). Crank/cam: 1k pull-up + 220R + 1nF-class RC, no Schmitt/conditioner IC | nets, BOM |
| MAP / baro | MPX4250AP on board (250 kPa abs; wiki says up to 1.5 bar boost) + KP234 baro (U11) added v1.3 | BOM |
| Supply | 1N5818 (D12) series reverse diode, 14D220K MOV (RV1, 22 V class), SMBJ40A TVS (D23, new in v1.3), polyfuse 0ZCM0008FF2G on sensor 5 V (F1), MC33814 + FZT753 PNP (Q1) + 22 uF/10 uF caps. Dead-5V forum case blamed MC33814 area | BOM, nets, forum t=6453 |
| Connector | J1 TE 174917-1, BOM has NO Digikey/Mouser part number (blank cells) | BOM VERIFIED |
| Case | Reuses stock ECU case; repo has 3D-print/DXF back plate and end plate (MX5-PNP-Backplate/Endplate .stl/.dxf) | Case/ directory (INFERRED use) |
| Missing | knock input (base tune knock_mode Off), CAN, wideband controller, sequential-spark COP outputs on stock connector, VVT/alternator/VSS handled only as GPIO | BOM, tune |
| Pins | wiki pin chart still mentions ULN2803 and a DRV8825 stepper; v1.3 has neither (documentation drift) | MX5_PNP.md vs BOM |

## 2. Base tune facts (VERIFIED, speeduino/Tunes Mazda/NA6 PNP base tune.msq, fetched today)

injLayout "Paired", alternate "Alternating", divider 2, nCylinders 4, trigger "4G63 / Miata / 3000GT", sparkMode Wasted Spark, reqFuel 12.7 ms, dwell run 4.0 / crank 6.0 ms, baroPin A12, knock_mode Off.
Firmware speeduino/fuel_calcs.cpp comment: "Default is 1 squirt per revolution ... in a non-sequential 4-stroke setup you cannot have less than 2 squirts" (VERIFIED).

## 3. Sold boards, prices, buyer experience

| Vendor / board | Price (today's fetch unless noted) | Contents / options | Source |
|---|---|---|---|
| SpeedyEFI NA6 "full kit" (1989-93) | $449 to $489 (aluminium TPS bracket option +$40) | NA6 PNP ECU, AFM delete plug, GM IAT, 8 ft MAP line, BMW vTPS, printed TPS adapter, vTPS adapter harness | speedyefi.com page, VERIFIED, kb/research/files/R03/sp_na6.html |
| SpeedyEFI NA8 (1994-95) | $399, shown out of stock | ECU preloaded, AFM delete plug pinned for IAT, GM IAT, 10 ft vac line; fuel pump pin A9 | sp_na8.html VERIFIED |
| Alex Engineering (Poland): NA 93-94, NB, NBfl | EUR 325 base; +EUR 70 CJ125-based LSU 4.9 controller with harness (no sensor); +EUR 20 BT; EU shipping EUR 10-15 (forum post 2024-09-22 by the maker; price is a single-source claim) | fits stock case after cutting holes for USB and MAP; extra COP outputs, boost, baro, immo input; ships with drivable base map | mx5nutz thread (nutz.html), UNVERIFIED (forum) |
| Fishdog/UA4C Seawolf (generic, VR conditioner + 2 ft harness) | about $300 (forum post, Mazdas247, undated) | not Miata-specific | UNVERIFIED |
| Loopy Engineering NB breakout board (Tindie, UK) | $20 bare, $85 with connector, sold out | passive breakout, 4-layer, no protection | page fetch tindie today, VERIFIED page |
| Speeduino official store | Dropbear V2 $420; v0.4 PCB $10; v0.4 component kit $145; 2.5 bar MAP $40; spare Dropbear connectors $20; Miata PNP: none listed | | speeduino.com/shop via page fetch |
| Comparison (not Speeduino) | AMP/DIYAutoTune MSPNP2 NA6 $829.99; MSPNP-Pro NA6 from $1,149.99; AMP NB2 with wideband $1,349.99; VEMS NA $1,245; Haltech Elite 750 + adaptor $1,489.50 | | web search results listing vendor pages; not opened one by one: UNVERIFIED prices |

Praise (SpeedyEFI NA6 reviews, 12 ratings, 4.67/5): easy install, runs first time on base tune, supportive vendor, good value, tune preloaded; "plug and play with sensors included". Complaints: preloaded tune built on April 2018 firmware (2019 review); auto-transmission/4-pin vTPS cars do not fit the supplied vTPS (1-star 2021); forgetting to pull the AT/ST_SIG fuse (killed pump driver; owner had to jumper the pump); email support slow (vendor says use Facebook group); support is by Facebook/Discord, not tickets. NA8 reviews: idle control and starting "a little lacking at first compared to Megasquirt". (sp_na6.html, sp_na8.html VERIFIED.)

Forum experience (Speeduino forum, read today, files thread_*.html):
- t=4583 (2021): "hundreds out there", problems "generally user error"; owner who killed the pump driver by not removing the fuse replaced the IC himself; UA4C owner had to add a flyback diode to the IAC.
- t=6453 (2024): 1990 car, fuel pump would not prime and fan did not run without the USB lead connected; the board's 5 V rail measured 1.13 V key on, 0.63 V key off; responder pointed at MC33814 (sources the 5 V); fixed by a bypass wire. One report, root cause not independently confirmed (INFERRED regulator fault).
- t=6281 (2024-2025): NB/NB2 boards run unstably above ~5000 rpm in full sequential; semi-sequential workaround; sync-loss counter stayed 0; a MK1 owner gave up and returned to stock ECU. Maker's later finding: Mazda CKP/CMP wiring is unshielded Hall/open-collector, RC filter insufficient, fix is a Schmitt trigger (MAX9926, op-amp, or 74HCT14), his first circuit inverted polarity and made starting hard until edges were switched. Developers could not reproduce on the bench. (Forum statements: UNVERIFIED as to root cause; the symptom is reported by at least three people.)

## 4. Early-revision lessons

- v1.0, v1.1 (2017-2018 dates in xls properties), v1.2: BOM strings contain no TVS or power-input varistor part beyond the MOV, no flyback Schottky on idle/boost/fan, no baro sensor. v1.3 adds SMBJ40A-Q TVS (D23), 3 x NBRS2H100T3G flyback diodes (D15-D17), KP234 baro sensor (U11) and removes four 10R resistors (R13,R14,R62,R63). VERIFIED by BOM diff of NA6_v1.2_BOM.tsv vs NA6_v1.3_BOM.tsv; v1.0/1.1 by string search of xls. WHY they were added is INFERRED (no changelog in repo).
- Older boards: forum says injector-pair jumper traces must be cut for sequential on early NA6 PNP (search summary; UNVERIFIED).
- Dropbear V2 is the only official board with CAN (Teensy 3.5) per wiki Hardware_requirements.md (VERIFIED, local clone).

## 5. Check of repo/research/other_miata_pnp_boards.md statements about Speeduino

| Statement | Result |
|---|---|
| NA6 PNP v1.3 processor "Arduino Mega 2560 plugged onto the board", no temp spec | Correct (BOM XA1; nothing in files states a temperature). |
| "two VNLD5090 (dual), four channels" for injectors | Correct for injectors (U2, U4). Board has four VNLD5090 in total (U7 idle/boost, U9 fan/tach too); not wrong, but easy to misread. |
| Driver's own clamp 41 to 52 V; "no clamp parts outside it"; "diodes on that sheet feed the indicator lights" | Correct against the netlist (D3-D10 chain from +12V via 2.4k + LED + 1N4448 to the INJ pin; orientation by KiCad convention, INFERRED). The 41-52 V figure is for VNLD5090-E (via third-party datasheet copies); the repo cites the VNL5090N3-E datasheet, a sibling part; minor. |
| "Both Speeduino board and ST put a 1 kOhm series resistor at each driver input" | Speeduino half VERIFIED (R5,R6,R17,R18,R39,R40,R48,R49 = 1k, with 100k pull-downs). ST half NOT checked (datasheet download failed); UNVERIFIED. |
| Wideband "none on board; any outside controller's 0-5 V output, on the stock oxygen-sensor wire" | Correct (wiki; O2_Sensor net J1.42 with 470R + 0.22 uF into SP720). |
| Paired injectors: one VNLD5090 channel per pin; tune "Paired", "2 squirts, alternating"; firmware "Default is 1 squirt per revolution" | Correct (tune divider 2, alternate Alternating, fuel_calcs.cpp). |
| "Its board file ... 2U 2V 2Y 2Z" pin names | Not checked: J1 is numbered 1-48 in the board file, Mazda letter names need a mapping table I did not find. UNVERIFIED. |
| "Speeduino NA6 PNP ... board notes: gitea.../MX5_PNP.md" | Exists; note it is the 2022 wiki copy and out of date in places (ULN2803, DRV8825 in pin chart; "1.5 bar" vs 2019 manual "1 Bar"). |
No wrong statement found.

## Implications for this project

1. (cost/ux, info, high) Price positioning: $399 assembled with on-board LSU 4.9, 2-3x injectors/ignition safety stack, USB-C compares favourably with SpeedyEFI NA8 $399 / NA6 $449-489 (no wideband, no AFM-delete/IAT/TPS bits in NA8 case beyond a plug) and Alex Eng. EUR 325+70 for wideband. Evidence: vendor pages above.
2. (ux, medium) Bundle contents buyers like: AFM-delete plug pinned for an IAT sensor, IAT sensor, vacuum line, vTPS adapter harness, base tune loaded. For this project the stock AFM is replaced by MAP on board; check the product page lists IAT solution and vac line (website/ not read by me).
3. (risk, medium) CKP/CMP conditioning: this project's Hall inputs are 1k pull-up + 4.7k series + 1 nF (design.py 433-446), no Schmitt/comparator, same class as Speeduino's RC. Field reports of rpm spikes/instability in full sequential with unshielded Mazda wiring. Suggest keeping a hardware option (or spare pads) for a 74HCT14/comparator stage and a firmware-side trigger filter default; evidence UNVERIFIED root cause, three independent reports. Confidence medium-low.
4. (ux/doc, medium) Fuel pump: Speeduino's famous trap is fuse removal. This project's INSTALL should say whether any fuse must be pulled (check other audits' scope). Confidence medium; evidence wiki + 3 forum reports.
5. (risk, low) 5 V rail failure with no USB: they use an MC33814 + pass transistor; one failure report. This project uses a different supply; no action beyond keeping a fault-tolerant rail. Info.
6. (supply, info) Stock 174917-1 harness connector has no purchasable source even on Speeduino's BOM (blank cells), confirming repo's own supply risk.
7. (info) What Speeduino gives up for 'far fewer parts': no sequential spark on stock connector (IGN3/4 only on header J6), no knock, no CAN (except Dropbear), no wideband, no alternator/VVT, passive injector clamp only (chip clamp 41-52 V), supply TVS only since v1.3. This project's extras are real differentiators but also the parts that have never been run.

## Sources actually read

- ext/speeduino-hardware/PNPs/Miata NA6/Latest/*.sch, BOM xlsx (via work/ TSV), Case/, README.md; Prior versions v1.0-v1.2 BOMs
- work/R03-speeduino-hardware/na6/v13/NA6_v1.3_nets.txt, _BOM.tsv, _footprints.csv (derived from the .kicad_pcb)
- work/R03-speeduino-hardware/web/MX5_PNP.md; kb/research/files/R03/Speeduino_mx5.pdf (manual, 2019, 44 pp, text mx5.txt)
- https://raw.githubusercontent.com/speeduino/Tunes/master/Mazda/NA6%20PNP%20base%20tune.msq ; speeduino/speeduino fuel_calcs.cpp (work/.../tunes)
- https://speedyefi.com/product/miata-89-93-na6-full-plug-and-play-kit/ , .../94-95-na8-miata-plug-and-play-ecu-kit/ (files sp_na6.html, sp_na8.html)
- https://speeduino.com/shop/ (page fetch), https://speeduino.com/forum/viewtopic.php?t=4583, 6453, 6281 (+ page 2 of the last two)
- https://www.mx5nutz.com/threads/speeduino-pnp-for-nbfl-nb-i-na-project.391107/ (nutz.html)
- https://www.tindie.com/products/loopyengineering/nb-01-05-ecu-breakout-board-mazda-mx5-miata (page fetch)
- Search summaries only: VNLD5090-E datasheet copies, AMP/DIYAutoTune prices.
- repo/scripts/design.py lines 400-446; repo/research/other_miata_pnp_boards.md

## Not checked

- Dropbear V2 and Core4 schematics, UA4C files (no time; only wiki listing). Community Miata boards beyond Alex Engineering and SpeedyEFI (pricing for Alex's current site not read: alexengineering.pl store page gave only category counts).
- ST primary datasheet (download failed): ST's input-resistor recommendation, VNLD5090 clamp exact table.
- Mazda letter-pin (2U, 2V, ...) to J1 number mapping; reason for MC33814 function and R13/R14/R62/R63 removal.
- MOV 14D220K ratings (18 Vdc class, from memory only, UNVERIFIED) versus 24 V jump start.
- SpeedyEFI NB availability; DIYEFI (named by a forum poster as offering NB with sequential and optional wideband) could not be found.
- The Speeduino NA6 PNP v1.3 schematic PDF text layer is empty; nets were taken from the PCB file instead.
