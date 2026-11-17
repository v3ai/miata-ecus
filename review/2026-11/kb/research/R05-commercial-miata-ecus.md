# R05 - Commercial plug-in and standalone ECUs for 1989-2005 Miatas (market table, read 2026-11-16)

## Summary
1. At 399 USD the product is cheaper than every assembled Miata plug-in ECU found today (cheapest verified: DIY-EFI Speeduino NB2 GBP 400 ex VAT = about 520 USD at an assumed 1.30; ME221 GBP 579 ex VAT; BMM 749 USD; AMP 1199.99 USD; EMU Black + adapter 1393 USD; Link 1595 USD; Haltech S2 2130 USD special).
2. Only DIY routes undercut it: rusEFI uaEFI board 275 USD + 20 USD Miata breakout board (Tindie) + sensors, unverified eBay Speeduino NA adapters (about GBP 250, hearsay). So "the most affordable Miata EFI" is NOT defensible as an absolute; "the lowest-priced assembled plug-in with built-in wideband" is, today.
3. Real cost of the product: 399 + LSU 4.9 sensor (119.20 USD ECUMaster USA kit price is the only verified sensor price) + IAT sensor if MAF is deleted (ME sells it for GBP 12-20) + optional TunerStudio licence (50-80 USD, secondary source) = about 530-600 USD before any tune. Competitors with onboard wideband need the same sensor.
4. Haltech and ECUMaster adapters, Link, ME, AMP, BMM all cover most NA/NB variants; Haltech excludes 1996-97 US OBD-II NA and names NB only as "00-04 Aust, 01-05 USA".
5. Plug-in vendors ship IAT sensor and aux plug (Haltech) or a harness (BMM wideband adapter, USB cable). Link includes USB cable and 7 bar MAP; ME221 includes only board + vacuum hose.
6. No NB 1999-2005 stock-ECU reflash tool found (EcuTek FAQ covers NC/ND; unverified for NB). So standalone is the only real alternative on NB.
7. rusEFI's own shop sells no Miata plug-in today (only NC 120-pin superseal adapter 50 USD, Honda OBD1, GM E38X, E92X).

## Market table (all prices read 2026-11-16 unless stated; tag VERIFIED unless noted)
| Product | Years | Price | In the box / notes | Source |
|---|---|---|---|---|
| This product | 1989-2005 | 399 USD | assembled, MAP, wideband controller on board, USB-C; LSU sensor and IAT not included (per review brief) | review brief |
| Link G4X MX5Link NB1X (RAV Performance, US) | 1998-2000 NB, manual only, non-VVT | 1595 USD | onboard 7 bar MAP, USB tuning cable included, sequential, 5D boost, antilag/launch/flat shift, knock windowing, 512 MB log, CAN, QuickTune, fits OEM case; no wideband listed | pages/www_ravperformance_com_products_mx5link-mx5nb1x.html |
| Link NB2X (RAV) | 2001-05 VVT NA + non-VVT Mazdaspeed | 1595 USD | as above | pages/rav_nb2.html |
| Link NB1X elsewhere | | AUD 2194 (CJ Motor), GBP 1122 ex VAT (Turbozentrum), NZD 2095+GST | from web search snippets only, not read: UNVERIFIED | search results |
| Haltech Nexus S3 PnP kit NA HT-213316 | 1989-95 NA, not 96-97 US OBD-II/SE/Anniversary, manual only | 2800 USD regular, 2520 special (excl tax) | includes Nexus S3 ECU, PnP harness, M14x1.5 IAT sensor + plug, aux 16-pin Tyco; onboard wideband (LSU 4.9/NTK), 4 bar MAP, Wi-Fi, 128 MB log, dual knock, launch, flat shift, traction, 4-cam VVT, flex, 2 CAN, USB-C; 1.6 needs full-range TPS | pages/haltech_ht213316.html (copied to kb/research/files/R05) |
| Haltech Nexus S3 NB HT-213303 | NB "00-04 Aust, 01-05 USA", manual only | 2800 / 2520 special | same | haltech_ht213303.html |
| Haltech Nexus S2 NA HT-212316 / NB HT-212303 | same | 2365 regular / 2130 special | S2: 4 inj, 4 ign, reduced factory functionality vs S3 | haltech_ht212316.html, ht212303.html |
| Haltech Elite 1000/1500 NA harness HT-140872 (harness only) | NA | 495 regular / 395 special | harness, IAT, aux plug; ECU extra | haltech_ht140872.html |
| ECUMaster EMU Black + NB1 adapter (ecumasterusa.com) | 1999-2000 NB1 manual only (adapter) | EMU Black 1169.10 (list 1299); adapter 224.10; EMU Classic 899.10 | adapter box: adapter + instructions, ECU separate; EMU Black has built-in 4 bar MAP and wideband controller (add a Bosch 4.2/4.9 sensor); base map and manual listed; no NA or NB2 adapter found in the shop catalogue | ecumasterusa_products_p1.json, ecu_nb1.js |
| ECUMaster WHP LSU 4.9 sensor kit with harness | | 119.20 USD | | same JSON |
| Motorsport Electronics ME221 PnP (BBR, UK) | NA 89-95, NB 99-00, NB2 01-05 | GBP 579.17 ex VAT (about 695 inc 20% VAT, INFERRED) | board + vacuum hose + stickers; 21 psi MAP, sequential on 1.8, DSP knock, closed-loop boost, launch, MEITE software, rolling-road base maps; options: IAT + plug GBP 20, IAT boss GBP 12, VTPS plate GBP 29.17 (NA); no wideband; buyer must remove ECU | bbr_me221-*.js |
| DIY-EFI CORE4 Speeduino NB2 (UK) | 2001-05 3-plug | GBP 400 ex VAT / 480 inc | daughterboard fits factory case, firmware + base map, TunerStudio; options wideband controller+harness GBP 70, +sensor GBP 120 total, boost solenoid kit GBP 35; 3 in stock | diy-efi_co_uk_product_diy-efi-core4-mazda-mx5-0105.html |
| Beer Money Motorsports (BMM) Miata ECU | NA 90-95, 96-97, NB1, NB2 | 749 (NA) / 775 (NB) 3D-printed case; +50 billet; most variants backorder only | ECU with case, USB cable, options-port harness, wideband adapter harness; internal wideband, 4 bar MAP, SD log 50 Hz, VVT, boost, flex, DBW, alternator and A/C control; TunerStudio; "off-road use only", "up to 30 days / several weeks" to ship. Firmware not named on page (UNVERIFIED) | bmm_products.json |
| AMP PnP (MS3Pro based, US) | 90-93, 94-95, 96-97, 99-00, 01-05, Mazdaspeed | 1199.99 without / 1349.99 with internal wideband | SD 8 GB, 48-pin options, base map; MSPNP successor (other audit covers) | amp_products.json |
| DIYAutoTune MSPNP | NA | refurbished Gen2 639.99 (other audit) | | diyautotune json |
| rusEFI shop uaEFI | universal | from 275 USD; options pigtails 100, crimp kit 40, enclosure 50, PRO +24 | 1 LSU 4.9 controller on board, knock, SD, CAN, USB; no MAP fitted; ships NJ within 5 business days; NC 120-pin adapter 50 USD; no NA/NB plug-in | pages/rusefi_p_uaefi.html |
| Loopy Engineering NB 01-05 breakout board (Tindie) | 2001-05 | 20 USD | board to wire Speeduino or other ECU into the Miata plug | pages/tindie.html |

## Cost against competitors (USD, parts only, no tune; GBP at assumed 1.30, INFERRED)
- This product: 399 + sensor 119 (or ~80-120) + IAT ~15 (UNVERIFIED) = 530-540; with TunerStudio 50-80 (secondary) up to ~620.
- DIY-EFI NB2 with wideband and sensor: GBP 520 ex VAT (~680 USD), GBP 600 inc VAT (~780).
- ME221 NA + IAT + wideband (not sold) : GBP 600 ex VAT + external wideband ~200 = ~1000.
- BMM: 749-825 + sensor ~100 = ~850-925.
- EMU Black NB1: 1169 + 224 + sensor 119 = ~1512. Link: 1595 + external wideband. AMP: 1350 with wideband. Haltech S2: 2130.
- Tuning costs (dyno tune 300-600) are not verified; they apply equally.

## Positioning and tagline
- Defensible: lowest-priced assembled plug-in with onboard wideband, saving ~120 USD or more versus the nearest assembled competitor (DIY-EFI, UK) and ~350+ versus BMM. Needs re-checking at launch and per region (UK/AU prices of competitors differ; ME221 and DIY-EFI are UK-based and VAT-exclusive prices look lower than they are).
- Not defensible as absolute: "most affordable Miata EFI" is beaten by self-built Speeduino/rusEFI (uaEFI 275 + breakout 20). Suggest "lowest-priced plug-in EFI with onboard wideband" and avoid superlatives that need substantiation.
- Gaps to exploit: only Haltech includes the IAT sensor; ME sells it as option; Link/ECUMaster/Haltech exclude 1996-97 or manual-only variants; BMM is backordered.

## Implications for this project
1. Document supported variants explicitly (manual only, NA 1.6 TPS issue, 1996-97 US) as Haltech does. Documentation.
2. Stock-ECU reflash alternative for 1999-2005 not found: standalone is the only path, so no competition from reflash tools (low confidence, absence of evidence).
3. Ship time: rusEFI ships in 5 business days, BMM 30 days: fast stock is a selling point.

## Sources actually read
Local snapshots in work/R05-commercial-miata-ecus/pages (Haltech product pages, Shopify products.json of ECUMaster USA, AMP/DIYAutoTune, BMM, rusEFI shop, DIY-EFI, RAV Performance, BBR .js endpoints, Tindie). Copies under kb/research/files/R05/. Web searches for Link regional dealers, ME221, MaxxECU, reflash, TunerStudio price (search summaries only).

## Not checked
MaxxECU Miata plug-in (none found), AEM Infinity/Series 2 Miata kits, Adaptronic, Reverant NB unit, ME442 Miata price, warranty terms of every vendor, shipping times other than rusEFI/BMM, Link wideband options, UK/EU/AU Link prices (snippets only), dyno tune prices, TunerStudio price (secondary), Speeduino shop Miata PNP, NA/NB Link US prices beyond NB1/NB2, cheap eBay Speeduino adapters (hearsay).
