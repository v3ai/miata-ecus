# R21 JLCPCB cost model (read 2026-11-16)

## Summary
1. Current JLCPCB PCBA fee table (page "PCB Assembly Cost", updated 2026-10-22) VERIFIED: Economic setup $8.18, stencil $1.53, SMT $0.0016/joint, $3.07 per unique non-preferred Extended part, manual/THT $0.0164/joint + $3.58 per order. Standard: setup $25.56, stencil $8.21, $1.53 per unique part (basic and extended), fixtures $16.42-41.04, packing $0.50+$0.00003/cm2 per board, handling fee if Standard < Economic + $14.93.
2. Economic PCBA is limited to 2-50 boards (some options 2-30), single-sided placement, 2/4/6 layers, 0402+, 0.4 mm pitch. **Quantity 100 forces Standard PCBA** (VERIFIED, capabilities page).
3. Daughterboard rev0.10 has **330 placements (not ~430)**, 1042 SMD pads, 92 unique LCSC lines of which 44 Extended: 7 are Preferred Extended (no fee on Economic) so **37 chargeable Extended lines = $113.59 per order** (VERIFIED from kb/parts_manifest.json `jlc_preferred` flag + fee table).
4. Central model, daughterboard 6L (PCB estimate UNVERIFIED): $83 / $66 / $52 / $48 / $45 per board at 5/10/30/50/100, ex shipping and tariff. Parts are ~$37-48 of it; fixed assembly fees dominate at q<=10.
5. Bare-PCB prices could NOT be obtained (quote SPA needs login/JS; no public price table). One official anchor: 6-layer 100x100 mm ENIG 5 pcs "from $35.1" (jlcpcb.com/resources/multiple-layer-pcb, undated). All PCB numbers below are UNVERIFIED estimates, +-40%.
6. US duty: JLCPCB pre-collects (DDP) **35% on PCB and SMT** (table image on us-tariff-policy-faq, updated 2026-10-29, VERIFIED); my independent stack for a PCBA is MFN ~2-3% + Section 301 25% + forced-labor Section 301 12.5% (since 2026-07-24) = ~40%; range 12.5% to ~55% depending on HTS (UNVERIFIED classification). Section 122 10% expired 2026-07-23; IEEPA duties ended 2026-02-24. De minimis is gone.
7. Biggest levers (q=10, per set): unique Extended lines ($11.4/bd for all 37, ~$0.31 per line), quantity (q5 $83 -> q50 $48), tariff avoided by buying THT parts (MAP sensor etc.) in the US (~$10 on MAP alone). 6L vs 4L is only ~$3/bd at q10 (UNVERIFIED).
8. Stock risk at q=100: STM32F407VGT6 JLC stock 126, 1x40 socket C124412 stock 65 (2 per board), MAP C90152 stock 155, TCAN1042 257 (manifest, live 2026-11-15).

## Assumptions (all of them)
- A1 Prices in USD, JLCPCB fee page of 2026-10-22 (FAQ page dated 2026-09-09 still shows old $8/$1.50/$0.0017/$3.5/$0.0173/$3 figures; trusted the newer pricing page and the Oct-2026 JLCPCB blog that quotes the same $8.18/$3.07 numbers).
- A2 Joint = SMD pad (1042 for cur_db from pcb_pads.csv: refs in the JLC BOM, pad_type smd). JLC's own joint count may differ slightly. UNVERIFIED mapping.
- A3 Chargeable Extended = LCSC line with jlc_library != base and jlc_preferred false (manifest). cur_db 37, ord_db 34, motherboards 4-5 (2920L300/30GR, BSMD1812-110-33V, USB4105-GF-A, USBLC6-2SC6, +SMD1812-200-30 on 99-00 and 01-05).
- A4 Parts price = JLC assembly-library tier price at (BOM qty x boards). No attrition/MOQ overage added (JLC FAQ: spare parts are included in the component fee; EasyEDA forum example 1/board x 5 boards billed 9 pcs; UNVERIFIED size). Real parts cost will be a few % to several $ per order higher.
- A5 Tier: Economic for q<=50, Standard at q=100 (and Standard rail/fiducial requirement assumed handled by JLC at no charge, UNVERIFIED: capabilities table says edge rails "Necessary" for Standard).
- A6 Standard fixture fee 2 fixtures (q<30) $16.42, 3 (30-99) $24.63, 5 (100-199) $41.04; stencil/fixture storage and $0.45 confirm-placement not included.
- A7 No X-ray fee: no QFN/DFN/BGA/LGA in any BOM package string (manifest). INFERRED; JLC decides at quote.
- A8 Hand-fitted parts (J1/J2 headers, harness header, MAP, sockets, JST, box header) are fitted by the seller: no JLC cost, but their parts cost is outside the model except where stated.
- A9 Motherboards: one design ordered at q; four designs each pay their own fixed fees (the four 154x162 boards cannot share a panel, panel max 250x250).
- A10 Bare PCB totals (UNVERIFIED estimates, order totals, USD): DB 6L ENIG 125x76: 45/70/165/250/420; DB 4L: 22/36/85/130/220; MB 2L HASL 154x162: 16/28/75/115/210 (5/10/30/50/100 pcs). Basis: JLC $35.1 anchor for 6L 100x100 5 pcs, JLC 2023 blog "4-layer $70.6/m2", my recollection that 2L 150x150 5 pcs is about $14 (UNVERIFIED). Both boards exceed 100x100 in at least one dimension so they are in the larger-size price band.
- A11 Shipping and tariff: see sections below; goods value for tariff = PCB + assembly + parts, no freight.

## Fee tables (VERIFIED, https://jlcpcb.com/help/article/pcb-assembly-price, "Last updated Oct 22, 2026")
| Item | Economic | Standard |
|---|---|---|
| Setup | $8.18 | $25.56 single / $51.12 double side |
| Stencil | $1.53 | $8.21 / $16.42 |
| SMT per joint | $0.0016 (to 100k) | $0.0016 to 50k, $0.0013 to 100k, $0.0012 above |
| Manual/THT per joint | $0.0164 (<=10k) | same |
| Hand-soldering labor | $3.58/order | $3.58/order |
| Component loading | $3.07 per unique Extended (Basic and Preferred free) | $1.53 per unique part, basic or extended |
| Packing | free | $0.50 + $0.00003 x area cm2 per board |
| Handling | none | at least $14.93 over Economic if order also qualifies for Economic, else difference charged |
| Single-board surcharge | none | min $0.48/board SMT fee |
| X-ray (BGA/QFN/leadless) | $1.64 per pc (1-10) ... $0.33 (201-500) | same |
| Fixtures | none | $16.42 (1-29), $24.63 (30-99), $41.04 (100-199) |
| Confirm Parts Placement | $0.45 | $0.45 |
| Large size | >650 cm2 $57.46 (not relevant) | |
Capabilities (https://jlcpcb.com/capabilities/pcb-assembly-capabilities, VERIFIED today): Economic single-sided placement only, 2/4/6 layers, 0.8-1.6 mm, qty 2-50 (the options table caps some thickness/colour combinations at 30; 1.6 mm green HASL/ENIG is 2-50, ENIG 2-30 on one row), single PCB 10x10 to 470x500, panel 250x250 max, mouse-bite panels only, standard stackup only, min 0402, pitch 0.4 mm, **reflow 255 C not adjustable** (Standard 240 C), no SPI. Standard: 1-32 layers, V-cut OK, 2-80000 pcs, min 70x70 mm, SPI, edge rails and fiducials necessary.
Cross-check: JLCPCB blog https://jlcpcb.com/blog/reduce-pcb-assembly-cost-prototype (Oct 2026) gives same fees; its test board (4L, 140x75 mm, 75 lines, 43 chargeable Extended, single-sided SMT) quoted $140.49/bd at 2, $94.97 at 5, $59.37 at 10, $49.62 at 20, $37.36 at 50 (PCB+assembly+parts, no shipping). My 4L ordered-rev model gives $74/$60/$44 at 5/10/50 for a board with 34 chargeable Extended lines, i.e. same order of magnitude and plausible.

## Daughterboard model (USD per board, order total in brackets), ex shipping and tariff
| q | tier | PCB 6L (est) | assembly | parts | total/bd | (order) |
|---|---|---|---|---|---|---|
| 5 | Econ | 9.00 | 26.33 | 47.72 | 83.05 | 415 |
| 10 | Econ | 7.00 | 14.00 | 45.07 | 66.06 | 661 |
| 30 | Econ | 5.50 | 5.78 | 41.04 | 52.31 | 1569 |
| 50 | Econ | 5.00 | 4.13 | 39.15 | 48.29 | 2414 |
| 100 | Std | 4.20 | 4.16 | 36.74 | 45.11 | 4511 |
Assembly = 8.18+1.53+37x3.07 (=122.9 fixed) + 1042 x $0.0016 per board (=1.67). At q=100 Standard: 25.56+8.21+92x1.53 (=140.76)+fixtures 41.04+SMT 150.5+packing 50 = $416 (=4.16/bd). Forcing Standard at q<=50 costs +$14/+7/+3/+2 per board at 5/10/30/50 (the $14.93 handling-fee rule makes Standard never cheaper than Economic for the same design).
Ordered rev0.9 (4L, 302 placements, 976 pads, 34 chargeable Ext, 88 lines): 74.5 / 59.8 / 47.6 / 44.1 / 41.6 per board (PCB est 4.4/3.6/2.8/2.6/2.2).
Parts: manifest prices at tier. Largest lines: STM32F407VGT6 $5.05 (@1) - 3.34 (top), VND7NV04 x8 $2.68 each, AD8628 $2.82, TLS115B0EJ x2 $1.26.

## Motherboard model (2L 154x162 mm HASL, JLC fits SMD only; MAP, sockets, headers by seller)
| q | MB 1989-95 (4 ext) total/bd | 1999-2000 (5 ext) | 1996-97 (4 ext) | split: PCB / asm / parts (89-95) |
|---|---|---|---|---|
| 5 | 9.22 | 9.93 | 9.18 | 3.20 / 4.48 / 1.54 |
| 10 | 6.43 | 6.83 | 6.39 | 2.80 / 2.28 / 1.35 |
| 30 | 4.57 | 4.76 | 4.53 | 2.50 / 0.82 / 1.25 |
| 50 | 4.01 | 4.14 | 3.97 | 2.30 / 0.52 / 1.19 |
| 100 (Std) | 4.70 | 4.78 | 4.65 | 2.10 / 1.55 / 1.05 |
Fixed fee per motherboard design on Economic: 8.18+1.53+4x3.07 = $22.0 (five Ext: $25.1); four designs = about $93 per order round. 52 SMD pads/board only. The seller-fitted THT part cost (self-order BOM) is separate: MAP sensor C90152 $29.33@1 (JLC) / $29.61 (LCSC), socket 1x40 C124412 $0.57 x2, TE harness header not in LCSC/JLC at all (manifest lines have no LCSC code).
Option "JLC fits all THT" (190 PTH pads, 89-95 board, parts incl. MAP+sockets ~$30.7): total/bd 43.8/40.6/38.5/37.9/38.6; THT labor alone = $3.58 per order + 190 x $0.0164 = $3.12/bd (+$0.72/bd at q5). Not possible for the harness header and the NRND MAP only if stock is short (155).

## Bare PCB: size steps, layers, finishes (what is VERIFIED)
- 6-layer boards do not support HASL; finish is ENIG 2 uin (OSP also listed in general capabilities) (https://jlcpcb.com/capabilities/pcb-capabilities line "HASL ... boards with 6 or more layers ... do not support HASL"; https://jlcpcb.com/6-layer-pcb "Surface Finish ENIG 2u"). VERIFIED.
- Via-in-pad (epoxy/copper filled and plated over, POFV) is the default and free for 6+ layer boards, via diameter 0.15-0.55 mm; on 2/4-layer it is an option with plugged-via rules (capabilities page lines 340-354). VERIFIED. 0.1/0.15 mm hole and 0.2/0.25 mm via under 0.45 pad cost extra (line 206).
- Min trace/space multilayer 3.5/3.5 mil; 6-layer page "from $2" is a promo for 5 pcs 50x50 (multiple-layer-pcb page). 
- The 100x100 mm price step and per-layer prices are NOT on a public page I could reach (quote tool is a login-gated SPA: cart.jlcpcb.com/quote; no price API found in its JS chunks). Step is widely known (UNVERIFIED): boards <=100x100 mm in 5/10 pcs get the cheap flat price; larger boards are priced per area. 125x76 (95 cm2) is above the step only because one side exceeds 100 mm: fitting it into 100x100 needs <=100 cm2 with both sides <=100, i.e. 20% shorter long side with 95% area utilisation: not realistic (J1/J2 1x40 headers are 101.6 mm long by themselves, INFERRED from 40 x 2.54).
- Motherboard 154x162 (249 cm2) cannot go under the step (stock case outline).

## Parts/assembly policies
- Preferred Extended parts free on Economic (FAQ). Global sourcing/attrition: JLC FAQ part 2 says spare parts are priced in; leftover parts cannot be shipped back (blog line 365).
- Through-hole: JLC does "wave soldering" THT only for parts marked as such in the library; $3.58/order + $0.0164/joint (VERIFIED price page; FAQ). Unused holes are masked (capabilities FAQ). The self-order BOM says J1/J2 headers must be soldered while plugged into the motherboard to come out straight (repo fab_*_self_order_bom.csv), so JLC fitting them would be mechanically wrong: keep seller-fitted.
- Stacked-part feature (DIP in socket) exists but costs manual operation (capabilities FAQ).

## Shipping (UNVERIFIED numbers)
JLCPCB shows shipping only on the quote page after choosing "Ship to" (https://jlcpcb.com/help/article/how-much-does-shipping-cost, VERIFIED statement); no public rate table. Combine Shipping (free handling, 15 days free storage, then $1.5/m3/day, https://jlcpcb.com/help/article/combine-shipping-service VERIFIED) lets several orders ship together (useful because the 4 motherboard orders + daughterboard order are separate orders). Sea shipping exists (u.s-sea-shipment-instructions, not read).
Weight estimate INFERRED: DB assembled ~45 g, MB 2L 154x162 ~70 g, with packing ~150 g/set. Express estimate (my guess from forum reports, UNVERIFIED, +-40%): q5 $35, q10 $45, q30 $75, q50 $100, q100 $180 for DB+MB together = $7.0, 4.5, 2.5, 2.0, 1.8 per set. Forum anecdote (PedalPCB) of $70-90 express on $25 order is pre-DDP-era/tariff-era and not used.

## US duty, as of 2026-11-16
VERIFIED from JLCPCB (https://jlcpcb.com/help/article/us-tariff-policy-faq, 2026-10-29): JLC pre-collects import taxes on DDP orders; rate table (image rs.jlcpcb.com/static/image/news/Tariff-us.png, saved in files dir) PCB 35%, SMT 35%, Stencil 90%; individual customers must use DDP; companies may choose CPT (buyer pays carrier/CBP, needs EIN, mandatory above $2,500); 35-90% rates are flat averages with no true-up (only the old 175% orders get refunds). JLC says PCBA are "intermediate products", so the exempt electronics HS codes (8471, 847330, 8542 etc.) do not apply. Their listing: reciprocal and fentanyl duties ended 2026-02-24; Section 301 25%; "122 tariff 12.5% new from July 24 2026" (actually the forced-labor Section 301 duty, see below).
Independent sources (secondary, SEO/trade pages, consistent with each other, UNVERIFIED against Federal Register but 91 FR 47318 / heading 9903.05.31 is cited): gingercontrol.com guide: MFN + China-list Section 301 (7.5-100%) + 12.5% forced-labor Section 301 (heading 9903.05.31, since 2026-07-24, exemptions via note 52 e.g. Section 232 goods) ; Section 122 10% applied 2026-02-24 to 2026-07-23 only (150-day limit, not extended); IEEPA duties not collected since 2026-02-24 after the Supreme Court ruling; de minimis eliminated (China 2025-05-02, global 2025-08-29); MPF 0.3464% of value on formal entries (informal entry flat $2.77 below $2,500/$250 item limits for express); 178 Section 301 exclusions extended to 2027-01-09/10 (GHY, KPMG Nov 10 2026 notice). tarifftracker.ai (older Section-122 era) says 8534.00 PCBs 25% + 10%.
My stack for a PCBA (INFERRED, HTS unverified): ECU assembled board most plausibly 8537.10.91xx (UNVERIFIED MFN ~2.7%) or 8543.70; Section 301 List 1/3: 25%; forced labor 12.5% => about 40% of customs value. JLC's flat 35% is within 5 points, i.e. consistent. Scenarios per $ of goods value: low 12.5% (if some 301 exclusion or a code outside lists, unlikely), central 35-40%, high ~55% (if Section 232 auto-parts 25% applies to the code and forced-labor then exempts: 2.7+25+25 = 52.7%; whether 8537.10/8543.70 is on the 232 auto-parts annex NOT verified, search found no confirmation).
Duty on the central case, per set (DB+MB SMD-only, goods value from the models): q5 $92 -> $32; q10 $72.5 -> $25; q30 $57 -> $20; q50 $52 -> $18; q100 $50 -> $17 at 35%. Range at q10: $9 (12.5%) to $40 (55%). Duty applies on top of all costs and also on JLC-fitted THT parts (MAP $29 => ~$10 duty), so buying MAP/sockets/headers from US distributors avoids it (INFERRED; whether JLC charges the 35% on components too is not stated: UNVERIFIED).

## UK / EU in brief
- EU: since 2026-07-01 no low-value exemption; B2C parcels <=EUR150 pay a temporary EUR3 per HS code per shipment, B2B pay standard duty regardless of value (https://jlcpcb.com/help/article/eu-customs-reform-faq, 2026-10-28, VERIFIED). VAT: JLC collects for individuals up to EUR150/GBP135, customs collects for companies and above (https://jlcpcb.com/help/article/customs,-duties-and-taxes, 2026-11-10, VERIFIED). Duty rate for 8537.10.91: about 2.1% (single aggregator, UNVERIFIED). VAT 19-25% depending on state.
- UK: 8537.10 lines 2.0% third-country duty (aggregators, UNVERIFIED) + 20% VAT. Rough landed uplift: EU/UK ~ +22-27% (duty+VAT) on goods+shipping vs ~35-40% duty only (before sales tax) for the US. For UK/EU VAT is recoverable by a registered business.

## Cost levers ranked (daughterboard unless stated; per board; DB q10 / q50)
| Rank | Lever | Saving | Basis |
|---|---|---|---|
| 1 | Order quantity 5 -> 50 | $83 -> $48 per DB (-42%); fixed 123 $/order | model |
| 2 | Cut chargeable Extended lines (37 now) | $3.07 per line per order: $0.31/bd @10, $0.06 @50; all 37 gone = $11.4 @10 | fee table |
| 3 | US tariff: keep high-value THT parts (MAP $29, sockets) outside the JLC order | ~$10 per set on MAP (at 35%) | A11, UNVERIFIED base |
| 4 | Tier: stay on Economic (<=50) | $14/7/3/2 per board vs Standard at 5/10/30/50 | fee table |
| 5 | 6L -> 4L | about $3.4/bd @10, $2.4 @50 (PCB est only); assembly unchanged; also drops mandatory ENIG | A10, UNVERIFIED |
| 6 | JLC fits motherboard THT vs seller | +$3.1/bd +$3.58/order for 190 joints; cheaper than ~10 min seller labor; blocked for TE header (no LCSC) | price page |
| 7 | Move motherboard SMD to hand/delete | saves 4-5 x $3.07 = $12-15 per design per order (+ ~$0.1/bd joints); not worth hand labor at q>=10 | fee table |
| 8 | Panelising | no effect on fees (setup per design, SMT per joint); Standard $0.48/bd surcharge is irrelevant since assembly is >$0.5/bd; motherboards cannot be paneled (250x250 limit); DB 2-up 250x76 only at the limit | capabilities + price page |
| 9 | Shrink under 100x100 | not feasible for either board | A10 |
| 10 | JLC fits J1/J2 headers | +$1.67/bd @10 (+$0.41 parts) and bent-header risk | model |
Single-extended-line candidates: LEDs KT-0603G/B/Y (3 lines, red KT-0603R is Basic), three BAT54 variants (C19726, C124205, C916423), three 1206 resistors, ES1D/B360A/FXL/MWSA are all separate lines; every merge of two lines saves $3.07/order. (Part-choice itself belongs to the alt-part audits.)

## Implications for this project
1. Fix the "~430 parts" figure: the JLC BOM/CPL has 330 placements (cur_db) / 302 (ord_db) and 1042/976 SMD pads (VERIFIED, evidence/*/fab_*cpl.csv, pcb_pads.csv). Any cost estimate based on 430 overstates SMT by ~30%; no consequence for fees except $0.0016 per joint. Confidence high.
2. The order is fee-dominated at small q: fixed assembly cost is $123 per DB order and $22-25 per MB design, i.e. about 19% of the $661 daughterboard order at q=10; the first build of 5 sets costs about $92 per set goods value before shipping/duty; tariff (~$25-32) plus shipping ($5-7) is a visible 8% chunk. Confidence medium (PCB estimates unverified).
3. Staying at <=50 boards per order keeps Economic (saves $2-14/bd); a 100-board order must go to Standard and add edge rails/fiducials (unknown fee) - order two 50s if the price in the quote is lower (test in the quote tool). Confidence medium.
4. Tariff budget 35% (JLC prepaid, verified) is the planning number; keep a CPT/company route (EIN) as an alternative and avoid declaring value changes. Buy MAP sensor, sockets, headers locally to dodge duty. Confidence medium; HTS classification (8537.10.9170 vs 8543.70) and Section 232 auto-parts status need a customs broker/CBP ruling.
5. JLC stock for single-source ICs: STM32F407VGT6 126, TCAN1042VDRQ1 257, TLS115B0EJ 556 pcs: a 100-board run is blocked or needs global sourcing/pre-order; the motherboards' 1x40 socket (65) and MAP (155) are limits for JLC THT fitting. Confidence high (live manifest, 2026-11-15).
6. Combine Shipping can merge the DB order and four MB orders into one parcel (VERIFIED feature), saving per-parcel express minimums. Confidence medium.
7. Economic reflow is a fixed 255 C profile (VERIFIED); check heat-sensitive parts (microSD socket, LEDs, electrolytics) against 255 C peak before Economic orders; Standard is 240 C. Confidence medium.

## Sources actually read (all fetched 2026-11-16; saved in kb/research/files/R21-jlcpcb-cost-model/*.txt/.html)
- https://jlcpcb.com/help/article/pcb-assembly-price (2026-10-22); https://jlcpcb.com/help/article/pcb-assembly-faqs (2026-09-09, partly stale); https://jlcpcb.com/capabilities/pcb-assembly-capabilities; https://jlcpcb.com/capabilities/pcb-capabilities; https://jlcpcb.com/6-layer-pcb; https://jlcpcb.com/resources/multiple-layer-pcb; https://jlcpcb.com/blog/reduce-pcb-assembly-cost-prototype; https://jlcpcb.com/blog/pcba-cost-breakdown (images only); https://jlcpcb.com/help/article/us-tariff-policy-faq (+Tariff-us.png); https://jlcpcb.com/help/article/customs,-duties-and-taxes; https://jlcpcb.com/help/article/eu-customs-reform-faq; https://jlcpcb.com/help/article/how-much-does-shipping-cost; https://jlcpcb.com/help/article/combine-shipping-service.
- Secondary: gingercontrol.com/blog/importing-from-china-tariff-guide, tarifftracker.ai/guides/china-electronics-tariffs, web searches (Section 122 expiry, 301 exclusions to Jan 2027 via GHY/KPMG snippets, EU/UK duty aggregators).
- Local: kb/parts_manifest.json, evidence/*/fab_*cpl.csv, pcb_pads.csv, work/R21-jlcpcb-cost-model/{parts.py,model.py}.

## Not checked
- Real JLCPCB PCB quote (no account); 100x100 step, finish upcharges, size band prices, edge-rail fee on Standard, real shipping quote, actual attrition/MOQ, whether DDP 35% applies to components, HTS classification, Section 232 auto-parts coverage for ECU codes, Federal Register text of 91 FR 47318, EU/UK official tariff pages, JLC sea shipping, whether the 6L board needs impedance/stackup surcharge.
