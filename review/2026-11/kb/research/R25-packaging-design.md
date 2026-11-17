# R25 Packaging design for shipping an assembled two-board ECU (2026-11-16)

## Summary (10 lines)
1. Stack estimate: about 180-260 g bare (INFERRED, section 2), lower than the 250-400 g first assumed. Packed weight is 0.45-0.7 kg in every spec below.
2. Pink antistatic bags only stop the bag itself from charging. They do not shield against an external field or discharge. A populated board needs a metallised static-shielding bag for shipping (vendor sources agree, section 3).
3. Shielding bags are cheap. LCSC sells a 210x240 mm zip shield bag at $0.056 each at 100 (VERIFIED, live). Uline sells 9x12 in reclosable at $0.57 each (VERIFIED).
4. The through-hole pins underneath will puncture a bare bag. A 1/8 in pink PE foam pouch (Uline, $0.33-0.39 each) or a pin guard has to go inside the shield bag.
5. A 9x9x4 in stock RSC (inside 229x229x102 mm) is the smallest stock size that gives 25 mm cushioning on all sides (33 mm slack vertically). Uline 32 ECT costs $0.57 and the 200 lb test version $0.68 (VERIFIED).
6. US-stock ESD foam is the expensive item. A 24x24x1 in pick-and-pluck sheet is $15 (INFERRED about $7.5 per top+bottom kit). Chinese custom EPE/EVA kits are listed at about $0.2-1.3 per piece with an MOQ of 100 (listing prices, UNVERIFIED).
7. Carrier dimensional weight: a 9x9x4 in box billed by UPS or FedEx at divisor 139 comes to 3-4 lb against an actual 1-1.3 lb. USPS applies dimensional weight only above 1,728 in3, so these boxes are never DIM-priced on USPS (VERIFIED, DMM 283).
8. Itemised cost per shipped unit (25 / 100 / 500): A cheapest safe $1.33 / 1.33 / 1.31; B recommended $3.58 / 3.26 / 2.93; C premium $11.87 / 6.16 / 5.20.
9. Failure modes that matter: bent pins on the underside, MLCC flex cracks, harness-latch damage, microSD lid and MAP barb. Foam must carry the load at the standoff points and board rim, never on the pins.
10. Cross-check gaps: the UPS divisor (166 or 139), the exact ISTA drop procedure, and all Chinese prices rest on secondary or listing sources, so they are tagged accordingly.

## 1. Dimensions and weight of the shipped item
- Task statement: 154 x 162 x 35 mm. Board bbox 154 x 162 in kb/interconnect.md (cur_mb9697 bbox line); daughterboard 125x76 mm 6-layer 1.6 mm (evidence/cur_db/pcb_stats.json, board_thickness_mm 1.6). VERIFIED (design files).
- Weight (INFERRED, density FR4 about 1.85 g/cm3, not a measured value):
  - 2-layer 154x162x1.6 mm: 249.5 cm2 x 0.16 cm x 1.85 = about 74 g (the outline is smaller than the bbox, so this is an upper bound).
  - 6-layer 125x76x1.6 mm: about 28 g.
  - 4 M3x11 standoffs about 5 g; 2 x 1x40 headers and 2 sockets about 12 g; harness header 48-pin (weight UNVERIFIED, guess about 35 g); MAP sensor about 7 g (UNVERIFIED); remaining parts about 20 g.
  - Sum about 180 g; plausible range 170-260 g. The first estimate of 250-400 g is high unless the stock case is included. The seller should weigh the first real stack, since this is the least certain input.

## 2. Shielding versus pink antistatic bags
| Product | What it does | Source |
|---|---|---|
| Pink antistatic poly (Uline S-5891, 8x10 in, 2 mil LLDPE, resistivity <10^12 ohm/sq) | Low-charging, dissipative film. Uline states it "does not meet MIL-PRF-81705D & E", i.e. it is not a shielding bag. Price $57/1000 (1 ctn), $46/1000 (6+). | VERIFIED, Uline page fetched 2026-11-16 (kb/research/files/R25/uline_S-5891.html) |
| Metal-in shielding bag (Uline S-2149 open-end 12x16 $57/100; S-2509 reclosable 12x16 $80/100; "Faraday cage", meets MIL-STD-3010, EIA 541, ANSI/ESD S20.20) | Blocks external field and discharge as well as low-charging | VERIFIED, Uline pages |
| Pink bag vs shield bag, concept | Pink bags prevent charge build-up on the bag. They do not shield contents from an external field. Shipping sensitive parts needs a metallised bag (IEC 61340-5-3). Reported ESDA STM11.31 figures: shield bags stop about 97% of a 1 kV pulse. | UNVERIFIED (vendor and distributor pages: gotopac, ppcflex, racklify, antistat.co.uk via search; two or more agree, none is the standard text) |

Conclusion (INFERRED): for a populated board that has an MCU, a USB port and exposed harness pins, use a shielding bag. The cost difference is $0.06-0.5 per unit against a $399 product. A pink bag alone is not "safe" against an external discharge field.

Fit: the stack is 154x162x35 mm and lies flat in a bag, so the bag inside width must be at least about 154+35 = 189 mm plus margin, and the length at least about 162+35 = 197 mm plus the zip lip (INFERRED geometry). These bags fit:
- LCSC C7543868, 210x240 mm.
- Uline S-3753, 9x12 in (229x305 mm).
- Uline S-6374, 10x10 in.
- Uline 8x10 in (S-2263 at $37/100) is marginal (203 mm against 189 mm).
- LCSC 150x200 mm (C7543867) does not fit.

Inside the bag the board still needs a dissipative cushion. Without one, pin tips puncture a 3 mil metallised film and break the shield (INFERRED). Uline S-12583, a 9x12 in 1/8 in pink PE foam pouch, costs $59 per 150, $56 at 2 ctn and $50 at 5+ ctn. The page says 1/8 in polyethylene foam; the anti-static grade is from the section title (VERIFIED, ul_Anti-Static-Foam-Pouches.html).

## 3. Foam, void fill and ESD implications
- Pink antistatic PE or PU foam is dissipative (about 1e9-1e12 ohm/sq per one vendor, below 1e11 per another; sources disagree and I did not read the standard). It is meant for one-time shipping and can lose its properties with age. Black conductive foam is about 1e3-1e5 ohm/sq and is better for repeated factory use (Chip Quik/Mouser and Desco via search, UNVERIFIED).
- Rule I used (INFERRED from the above): only material that touches the board inside the shield bag needs to be dissipative. Foam, paper and plain air pillows outside the sealed bag are allowed to be ordinary materials, because the metal layer carries the field. This is why the specs below use cheap outer cushioning.
- Uline anti-static foam prices (all VERIFIED 2026-11-16):
  - Pick-and-pack 24x24 in, 1 in, 1x1 in squares (S-15325): $15 / 14 / 13 per sheet at 1 / 3 / 6+ cartons of 12.
  - The same 2 in (S-15326): $26 / 25 / 24, 6 sheets per carton.
  - Plank foam with adhesive, 16x16x1 in (S-12892): $97 per 10.
  - Convoluted PU set, 10x10x2 in (S-18409): $3.80 per set, 24 per ctn. A set is 2 interlocking sheets, total height 2 in, base 3/4 in. It is built for flat items, not a 35 mm tall stack.
- Pink bubble roll (Uline S-13053, 3/16 in, 12 in x 300 ft, perforated): $47 / 45 / 44 / 43 at 1 / 3 / 6 / 10+ rolls (VERIFIED). Cost about $0.157 per foot of 12 in width. Uline Air anti-static roll S-5270 is $31 per 175 ft (search snippet, UNVERIFIED). Uline's air pillow machine is $2,740 (snippet, UNVERIFIED), which is not worthwhile at this volume.
- Chinese custom EPE/EVA inserts (Alibaba listings via search, not quotes, UNVERIFIED): EPE inserts $0.10-0.60 each with an MOQ of about 100; anti-static pearl-cotton tray $0.10-0.45 with an MOQ of 2,000; die-cut EVA $1.25 at 100-4,999. ESD claims need test data from the supplier. A cheap Alibaba shielding zip bag is listed at $0.08 at 1,000+ (listing, UNVERIFIED).
- Kraft paper fill is cheap and not ESD-safe. Use it only outside the shield bag.

## 4. Boxes (Uline, VERIFIED 2026-11-16, page text fetched)
| Item | Inside (in) | Outside (in) | Price per box | Notes |
|---|---|---|---|---|
| S-21587 32 ECT RSC | 9x9x4 | 9 3/8 x 9 3/8 x 4 5/8 | $0.57 (all qty from 25) | bundle 25; 10 lb per bundle of 25 |
| S-4595 200 lb test RSC | 9x9x4 | same | $0.68 | 12 lb per bundle of 25 |
| S-4346 200 lb RSC | 10x10x4 | 10 3/8 x 10 3/8 x 4 5/8 | $0.76 | |
| S-20460 32 ECT RSC | 10x10x4 | same | $0.64 | |
| S-4119 RSC | 12x10x4 | 12 3/8 x 10 3/8 x 4 5/8 | $0.98 | |
| Indestructo mailer S-16535, white, tab-locking | 10x8x4 | n/a | $1.97 / 1.83 / 1.73 / 1.62 at 100 / 300 / 500 / 1000 | min 100, no tape needed |
| Indestructo mailer S-10701 | 8x8x4 | n/a | $1.94 / 1.81 / 1.69 / 1.56 | |
| Colored mailer S-12696W 12x12x4 gloss | 12x12x4 | n/a | $6.20 at 25 (search snippet, UNVERIFIED) | too big |

- Cushion fit (INFERRED): the stack needs an inside box of at least 204 x 212 x 85 mm for 25 mm all round. 9x9x4 in (229x229x102 mm) leaves 37 / 33 mm at the sides and 33 mm top and bottom, so 25 mm foam fits with a few mm of slack. 8x8x4 (203x203) leaves only 20-25 mm sideways. 10x8x4 leaves 20 mm on the 162 mm side.
- Chinese or custom: printed mailer boxes at 25-100 units run about $1-3.5 each in blog guides, and Packlane quotes $6.57 each at 25 for a small product box (UNVERIFIED, third-party summaries). Alibaba corrugated mailer listings: $0.30-0.50 at 100 pieces, custom logo often needs 500-1,000 pieces (listings, UNVERIFIED).
- Box weight: 32 ECT 9x9x4 about 181 g, 200 lb version about 218 g, Indestructo 10x8x4 about 218 g (bundle weights divided by count, INFERRED).

## 5. Carrier rules (dimensional weight)
- USPS (VERIFIED, DMM 283, "Updated 7-12-26", kb/research/files/R25/usps283.htm): round each dimension up to a whole inch, multiply, and only if the result exceeds 1,728 in3 divide by 139 and round up. The cap is the 70 lb price.
- FedEx (VERIFIED, FedEx page, fedex_dim.html): "Round each measurement to the nearest whole inch", divide by 139 for US, Puerto Rico and international.
- UPS: the UPS page itself did not download. Search summaries say 139 for Daily Rates and 166 for Retail Rates (UNVERIFIED). Third-party sites say rounding up since August 2025 (UNVERIFIED).
- Worked numbers (INFERRED, my script cost.py):
  - 9 3/8 x 9 3/8 x 4 5/8 in rounded up is 10x10x5 = 500 in3, which is 3.6 so 4 lb at 139 (and 4 lb at 166).
  - Rounded to the nearest inch it is 9x9x5 = 405, which is 3 lb.
  - The 10x8x4 mailer (10 3/8 x 8 3/8 x 4 5/8) rounded up is 11x9x5 = 495, 4 lb at 139 and 3 lb at 166.
  - Actual packed weight is 0.45-0.7 kg (1.0-1.5 lb), so UPS or FedEx bill the DIM weight. Under USPS none of these is DIM-priced (all below 1,728 in3).
  - Every inch counts: dropping a dimension by one inch (for example 9x9x4 inside to 8x8x4 outside 8 3/8 x 8 3/8 x 4 5/8 gives 9x9x5 = 405 in3, 3 lb) cuts the DIM bill by one pound.
- International: US de minimis has been suspended and the EU ended its EUR 150 duty exemption on 2026-07-01 per search summaries only (UNVERIFIED, sources conflict on dates). Rely on a customs broker for HS codes. The seller's own country is not in the brief. Keep paperwork inside a pouch outside the box.

## 6. Failure modes (what the pack-out must protect)
1. Bent header pins. The 2.54 mm headers J1/J2 and the through-hole pins under the board must not carry load. Foam supports the board only at the four standoff positions and the board rim (HD1-HD4 positions in kb/interconnect.md), with a relief cavity under the pins.
2. Cracked MLCCs from flex. Standard X7R parts crack at 2-3 mm board bend (AEC-Q200 minimum is 2 mm; Syfer/AVX/Vishay summaries, UNVERIFIED as secondary). The 154x162x1.6 mm board carrying a heavy header is the flex risk. Corners and edges bearing on foam are better than the centre bearing. Flex-termination MLCCs tolerate 5-10 mm (vendor claims). This is a design cross-check for the 2-layer motherboards: check MLCCs near mounting holes and board edges.
3. Harness-header latch and shroud damage. The large plastic header sits at one edge. Its pocket must be clear of loading, with the foam taking load on the board, not on the header.
4. Hinged microSD socket: ship with the lid closed and clearance of at least 3 mm above it (INFERRED). Decide whether a card is fitted; unfitted is safer and a card could be a separate item.
5. MAP barb on top: foam must not load it sideways. A small cap or foam pocket stops a drop pushing the barb into the board.
6. Humidity: a shield bag is not a moisture barrier bag. A humidity card and a 1/6 unit desiccant ($0.12) are cheap but only matter for a sea or long storage route (INFERRED).

Bare versus inside the case: the project's case is the customer's stock ECU case (review brief section 1), so the seller probably ships the bare stack or a core-swap. A metal case adds stiffness around the board and screws it down at the same standoffs, but it also adds weight (Miata ECU case weight UNVERIFIED, perhaps 300-700 g) and its own dimensional-weight issues. Shipping the stack bare needs the foam to hold the board rim, not the pins.

## 7. The three packaging specifications
All unit costs are consumed material per shipped unit at the stated order size, in USD, prices dated 2026-11-16. Tags: V = price read on a supplier page; E = my estimate, not a priced source.

### Spec A: cheapest safe
Pack-out: stack into the pink foam pouch, then into the shield bag, fold and tape the bag, place in the 9x9x4 box on a scrap-corrugated cradle (supports at the board rim and standoff points, pin relief), kraft paper fill, tape, label. About 4-5 min (E).
| Item | 25 | 100 | 500 |
|---|---|---|---|
| Shield bag LCSC C7543868 210x240 mm (V; min 100 so the first run buys 100 = $5.57; I did not check LCSC's shipping charge) | 0.056 | 0.056 | 0.056 |
| Pink 1/8 in PE foam pouch S-12583 (V; first run buys 150 = $59) | 0.393 | 0.393 | 0.373 |
| Box S-21587 9x9x4 32 ECT (V) | 0.57 | 0.57 | 0.57 |
| Corrugated cradle from scrap and kraft fill (E) | 0.15 | 0.15 | 0.15 |
| Tape (E) | 0.06 | 0.06 | 0.06 |
| Labels, printed card (E) | 0.10 | 0.10 | 0.10 |
| Total | 1.33 | 1.33 | 1.31 |
Packed outside 9 3/8 x 9 3/8 x 4 5/8 in (238x238x117 mm); weight about 0.45 kg (stack 0.2 + box 0.18 + fill/bag/pouch 0.06; INFERRED). Risk: paper fill is weaker than foam, so the drop test (section 8) decides whether A is acceptable.

### Spec B: recommended
Pack-out: pouch, shield bag, die-cut cushioning pad pair (25 units: cradle plus a pink bubble wrap), 9x9x4 200 lb box, tamper label across the flap, label. About 6 min (E).
| Item | 25 | 100 | 500 |
|---|---|---|---|
| Shield bag Uline S-3753 9x12 reclosable, certified wording (V) | 0.57 | 0.57 | 0.54 |
| Pink foam pouch S-12583 (V) | 0.393 | 0.393 | 0.373 |
| Box S-4595 9x9x4 200 lb (V) | 0.68 | 0.68 | 0.68 |
| Cushion: at 25, corrugated cradle (E 0.15) plus pink bubble S-13053 about 3 ft (V price, E length 0.47); at 100 and 500, custom die-cut EPE kit (E, Alibaba listing based, UNVERIFIED) | 0.62 | 0.90 | 0.80 |
| Tamper-evident label S-8326, 1 per box (V; 100 per roll $36/34/30) | 0.36 | 0.36 | 0.34 |
| Tape, shipping label, card (E) | 0.16 | 0.16 | 0.16 |
| Rubber stamp logo on box, amortised over run (E, about $20 stamp) | 0.80 | 0.20 | 0.04 |
| Total | 3.58 | 3.26 | 2.93 |
Packed 9 3/8 x 9 3/8 x 4 5/8 in; weight about 0.55 kg. A US-stock pick-and-pluck cushion kit would add about $7 per unit instead (INFERRED), which is not worth it above 100 units.

### Spec C: premium
Pack-out: pouch, shield bag, humidity card and desiccant in the bag, ESD foam kit, white tab-lock mailer (10x8x4, no tape), tamper label, printed quick-start card and sticker. About 9-10 min (E).
| Item | 25 | 100 | 500 |
|---|---|---|---|
| Shield bag S-3753 (V) | 0.57 | 0.57 | 0.54 |
| Pink foam pouch S-12583 (V) | 0.393 | 0.393 | 0.373 |
| Box Indestructo S-16535 10x8x4 white (V; min 100, so at 25 units the first run pays for 100 = $197) | 1.97 | 1.97 | 1.73 |
| Cushion: at 25, Uline pick-and-pluck 1 in S-15325 kit (V price $15/sheet; E yield of 4 pads per sheet = $7.50 per kit); at 100 and 500, custom die-cut ESD EPE/EVA kit (E) | 7.50 | 1.80 | 1.40 |
| Humidity card S-8028, 200 per can at $37/34/31 (V; min 2 cans) | 0.185 | 0.17 | 0.155 |
| Desiccant 1/6 unit S-1055, 1,200 per container $150 (V) | 0.125 | 0.125 | 0.114 |
| Tamper label S-8326 (V) | 0.36 | 0.36 | 0.34 |
| 1-colour logo sticker 2.5 in (promo price 100 for $25-47 per one vendor snippet, UNVERIFIED) | 0.47 | 0.47 | 0.30 |
| Printed card, label, extras (E) | 0.30 | 0.30 | 0.25 |
| Total | 11.87 | 6.16 | 5.20 |
Packed about 10 3/8 x 8 3/8 x 4 5/8 in (264x213x117 mm); weight about 0.6-0.65 kg. Accessories (USB cable about $1-2, printed jumper card) are not included; their prices were not researched (UNVERIFIED).

Common one-off costs (E): rubber stamp about $20, one-colour sticker or card print setup $55 (Promotional Product Inc listing for 2 in round: $1.21 each at 100 plus $55 setup, UNVERIFIED snippet).
Not recommended: bubble mailers or poly mailers (no crush or flex protection, and the barb and header pins would puncture them), loose peanuts (EPS peanuts are not dissipative unless the pink type is used and move around the boards), and inflatable void fill without a shield bag.

## 8. Home drop and vibration test (before the first shipment)
Use a dummy (a scrapped or spare stack, or a stack plus a weight to match the real mass; do not use the only good board). Test the fully packed box.
1. Before: photograph, weigh, measure pin straightness and the board gap, record capacitor values (a cheap LCR meter) on a handful of MLCCs near the standoff holes and board edge, and mark a pin reference.
2. Drop sequence modelled on ISTA 1A style (UNVERIFIED: third-party pages describe 10 drops from 30 in for packages under about 21 lb; I did not read the ISTA document): one corner, three edges and six faces, or at minimum the corner, one edge, the flat bottom, the header edge and the MAP side, from 76 cm (30 in) onto concrete or hard floor. Use the chosen box and tape exactly as shipped.
3. Vibration (no standard, a sanity check only): put the box on the back seat or cargo floor with other boxes and drive 30-60 min of rough road, or tape it to a running washing machine's top for 20 min in spin. Then repeat step 1.
4. Pass criteria: no pin out of line by more than the socket tolerance, no cracked or chipped part, MLCC values unchanged (within meter noise), no moved pad or latch damage, shield bag not punctured, the microSD lid closed and the MAP barb intact. Fail on any: add 5-10 mm foam or switch to the next spec up.
5. Check the board under magnification for hairline cracks beside capacitors, and power it on once the first board is built (no board has been built yet).

## Implications for this project
| # | Implication | Goal | Evidence | Confidence |
|---|---|---|---|---|
| 1 | Specify metal-in shielding bags, not pink bags, for shipping the populated stack; use a pink foam pouch inside to protect the bag from pin tips. Cost about $0.45-0.95 per unit. | 6 | Uline S-5891 vs S-2149/S-2509 pages; vendor ESD comparisons | high on facts, medium on risk |
| 2 | Buy the 9x9x4 in stock RSC (S-21587 / S-4595); it is the smallest stock box with 25 mm of foam all round. Do not use 12x12x4 (S-4215) or 10x10x4 unless needed. | 6, 5 | Uline pages | high |
| 3 | Plan cushioning cost: US-stock ESD pick-and-pluck foam is about $7 per kit, which dominates the pack; at 100+ units use a custom die-cut kit (about $1-2) and test the supplier's resistance data. | 5, 6 | Uline S-15325; Alibaba listings | medium |
| 4 | For parcels use USPS Ground Advantage where possible. UPS and FedEx bill 3-4 lb against 1-1.5 lb actual for these boxes. | 6 | USPS DMM 283; FedEx page; computation | high for USPS and FedEx; low for UPS |
| 5 | Board design cross-checks from packaging: foam must support the board at HD1-HD4 positions and the rim, so the 2-layer motherboards should keep MLCCs away from the mounting holes and edges; underside pins need a relief cavity. Flag to the layout/hardware reviewers. | 1, 6 | Syfer/AVX/Vishay flex-crack figures (secondary) | medium |
| 6 | Add a printed quick-start card and ESD/fragile stickers; tamper labels cost $0.34-0.36 each (S-8326) but are not recommended on plastic surfaces. | 4 | Uline S-8326 | medium |
| 7 | Weigh the first real stack. The 250-400 g estimate looks high; the inferred 180 g changes nothing in the box choice but changes the DIM calculations only slightly. | 6 | computation | medium |
| 8 | Order the LCSC shield bags together with the JLC/LCSC part order to avoid separate shipping (LCSC min 100). | 5 | LCSC page | medium |

## Sources actually read
- Uline product and category pages, fetched with curl on 2026-11-16 and saved to kb/research/files/R25/: S-2149, S-2509, S-4215, S-4346, S-20460, S-4119, S-4595, S-21587, S-5891, S-18409, S-1058, S-1055, S-8028, S-15067, S-9926, S-13053, S-8326, plus categories for open-end and reclosable shield bags, pick-and-pack foam, plank foam, convoluted foam, foam pouches and white Indestructo mailers.
- USPS DMM 283 (pe.usps.com/text/dmm300/283.htm), FedEx dimensional weight page.
- LCSC C7543868 page and the tools/lcsc.py lookups for C7543867, C7543868, C42383477.
- web search summaries (not read at primary level): UPS dimensions page, Alibaba listings, Packhelp/Packlane, sticker prices, ESD bag explainers, ISTA drop heights, MLCC flex, de minimis news.

## Not checked
- UPS's own divisor page did not download (the page returned an empty shell), so the UPS divisor is a secondary claim.
- Amazon, eBay and bulk-marketplace prices for bags and foam; Chinese custom-box quotes and the one-colour print options were not obtained, only search-listing ranges.
- Actual weight of the TE 174917-6 header, the MAP sensor and a Miata ECU case.
- The ISTA 1A/3A texts and ASTM D4169 itself.
- Shipping charges for LCSC or Uline items; tape and label prices; international customs rules for the seller's own country.
