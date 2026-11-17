# R26 Shipping, carriers, customs (notes, 2026-11-16)

ASSUMPTION: seller is in the United States (owner location not given). Package 9x7x3 in (22.9x17.8x7.6 cm, 189 cu in = 0.109 cu ft), 250-450 g (0.55-0.99 lb, i.e. under 16 oz), declared value 399 USD.
UK/EU seller variant: see section 8.

## Summary
1. USPS Notice 123 (effective 2026-10-04, includes the holiday temporary price increase to 2027-01-17) is the only carrier price list I could read in primary form. UPS/FedEx rate PDFs blocked automated access (Access Denied) so their prices are secondary-source only.
2. Cheapest sensible domestic: USPS Ground Advantage, commercial (label platform) price 7.33-8.95 USD for <16 oz zones 1-9; retail 10.05-13.65. USD 100 insurance included. Add Signature Confirmation 4.15 (electronic) and extra cover to 399 USD. Realistic all-in budget about 14-18 USD (label + signature + cover + box).
3. Premium: Priority Mail (1 lb commercial 9.44-16.07 zones 1-8; retail 11.50-17.95), same 100 USD included cover, 1-3 day target; or UPS/FedEx with declared value (list 12-16 USD+, 2 lb billable by dimensional weight, secondary data).
4. Full-value cover 399 USD: USPS merchandise insurance fee 6.05 USD (300.01-400 tier) vs third-party (ShipStation ParcelGuard claims 0.55 per 100 = about 2.20, vendor claim).
5. International is where the money goes: USPS retail First-Class Package Intl 9-16 oz = 26.00 (Canada), 31.95 (UK), 29.40-29.95 (FR/DE), 41.25 (AU/NZ), 33.95 (JP). Priority Mail Intl 1 lb 43.55 Canada, 66-83 elsewhere, with 200 USD cover included. Buyer pays import VAT/GST (and carrier fees) on a 399 USD item in nearly every market.
6. Tariff classification: US HTS 8537.10.91.60 "programmable controllers" (CBP ruling NY N275130, 2.7%); UK/EU 8537 10 91 / 98 with 2% UK (UK tariff API). Uncertain: a plug-in ECU "for a motor vehicle" could be argued under 8708/8537; CBP rulings consistently use 8537.10.
7. USPS DDP now exists (Jul 2026) for Canada, Germany, UK (135-900 GBP) and 21 more European destinations; NOT for Australia, NZ, Japan.
8. De minimis: US suspended for all countries and modes (CBP rules June/July 2026); EU 3 EUR duty from 2026-07-01 applies to under-150 EUR parcels only (not our item).
9. Inbound from China: formal/informal entry required, 2.7% MFN + 12.5% Section 301 forced-labour tariff (from 2026-07-24) + possibly legacy 301 (not verified for this HTS).
10. Pricing: ship calculated for international; domestic free shipping is cheap to build in (about 15 USD = 3.8 pct of 399).

## 1. USPS domestic (VERIFIED, https://pe.usps.com/text/dmm300/Notice123.htm, saved kb/research/files/R26/usps_notice123_2026-10-04.txt, "Notice 123 Effective October 04, 2026")
Holiday temporary increase 2026-10-04 to 2027-01-17 (VERIFIED summary page https://www.webull.com/news/15464841938289664, secondary; PRC docket CP2026-10): GA zones 1-4 0-3 lb +0.50 retail/+0.40 commercial; zones 5-9 +0.75/+0.55. Prices below are the Notice 123 tables as published (I assume they include it; the table cannot show this). After 2027-01-17 expect roughly 0.4-0.75 less (INFERRED).
Rows are "weight not over". Zones 1 to 9 (zone 1&2 .. 8 and 9 for retail).
| Service (<16 oz / 1 lb) | Z1 | Z2 | Z3 | Z4 | Z5 | Z6 | Z7 | Z8 | Z9 |
|---|---|---|---|---|---|---|---|---|---|
| GA Commercial, 15.999 oz | 7.33 | 7.34 | 7.70 | 7.86 | 8.24 | 8.41 | 8.62 | 8.95 | 8.95 |
| GA Retail, 15.999 oz | 10.05 | 10.45 | 10.70 | 11.10 | 11.70 | 12.10 | 12.70 | 13.65 | 13.65 |
| Priority Commercial, 1 lb | 9.44 | 9.72 | 10.11 | 10.80 | 13.82 | 15.32 | 15.93 | 16.07 | 33.33 |
| Priority Retail, 1 lb | 11.50 | 12.00 | 12.15 | 12.40 | 14.05 | 15.50 | 16.60 | 17.95 | 35.25 |
| Priority Mail Express Commercial, 0.5/1 lb | 32.51/32.99 | 32.51/33.53 | 33.26/35.91 | 35.59/40.45 | 40.53/47.39 | 43.34/51.12 | 46.26/54.36 | 49.98/58.14 | 65.80/76.77 |
Notes: weight under 1 lb is one price per zone since the 2026-07-12 change (https://support.pirateship.com/en/articles/15453569, secondary). Dimensional weight (divisor 139) only matters over 1 cu ft, not here (UNVERIFIED rule, secondary; our 0.109 cu ft is far below).
Delivery: GA 2-5 business days, Priority 1-3 (UNVERIFIED, ship.com secondary; usps.com service commitment not read).
Insurance included: 100 USD with GA and Priority (VERIFIED via https://www.usps.com/ship/insurance-extra-services.htm through fetch summary). Merchandise insurance fee table (Notice 123): to 50 USD 2.80; 100: 3.50; 200: 4.50; 300: 4.55; 400: 6.05; 500: 7.55 (then +1.50/100 above 600). So cover 399 = 6.05 (VERIFIED). Whether the included 100 USD is credited is not stated: treat 6.05 as the full cost.
Signature Confirmation: 5.15 retail / 4.15 electronic; Adult Signature Required 9.70; Adult Signature Restricted Delivery 10.00 (VERIFIED Notice 123). Claims must be filed within 60 days; need proof of value (VERIFIED usps.com fetch).
Loss/theft exposure: with tracking and insurance the seller is reimbursed up to insured value but claims need time and proof; "delivered" porch theft is the main exposure: Signature Confirmation closes it (INFERRED). Without signature the seller carries 399 - 100 = 299 USD uninsured on a loss if cover is not bought.
Cubic pricing: package 0.109 cu ft qualifies for the lowest cubic tier; Pirate Ship notes cubic max length raised to 22 in (secondary).

## 2. UPS / FedEx (secondary only; primary PDFs returned Access Denied)
- UPS Ground Saver list 1 lb: 13.00 (zone 2) to 16.26 (zone 8), effective 2026-05-06 per darrigoconsulting/branvas (UNVERIFIED); ship.com: 15.31 zone 5 list, 50 USD liability, 2-7 days. UPS Ground 1 lb 11.99-15.03 (UNVERIFIED, one aggregator). UPS Ground Saver does not take under-1 lb at a lower tier.
- Dimensional weight: 189 cu in / 139 = 1.36 lb so UPS/FedEx bill 2 lb (INFERRED; divisor 139 is secondary). Declared value above 100 USD costs about 1 USD per 100 (UNVERIFIED memory).
- FedEx Ground Economy: 11.99-15.01 list 1 lb zone 2-8 plus 1.15 delivery/returns surcharge (secondary); demand surcharges 2.55 (Oct 26-Nov 22) and 4.05 (Nov 23-Dec 27) 2026 (secondary, from fedex.com FGE fee PDF search hit, not opened).
- UPS announced published Daily Rates up 5.9 pct on 2026-12-21 (UPS homepage snippet via search).
- Discounted platforms: Pirate Ship (free; claims up to 87 pct off USPS, 85 pct UPS), Shippo (free 30 labels/month, Pro 19 USD/mo), ShipStation 14.99/mo, EasyPost per-label. Commercial USPS prices above are what these platforms resell (the "Commercial" columns). All claims vendor marketing (UNVERIFIED).
- Recommendation INFERRED: USPS GA/Priority via a free platform; UPS/FedEx not competitive for a 0.5-1 lb 189 cu in parcel (2 lb billable, higher list).

## 3. International, USPS (VERIFIED Notice 123, retail unless stated)
Price groups (VERIFIED Notice 123 country table, columns PMEI / PMI / FCPIS): Canada 1/1/1; Australia 12; New Zealand 12; France 15; Germany 16; Japan 17; UK 20.
| Dest (group) | FCPIS 9-16 oz retail | FCPIS commercial | PMI 1 lb retail | PMEI 1 lb retail |
|---|---|---|---|---|
| Canada (1) | 26.00 | 24.69 | 43.55 | 67.05 |
| Australia / NZ (12) | 41.25 | n/r | 70.65 | 95.40 |
| France (15) | 29.40 | n/r | 69.50 | 88.25 |
| Germany (16) | 29.95 | n/r | 82.30 | 102.20 |
| Japan (17) | 33.95 | n/r | 66.05 | 95.60 |
| UK (20) | 31.95 | n/r | 69.70 | 93.15 |
PMI commercial base 1 lb Canada 42.14 (~3 pct below retail). International insurance (PMI/PMEI): up to 200 USD included; 200.01-300 13.85; 300.01-400 17.55 (VERIFIED). FCPIS insurance not found: UNVERIFIED that it has none (memory), so for 399 USD use PMI/PMEI or a carrier with declared value.
Transit: FCPIS/PMI 6-14 business days, PMEI 3-5 (UNVERIFIED memory/secondary).
So full-value cover costs: Canada PMI 43.55+17.55 = 61.10 USD; UK PMI 69.70+17.55 = 87.25 USD.
Paperwork: electronic customs data (CN22/CN23 data via label tools) required; description, HS code, value, origin; EU/NI stricter goods-description rules from 2026-01-01 (Shippo, secondary).
Typical buyers' complaints: courier brokerage/disbursement fees (UK Royal Mail 8 GBP handling fee, Parcelforce 12 GBP, DHL min ~11 GBP: secondary, "UNVERIFIED"; Canada Post ~9.95 CAD handling when tax/duty assessed: secondary conflicting with a 5 USD claim; UPS/FedEx Canada brokerage 20+ CAD: anecdotal).

## 4. HS classification (ECU)
- US: HTS 8537.10.91.60 "Programmable controllers", general duty 2.7 pct, free for many FTA partners, column 2 35 pct (VERIFIED hts.usitc.gov API today; JSON in kb/research/files/R26/hts8537.json). CBP ruling NY N275130 (2016-05-10, engine ECU, "programmable device controlling an internal combustion engine", 8537.10.9060, 2.7 pct, https://www.customsmobile.com/rulings/docview?doc_id=N275130, VERIFIED via fetch). Other rulings by search snippet use the same number (Japan ECU 2013, powertrain unit 2015). Contrary older: 1992 ruling 9032 (UNVERIFIED snippet).
- UK Global Tariff: 8537 10 91 99 "Other" programmable memory controllers: third-country duty 2.00 pct, VAT 20 pct (VERIFIED UK Trade Tariff API today). The UK/EU nomenclature has specific 10-digit subheadings for ECUs of defined types (8537109125-8537109175; 8537109845-8537109893) mostly for appliance/vehicle OEM use; a universal aftermarket ECU falls to "Other" 8537 10 91 99 or 8537 10 98 99 (INFERRED).
- Reasoning: the product is a programmable controller (microcontroller + memory, <=1000 V) -> 8537.10. Heading 8708 (parts of motor vehicles) excluded because 8537 is a more specific electrical heading and EN notes to Section XVII exclude articles of 85 (INFERRED; Section XVII Note 2(f)? not verified). Uncertainty: medium. Recommend a binding tariff information ruling only if volume warrants.
- EU TARIC not queried (no verified EU duty rate; secondary/memory 2.2 pct UNVERIFIED).

## 5. Destinations, 399 USD, buyer-side cost
| Dest | VAT/GST | Duty | Who collects / DDP | Seller scheme applies at 399? |
|---|---|---|---|---|
| UK | 20 pct import VAT (VERIFIED API) | 2 pct (VERIFIED API) | Over 135 GBP: normal import VAT at border, buyer pays; seller point-of-sale VAT only for consignments up to 135 GBP (VERIFIED gov.uk VAT overseas goods page). USPS DDP available for 135-900 GBP via PMI/PMEI (VERIFIED USPS Postal Bulletin 22707) | No (399 USD about 300 GBP exceeds 135) |
| EU | 20-25 pct import VAT national | about 2.2 pct (UNVERIFIED) | IOSS only for consignments up to 150 EUR, so over 150 EUR import VAT at border; 3 EUR duty and 2 EUR handling fee target under 150 EUR (Consilium via search summaries; 403 on direct fetch) | No |
| Germany, France etc. | | | USPS DDP "required" for dutiable items in FR, BE, DK, FI, PT, LU...; DE required; optional in AT, IT, NL, ES, SE... (VERIFIED Postal Bulletin 22707 effective 2026-07-01) | |
| Canada | 5 pct GST plus provincial/HST | 0 if CUSMA-origin; origin of a US-assembled board with Chinese parts is doubtful (INFERRED) ; surtax claims unverified | Canada Post handling about 9.95 CAD (secondary) ; DDP optional by USPS | No federal scheme for sellers on goods; (UNVERIFIED) |
| Australia | 10 pct GST | goods up to 1000 AUD: no duty (UNVERIFIED), 399 USD about 610 AUD | LVIG: overseas seller must register and collect GST at sale once AU sales reach 75,000 AUD (secondary); under the 1000 AUD limit | Yes, scheme covers it; below the sales threshold buyer pays at border |
| New Zealand | 15 pct GST | none for goods under 1000 NZD (UNVERIFIED) | Offshore supplier registers/collects once supplies exceed 60,000 NZD (secondary) | Yes (399 USD about 690 NZD) |
| Japan | 10 pct consumption tax | 8537.10 duty not verified | Low-value (up to 10,000 JPY) exemption irrelevant; platform rules from 2028-04 (secondary) | No |
DDP cost from express carriers: DHL 2 pct of duties/taxes min 17 USD, UPS 2 pct min 7-11.5, FedEx 15 USD or 2 pct (secondary, conflicting, UNVERIFIED). USPS DDP fee not stated in the bulletin.

## 6. US de minimis and inbound from China
- VERIFIED (Federal Register API, documents 2026-12670 and 2026-12669): CBP indefinitely suspended the de minimis exemption for non-postal modes effective 2026-06-24 (all entries need formal or informal entry) and for mail effective 2026-07-24, with a new postal informal entry process.
- VERIFIED (FR 2026-15181, USTR): Section 301 forced-labour action imposes 12.5 pct on products of China from 2026-07-24 (other economies 10 or 12.5). Annex exemptions not checked.
- Legacy Section 301 China lists (25 pct): HTS 8537.10.91 membership NOT verified (UNVERIFIED). IEEPA tariffs struck down 2026-02-20 per secondary sources (not verified here).
- Expected duty for assembled boards classed as 8537.10: 2.7 + 12.5 = 15.2 pct (plus 25 pct if on legacy list). Bare PCBs/parts are different headings.
- Courier: DHL Express/FedEx/UPS from China include brokerage when paid by importer; plan formal entry and broker or carrier "duty and tax forwarding" fee about 15-20 USD (secondary). USPS-class China postal: postal informal entry now.

## 7. Returns and pricing policy
- Returns: domestic return label about the same as outbound (GA zone price 7-9 commercial) ; USPS returns options in Notice 123. Exchange: two-way cost 15-20 USD domestic; international return needs a customs return declaration and may cost 26-60 USD one way with duty refund difficult (INFERRED).

## 8. UK/EU seller variant (brief)
Royal Mail/Evri/DPD rates not read. UK->EU: VAT collection for over 150 EUR at border (buyer), UK->US: US duty and Section 301 do not apply (UK origin, MFN 2.7 pct plus any reciprocal tariff, not verified). Use IOSS only below 150 EUR.

## Implications for this project
1. Budget about 15 USD domestic: GA commercial (8-9) + Signature Confirmation 4.15 + 6.05 insurance on 399 (or 2.20 third-party) + 1-2 box. High confidence on price lists, medium on delivery times.
2. Ship international as Priority Mail International (cover 399 USD) or DDP-capable service; quote shipping at checkout; for UK/Canada/Germany use USPS DDP where available so buyers see no border fee. Confidence medium.
3. Use HTS 8537.10.9160 / UK 8537109199 on customs forms, description "engine control unit, programmable controller for automobile". Medium.
4. Box: 9x7x3 in is within cubic tier; keep under 16 oz to stay at the 15.999 oz price; any weight over 1 lb moves to 1 lb+ rows. High.
5. China inbound: budget 15.2 pct duty plus broker fee; de minimis is gone; check Section 301 legacy list for chosen HTS. Medium.
6. Seller registration for AU/NZ GST only after 75,000 AUD / 60,000 NZD sales; not needed initially. Medium.

## Sources actually read
Notice 123 (usps), usps.com insurance page, Pirate Ship July 2026 article, Postal Bulletin 22707, USITC HTS API, UK Trade Tariff API, Federal Register API (2026-12669/12670/15181/22735), gov.uk VAT overseas goods, customsmobile N275130; the rest search snippets.
## Not checked
UPS/FedEx primary rates (blocked); EU TARIC rate; Canada CBSA, Australia ABF, NZ, Japan official pages (403/404); DDP fees; Section 301 legacy list for 8537.10.91; USPS service commitments; Royal Mail/Evri; JLCPCB courier prices (see R21); dimensional-weight rules; FCPIS insurance.
