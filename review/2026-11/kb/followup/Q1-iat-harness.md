# Q1: a buyable wiring harness for the intake air temperature (IAT) sensor

Date of all live checks: 2026-11-17. Tags: VERIFIED (read today in a primary source), INFERRED, UNVERIFIED.

## Recommendation
Key correction first: only the ORDERED boards (all five) have J3 and JP1. The CURRENT boards (1989-95 rev 0.13, 1996-97 / 1999-2000 / 2001-05 rev 0.9) have no J3: the stock harness IAT wire goes straight to the ECU, and in the current 1989-95 board JP1 is the injector jumper (evidence/cur_mb*/pcb_footprints.csv; motherboards/*/README.md "The separate IAT connector and its jumper are gone"; INSTALL.md section 7). All VERIFIED.
1. **CURRENT boards, and ORDERED boards with JP1 on STOCK (the best route, no J3, no crimping):** buy a sensor-on-adapter that plugs into the car's own airflow-meter plug.
   - 1990-93: Speedy EFI "89-93 Mazda Miata AFM/MAF Delete Plug", variants "With GM IAT" / "Without GM IAT"; the page shows a **$34.00 to $45.00 range** (per-variant price not shown separately today; $45 with sensor is the likely pairing, INFERRED); stock not stated ("restocks every Monday, processing 3-5 days"); a separate GM open-element IAT is $18.00 there; https://speedyefi.com/product/89-93-mazda-miata-vaf-maf-delete-plug/ . Reviews are mixed on wire length (UNVERIFIED, no length given). Or MiataSource "90-93 AFM to IAT Harness", **$45.00**, 4 ft, "100% plug and play to factory AFM connector", GM IAT and weld bung are add-on options (price not read; Shopify JSON read today: one variant, $45.00; availability flag not returned, so in-stock is UNCONFIRMED); https://miata-source.com/products/90-93-afm-to-iat-harness
   - 1994-97: MiataSource "94-97 MAF to IAT Harness" **$45.00**, https://miata-source.com/products/94-97-maf-to-iat-harness (search snippet: 4 ft, plug and play; page price read today, 4 ft not re-read on this page).
   - 1999-2005 (sensor on the stock airbox plug): no off-the-shelf adapter found (not checked at Flyin' Miata / Trackspeed, see Not checked). Use a GM sensor with DIYAutoTune's connector kit and splice to the stock plug's mate.
   - Then enter the GM resistance curve in TunerStudio (INSTALL.md section 7).
2. **ORDERED boards using J3 (JP1 on EXT):** no complete J3 harness was found to buy (search not exhaustive). Two routes. (i) Crimp route: DIYAutoTune "GM Open Element IAT" with 6 in pigtail (IAT-wPiggy, $23.99, in stock, price read today; the pigtail's free-end finish is UNVERIFIED) or with connector and pins (IAT-wConn, $19.99; then the sensor-side pull-to-seat pins must be crimped too), https://www.diyautotune.com/product/gm-open-element-iat-sensor-with-pigtail/ , plus Molex 0436450200 housing (LCSC C114089, 39,381 stock, $0.1095 at 1; DigiKey WM1845-ND 210,865 stock, $0.39 at 1) and two 0430300007 terminals (LCSC C293530, 53,576 stock, $0.0766), crimped with a Micro-Fit crimper; parts about $0.26 plus 0.5-1 m of 20-24 AWG wire. (ii) No crimp tool (ends UNVERIFIED): Molex 214751-1023, a 2-circuit Micro-Fit 3.0 female-to-pigtail lead, 600 mm, 18 AWG, tin; an aggregator page lists DigiKey 1,094 in stock at $3.45 and Mouser 637 at $3.12 (not read on DigiKey/Mouser, both block this machine); solder-splice to the sensor pigtail; total about $27. Also the J3 header the seller must fit: the manifest part C587650 is Molex 43650-0**2**02 (gold), LCSC stock 0; the tin 43650-0200 is LCSC C192562, 7,187 in stock, $0.5472 at 1 (tools/lcsc.py search today) and matches the tin terminals C293530 (avoid a gold header with tin terminals if possible).
3. Seller side: stock 1 housing + 2 terminals per board and crimp the lead (about 10 minutes with a Molex-type crimper; INFERRED). Alternatively point buyers to the Speedy/MiataSource adapter (JP1 = STOCK).
4. Do not change J3 in the next revision: it no longer exists on the current boards. Do not adopt a pluggable terminal on the ordered footprint: JLCPCB stocks none at 3.0 mm pitch (see Option D).

## Options compared
| # | Option | Vendor / part | Price (2026-11-17) | ECU end | Works with | Crimp tool | Verdict |
|---|---|---|---|---|---|---|---|
| A | AFM-delete adapter + GM IAT | Speedy EFI 89-93 delete plug w/ GM IAT | $45.00 | Mazda AFM plug (pigtail to sensor) | Current boards; ordered with JP1 STOCK; 1990-93 | no | Best for 1990-93 |
| A2 | AFM-to-IAT harness | MiataSource 90-93 / 94-97, 4 ft | $45.00 (sensor, bung extra) | Mazda AFM plug | same, 1990-97 | no | Good |
| B | Sensor + pre-wired pigtail | DIYAutoTune IAT-wPiggy | $23.99 (verified) | 6 in pigtail, ECU-end finish not stated (UNVERIFIED) | ordered J3 after you add Micro-Fit | yes (Micro-Fit) | OK |
| B2 | Sensor + connector + pins | DIYAutoTune IAT-wConn | $19.99 | uncrimped | same | yes | cheapest |
| B3 | AMP kit with bung, 8 ft wire, 3 pins | DIYAutoTune PNP-IAT-AL / -SS | $34.99 | Weatherpack-style pins for AFM plug | AFM plug | yes (Weatherpack) | not for J3 |
| C | Molex receptacle-to-pigtail lead | Molex 214751-1023, 600 mm, 18 AWG, tin (aggregator page; its end description is inconsistent) | $3.12 Mouser (637) / $3.45 DigiKey (1,094) per aggregator dated 2026-11-15; distributor pages not read | 2-circuit female Micro-Fit, free end | J3 mate (same family; end style UNVERIFIED) | no (solder splice) | plausible, confirm before ordering. The 214755 series (e.g. 214755-1022, DigiKey $3.37, 938 stock, 20-week lead) is receptacle-to-receptacle, NOT a free-end lead |
| D | Change J3 to 2-pos pluggable block | JLC-stocked 3.5 mm parts (e.g. C395830 $0.0874, 70,293 stock) | n/a | flying leads | pitch 3.5 vs J3 3.0 | no | does not fit |

## Evidence
### J3 on the ordered boards (VERIFIED)
- ord_mb8993/9495/9697/9900/0105 pcb_footprints.csv: J3 Molex_Micro-Fit_3.0_43650-0200_1x02_P3.00mm_Horizontal, LCSC C587650, at (155.0, 202.3), rotation 180, with a 3.0 mm NPTH peg at (153.5, 206.62); JP1 "IAT SEL" 1x3 header. pcb_pads.csv: pad 1 = IAT_EXT (x 155.0), pad 2 = GND (x 152.0); pad 1.5 x 2.02 mm, drill 1.02 mm. Netlist: IAT_EXT = J3.1, JP1.3; HARN_IAT = J1.2P/3K etc, JP1.1; IN_IAT = JD2.7, JP1.2 (ord_mb8993/pcb_nets.txt).
- Part: manifest MPN is Molex 43650-0202 (436500202, gold; footprint is named 43650-0200), manifest line C587650, LCSC stock 0 (kb/parts_manifest.md:344; tools/lcsc.py today: "EXTENDED, stock 0, $0.8011"). Mating housing 43645-0200 and terminal 43030-0007 per ordered-boards/2026-11/INSTALL.md:73 and additional-parts/shopping_list.html:145-148 (q 2 terminals for the IAT lead). That 43645 mates with the 43650 header was not confirmed from a Molex drawing (molex.com unreachable, 3 attempts); search results describe 43650 as the single-row 3.0 mm right-angle header and 43645 as the single-row receptacle housing of the same family: INFERRED, high confidence, no drawing read.
- Housing C114089 (436450200): LCSC page JSON today, 39,380 in stock, $0.0686 at 5000 (tools: stock 39,381, $0.1095 at 1, $0.0916 at 50). DigiKey 0436450200 (WM1845-ND): 210,865 in stock, $0.39 at 1, $0.334 at 10, $0.2839 at 100 (page fetch of digikey.com page today). Terminal C293530 (430300007, 20-24 AWG, tin): 53,576 stock, $0.0766 (tools). Gold-plated 430300003 C277623 $0.0507 at best, 46,670 stock.
- Pin 1 side of J3 was not checked against a Molex drawing (kb/boards/B17:51); a lead made from the repo's pin map should be beeped out before use (INSTALL.md:79).

### Which cars need an external IAT (VERIFIED from repo)
- INSTALL.md section 7 (repo/INSTALL.md:~296-312): stock airbox and meter fitted -> nothing; 1990-93 meter removed -> GM open-element sensor on an adapter into the meter's plug (MiataSource, Speedy EFI); 1994-97 meter removed -> sensor wired to the two IAT wires at the meter's plug (AMP: third and fourth wire on 1994-95; confirm with a meter); 1999-2005 stock airbox removed -> sensor on the stock IAT plug; turbo: after the intercooler.
- Recommended sensor: GM open element, 3/8 NPT (ordered docs: "M12 x 1.5 open element" in additional-parts/shopping_list.html:147: this contradicts the GM 3/8 NPT sensors every vendor above sells; a mismatch to fix in the docs, INFERRED).

### Firmware assumptions (VERIFIED, repo/firmware/board/miata_pins.h:74-77, miata_board.cpp:20-39)
Pull-up 2.7 kohm to 5 V, ADC-side load 5.6k + 10k = 15.6 kohm to ground. Effective bias 2.30 kohm, effective supply 4.262 V (computed). Calibration is not in firmware: the user enters the curve (INSTALL.md section 7). Example: GM sensor at 87 F, 2,238 ohm -> pin voltage 2.10 V (recomputed, INFERRED).
DIYAutoTune calibration data read today: -40 F 100,700 ohm; 87 F 2,238 ohm; 146 F 177 ohm; also quoted "300 ohm at 210 F, 3400 ohm at 70 F"; 3/8 NPT; wiring A signal, B ground; connector pins pull-to-seat (cannot be pushed in from the back).

### Vendors read today
- DIYAutoTune GM Open Element IAT: $15.99 sensor only, $19.99 with connector & pins, $23.99 with 6 in pigtail (JSON-LD; page diyautotune.com/product/gm-open-element-iat-sensor-with-pigtail). GM IAT Connector & Pins $4.99. AMP kit with bung and 8 ft wire $34.99 (PNP-IAT-AL, PNP-IAT-SS).
- Speedy EFI: $34 / $45 variants, "Restocks every Monday, processing 3-5 days".
- MiataSource: $45.00, 4 ft, InStock.
- Not found: any Micro-Fit-ended IAT harness; no vendor sells the sensor with Micro-Fit.

### Option D, flying-lead terminal at J3 (VERIFIED footprint, search results from tools/lcsc.py)
JLC-stocked 2-position pluggables found are 3.5 mm pitch (C395830 DORABO DB2ERC-3.5-2P-GN 70,293 stock $0.0874; C441321 KF2EDGV-3.5-2P 23,797 stock $0.0589; C560212 plug screw type 11,068 $0.187). All extended parts. The search for 3.0 mm pitch returned nothing. The J3 pads are 3.0 mm apart with 1.02 mm drills and a 3.0 mm peg hole: a 3.5 mm part is 0.5 mm off pitch and would need a new footprint, so it only makes sense in a new revision, and the current boards have no J3 at all.

## Sources read today
- repo/INSTALL.md, repo/README.md, repo/motherboards/*/README.md, repo/ordered-boards/2026-11/{INSTALL.md,README.md,additional-parts/shopping_list.html}, repo/firmware/board/miata_pins.h, miata_board.cpp
- evidence/ord_mb*/pcb_footprints.csv, pcb_pads.csv, pcb_nets.txt, evidence/cur_mb*/pcb_footprints.csv; kb/parts_manifest.md, kb/boards/B17
- tools/lcsc.py: C587650, C114089, C293530, C259786, searches for 43645, 43025, 43030, 3.5 mm pluggables
- https://www.diyautotune.com/product/gm-open-element-iat-sensor-with-pigtail/ ; https://diyautotune.com/products/gm-iat-temperature-sensor-kit-aluminum-bung ; .../gm-iat-temperature-sensor-kit-stainless-steel-bung ; .../gm-iat-sensor-connector-pins
- https://speedyefi.com/product/89-93-mazda-miata-vaf-maf-delete-plug/ ; https://miata-source.com/products/90-93-afm-to-iat-harness ; https://miata-source.com/products/94-97-maf-to-iat-harness
- https://www.lcsc.com/product-detail/C114089.html ; https://www.digikey.com/en/products/detail/molex/0436450200/268974
- Web search snippets only (not page reads): element14 AU 214751-1023, RS 2-way Micro-Fit pigtails, Bosch 0 280 130 039 listings

## Not checked
- molex.com, Mouser, DigiKey cable pages and RS/element14 pages blocked or timed out: no verified Molex order number, length, stock or US price for a pre-crimped 2-circuit lead. Candidates (214751-xxxx female-to-free-end 18 AWG, 300 mm = 214751-2022 per a snippet) are UNVERIFIED; also unclear whether the dual-row 43025 family or the single-row 43645 housing is the right mate for a 43650 header.
- Flyin' Miata, Trackspeed, rusEFI/Hellen and AEM IAT kits: not opened; Bosch 2-pin NTC prices only from snippets (one listing $27-53, resistance curve not confirmed). The 1999-2005 plug adapter: none found.
- Pigtail wire length and bare-end finish of IAT-wPiggy; MiataSource option prices; US shipping.
- Molex crimp-tool price; crimp time of 10 minutes is an estimate.

## Fact-check log (2026-11-17)
Re-verified: J3/JP1 on all five ordered boards, none on current boards (pcb_footprints.csv); J3 pads 3.0 mm pitch, 1.5 x 2.02 pads, 1.02 mm drills, 3.0 mm NPTH peg; pull-up 2.7k and 15.6k load (miata_pins.h:72-77); INSTALL.md section 7; DIYAutoTune $15.99 / $23.99 / $19.99 (SKUs IAT-Sensor / IAT-wPiggy / IAT-wConn, InStock, 6 in pigtail); MiataSource 90-93 and 94-97 $45.00, 4 ft (Shopify JSON); LCSC C114089, C293530, C587650 (stock 0), C395830 via tools/lcsc.py; DigiKey 0436450200 210,865 stock, $0.39/$0.334/$0.2839; no JLC-stocked 3.0 mm pluggable terminal block (3 searches empty; the 3.0 mm hits are Micro-Fit clones that still need crimping).
Corrected:
- J3 MPN is 43650-0202 (gold) in the manifest; tin 43650-0200 = C192562 (7,187 stock) added as the way to fit J3 today.
- Speedy EFI: per-variant price and stock were not shown; downgraded to the $34-$45 range, stock unconfirmed.
- MiataSource: in-stock flag not confirmed (price and 4 ft verified).
- Option C: the 300 mm free-end 214751 idea and the AU price were unconfirmed; 214751-1023 is 600 mm; the 214755 series is receptacle-to-receptacle.
- "About 3 m of 22 AWG" replaced by 0.5-1 m of 20-24 AWG.
- Added the sensor-side crimp need for IAT-wConn and the gold/tin mismatch.
Break attempts: a thermistor has no polarity, so the unverified pin-1 side is harmless; JP1 ships on EXT, so with nothing on J3 the IAT input floats: set the shunt to STOCK unless a lead is fitted.
Still unverified: Molex mating drawing; 214751-1023 end style and live DigiKey/Mouser stock; Speedy per-variant price and wire length; any 1999-2005 adapter; Flyin' Miata/Trackspeed/AEM/Bosch kits; crimp time and tool price; IAT-wPiggy free end.
