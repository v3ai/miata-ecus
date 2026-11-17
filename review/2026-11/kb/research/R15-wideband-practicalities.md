# R15 - Wideband (Bosch LSU 4.9) practicalities: sensor, plug, pigtail, AEM 30-3427, install rules, what buyers expect

Date of all web reads: 2026-11-16. Files kept in `kb/research/files/R15/` (index at the end). Scratch: `work/R15-wideband-practicalities/`.

## Summary (10 lines)
1. Bosch LSU 4.9 pinout/plug (Bosch primary docs, VERIFIED): 6 pins, 1 IP, 2 VM, 3 H-, 4 H+, 5 RT (trim), 6 UN. The trim resistor (30-300 ohm per Bosch circuit) is inside the sensor's connector module, so the sensor and its own plug are a matched pair.
2. Common part numbers: 0 258 017 025 (about 0.83-1.0 m lead, the one every aftermarket controller names) and 0 258 017 123 (same sensor, short lead about 0.33 m, forum/seller source only). Genuine street price in USD today: 64-125 (see table).
3. Mating plug is Bosch BAK 1.5 six-way (sensor side has the female plug housing, "CONN-100321"/Bosch 1 928 404 669 per one UK distributor; Bosch Motorsport kit 1 987 280 016 / D 261 205 356-01). Pre-wired pigtail 12 in from Ballenger: USD 19.99 x1, 17.99 x100.
4. AEM 30-3427 = "X-Series Wideband Sensor Harness", replacement for 30-0300 / 30-0334 gauges, ends in the Bosch LSU 4.9 plug (and AEM/FAE plug) on the sensor side; retailers say 72 in long. USD 35.96 at one US shop today (out of stock, ships week of Nov 30); 22-51 USD elsewhere; availability patchy. AEM's own product page is Cloudflare-blocked; the gauge-end connector is NOT documented anywhere I could read (see 2.3).
5. AEM manuals (30-0300 rev 12/2022, 30-0310) give the 8-way gauge-side pin table the repo uses (1 green RT, 2 white H-, 3 orange COM, 5 red IP, 6 black UN, 8 brown H+, 4 and 7 unused) - VERIFIED; the claim that this is a JST PUD (SPUD-001T-P0.5) connector is INFERRED only: the manual sentence "Replacement pins are JST P/N SPUD-001T-P0.5" sits in the wiring-notes block after the Power/IO notes and before the Connector B table, so it may refer to the 10-way Power/IO connector (or both).
6. A seller-made pigtail is cheap: JST PUDP-08V-S housing 0.17-0.29 USD + SPUD-001T-P0.5 contacts 0.01-0.02 USD each (LCSC, today) + Bosch plug kit 7-18 USD + 1-2 m wire; about 10-22 USD all in, against 36 USD for AEM. But SPUD only takes 22-26 AWG (0.13-0.33 mm2).
7. Bosch install rules (Technical Product Information Y 258 E00 015e, 14.6.2005): at least 10 deg from horizontal with the connector up, tighten 40-60 Nm, thread boss 10.5 mm min (13 mm for hot), exhaust gas < 930 C, hexagon < 600 C, connector < 120 C, cable < 250 C, absolute exhaust pressure <= 2.5 bar, never heat the sensor before engine start / during condensation (heater limited to 2 V effective).
8. Pressure error (Bosch graph p.8): +about 3 % of Ip at 1.2 bar abs, +9-11 % at 1.5 bar abs (0.5 bar boost), -10 % at 0.7 bar; temperature +4 %/100 C of the ceramic. Matters for turbo conversions and for high back-pressure systems.
9. Free-air calibration: not needed for a trim-resistor controller on a new sensor (AEM: "preferred and recommended" is the trim resistor; free air is only for aged sensors). The rusEFI/FOME wideband firmware has no free-air function (grep, INFERRED no need).
10. Buyers of ECUs with built-in wideband (ECUMaster EMU Black, MaxxECU Street, Haltech) are sold the sensor with the plug as an add-on kit (ECUMaster USA: sensor + 6-ft harness 111.20 USD sale/139 list; sensor + plug and terminals only 103.20/129) or in a premium bundle; none ships the ECU with a ready sensor lead in the base box. A 399 USD ECU that ships only a header and expects an AEM purchase is in line with the market but loses 36-70 USD of buyer effort.

---

## 1. Bosch LSU 4.9

### 1.1 Pinout, trim resistor, electrical (VERIFIED, two Bosch documents)
Bosch Motorsport data sheet 69034379 (27 Jan 2026) `files/R15/bosch_lsu49_motorsport_ds.pdf` p.2 and Bosch Technical Product Information Y 258 E00 015e (2005) `files/R15/bosch_lsu49_techinfo.pdf` p.2 section 1.2:

| Pin | Bosch name | Wire colour (Bosch 2005) | AEM harness colour (30-0300 manual) | Board net (kb/interconnect.md) |
|---|---|---|---|---|
| 1 | Pump current APE / IP | red | red (AEM pin 5) | LSU_IP |
| 2 | Virtual ground IPN / VM | yellow | orange "COM" (AEM pin 3) | LSU_VM |
| 3 | Heater - | white | white (AEM pin 2) | LSU_HTR_N |
| 4 | Heater + (Vbatt) | grey | brown (AEM pin 8) | +12V via F2 |
| 5 | Trim resistor RT / IA | green | green (AEM pin 1) | LSU_RT |
| 6 | Nernst voltage UN / RE | black | black (AEM pin 6) | LSU_UN |

The functions match one to one between Bosch and AEM, so the repo's table in INSTALL.md (lines 66-79) is consistent with both primary documents (checked, correct). Colour of the sensor wires from the sensor to the plug is irrelevant to the user.
- Trim resistor: "The connector module contains a trimming resistor, which defines the characteristics of the sensor and is necessary for the sensor function" (Bosch techinfo p.2); circuit drawing shows 30-300 ohm. It sits in the sensor's plug, not in the mating plug. A pigtail needs no resistor.
- Heater: 7.5 V nominal effective, 7.5 W steady (Motorsport ds p.1); AEM gauge specs 1.5 A nominal / 3.0 A peak at 13.8 V (30-0300 manual p.~14). Heater frequency >= 100 Hz.
- Nernst cell 300 ohm operating point (ceramic 780 C) (techinfo p.8 graph).
- Wire length: Bosch Motorsport ds: automotive connector version 95 cm; motorsport connector version 20-90 cm. Wbo2.com table quoted on the rusEFI forum (https://www.rusefi.com/forum/viewtopic.php?p=43398): 17 025 = 830 mm, 17 123 = 330 mm (UNVERIFIED, forum quoting a vendor page). Sellers' figures: 975 mm (efihardware), 1 m (Ballenger), 830 mm overall + 975 to connector (Bosch distributor wording). Treat as "about 0.8-1.0 m depending on where it is measured".

### 1.2 Part numbers in use
| Bosch P/N | What | Source | Tag |
|---|---|---|---|
| 0 258 017 025 | LSU 4.9 with automotive plug; named in Bosch Motorsport ds as order number; the one aftermarket controllers (AEM, ECUMaster, MaxxECU, FOME) specify; "7025" | Bosch ds; tiperformance.com.au listing; INSTALL.md | VERIFIED (Bosch ds names it) |
| 0 258 017 123 ("7123") | same sensor, shorter cable | tiperformance.com.au "(the 7123 has the same sensor, with a shorter cable length)"; rusEFI forum 330 mm | UNVERIFIED (seller + forum) |
| 0 281 004 150 | LSU 4.9 about 1.2 m, other (VAG) plug? | rusEFI forum, "overall length 1215 mm" | UNVERIFIED |
| B261.209.358-03 | Bosch Motorsport LSU 4.9 with AS607-35PN motorsport connector | Bosch ds p.3 | VERIFIED |
| 0 281 004 821 (770motorsports), 7052, 4821, 7123 | automotive variants with other cables/plugs sold as "LSU 4.9"; the plugs are said to differ per variant | seller pages (search snippets) | UNVERIFIED |
The only variant the repo's design needs is the 6-pin automotive plug (025/123/0 281 004 821 family all quoted as 6-pin BAK). A buyer must be told to buy exactly 0 258 017 025 (or one with the same plug): sellers warn "the sensor connector is different for each sensor".

### 1.3 Mating plug (harness side) - part numbers and prices
Bosch Motorsport ds p.1: sensor plug 1 928 404 687 "series production type, not available from Bosch Motorsport"; mating connector D261.205.356-01. (The ds lists them in a block; I read "Connector 1928.404.687 / Mating connector D261.205.356-01" as the sensor-side plug and its mate.) VERIFIED as printed.
| Item | Seller / P/N | Price (USD unless noted, 2026-11-16) | Tag |
|---|---|---|---|
| Bosch 6-way LSU 4.9 connector, housing + lock only, "Bosch BAK 1.5 series" | Ballenger CONN-100321 | 15.99 x1; 14.99 x25; 13.99 x100 | VERIFIED (page fetched) |
| Same + terminals + seals = kit, "Bosch Motorsport D 261 205 356-01" | Ballenger CONN-75762 | 17.99 x1; 16.25 x100 | VERIFIED |
| Pre-wired pigtail, 12 in leads, terminals crimped, cavity plug | Ballenger CONN-85762 | 19.99 x1; 18.99 x25; 18.49 x50; 17.99 x100; 15.99 x500 | VERIFIED |
| 5 ft pigtail, 18 AWG TXL, split loom | VEMS Tuning (shop.vemstuning.com) | 19.00 sale (23.00 list) | VERIFIED (page fetched) |
| Connector component kit | ICT Billet WC0XY01 | 26 sale (30 list), says "Germany", OEM brand parts | VERIFIED |
| Connector kit | Milspec Wiring M 12-4669K | 16.00 each | VERIFIED |
| 6-way female sealed housing, Bosch 1 928 404 669 | auto-click.co.uk | price not captured; says "BAK series 6-way sealed female, LSU 4.9 plug", mate male housing 1928405111 | UNVERIFIED (one UK distributor) |
| Bosch Motorsport "mating connector 6 pin for LSU4.9", 1 987 280 016 (housing, terminals, seals) | bosch-motorsport-shop.com.au | price not captured | VERIFIED name only |
| ProWire USA "LSU 4.9 connector kit with terminals and seals" | prowireusa.com | 9.85 x1 down to 7.30 x100 | UNVERIFIED (search snippet; page Cloudflare-blocked) |
| XTRA Motorsport LSU4.9-CON-SET | xtramotorsport.com | EUR 4.96 | UNVERIFIED (snippet; page blocked) |
| eBay "6 Pin For Bosch LSU4.9 ... Plug Kit" (VW 1J0973713 type) | ebay.com/itm/306791124931 | 8.99 | UNVERIFIED (snippet) |
| MaxxECU "O2 sensor plug" | maxxecu.com store | 8.29 | UNVERIFIED (snippet) |
LCSC / JLC: `tools/lcsc.py -s "LSU 4.9"`, "LSU4.9", "oxygen sensor connector 6 pin" returned nothing: no LCSC/JLC stock of the Bosch BAK 1.5 plug (VERIFIED by live search, 2026-11-16). AliExpress/Amazon not reachable by search tool (not checked, see not-done). TE equivalent: ICT Billet says terminals suit "AMP/TE MCP 1.5K" crimpers; no TE part number for the housing established.
Crimping: the Bosch BAK 1.5 terminals need a suitable crimp (MCP 1.5K die per ICT Billet) - a hand tool concern for a seller doing >10 units; pre-crimped pigtails avoid it.

### 1.4 Prices of the genuine sensor (0 258 017 025)
| Seller | Price | Note | Tag |
|---|---|---|---|
| Ballenger Motorsports (VA, US), SNSR-01029, 1 m lead | 69.97 x1; 68.99 x10; 67.99 x25; 65.99 x50; 63.99 x100 | "Bosch Motorsports lambda sensor", in stock | VERIFIED today |
| efihardware.com (AU) | AUD 130 ex GST (about USD 88 per the page) | "Genuine Bosch", 97.5 cm lead | VERIFIED |
| 797performance / Innovate / threepiece / drifthq / urotuning (Nuke Performance) | 89.99 / 83.08 / 131.99 / - / 119.20 | search results; urotuning page fetched shows 119.20 | VERIFIED for urotuning, others snippets |
| MaxxECU store | 124.40 | snippet | UNVERIFIED |
| ECUMaster USA kit sensor + 6 ft harness FCI SICMA 2.8 | 111.20 sale (139.00 list; Black Friday banner live) | page fetched | VERIFIED |
| ECUMaster USA kit sensor + connector and terminals | 103.20 sale (129.00 list) | page fetched | VERIFIED |
| tiperformance.com.au | AUD 129 inc GST for 7123/7052/4821 | | VERIFIED page |
The R05 note's "119.20 USD ECUMaster kit" was the earlier price; today the same kit is 111.20 with a sale on (139 list). Buying price for the seller at 100 pieces from Ballenger is 63.99 (VERIFIED).

### 1.5 Genuine vs counterfeit
- tiperformance.com.au review: "90% of the LSU 4.9 being sold out there are fakes" (customer review, UNVERIFIED) and its listing "Genuine Bosch sensor with hologram for proof of authenticity".
- kartsportnews (https://www.kartsportnews.com/2025/11/20/fake-sensors/, a dealer bulletin, UNVERIFIED): genuine has "BOSCH Germany" and part number etched on the barrel (fakes only "Germany"), genuine cable cover is ribbed, fakes smooth; counterfeits work initially but fail quickly (heater).
- HP Academy / hptuners forum threads: tuners report early failures and suspect fakes; none confirmed (UNVERIFIED).
- There is no Bosch authentication procedure published that I found. Practical rule: buy only from Bosch Motorsport distributors (Ballenger, efihardware, Bosch Motorsport shops, ECUMaster/AEM/Haltech kits) - INFERRED.

### 1.6 Installation and life rules from Bosch (VERIFIED, techinfo Y 258 E00 015e)
| Rule | Value | Where |
|---|---|---|
| Exhaust gas temp continuous / max | <= 930 C / <= 1030 C for max 250 h lifetime | 2.2, 2.3.1 |
| Hexagon temp continuous / max | <= 600 C / <= 680 C (250 h) | 2.2, 2.3.1 |
| Cable grommet / cable | <= 250 C; 280 C max 40 h | 2.2, 2.3.2 |
| Connector | <= 120 C (Motorsport ds says < 140 C) | 2.2; ds p.1 |
| Exhaust pressure (absolute) | <= 2.5 bar continuous; <= 4 bar max 250 h | 2.4 |
| Install angle | at least 10 deg from horizontal, electrical connection upward; about 90 deg to gas flow (max 90+15 / 90-30 deg); other angles to be tested | 4.4 |
| Condensation | heater must not be switched on until no condensation; heater <= 2 V effective during condensation phase; never switch on sensor heating or the control unit before engine start; design: pipe in front of sensor without pockets/edges, downward slope recommended, front hole of protection tube not facing the stream | 1.6, 4.3 |
| Thread | M18 x 1.5, torque 40-60 Nm, high-temperature grease (Bosch 5 964 080 112), no cleaning fluids or greasing on the plug | 4.6-4.8 |
| Thread boss | stainless (1.4301/304), 10.5 mm min height, 13 mm for hot applications, >= 16 mm increases condensation thermo-shock risk | 4.9 |
| After shutdown | avoid excessive cable grommet heating after engine off following max load | 4.5 |
| Sealing | cover sensor and plug when applying underbody wax / spray oil | 4.10 |
| Contamination | silicone, oil, coolant, leaded fuel, sealants hurt the ceramic; link ECU article and manuals: >= 500 h unleaded, about 50 h leaded (one manufacturer manual, UNVERIFIED secondary) | 4.11 |
Bosch Motorsport ds additionally: "Install at a point where the gas is as hot as possible", "as far as possible vertically (wire upwards)" (this conflicts mildly with AEM's advice below), not near the pipe outlet (outside air), leak-free exhaust, protect from condensate, do not paint.
AEM 30-0300 manual (12/2022, p.~12) `files/R15/aem_30-0300_fae.pdf`: place 18 in (45 cm) downstream of the head port/turbo, upstream of the cat, as far from tailpipe as possible, leak-free; bung orientation more than 10 deg above horizontal and "avoid a completely vertical sensor orientation to prevent overheating"; torque 30 ft-lb / 40.6 Nm (AEM) vs Bosch 40-60 Nm - disagreement; trust Bosch for the sensor, since it is the maker (INFERRED). Tech Edge (wbo2.com) suggests staying >= 15 deg off vertical (secondary).

### 1.7 Pressure and temperature effects on readings (VERIFIED, Bosch techinfo p.8 graph, read from image)
Delta Ip / Ip(1013 hPa) versus absolute exhaust pressure, lambda > 1 curve: about -22 % at 0.5 bar, -10 % at 0.7, 0 at 1.0 (about -3 % at 0.9), +3 % at 1.1-1.2, +8 % at 1.4, +10 % at 1.5, +16 % at 1.9, +22 % at 2.5. Lambda < 1 curve flattens: +9 % at 1.5, +12 % at 2.5. Temperature: +4 % of Ip per 100 C ceramic temperature (controller holds the Nernst cell at 300 ohm so this is normally compensated). For an NA Miata, back pressure at the front sensor of 0.05-0.2 bar gauge (INFERRED, not measured) gives +1-6 % of the pump current, i.e. about 0.01-0.03 lambda near stoich; for a turbo conversion at 0.5 bar boost the exhaust-side absolute pressure can be 1.5-2 bar and the error reaches 10-20 % (INFERRED from the curve; the effect on lambda reading is smaller on the rich side). Leak air in the exhaust and cold-air scavenging at idle make readings lean (Bosch ds, AEM manual).

### 1.8 Sensor life
Lifespan article at Link ECU (https://linkecu.com/tech-articles/lsu-4-9-sensor-lifespan/) not read in full (UNVERIFIED). Bosch does not publish an hour rating in the documents above other than limits. Typical claims: 500+ h unleaded, shortened by rich running (lambda <= 0.75), leaded fuel, silicone. For the buyer: plan the sensor as a consumable (INFERRED).

## 2. AEM 30-3427

### 2.1 What it is (retailer pages read today; AEM's own page returns HTTP 403 (Cloudflare) to curl and page fetch)
- Title: "AEM X-Series Wideband Sensor Harness" (AEM product page title via search result); sold as "Sensor Harness for 30-0300 X-Series Wideband Gauge - 30-3427"; fits gauges 30-0300 and 30-0334 (AEM page per search result; one retailer adds 30-0333, UNVERIFIED).
- Description (onefastshop.com SKU AEM30-3427 and a UK retailer): "A replacement sensor harness that runs between an AEM X-Series wideband gauge and its oxygen sensor. It plugs straight into either a Bosch LSU 4.9 sensor or an AEM/FAE sensor, and the long loom reaches the sensor in most installations. It replaces a damaged or lost sensor cable; the sensor itself is a separate part." GTIN 840879026646. "Made in CN".
- Length: 72.000 in (one Canadian parts retailer's spec line, from search summary; UNVERIFIED). "Long length wiring loom" elsewhere.
- Ends: sensor end = Bosch LSU 4.9 plug (retailers: "direct connection to Bosch 4.9 and AEM FAE sensor plug"); gauge end = AEM's 8-way sensor connector "Connector B" of the 30-0300 gauge. The housing type of that end is not stated on any page read.
- Price and stock (2026-11-16): onefastshop.com USD 35.96 (list 40.46), out of stock, "Order now, ships the week of Nov 30"; iagperformance USD 35.96, out of stock, "Contact us for ETA"; UK retailer GBP 31.99 (list 35.99) inc VAT; search results quote 22-51 USD at other shops; a Canadian shop CAD 50.34 or 19.99/24.99 on the page (ambiguous, the fetched text mixes figures). All VERIFIED as read, but the availability varies day to day.
- Wire colours/pinout (VERIFIED, AEM 30-0300 manual rev 12/29/2022 "Connector B - AEM/FAE UEGO Sensor" in `files/R15/aem_30-0300_fae.pdf` p.10 and 30-0310 manual p.4 `aem_30-0310.pdf`; the same table appears in the 2016/2017 revisions per a mirror): 1 green trim resistor; 2 white heater-; 3 orange COM; 4 not used; 5 red pump current; 6 black sense; 7 not used; 8 brown heater+.
- AEM text: "Avoid cutting or extending the sensor harness... Replacement pins are JST P/N SPUD-001T-P0.5 terminals for 22-26 AWG wire" (30-0300 manual p.10, bullets under "Important Notes on Wiring"). In the 30-0302 manual (a temperature gauge with only the 10-pin connector A) the same sentence appears as "To populate optional extras, use JST P/N SPUD-001T-P0.5 terminals" next to connector A, which shows the sentence is about the 10-pin Power/IO connector in that family. So the SPUD evidence supports the 10-way connector A with certainty and the 8-way sensor connector only by analogy. INFERRED for J2; the repo's own README already says "never tried", which stands. Residual risk that AEM's 8-way connector is some other 2 mm 2x4 housing (JST PUD is the likely one, because a 2x4 with pins 4 and 7 blank fits the PUD footprint, but I found no photo or teardown text; the web search for "PUDP-08V-S AEM" found nothing).
- Also from the AEM 30-0300 text: the gauge uses 5 A inline fuse and 1.5 A nominal / 3 A peak heater supply; the JST PUD is rated 3 A, -25..+85 C (JST/LCSC attributes) - the heater peak is at the connector's limit (INFERRED).

### 2.2 Alternatives for the lead
| Option | Price | Notes | Tag |
|---|---|---|---|
| AEM 30-3427 | 36 USD (22-51) | single-sourced, often out of stock, brand-new connector type unverified | VERIFIED price |
| Seller-built pigtail (see 4) | 10-22 USD at 10-100 pcs | ties J2 to a standard JST part, gives full control | INFERRED |
| Ballenger 12 in pigtail + 5 ft VEMS pigtail | 17.99-19.99 / 19.00 | pre-crimped, no Bosch crimping needed | VERIFIED prices |
| Innovate LC-2 / 14point7 Spartan 3 lead | not retrieved | these ship their own harness and are separate controllers (searches returned nothing usable; one diyautotune listing of Spartan 3 Lite V2 USD 81.99-181.99 with sensor option) | UNVERIFIED |
| Bosch Motorsport mating connector 1 987 280 016 | not captured | full kit, genuine | VERIFIED name |

## 3. How ECUs with built-in wideband present it to buyers
| Vendor | What is sold | Evidence |
|---|---|---|
| ECUMaster EMU Black | ECU has built-in LSU 4.2/4.9 controller; sensor and harness are separate kits: "WHP kit sensor + 6-ft harness with FCI SICMA 2.8 terminals" 111.20 sale (139 list), or "sensor + connector and terminals" 103.20 (129 list); in stock | ecumasterusa.com pages fetched today (VERIFIED) |
| MaxxECU Street/Premium | Premium kit includes ECU, harness, accessories and an LSU 4.9 (USD 1105.84 per search snippet); sensor alone 124.40; plug 8.29 | maxxecu.com store snippets (UNVERIFIED); MINI has no built-in wideband (MaxxECU page snippet) |
| Haltech | sells LSU 4.9 sensor with factory calibration resistor connector (HT-010718), not Deutsch DT-6; Nexus kits include the ECU with onboard wideband; sensor optional | billysspeedshop snippet (UNVERIFIED), kb R05 Haltech page (VERIFIED earlier) |
| rusEFI shop uaEFI | board with LSU controller; "Pigtails and wideband cable +100 USD" and "crimp kit with mating plugs +40" are options; sensor not listed | work/R05/.../rusefi_p_uaefi.html fetched by R05 (VERIFIED) |
| BMM Miata ECU (R05) | ships "wideband adapter harness" with the ECU | kb R05 |
| DIY-EFI CORE4 (R05) | wideband controller + harness GBP 70, plus sensor GBP 120 total as options | kb R05 |
| ME442 (Motorsport Electronics) | no page retrieved; not found by search | not done |
Pattern: the sensor is always an add-on, usually sold as a kit with a ready harness or at least plug+terminals, price 100-140 USD; buyers expect the vendor to say which sensor, to supply the lead, and to document the install.

## 4. Product question: cheapest good way to offer the wideband connection
Facts (VERIFIED unless noted): J2 on the boards is JST S08B-PUDSS-1; LCSC C412098 (S08B-PUDSS-1(LF)(SN)) extended, stock 10,084, 0.3625..0.1992 USD; C20089206 stock 0; matching housing PUDP-08V-S = LCSC C490532, extended, stock 12,171, 0.2899..0.1651 USD; contact SPUD-001T-P0.5 = LCSC C267125, stock 131,221, 0.0182..0.0099 USD, wire 22-26 AWG (0.13-0.33 mm2) (all `tools/lcsc.py` today).

| Option | Parts/unit (USD) | Source | Notes |
|---|---|---|---|
| A. Buyer buys AEM 30-3427 | 0 to seller; buyer pays 22-51, typ. 36 | AEM dealers | connector fit never tested; single-sourced; stock gaps; but it is a finished, crimped, labelled product (INFERRED) |
| B. Seller-made pigtail, Bosch plug kit + JST PUDP-08V-S | Bosch plug kit 7.30-17.99 (ProWire snippet 9.85/7.30@100; Ballenger CONN-75762 17.99/16.25@100; XTRA EUR 4.96) + PUDP-08V-S 0.17-0.29 + 6 x SPUD 0.06-0.11 + 1.5-2 m of 6 conductors 22 AWG about 0.7-1.2 + loom/heat-shrink about 0.5 = about 9-20 (INFERRED sum; wire/loom costs are estimates) + 10-15 min labour | Bosch plug: Ballenger/ProWire/XTRA; JST parts: LCSC | needs Bosch BAK crimp tool (MCP 1.5K die) and a JST SPUD crimper; or buy Ballenger CONN-85762 pre-crimped pigtail 17.99-19.99 and splice to 22 AWG wires with the JST end |
| C. Pre-made Bosch pigtail with JST end made by a harness shop | not quoted | | UNVERIFIED |
| D. Kit: genuine sensor + pigtail (+ bung) | sensor 63.99 (x100) to 69.97 (x1) + B pigtail 9-20 = 73-90 cost | Ballenger sensor | risk of counterfeit supply is zero only with a Bosch distributor; weld bung not priced (not researched) |
INFERRED recommendation: offer (B) as default shipped item, and (A) as the documented fallback for buyers who want to buy a retail part; offer (D) as an optional add-on. A pigtail with JST on the board end is also independent from AEM's catalogue and from the unverified connector identity of 30-3427, because the seller controls both ends. Caveats: (1) the PUD contact takes 22-26 AWG only, heater current up to 3 A fits 22 AWG for 1.8 m (about 0.05 ohm per m x 2) with loss of about 0.2 V at 2 A (INFERRED, 22 AWG about 53 mohm/m); (2) PUD ratings -25..85 C; the J2 plug is inside the car/ECU case, fine; (3) the cable passes through the firewall: ground/heat routing text is needed.

Instructions a buyer needs (to go into INSTALL.md / the box): see implications 8-10 below. The existing INSTALL.md section 6 (lines ~283-297) already covers: same M18 x 1.5 thread, genuine sensor, harness colours, route away from exhaust, never leave sensor in a running exhaust unpowered. Missing: 10 deg angle and connector-up, sensor position (18 in from head / upstream of cat), thread torque and anti-seize (use high-temp, not copper that bridges? Bosch says special grease 5 964 080 112; ordinary nickel anti-seize is typical secondary advice, UNVERIFIED), no silicone sealant, treat the sensor as a consumable, no free-air step needed, what to do with the stock narrowband plug (already there), checking with a meter that the heater+ pin reaches pin 8.

## 5. Free-air calibration and this controller
- AEM: trim-resistor mode is default and recommended; free-air calibration is an option for aged sensors, with the sensor removed from the exhaust (AEM 30-0310 manual p.4-5, 30-0300 manual).
- The board's wideband (FOME/mck1117 firmware, `ext/wideband-mck1117`): grep of `firmware/*.cpp/h` finds no free-air calibration command; the controller is a CJ125-type circuit that uses the sensor's trim resistor through the RT pin (VERIFIED absence of feature; INFERRED that none is needed). Heater logic: Preheat state at 2.0 V (comment "Max allowed during condensation phase (preheat) is 2v", `firmware/heater_control.cpp:169-170`), preheat time 5 s (`wideband_config.h:45`), then ramp from 7 V; heating is only allowed when the ECU sends "allow" (rusEFI engine.cpp:169: `heaterControlEnabled = forceO2Heating || rpmCalculator.isRunning()`), otherwise auto-start from battery voltage if no CAN command arrives (`heater_control.cpp:60-69`). That matches Bosch rule 4.3.2 (do not heat before engine start) when CAN works; with a dead CAN link the wideband falls back to battery-voltage start (INFERRED worth a firmware owner check, out of scope).
- "Never leave an unpowered sensor in a running exhaust" - the Bosch techinfo does not literally say this; the cause is soot/condensate on a cold sensor, plus the rule that the sensor is heated only when exhaust is dry. INSTALL.md wording is a common secondary rule (UNVERIFIED as a Bosch quote), keep it as advice not attributed to Bosch.

## Implications for this project
Goals: (1) errors, (2) free removals, (3) cheaper JLC parts, (4) UX, (5) cheaper overall, (6) packaging/shipping.
1. (UX/doc, medium-high) The identification of J2 as JST PUD and of AEM 30-3427's gauge end as PUDP-08V-S is INFERRED from a manual sentence that, in the sibling 30-0302 manual, refers to the 10-way connector A. Do not tell buyers "30-3427 fits" until one real harness has been plugged in; consider shipping a seller-made pigtail so the claim is under seller control. Evidence: aem_30-0300_fae.txt:105-113, ECUMaster-style fetches above. Confidence medium. Boards: all motherboards (J2), ordered boards too (same JST footprint, can be checked by hand with one sample harness before shipping).
2. (cost/product, medium) Seller-made pigtail 9-20 USD parts versus 36 USD AEM. LCSC stocks the housing and contacts (PUDP-08V-S C490532 12,171 pcs; SPUD C267125 131,221 pcs). Bosch plug via Ballenger 16.25-17.99 at 100 or ProWire 7.30-9.85 (snippet). Confidence medium.
3. (supply, medium) AEM 30-3427 is out of stock at the main US shops with ship dates in 2-3 weeks (onefastshop "Ships the week of Nov 30", iagperformance "contact us"), so the INSTALL.md dependency on it is fragile; offer an alternative lead in the docs. Confidence high for today's state.
4. (doc, medium) INSTALL.md should say sensor must be 0 258 017 025 (or 4.9 with the six-pin plug), name the genuine sources (Ballenger 63.99-69.97 at 100/1, efihardware AUD 130 ex GST, ECUMaster kit 103-111) and the counterfeit tells (BOSCH Germany etch, ribbed cable cover, hologram/packaging - UNVERIFIED single bulletin). Counterfeit rate "90%" is an unverified review comment; do not repeat as fact.
5. (UX/doc, medium) Add Bosch's install rules to INSTALL.md section 6: connector up and at least 10 deg from horizontal, 40-60 Nm with high-temp grease, not near tailpipe, boss 10.5-13 mm, <930 C gas, plug <120 C (keep the plug away from the manifold), no silicone sealants, cover plug when undercoating. Check whether the Miata stock sensor boss geometry meets the 10.5 mm minimum and angle (not checked). Confidence high that the rules are real (Bosch primary). Note the AEM/Bosch disagreement on vertical position and torque (AEM 30 ft-lb vs Bosch 40-60 Nm).
6. (UX, low-medium) Free-air calibration is not required; INSTALL.md need not mention it. The repo should avoid promising a "calibrate" step. Pressure sensitivity: tell turbo-conversion buyers the reading shifts +10 % of Ip at 1.5 bar abs (Bosch graph).
7. (firmware/safety, medium, owner of firmware R02/R10 to confirm) The mck1117 heater logic starts heating from battery voltage if no CAN allow arrives (heater_control.cpp:60-69); with CAN fault the sensor could be heated before engine start, against Bosch 4.3.2. Verify how the shipped firmware sets this (`HEATER_BATTERY_*` constants) before shipping. Confidence medium, not traced fully.
8. (packaging, low) A pigtail/harness adds a bag and a cable to the box; weight negligible. A sensor in the box adds about 0.2 kg and 64-70 USD working capital per unit.
9. (UX, medium) Position 4.9 sensor in Miata: AEM says 18 in from the head and before the cat; the stock narrowband boss at the front of the cat/collector is within that rule for most NA cars but not verified; add "use the stock O2 sensor position (same M18 x 1.5, INSTALL.md) only if the boss is 10.5-13 mm tall" as a check (INFERRED from Bosch 4.9).

## Sources actually read
- `files/R15/bosch_lsu49_motorsport_ds.pdf` (Bosch Motorsport 69034379, 27 Jan 2026) and `bosch_lsu49_techinfo.pdf` (+ .txt; Bosch Y 258 E00 015e 14.6.2005; from ecotrons.com mirror). Page 8 graph read from image.
- `files/R15/aem_30-0300_fae.pdf` (documents.aemelectronics.com, doc 10-0400, 12/29/2022), `aem_30-0310.pdf` (bar-tek.com mirror of AEM doc 10-0310, 9/29/2015). (aem_30-0302 was read and deleted: it is a temperature gauge manual; used only for the connector-A SPUD sentence.)
- Retailer pages (fetched/curl): onefastshop.com AEM30-3427, iagperformance.com 30-3427, parkautomotorsports.ca, billysspeedshop.com (GBP 31.99), maperformance.com; bmotorsports.com ids 2081, 2082, 2080, 3271, 1645 (Ballenger); ecumasterusa.com WHPWB491 and WHPWB492; ictbillet.com WC0XY01; shop.vemstuning.com pigtail; milspecwiring.com; efihardware.com 2977; urotuning.com; tiperformance.com.au; auto-click.co.uk 1928404669; bosch-motorsport-shop.com.au; rusEFI forum post p=43398; askmanual.pages.dev AEM 30-0300 (text of manual incl. connector B table and SPUD sentence); `tools/lcsc.py` live searches; repo files INSTALL.md, README.md, kb/interconnect.md, ext/wideband-mck1117/firmware/heater_control.cpp, wideband_config.h, repo/firmware/ext/rusefi/.../engine.cpp, AemXSeriesLambda.cpp.
- web search results (snippets only, UNVERIFIED where noted): ProWire, XTRA Motorsport, eBay, MaxxECU, Haltech, Link ECU lifespan article, kartsportnews fake sensors, wbo2.com position/installation guide.

## Not checked
- AEM's own 30-3427 product page (HTTP 403), so description/length/connector straight from AEM unverified; no photo of the gauge-end housing; no teardown naming PUDP-08V-S.
- ME442 wideband details, Innovate LC-2 and 14point7 Spartan 3 prices and harnesses, Bosch Motorsport harnesses (price), AliExpress/Amazon pigtails and clone sensors (marketplaces not reachable by the search tool), TE-branded Bosch-compatible housing numbers.
- Wire/loom prices and a seller labour estimate (estimates), weld-in bung price, the Miata stock O2 boss geometry and angle, real back-pressure at the Miata front sensor, how much this controller's reference calibration depends on RT.
- Link ECU lifespan article and wbo2.com installation guide were not read in full.
