# Q4. Complete installable kit: what it contains and what it costs

Date of live checks: 2026-11-17. USD. Arithmetic: `work/followup/Q4-complete-kit-cost/kit.py` (output saved as `out.txt` next to it). Tags: VERIFIED (page or API read today, or computed from verified inputs), INFERRED (reasoned from verified facts, reasoning shown), UNVERIFIED (search snippet, memory, guess; named as such). The parallel IAT note `kb/followup/Q1-iat-harness.md` did not exist when this was written; the fact-checker cross-read it (it agrees on the $45 Speedy EFI / MiataSource adapters and the $19.99 DIYAutoTune sensor with connector, and says J3 exists only on the ORDERED boards; the Molex 43650-0200 header C587650 shows JLC stock 0 today). **Fact-checked 2026-11-17; the corrected numbers are the ones in the text, see "Fact-check log" at the end.**

## Kit contents and cost

### 1. What the install needs, year by year (from `repo/INSTALL.md`, README, `additional-parts/order_all_boards.csv`)

Design state: **CURRENT boards** (rev 0.10 daughterboard; motherboards 1989-95 rev 0.13, others rev 0.9) have the 8-pin JST PUD header J2 for the sensor and no IAT socket (INSTALL.md section 7: "no separate air-temperature plug"; README "Air temperature sensor"). **ORDERED boards** (rev 0.9 daughterboard, motherboards 0.11/0.9/0.7) have a 2x3 Molex Micro-Fit J2 (`ordered-boards/2026-11/INSTALL.md` line 60) and a 1x2 Micro-Fit IAT socket J3 (line 73, mating housing 43645-0200) with a STOCK/EXT shunt JP1. VERIFIED from the files.

| Item | 1989-93 | 1994-95 | 1996-97 | 1999-2000 | 2001-05 | Class |
|---|---|---|---|---|---|---|
| Board set (daughter + year motherboard) | yes | yes | yes | yes | yes | REQUIRED |
| Bosch LSU 4.9 wideband sensor | yes | yes | yes | yes | yes | REQUIRED (INSTALL section 6; closed-loop fuel is on from first start, README line 44) |
| Sensor-to-ECU lead (6 wires) | yes | yes | yes | yes | yes | REQUIRED |
| MAP vacuum hose (INSTALL section 5) | yes | yes, longest run (ECU behind seat) | yes, longest run, tee always | yes | yes | REQUIRED |
| Barbed tee | if cruise control (most) | if cruise control | always | free nipple: not needed | free nipple: not needed | REQUIRED for some cars; include one in every kit (about $0.2) |
| USB-C cable to laptop | yes | yes | yes | yes | yes | REQUIRED (INSTALL "What you need") |
| Case washers/screws, ties | yes | yes | yes | yes | yes | REQUIRED, trivial (S5 says add four M4 screws and washers) |
| Quick-start card | yes | yes | yes | yes | yes | REQUIRED, already in S5 packaging |
| Jumper shunts (6 on 1989-95), pin headers, standoffs, M3 screws, MAP sensor, sockets, harness header | on the board set | on the board set | on the board set | on the board set | on the board set | already inside S3's "hand-fitted parts" line |
| IAT sensor + lead | only if AFM removed | only if AFM removed | only if AFM removed | only if airbox removed | only if airbox removed | OPTIONAL: stock sensor (inside the airflow meter 1989-97, airbox 1999-2005) is read through the harness and stays |
| Variable TPS conversion | manual cars: optional | not needed | not needed | not needed | not needed | OPTIONAL. README lines 213-222: car runs without it; lost: closed-loop idle, throttle-based acceleration fuel, overrun fuel cut; rusEFI then flags the throttle sensor as failed. Not required for a start |
| Fuel-pump wire F/P to 2T | only if AFM removed | | | | | OPTIONAL (INSTALL section 4) |
| O2 weld bung M18 x 1.5 | | | | | | OPTIONAL: only to keep the stock sensor (INSTALL section 6.1) |
| microSD card | | | | | | OPTIONAL: logging only; "a card is not needed to run" |
| D3/D4 SMCJ30A clamps | ordered rev 0.9 daughterboard on 1989-93 only | | | | | seller-fitted, $0.30 each (JLC C224048, stock 11,546 today); goes in the board cost |
| 20-way ribbon cable (J5 add-ons) | | | | | | OPTIONAL |
| Wire and terminals for one-wire-per-injector (1990-93 manual cars, INSTALL.md): about 3 m each of two colours 18-20 AWG and two terminals for cavities 2Y and 2Z | 1989-93 | | | | | OPTIONAL: the car runs on the paired stock wiring; only for track use with 20 mH injectors; not priced; missed in the first draft |

**Customer must still own:** laptop with TunerStudio (free "MS Lite" is the entry edition; the registered edition on efianalytics' own page today is $69.95 on sale, text says "normally $79.95", strike-through $89.95 [VERIFIED page text, list price inconsistent]; the autotune function needs the registered edition per S4/R11, [UNVERIFIED today]); multimeter and timing light (INSTALL); hand tools to remove the ECU, cut the case (tin snips or nibbler, file, drill), a 22 mm / 7/8 in oxygen-sensor socket (UNVERIFIED size, not in the repo); anti-seize (UNVERIFIED which kind: R15 says Bosch specifies a special grease). The **stock ECU case** (the board lives in it; no core is collected, S5 section 4). A ride that is not an automatic, a Mazdaspeed, or a car with a failed MAP/air path is outside the kit (README).

**Sensor facts for the walk-through.** Thread: INSTALL says the LSU 4.9 has "the same M18 x 1.5 thread" as the stock front sensor; supported only by a vendor line that M18 x 1.5 is the standard wideband thread (UPR page via search; no Miata drawing found) [UNVERIFIED for the Miata bung: not checked on any car]. Exact Bosch number: **0 258 017 025** (the number the repo and every aftermarket controller names; 1 m lead, 6-pin plug; R15 section 1.2). Ballenger's page for SNSR-01029 reads "Bosch LSU 4.9 ... with Bosch Connector ... (1m/39.4in length)" and lists the sensor-side receptacle CONN-100322; its Cross References line prints "Bosch Part Number: 0 258 017 025 ( 0258017025 )" and lists CONN-75762 as the mating plug kit [VERIFIED by the fact-check, correcting the first draft]. Cable lengths: the sensor's own lead is 1 m (page: 1,000 mm; shipping weight 0.35 lb); I did not find how far the stock front sensor sits from each ECU position. Working lengths for the lead are guesses: **2 m (1989-93, 1999-2005), 3 m (1994-97, ECU behind the seat)**, so total reach is 3-4 m [UNVERIFIED, nobody measured a car]. If the cable falls short, the fix is a longer seller lead, not an extension: the jointed Bosch plug is the weak point. Weld bung: needed only to keep the stock sensor. AEM 30-3427 is stated by retailers as 72 in (R15, secondary).

**MAP hose.** Barb on the MPX5700AP: OD 4.62-4.93 mm (datasheet drawing p.7, P20); NXP AN1513 recommends 1/8 in ID hose with clamps (P20 item 8, from a search summary of AN1513) [INFERRED fit]. INSTALL says 3-4 mm ID, about 3 m, 4 mm tee. A 3/16 in (4.75 mm) hose is almost the barb diameter and is outside INSTALL's range; I priced 1/8 in (3.2 mm). Length: INSTALL.md line 114 says "about 3 m" with no year split, so the fact-check prices 3 m for every year (the first draft used 2 m for four year ranges, a guess). Routing: firewall plug behind the washer bottle (NA) or the large driver-side grommet (NB): no grommet is needed in the kit; INSTALL says drill the plug or slit the grommet.

**USB-C.** The board's USB-C jack (J4) is 80 mm from the left board edge (INSTALL section 3), in a slot cut in the stock case. INSTALL says to leave a cable plugged in and run it to the glovebox. USB 2.0 is the speed in use (480 Mbps is enough for TunerStudio); the cable limit for USB 2.0 is 5 m so 3 m is within it [INFERRED, standard]. Panel-mount extension: would let the jack live in the trim; no product priced and no fit tested [Not checked]. Laptops with only USB-C ports need C-to-C; same cost class; I priced A-to-C [UNVERIFIED; ask on the order form].

### 2. Prices, three ways

Retail q1 = cheapest reputable in-stock listing found. Seller cost q10 and q30-50 = the vendor's own break where a page showed one; otherwise the q1 price is carried (stated). "Stock" = what the page showed.

| Item | Vendor, part no. | URL | Retail q1 | Seller q10 | Seller q30-50 | Stock shown | Tag |
|---|---|---|---|---|---|---|---|
| Bosch LSU 4.9 sensor 1 m lead (0 258 017 025 by R15) | Ballenger, SNSR-01029 | bmotorsports.com/shop/product_info.php/products_id/1645 | 69.97 | 68.99 | 67.99 (25+), 65.99 (50+), 63.99 (100+) | "In Stock", ships from VA | VERIFIED price; page "Cross References" prints "Bosch Part Number: 0 258 017 025", mating plug kit CONN-75762 (VERIFIED, fact-check); authorisation by Bosch UNVERIFIED |
| Same sensor, mainstream | DIYAutoTune / AMP, "Bosch LSU 4.9 Wideband O2 Sensor" | diyautotune.com/products.json | 109.99 | n/f | n/f | available:true | VERIFIED |
| Same, kit with FCI plug harness | ECUMaster USA 103.20 (sensor + plug and terminals) / 111.20 (6 ft harness) | ecumasterusa.com/products.json | 103.20 | n/f | n/f | available | VERIFIED (not an LSU for this board's plug) |
| Same, other US shops | UroTuning (Nuke Performance, dropship) 119.20; threepiece.us 131.06; Chief Enterprises 151.35 (qty in stock 0) | urotuning.com; threepiece.us; chiefenterprises.com | 119.20 / 131.06 / 151.35 | | Chief 113.51 at 60+ | threepiece "Regularly stocked"; Chief stock 0 | VERIFIED page reads |
| Sensor lead, AEM 30-3427 (X-Series harness) | onefastshop / makperformance AEM30-3427 | onefastshop.com/products/aem-sensor-harness-for-x-series-wideband-gauge-30-0300-30-0334 | 32.36 (list 40.46) | n/f, q1 carried | n/f, q1 carried | page markup shows both InStock and "Sold out" strings; Ridium Works sold out; one earlier note said out of stock | VERIFIED price; stock UNVERIFIED. Other listings: 35.96 (Ridium, SpecialtyZ), 48.99, 49.41 |
| Bosch 6-way plug kit, housing + terminals + seals (D 261 205 356-01) | Ballenger CONN-75762 | bmotorsports.com/.../products_id/2081 | 17.99 | 17.99 (no break below 25) | 16.99 (25+), 16.49 (50+) | In Stock | VERIFIED |
| Bosch plug with pre-crimped 12 in leads | Ballenger CONN-85762 | .../products_id/2082 | 19.99 | 19.99 | 18.99 (25+), 18.49 (50+) | In Stock | VERIFIED |
| JST PUDP-08V-S housing (current boards) | LCSC/JLC C490532 | via `tools/lcsc.py` | 0.2902 | 0.2902 | 0.2902 (0.2446 at 50) | JLC 12,151 | VERIFIED |
| JST SPUD-001T-P0.5 contact x6 | C267125 | | 0.0182 each | 0.0182 | 0.0182 (0.0146 at 1000) | JLC 131,021 | VERIFIED |
| Micro-Fit 43025-0600 housing (ordered boards) | C293525 | | 0.1136 | 0.1136 | 0.1136 (0.0934 at 50) | JLC 55,291 | VERIFIED |
| Micro-Fit 43030-0001 contact x6 | C259786 | | 0.015 each | 0.015 | 0.015 | JLC 2,163,133 | VERIFIED |
| Micro-Fit 43645-0200 1x2 housing (IAT socket J3, ordered boards) | C114089 | | 0.1095 | | 0.1095 (0.0916 at 50) | 39,381 | VERIFIED |
| 22 AWG 6-core wire, loom, heat-shrink | not looked up | | | | 0.55 per m + 0.50 | n/a | UNVERIFIED (R15 estimate: 0.7-1.2 per 1.5-2 m) |
| Silicone vacuum hose 1/8 in (3.2 mm) ID, 25 ft roll | HPS HTSVH3-REDx25 (black HTSVH3-BLKx25 is the same hose, 77.45 on Zoro per a search result) | milkymotorsports.com/products/high-temperature-silicone-vacuum-hose-tubing-1-8-id-25-feet-roll-red (Shopify JSON) | 70.30 | 70.30 | 70.30 (no break found) | stock flag not read | VERIFIED price (fact-check). The Walmart snippet price 8.79 / 6.39 in the first draft is NOT supported and is withdrawn. Alternatives: Vibrant 3/16 in 25 ft, Coyote Direct VIB2102, 46.50 (list 62.50), JSON VERIFIED, ID 4.75 mm is just outside INSTALL's 3-4 mm; Zoro Select 1/8 in ID x 1/4 in OD 25 ft 42.15 (search-result read, UNVERIFIED) |
| Barbed tee, nylon 3/16 in | Thogus TT9333/N 10-pack (Zoro), Zoro Select 25-pack | zoro.com | 0.63 each (6.29 per 10) | 0.63 | 0.17 each (4.15 per 25) | not seen | UNVERIFIED snippets; INSTALL.md wants a 4 mm tee, and a 3/16 in (4.76 mm) barb on 1/8 in hose is a stretch fit: pick a 1/8 in or 4 mm tee instead; price kept as a guess |
| USB-C cable 3 m, USB 2.0, A-to-C | L-Com USBCA2-MM-10FT | l-com.com | 12.79 | 12.79 | 12.15 (25-49) | 145 shown (search-result read) | VERIFIED price tiers by a search-result read of the L-Com page (12.79 for 1-24, 12.15 for 25-49, 11.51 for 50-99, 145 available); StarTech 12.79 Staples, Monoprice 13.88 |
| Case washers / ties | | | n/a | | 0.20 | | UNVERIFIED guess |
| **IAT sensor, GM/ACDelco type, 3/8 in NPT, with Delphi connector side** | Ballenger SNSR-02057 | .../products_id/400 | 15.00 | 13.99 | 13.49 (25+), 12.99 (50+) | In Stock | VERIFIED |
| IAT with pigtail | Ballenger SNSR-02057PK | .../products_id/4173 | 17.00 | 15.99 | 15.49 (25+), 14.99 (50+) | In Stock | VERIFIED |
| IAT, "GM Open Element" with options | DIYAutoTune | products.json | 15.99 / 19.99 with connector+pins / 23.99 with pigtail | | | available | VERIFIED |
| IAT 3/8 NPT weld bung | DIYAutoTune | | 12.99 | | | available | VERIFIED |
| AFM-to-IAT plug-in lead (1989-93) | MiataSource "90-93 AFM to IAT Harness" | miata-source.com/products/90-93-afm-to-iat-harness | 45.00 (sensor and bung extra) | | | InStock in markup | VERIFIED |
| MAF/AFM delete plug 1989-93 with GM IAT / without | Speedy EFI | speedyefi.com/product/89-93-mazda-miata-vaf-maf-delete-plug/ | 45.00 / 34.00 | | | InStock | VERIFIED. 94-98 version 45 / 29 |
| 1989-93 TPS upgrade kit with OEM TPS / with BMW TPS / without sensor | Flyin' Miata 07-360XX | flyinmiata.com/products/tps-upgrade | 99.99 / 249.00 / 55.99 | | | not shown | VERIFIED (JSON). Plug fit to this board not checked. Cheaper: Speedy EFI "VTPS adapter, and BMW type VTPS for NA6" $29.00, in stock (store API read today; contents and fit not read). Kia sensor + printed mount (repo's route): sensor price not found |
| O2 weld bung M18 x 1.5 + plug | Innovate kit via DIYAutoTune | | 12.99 | | | available | VERIFIED |
| microSD card | not priced reliably | | search snippets disagree ($7.95 stale to $27.72); memory prices look volatile | | | | UNVERIFIED; left out of the kit |
| TunerStudio | efianalytics.com/register/browseProducts.jsp | | registered edition $69.95 (sale), Ultra $99.95 (sale) | | | | VERIFIED re-read: registered "TunerStudio MS" $69.95 sale ("Normally $79.95", strike-through $89.95); Ultra $99.95 sale (strike-through $129.95); the page is inconsistent about the list price, so quote the sale price with a date |
| MAP sensor, for reference | JLC/LCSC C90152 MPX5700AP | | 29.15 | | 27.52 (30+) | 155 | VERIFIED (already inside S3) |

n/f = no quantity price found; q1 price carried.

**Counterfeit and authorisation.** I did not find a Bosch authorised-distributor list or an authorised-reseller statement for Ballenger. Genuine-sensor claims on the pages I read are the sellers' own. The safest low-risk step is to buy through one vendor, inspect the laser-etched part number and date code on the first unit against Bosch's datasheet (not done: no unit in hand), and say so in the kit page. Also note the Ballenger page text says the sensor "is only for use with advanced controllers" and calls it a Bosch Motorsports lambda sensor, which is the vendor's wording, not Bosch's. [INFERRED risk, not a finding that it is fake.]

### 3. Seller-made sensor lead (the BOM that makes the numbers)

| Part | Current boards (JST) | Ordered boards (Micro-Fit) |
|---|---|---|
| Bosch plug kit CONN-75762 at 30 | 16.99 | 16.99 |
| Board-end housing + 6 contacts at 30 (LCSC, with 35 % duty applied as an assumption) | (0.2902 + 6 x 0.0182) x 1.35 = 0.54 | (0.1136 + 6 x 0.015) x 1.35 = 0.27 |
| Wire 22 AWG 6-core, 2 m (3 m for 1994-97) at 0.55 per m + loom 0.50 | 1.60 (2.15) | same |
| **Lead total at 30** | **19.13 (19.68 for 3 m)** | **18.86 (19.41)** |
| At q1 / q10 | 20.13 | 19.86 |
| AEM 30-3427 instead | 32.36 | does not fit a Micro-Fit header |

Labour: about 15 minutes to cut, strip, crimp 12 terminals, loom, and continuity-check against the table in `ordered-boards/.../INSTALL.md` line 62 or `repo/INSTALL.md` header map [guess]. Tools not priced: a Bosch BAK terminal crimper (ICT Billet says MCP 1.5K die, R15 [UNVERIFIED]), a JST SPUD crimper or Micro-Fit crimper. Using Ballenger's pre-crimped pigtail (CONN-85762, $18.99 at 25) instead of the plug kit removes the Bosch crimp (+$2) but adds a splice per wire. The JST PUD contacts take 22-26 AWG only and 3 A (P21 item 7: tight against the heater's cold inrush); the Micro-Fit side is 8.5 A and has no such limit. [P21 VERIFIED]

### 4. Cost to make and ship one complete kit, batch 30, per year range

Basis: S3 made cost at batch 30 for the **current design** = $152.9 per set, which includes outbound postage $20.7 (2 lb row, signature, $6.05 cover), packaging $3.3 and the payment fee $11.9 at $399. For a kit I remove the fee and S3's outbound line, and recompute postage, cover and fee at the kit price. Year deltas are S3's (1996-97 +6.0, 1999-2000 +6.0 incl. extra extended line, 2001-05 +2.2). Zone 5. Hose corrected to 3 m of HPS 1/8 in at $70.30 per 25 ft (fact-check).

| Line (USD per kit) | 1989-93 | 1994-95 | 1996-97 | 1999-2000 | 2001-05 | Basis |
|---|---|---|---|---|---|---|
| Board set, S3 batch 30 without fee and without outbound postage | 120.3 | 120.3 | 126.3 | 126.3 | 122.5 | S3 table (152.9 less 11.9 fee less 20.7 outbound = 120.3; plus year delta) |
| LSU 4.9 sensor | 67.99 | 67.99 | 67.99 | 67.99 | 67.99 | Ballenger at 25+ (VERIFIED page) |
| Sensor lead (own build) | 19.13 | 19.68 | 19.68 | 19.13 | 19.13 | section 3 |
| Hose 1/8 in, 3 m (9.84 ft) at 2.812 per ft | 27.67 | 27.67 | 27.67 | 27.67 | 27.67 | HPS roll 70.30 / 25 ft (VERIFIED JSON); was 2.31 / 3.46 from an unverified snippet |
| Tee | 0.17 | 0.17 | 0.17 | 0.17 | 0.17 | 25-pack, UNVERIFIED snippet |
| USB-C cable 3 m | 12.15 | 12.15 | 12.15 | 12.15 | 12.15 | L-Com 25-49 tier (page read via search tool) |
| Washers, ties | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | guess |
| Inbound freight on kit items, 3 % | 3.82 | 3.84 | 3.84 | 3.82 | 3.82 | assumption (no vendor shipping quoted) |
| Duty / tariff | in the board line (35 % of PCB + SMT + SMD, S3) | | | | | kit items are bought in the US; only the LCSC bits carry 35 % (included in the lead) |
| Extra packaging: box 12x12x4 Uline S-4215 $1.00 vs 9x9x4 $0.68; extra fill $0.40 | 0.72 | 0.72 | 0.72 | 0.72 | 0.72 | S5 / R25 prices (saved Uline pages); fill is a guess |
| Outbound: GA commercial 3 lb zone 5 12.12 + signature 4.15 + cover 500.01-600 tier 9.05 | 25.32 | 25.32 | 25.32 | 25.32 | 25.32 | Notice 123 saved text, re-read in the fact-check (zone 5 rows 2/3/4 lb = 10.50 / 12.12 / 13.89; cover 6.05 at 300.01-400, 9.05 at 500.01-600). Parcel about 2.1 lb INFERRED |
| **Total cost to make and ship, before payment fee** | **277.5** | **278.1** | **284.1** | **283.5** | **279.7** | payment fee (about 2.9 % + $0.30 of the selling price) not included |
| Extra labour: lead 15 min + kitting 6 min at $27/h | 9.45 | 9.45 | 9.45 | 9.45 | 9.45 | rate from S3's "$20-30 for 45-60 min" |

**Ordered boards.** Daughterboard rev 0.9 is about $6 cheaper (S3), Micro-Fit lead $0.27 cheaper, so the kit costs about $6.3 less. Add two SMCJ30A at $0.30 on 1989-93. The ordered 1999-2000 board has the 64-pin 176122-6 header at $12-30 against $12.2 for the 76-pin in S3: add $0-18 (S3 section 5). The ordered boards have the IAT socket, so an IAT sensor can plug in at J3 with JP1 on EXT: lead $0.3 in parts (housing C114089 + 2 contacts). On the current boards an external IAT can only be wired into the stock sensor's plug (INSTALL section 7).

**Optional items, seller cost if ever stocked (not in the totals):** IAT 13.49 + pigtail kit 15.49 (SNSR-02057PK includes the sensor) and bung 12.99 = about 28.5 for the sensor and bung; plug-in leads 45 (MiataSource, Speedy EFI incl. sensor). TPS 55.99-249. These are retail prices from US sellers; no wholesale found.

## Comparison

### (a) Customer buying the same items separately (retail q1, 2026-11-17)

| Line | Cheapest listing | Mainstream |
|---|---|---|
| ECU (this product) | 399.00 | 399.00 |
| LSU 4.9 sensor | 69.97 (Ballenger) | 109.99 (DIYAutoTune/AMP) |
| Sensor lead | 32.36 (AEM, if in stock; fit unverified) | 32.36 |
| 1/8 in silicone hose, 25 ft roll (the smallest verified pack) | 70.30 (HPS HTSVH3-REDx25, milkymotorsports.com JSON, VERIFIED) | 77.45 (same hose, black, Zoro listing via search, UNVERIFIED) |
| Tee | 0.63 | 0.63 |
| USB-C cable 3 m | 12.79 | 12.79 |
| **Sum** | **585.05** | **632.22** |

Items alone: $186 (cheapest) to $233 (mainstream), from five or six sellers, each with its own shipping (not found; not included). If the customer finds a 3 m length of hose for about $28 (the per-foot price of the roll; UNVERIFIED that a short length is sold) the cheapest basket is $542.4.

### (b) Competitors, current price and contents

| Product | Price today | Includes | Excludes / add-on | Source, tag |
|---|---|---|---|---|
| DIYAutoTune AMP PNP 1990-93 NA6 with internal wideband | 1,199.99 (1,099.99 without wideband) | ECU, 6 ft vacuum hose and T, Bosch LSU 4.9 sensor, 6 ft cable, M8 serial tuning cable, TunerStudio registration code, base map | IAT, TPS | VERIFIED, diyautotune.com products.json, "What's in the Box" |
| AMP EFI, same product | 1,349.99 (1,199.99 without) | same | same | VERIFIED, ampenginemanagement.com products.json |
| DIYAutoTune refurbished MSPNP2 Gen2 (1990-99) | 639.99 | refurbished MS2 ECU | no wideband; add external controller + sensor, e.g. Spartan 3 Lite V2 w/ LSU 4.9 134.99 (variant "w/ LSU 4.9 Sensor") = 774.98 | VERIFIED |
| Speedy EFI Speeduino NA6 full kit | 449 (variant out of stock today) | Speeduino NA6 ECU, MAF/AFM delete plug, GM IAT, 8 ft MAP line, BMW vTPS, printed adapter, harness | no wideband: + Spartan 3 Lite w/ sensor 134.99 = 583.99 | VERIFIED, speedyefi.com |
| Speedy EFI 94-95 plug-and-play kit | 399 | ECU kit (contents not read) | + wideband 134.99 = 533.99 | VERIFIED price only |
| rusEFI shop uaEFI + Miata breakout | 275 + 20 | board with LSU controller, no MAP, no plug-in | pigtails +100 / crimp kit +40, enclosure +50, sensor; sum with sensor 404.99 as a bare minimum | R05, read 2026-11-16, not re-fetched (UNVERIFIED today) |
| Motorsport Electronics ME221 PnP | GBP 579.17 ex VAT, about 750 ex VAT at 1.30 | board, vacuum hose, stickers | no wideband (+ external about 135-200), IAT GBP 20 | R05, UNVERIFIED today |
| DIY-EFI CORE4 NB2 (UK) | GBP 400 ex VAT; GBP 520 with wideband and sensor, about 676 | Speeduino daughterboard, base map | | R05, UNVERIFIED today |
| BMM Miata ECU | 749-775 | ECU with case, USB cable, wideband adapter harness, internal wideband | sensor about 110 | R05, UNVERIFIED today |
| Link G4X NB1X (RAV) | 1,595 | ECU, onboard MAP, USB tuning cable | no wideband listed; + external 134.99 = 1,729.99 | R05, UNVERIFIED today |
| Haltech Nexus S3 NA PnP | 2,520 (2,800 regular) | ECU, PnP harness, IAT sensor + plug, onboard wideband controller | + LSU about 110 | R05, UNVERIFIED today |

R05's AMP figures (1,199.99 / 1,349.99) were the two dealers' prices for one product: today DIYAutoTune is $150 lower than AMP for the same ECU (both re-read in products.json today, VERIFIED). The nearest like-for-like competitor with a wideband, sensor, hose and tuning cable is **DIYAutoTune at $1,199.99**. The nearest cheapest plug-in with sensor is the Speeduino at $534-584 (Speedy EFI NA6 full kit $449, out of stock today, VERIFIED store API; Spartan 3 Lite V2 with LSU 4.9 $134.99, in stock, VERIFIED; the Speedy kit contents are not re-read).

## Stock or link

| Item | Decision | Reason |
|---|---|---|
| Board sets, plug kit, wire, hose roll, tees, USB cable, washers | stock | same on all cars, no returns risk; hose is now the dearest of these ($28 a kit) so look for a cheaper 1/8 in source before the first order |
| LSU 4.9 sensor | stock, small (5 or 10), one vendor | $68 each, counterfeit and DOA are real risks (R15), but you need the part to build a kit and know where it came from |
| AEM 30-3427 | link as fallback only | $32 retail, fit on this board untried, stock gaps |
| IAT sensor, bung, AFM-delete lead | link (Q1 agrees: Speedy EFI / MiataSource adapters, $45) | optional, year-specific, bungs need welding |
| TPS (1989-93) | link to Speedy EFI "VTPS adapter and BMW VTPS for NA6" $29.00 (in stock, VERIFIED price only, fit to this board not checked), Flyin' Miata ($56-249) or the repo's printed route | optional |
| O2 weld bung | link | only to keep the stock sensor |
| microSD | link or customer | optional, volatile price, S5 ships with no card |
| TunerStudio | link | the customer buys their own |

## Sources read today

- Project files: the review brief; REPORT.md section S3, S4-user-experience.md (lines 24-39, 161), S5-packaging-and-shipping.md; kb/research/R15 (sections 1.2-1.4, 4), R05 (market table), kb/parts/P21, P20 (hose), repo/INSTALL.md, repo/README.md (lines 40-60, 140-226), repo/additional-parts/order_all_boards.csv, repo/ordered-boards/2026-11/INSTALL.md (lines 39-80, 216-226), evidence/ord_mb*/pcb_footprints.csv (J2 C127367, J3 C587650), kb/research/files/R26/usps_notice123_2026-10-04.txt (Ground Advantage commercial rows 1-5 lb, signature, merchandise insurance table), kb/research/files/R25/uline_S-4119/S-4215/S-4346.html.
- Live, 2026-11-17 (curl / page fetch / `tools/lcsc.py`): bmotorsports.com (Ballenger) products 1645, 2081, 2082, 3271, 2080, 400, 4172, 4173; diyautotune.com products.json; ampenginemanagement.com products.json; ecumasterusa.com products.json; urotuning.com and drifthq.com sensor JSON; threepiece.us sensor page; chiefenterprises.com sensor page; onefastshop.com, makperformance.com, ridiumworks.com, specialtyz.com, prestigeautolab.com, msvracingpowersports.com (AEM 30-3427); miata-source.com AFM-to-IAT harness JSON; speedyefi.com (89-93 plug, 94 plug, NA6 and NA8 kits); flyinmiata.com/products/tps-upgrade.json; coyotedirect.com Vibrant hose JSON; efianalytics.com/register/browseProducts.jsp; LCSC/JLC lookups C490532, C267125, C412098, C127367, C293525, C259786, C114089, C587650, C124412, C5305, C49257, C90152, C224048, C17477.
- Search snippets only (UNVERIFIED): HPS hose and Walmart price, Zoro/Thogus tees, L-Com/StarTech/Monoprice USB cables, microSD prices, ACDelco 213-190 / GM 25036751 cross-references, M18 x 1.5 bung vendor text.
- Blocked or unusable: aemelectronics.com (403), mouser.com (access denied), Walmart and Zoro pages (robot check/403), ballengermotorsport.com (domain; the shop is bmotorsports.com).

## Not checked

- No car measured: lead length per ECU position, hose length, whether the stock front O2 bung is M18 x 1.5 and accepts an LSU 4.9 (no Miata-specific source found), whether an extension or weld bung is needed.
- Whether SNSR-01029 is Bosch part 0 258 017 025 and whether Ballenger is an authorised Bosch seller; laser-mark check not done.
- AEM 30-3427 length, gauge, and fit on the JST header; wholesale prices from AEM dealers.
- Crimp tools (Bosch BAK, JST SPUD, Micro-Fit): not priced. Wire, loom, ties, washers, hose and tee prices are guesses or snippets.
- microSD price; any USB-C panel-mount extension; C-to-C cable prices.
- Competitor prices other than DIYAutoTune/AMP, Speedy EFI and the Spartan 3 variant are R05 values from 2026-11-16, not re-fetched; Haltech, Link, ME221, BMM, DIY-EFI contents not re-read. Speedy EFI NA8 kit contents not read.
- Parcel weight and size of the kit parcel (calculated, not weighed); the Uline 12x12x4 box fit with the real items; USPS 3 lb row used; any holiday surcharge.
- Payment fee rate, sales tax, returns, warranty cost, and chargebacks are not modelled.
- Whether the 35 % duty applies to JLC-bought parts (S3 open item); duty on LCSC-bought small parts applied at 35 % as an assumption.
- Whether the TPS conversion links R28/R30 conflict with a plug-in Flyin' Miata kit.
- Q1-iat-harness note was absent; IAT lines are not cross-checked with it.

