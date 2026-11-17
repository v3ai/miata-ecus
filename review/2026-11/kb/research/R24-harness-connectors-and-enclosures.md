# R24 - Harness connectors and enclosures

Status: FINISHED 2026-11-16. Currency: USD unless "CAD". Aggregator = Findchips (Supplyframe) page fetched today; snapshots saved in `kb/research/files/R24/` (index at bottom).

## Summary
1. The harness headers are NOT salvage/clone-only. Today an authorised distributor (Newark/Farnell) lists stock of 174917-6 (471), 178780-1 (160), 353830-5 (153), 174915-6 (320); RS AU showed 178 of 174917-6; LCSC/JLC lists 174917-6 (32 in stock, $12.9). Prices CAD 10.66@1 / 7.90@100 (174917-6), CAD 20.85 / 15.09 (178780-1), CAD 14.03 / 11.05 (353830-5). TE's own pages say "Active" yet "not currently available" for all of them, so TE cannot be the source; distributors can.
2. The hard one is 176122-6 (64-pos, used by the ORDERED 1999-2000 board rev 0.7): no authorised stock, reel MOQ 1600 (Avnet $9.23-10.09), Sager 160 min at $12.61. The current rev 0.9 uses 178780-1 (76-pos) instead, which is buyable.
3. Full-reel quantities are cheap per part but huge in cash (174917-6: 2700 x $4.71 = $12.7k); not for 10-100 units. Buy cut quantities from Newark/Farnell/RS.
4. Hobby vendors do not sell the 48-pos header. Ballenger sells a 64-way NA header ($29.99, in stock) and the 72-way NB header ($59.99, special order), no terminals. Loopy Engineering (Tindie) NB board with connector $85, sold out since 2026-09-14. rusEFI states it neither makes nor stocks Miata hardware. Clone sellers (Kinkong) quote on request, no price, no quality data found.
5. Salvage economics are bad: a used ECU costs ~$150-190 (NA6/NB1) and ~$285-450 (NB2), against ~$6-11 for a new header. Salvage only makes sense for the case, not the header.
6. Stock-case reuse is the industry norm among hobby vendors (rusEFI MRE, Speeduino PnP vendors, DIY-EFI) but all say the customer cuts openings; nobody has published case dimensions (this project has none either). Commercial vendors with a higher price (BMM $749-775) ship a 3D-printed case.
7. Recommendation: first 10 units: new headers from Newark/Farnell/RS (about $8-15 each at that quantity) plus MJF 3D-printed shell as optional (est $20-35); buy 2-3 used ECUs only as fit-check cases. At 100: laser-cut/bent 5052 two-piece shell (est $12-25) or keep printed; keep "use your own case" as a discounted option. Numbers below.

## 1. Connectors

### 1.1 Status at TE (VERIFIED, page fetch of te.com product pages, 2026-11-16; the page read is a summary, not raw HTML; te.com blocks curl with 404)
| P/N | TE description | TE status text | Replacement |
|---|---|---|---|
| 174917-6 | "HYBRID I/O CAP ASSY 48P GRAY", 040/070 series | Active; "This product is not currently available" | none listed |
| 178780-1 | "040/070 HYBRID CAP ASSY 76P" (non-flange) | same | none |
| 176122-6 | "HYBRID CAP ASSY 64P" | same | none |
| 353830-5 | 72-pos 3-row Multilock 040 III header, 2.5/3.1 mm | same | none |
Also (aggregator): 174518-7 "040/070 HYBRID CAP ASSY 64P" (Avnet MOQ 216, stock 0, 18 wk); 174915-6 = 76-pos (Newark/Digi-Key "76 position 3.50 mm"); 1123038-2 = "040III HD 72POS CAP ASSY H TIN" (Avnet/RS MOQ 2520, $7.95-8.64, stock 0) - an alternative 72-pos header listed by Speeduino/rusEFI wikis (INFERRED equivalent footprint; not checked).
Conflict: Digi-Key/Octopart say 174917-6 is a 3.50 mm pitch right-angle header ("Through Hole, Right Angle 48 position 0.138 in"), RS/Farnell call the same number a "Multilock 040/070 female housing, 48 way, 2 row"; LCSC says "P=4.5mm". "Cap assy" = shroud housing with tab (blade) contacts soldered to the board. Pitch to be taken from the TE drawing before relying on it (not done). Newark's description "Rcpt, 40Pos" is a mislabel.

### 1.2 Authorised stock and prices today (aggregator snapshot, Findchips 2026-11-16; Newark CAD)
| P/N | Newark stock | Newark price CAD 1 / 10 / 100 | Other |
|---|---|---|---|
| 174917-6 | 471 | 10.66 / 9.36 / 7.90 (250: 7.49) | Avnet MOQ 2700 (tube 270) $4.71-4.41, 18 wk; Greenchips 2,929 @ $4.47 (1) / 4.26 (100) (independent); IBS 2,150 @ $7.24 (1); Octopart $6.09; RS UK GBP 7.41 (search snippet); RS AU 178 in stock (snippet); LCSC C592838 32 in stock $12.92-12.16 (tools/lcsc.py today) |
| 178780-1 | 160 | 20.85 / 18.60 / 15.09 | Avnet MOQ 1620 $11.70-10.70; RS $18.08 (1), $14.46 (10), stock 0 |
| 174915-6 (76-pos, spare) | 320 | 15.18 / 14.08 / 12.74 | Avnet MOQ 162 $8.57 |
| 353830-5 | 153 | 14.03 / 13.03 / 11.05 | RS 14 in stock $5.67 (1); Avnet MOQ 252 $9.01-7.88; LCSC C5368971 stock 0 $13.51 |
| 176122-6 | none | n/a | Avnet reel MOQ 1600 $10.09-9.23; Newark Min 1600 CAD 9.92; Sager min 160 $12.61; LCSC C5171845 stock 0 (price $0.04 is a data error) |
Cross-check: Newark + RS + LCSC/JLC + Greenchips agree on stock for 174917-6, 353830-5, 178780-1. VERIFIED as of snapshot; stock moves. Aggregators are secondary; check the live Newark pages before ordering. USD for CAD: about 0.72 (INFERRED, assumption).

### 1.3 Hobby / aftermarket sources
| Source | Item | Price | Notes |
|---|---|---|---|
| Ballenger (bmotorsports.com, pages read today) | NA Miata 64-way ECU header CONN-100747 | $29.99 (1) in stock; "may take 2-5 days extra" | no terminals; header "normally soldered to the ECU board of an NA". Likely the 64-pos (22+16+26) = TE 174518-7 / 176122-6 class (INFERRED) |
| Ballenger | NB 72-way header CONN-100752 | $59.99, special order | no terminals; plugs 17/24/31-way $6.99-9.99 (1), $5.99-8.99 (100) ; plug kits with terminals $10.99-12.99 (1) |
| Ballenger | No 48-way header found in the search | - | UNVERIFIED (search did not show one) |
| Loopy Engineering (Tindie) | NB 01-05 breakout PCB; with pre-soldered 72-pin connector | $20 / $85 | sold out since 2026-09-14; ships from UK; points buyers to 353830-5 at RS |
| rusEFI eBay store | breakout PCBs for 48/72-pin (no header) | about $20-50 (search snippet) | eBay returned 403; UNVERIFIED |
| rusEFI wiki "Miata" | "proven open source designs... currently do not fabricate or stock those" | - | wiki.rusefi.com/Miata (via page fetch) |
| Kinkong (Wenzhou) | "48 pin male hybrid connector 174917-6 / 179375-1", own code CKK5481GA | "request a quote", small orders accepted | no brand, no plating, no price; no quality reports found anywhere. UNVERIFIED |
| Speedy EFI NA6 kit $449-489; Spark EFI board $25.90 | no header/case listed in either | | |
| Miata Turbo 2007 thread | onlinecomponents.com had the 64-pin housing, $30 min order; junkyard harness plugs; "$22 shipped" pin kits | 2007/2011 prices | stale |
Quality reports: none found for any clone header; no failure reports found either (absence of data, not evidence of quality).

### 1.4 Salvage (headers from used ECUs)
- Used ECU prices (asking, not sold; UNVERIFIED single-listing): NA6 1990-93 B61 eBay.ca $189.99 (offer); 1996 BPS1 $399.99; 1999 BP4W-18-881C $149.99 (Redline), $169.99 (Importapart); 2001-02 manual BTT3/BP6F $284.99-449.90 (Importapart/Redline/Partrequest, some immobilizer-locked). 1989 and 1994-95 not priced.
- Desoldering: no source with a measured time. rusEFI forum suggests a solder-wave dip, which fails on double-sided boards (UNVERIFIED forum). My estimate for 48-76 through-hole pads on a multilayer board: 10-20 minutes with a desoldering gun, risk of pad lifting (INFERRED/UNVERIFIED; at $30/h labour that is $5-10 plus board scrap).
- Verdict: header salvage costs far more than a new header (INFERRED: $150+ per donor versus $8-15).

### 1.5 What competing vendors do (VERIFIED where page read)
| Vendor | Connector | Case |
|---|---|---|
| rusEFI MRE 48-pin (wiki.rusefi.com Legacy-Miata-NA-48-pin-board) | own header on adapter board | customer opens stock case, removes stock PCB, installs board; hole J27 needs 3 x M4 washers (recessed thread, stock heat sink); 8 mm / 5/16 in USB hole in lid; MAP hose hole |
| DIY-EFI CORE4 (GBP 400 ex VAT) | 48-pin 2-plug | "fits in the factory enclosure" |
| Alex Engineering Speeduino PnP | - | remove handles and original PCB, cut openings, install board in stock case (search snippet of install guide) |
| BMM (R05) | - | ships ECU with 3D-printed case (+$50 billet), $749-775 |
| AMP/MSPNP | - | page does not say; $1,199.99 (R05) |
| Link MX5Link (R05) | - | "fits OEM case" |

## 2. Enclosure options
Stock mounting arrangements (from earlier notes, not re-verified): 1989-93 under passenger floormat on a bracket bolted to the floor (R16, manual F-127); 1994-97 behind passenger seat, three 10 mm nuts (R17); 1999-2005 under driver dash, two bolts, one on top of the case (R18/R19). No dimensions for any stock case exist in our sources; Miata Turbo thread "NB2 ECU case dimensions" is an unanswered question. Case outline therefore must be measured from real units.

| Option | Unit cost @10 | @100 | Tooling | Heat | EMI | Fit | Customer effort | Reversible | Ship (est) |
|---|---|---|---|---|---|---|---|---|---|
| A. Customer's stock case | $0 | $0 | none | stock alu case is a heat path (rusEFI notes heatsink contact at one screw) | alu shield kept | exact mounting by definition; vertical clearance unknown (Miata Turbo: Speeduino 0.3.2 "a little too tall") | high: open, remove board, cut USB/MAP/WB holes (30-60 min, INFERRED); needs tools | partly: keep stock PCB; cut case is not original | board only, <0.3 kg, flat box |
| B. Core programme (seller buys used ECUs) | $150-450 per core + labour 20-30 min + header salvage (INFERRED) | same, cores scarce | none | as A | as A | exact | low | stock ECU gone | ~0.6-1 kg (stock ECU 2-3 lb, UNVERIFIED eBay) |
| C1. 3D-printed (MJF PA12, JLC3DP) | $20-35 | $12-25 | none (no published JLC rate: UK service 0.20 GBP/cm3 x ~200 cm3 shell = ~GBP 40; JLC "from $1", cut ~70% on PAC-HP in July 2026; quote needed) | poor conductor, add thermal pad to lid or alu plate | none (add foil/shield plate) | any outline, BMM does it | low | full (stock ECU untouched) | 165x160x45 mm, ~0.2-0.3 kg |
| C2. Laser-cut + bent 5052 sheet, 2-piece | $20-35 (SendCutSend benchmarks 5052 0.063 in 9x6.6 in: $8.38@10, $6.45@100; two parts + bends) | $12-20 | none beyond CAD | good | good | any outline | low | full | ~0.4 kg |
| C3. Extruded alu (Hammond 1455 T/R2201, 165 mm wide) + custom end plates | ~$42 case (DigiKey June 2026, aggregator) + ~$15 plates = ~$57 | ~$40-45 (INFERRED, no 100 price read) | none | good | good | width 165 mm vs 154x162 board: must check | low | full | 0.5 kg |
| D. External ECU + adapter harness | enclosure as C + harness: plug kits $10.99-12.99 each x2-3 plus wire, labour | ~ $60-100 extra (INFERRED) | harness board | best (free choice) | fine | no bracket constraint | medium (route harness) | full | box + harness, 0.6 kg |
Mounting bracket pattern: needs measuring on real cases for each generation; none found online (not done).

## 3. Recommendation (INFERRED, numbers above are estimates, quotes needed)
First 10 units: header from Newark/Farnell/RS (buy 12-15 each: 174917-6 about USD 5.7-7.7, 178780-1 about 11-15, 353830-5 about 8-10 each at 10-100 pieces). buy 3 used ECUs (1990-93, 1996-97, 2001-05; about $190+400+285) first to measure outline, hole pattern, height, because INSTALL.md says nobody has fitted a board to a case and 1996-2005 outlines are placeholders. Do not run a core programme.
At 100: laser-cut/bent 5052 shell ($12-20) or printed (about $12-25) as default, stock-case reuse as an option; for headers ask Newark/RS for a 100-piece quote, or buy a full tube (162/252/270 pieces; 174917-6 270-tube about $1.2k at Avnet MOQ 2700 reel, not tube; check) via Avnet/Heilind quotes. Do not rely on clone headers unless a sample is tested for pin fit, retention and plating.

## 4. Implications for this project
1. review brief/README say headers are "hard to buy / salvage-clone only": wrong for 174917-6, 178780-1, 353830-5 today. Doc/BOM/shopping-list should name Newark/Farnell/RS/LCSC part pages and prices. Confidence high.
2. The ORDERED 1999-2000 motherboard uses 176122-6, which has no authorised stock below 1600 reel; plan to hand-fit 178780-1 only if the footprint matches (it is the rev 0.9 choice), else Ballenger CONN-100747 $29.99 (identity unverified). Check which footprint is on the ordered board. Confidence medium.
3. Headers are $6-15 each: not a cost lever; case is the larger unit-cost line (about $12-35) after the board.
4. Customer-effort/UX (goal 4): cutting a stock case is the biggest friction; offering a printed or sheet-metal case with openings is what BMM does; also makes the product reversible (stock ECU untouched).
5. Packaging/shipping (goal 6): with own case, parcel is a board in a box (<0.3 kg); with a shipped case about 0.3-0.5 kg.

## Sources actually read
te.com product pages 174917-6, 178780-1, 176122-6, 353830-5 (page fetch); Findchips snapshots (files/R24); bmotorsports.com pages 3454, 3455, 3460, 3461, 3464, 3465, 3467, 3484, 4740, 5654; Tindie Loopy NB 01-05; rusEFI wiki Miata and Legacy-Miata-NA-48-pin-board; Miata Turbo "where get ECU connectors" thread; Kinkong page; DIY-EFI CORE4 mk1; SpeedyEFI, SparkEFI pages; DIYAutoTune MM9093; JLC3DP July 2026 news; tools/lcsc.py lookups. kb notes R05, R16-R19.

## Not checked
Pitch/gender from TE drawings; live Digi-Key/Mouser pages (Cloudflare blocked); eBay/AliExpress listings (403 or none found); measured stock case dimensions and bracket patterns; JLC3DP/JLCCNC real quotes; 100-piece prices for Hammond; used 1989, 1994-95 ECU prices; desolder time measurement; clone quality; Ballenger 64-way identity versus 176122-6.
