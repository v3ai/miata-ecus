# R04 - MegaSquirt family and the MSPNP Miata plug-in ECUs (DIYAutoTune / AMP EFI)

Status: finished 2026-11-16. Files under `kb/research/files/R04/` (manuals_txt/, pinouts_img/, products_json/, docs/). Scratch: `work/R04-megasquirt-mspnp/` (dl/ = original HTML, txt/, img/, site/ = Shopify product JSON, web/ = forum/policy pages).

## Summary
1. Vendor today: AMP Engine Management (part of EFI Innovations; same shop as DIYAutoTune, which still sells the Toyota/Subaru MSPNP2 and Pro). The Miata MSPNP2 and MSPNP-Pro are no longer on the sitemap; the Miata line is now the "AMP PNP" (MS3Pro based, internal Bosch LSU 4.9 wideband optional). VERIFIED (site/sitemap_products.xml, product JSON).
2. AMP PNP Miata prices (2026-11-16, USD, 1 unit): $1,349.99 with internal wideband, $1,199.99 without, for all five Miata years; MaxSpark ignition kit $674.99 extra. VERIFIED (product JSON `price` in cents).
3. Old MSPNP2 NB1 list prices: $899.99 (DIYAutoTune/Vivid), $849.99 (AMP/SP Tuning), $829.99 (Summit); refurbished MSPNP2 NB1 $639.99, 90-day warranty, final sale, out of stock. Search-result snippets plus the refurbished page (VERIFIED for $639.99 only).
4. Every Miata variant is manual-transmission only; the 2004-05 Mazdaspeed has a separate unit; the 1.6 NA with B6ZE is not compatible with the 94-97 units. VERIFIED (product pages).
5. Install model: the MSPNP is its own case (two PCBs) with the stock harness connectors plugged into it. The stock ECU case is NOT reused. Mounted with zip ties (NB), self-tapping screws to the firewall (NA), no stock parts discarded. A separate "rear options" connector with pre-crimped pigtails carries wideband, spark outputs for COP, extra I/O. MAP: internal 4 bar sensor, vacuum hose through a firewall plug (NA) or grommet (NB). VERIFIED (manuals).
6. Surprises documented by the vendor itself: no immobiliser function (dash lamp flashes/lights, 2001-05), cruise-control vacuum line must be cut and teed, base timing MUST be checked with a timing light, MAF removal needs a GM IAT sensor spliced into the MAF connector, no variable TPS on 1990-93 (optional add-on), automatics not offered, check-engine lamp not driven (2009 vendor statement; the 2026 pinout lists "CEL (via DFIN1)", meaning unknown).
7. Support model: online installation pages per model/PCB version, TunerStudio, base tunes + firmware page, US phone/e-mail support ("real in-house tech support (20 years)", marketing claim), 45-day return only if sealed, opened electronics NOT returnable, 7% restocking fee for sealed ones.
8. The MS3Pro hardware manual (v1.102, 2016) gives circuit practice: 22 V input clamp that blows fuse F1 (so a 24 V jump start would blow it), injector outputs 5 A with thermal shutdown (high impedance only), 36 V clamp on high-current outputs, logic-level 5 V ignition outputs max 200 mA, replaceable fuses, -30..+80 C.
9. Not done: V3.0/V3.57 schematic PDFs and MS3X schematics were not obtained (msextra and DIYAutoTune links 404/scribd only); the I/O tables below were read from the vendor's pinout images.

## 1. Product line and prices

| Item | Price | Source / tag |
|---|---|---|
| AMP PNP Miata (each of 1990-93, 1994-95, 1996-97, 1999-2000, 2001-05), internal wideband | $1,349.99 | VERIFIED `kb/research/files/R04/products_json/amp-pnp-mazda-miata-*.json`, `variants[].price` (134999), fetched 2026-11-16 |
| same, no wideband | $1,199.99 | VERIFIED same |
| AMP PNP Mazdaspeed 2004-05 | separate product | VERIFIED sitemap |
| MaxSpark IGN1A ignition kit (per year group) | $674.99 | VERIFIED maxspark-ignition-kit-miata.json |
| MSPNP2 (old gen 2) 99-00 NB1 | $899.99 Vivid / DIYAutoTune page; $849.99 AMP & SP Tuning; $829.99 Summit; one retailer $1,250 | UNVERIFIED (search snippets, 2026-11) |
| Refurbished MSPNP2 NB1 | $639.99, 90-day limited warranty, final sale, includes RS232 cable and vacuum hose, out of stock | VERIFIED https://diyautotune.com/products/refurbished-mspnp2-mm9900 (SKU B-MSPNP2-MM9900) |
| MSPNP2 Toyota 90-92 / 93-95 (still sold) | $899.99 | VERIFIED product JSON |
| MSPNP-Pro Subaru 02-05 | $1,149.99 | VERIFIED mspnppro-sw0205.json |
| Used market | no sold-price data found (eBay/classifieds not reachable); one new-in-box MSPNP2 94-95 classified existed on miataturbo, price not shown | UNVERIFIED |

Note: the live URL `.../products/mspnp2-mm9900` on both ampenginemanagement.com and diyautotune.com now shows the AMP PNP content ($1,199.99 / $1,349.99), so older price memories and retailer lists are stale. INFERRED: price rose about 33-50 percent vs MSPNP2 era while adding SD card, wideband, 48 pin options.

Box contents (AMP PNP): ECU, 6 ft vacuum hose + T fitting, rear options kit (26 pin connector A, 22 pin connector B, pigtails large and small), Bosch LSU 4.9 sensor and 6 ft cable (wideband variant), M8 serial tuning cable, TunerStudio registration code. VERIFIED (product JSON).
Product features quoted: 16x16 tables, 4 sequential injector channels, 8 GB SD logging, CAN, 4 bar MAP, "Average install time under 1 hour", base map preloaded.

## 2. What the plug-in does with each stock function

Sources: installation pages (copies in `files/R04/manuals_txt/`) and pinout images (`files/R04/pinouts_img/MM*-ECU-Connector*.png`, `MM*Aux*`, `*Cooling-Fan*`). All VERIFIED unless tagged. "J" = internal jumper; unit has "Connector 1..4" = stock harness side, "Connector 2" optional use.

| Function | 1990-93 (NA6 1.6) | 1994-95 | 1996-97 | 1999-2000 (NB1) | 2001-05 (NB2) |
|---|---|---|---|---|---|
| Idle valve | stock IAC driven by PWM1 (4W) | PWM1 (4W) | PWM1 (4Q) | PWM1 (4M) | AMP page: I/O image only (not read) |
| Fans | Fan 1 relay on PWM2 (1L). Thermoswitch on thermostat housing also works; MSPNP command only active if jumper J6 fitted (1.6L), either source ON wins. Default turn-on 195 F | PWM2 (1L), Output 1 CLT>190; condenser fan Output 2 off by default (J4 selects A/C fan or VICS output) | Fan 1 PWM2 (1A) + condenser fan on Injector I out (4K) | Fan 1 PWM2 (1R) default CLT>195 F; fan 2 + A/C on Injector J | Fan 1 PWM2; Fan 2 Injector I (CLT>200 F default, Basic Settings Fan Control); A/C relay Injector J |
| A/C | A/C relay out Injector J (1J), A/C switch in 1Q | A/C relay 1J, switch 1Q (J4 assigns Output 2) | A/C relay Injector J (1B,1G), A/C switch in DI3 (1K) | A/C relay Injector J (1I,1S), A/C request DI3 (1P) | A/C relay Injector J, request DI3 |
| Alternator control | not applicable | not applicable | alternator field PWM3 only in optional pinout (2I) for NB alternator swap | PWM3 drives alternator field (1O), sense on 1T, charge lamp pin 1Q; AMP page: "Supports OEM NB alternator" | same (AIN2 alternator voltage ref) |
| VVT | n/a | n/a (VVT output High Current 1 at option pin 3J for swaps) | HC1 (VVT) for swap | HC1 VVT on optional connector 2K (NB1 has no VVT cam; for swaps) | HC1 VVT; AMP: "full factory VVT control" |
| VICS (intake butterflies) | none on 1.6 | not controlled by MSPNP2 Miata jumper text ("VICS ... FWD cars only"), no VICS pin in pinout | no VICS pin in pinout | VICS solenoid on Injector I (4Q), default ON when RPM>5500 | not listed in pages read |
| VTCS (NB2 swirl) | not covered | not covered | not covered | not covered | no VTCS found in pages read (repo already documents) |
| Tach | tach out on pin 1F (stock) | tach on 1F / 4I; J6 jumper enables tach out on pin 4I "for 1995.5+ only" | 4L tach out | 3K tach out | rear options "Tach Out" and OEM tach |
| Check-engine lamp | "CEL (via DFIN1)" | "CEL (via DFIN1)" (1E) | CEL via DFIN1 (1E) | CEL via DFIN1 (1E) | CEL via DFIN1 in I/O list |
| Fuel pump | relay 1C | pin 4T | relay 1U | 4N USA / 4P Europe, jumper J2 (JP2) selects USA vs Europe with immobiliser | per page 2001-05 (not read in detail) |
| O2 | narrowband on 2B/4N; wideband via option pin | 4N | front 3C, rear 3D via J5 | front 3C (4J rear) via J3 O2 select | front/rear via J2 |
| Immobiliser cars | n/a | n/a | n/a | jumper only for fuel pump on Euro cars | "MSPNP does not include functionality for the OE immobilizer; the fault indicator on the dashboard will illuminate and/or flash" (all three 2001-05 pages) |
| Automatic transmission | not offered | not offered | not offered | not offered | not offered (all product titles say Manual Transmission) |
| Cruise control | n/a | vacuum line must be cut and teed with the supplied Y (text in 94-97 pages) | same | not mentioned | not mentioned |
| Clutch switch | DI2 | DI2 | DI2 | DI2 (J2 removable if user wires own) | DI1 (J6 removable) |
| Variable TPS | optional, needs aftermarket TPS wired in, jumper J4 | stock | stock | stock | stock |
| MAF / IAT | MAF (AFM) removable, GM IAT spliced into AFM connector pins 1 and 6 (MSPNP2/Pro) | same | MAF pins 3 and 4 (AMP) | MAF unplugged if unused | MAF must be unplugged if not removed |
| Knock | optional, rear connector | optional | optional | knock sensor on 3F | knock |

Caveats: the 2001-05 column is the thinnest (pinout images not all viewed). VICS/VTCS statements for 94-97 and 2001-05 are from absence in the pinout images read, tag INFERRED. The meaning of "CEL (via DFIN1)" is UNVERIFIED (probably the lamp ground pin is only monitored). 2009 vendor statement on forum: "The MSPNP does not control the Check Engine light." (Matt Cramer, DIYAutoTune, https://www.miataturbo.net/mspnp-55/mspnp-check-engine-light-ca-smog-checks-32709/, forum post by vendor, UNVERIFIED as current behaviour.)

Other facts per year (VERIFIED, manuals): 90-93 ECU is behind passenger seat (door trim, carpet, three 10 mm nuts); 94-97 passenger side foot well/door sill, ECU bracket three 10 mm nuts; 99-05 under driver's dash by steering column, 2 nuts; NB unit "fits well between the brake and clutch pedals", zip-tied to the lower OE bracket and the clutch pedal bracket.
Hose routing: NA through a plug behind washer reservoir (drill a hole in it); NB through large firewall grommet on driver corner.
Timing check is mandatory (fixed 10 deg, adjust trigger angle 0-20 deg in TunerStudio or rotate CAS with 12 mm wrench).
Wrong base map risk: "Using the wrong startup map may result in a no-start condition, or even engine damage" (MSPNP2 94-95 manual).
Jumpers inside (top cover, 4 screws each end plate): CKP/CAS vs OE crank VR select (J3/J4), MAP internal/external (J6/J8/J9), 5 V on serial pin 9 (J7/J12/J13), fuel pump USA/Europe, tach out 4I, clutch switch, O2 front/rear select, VICS/A-C fan select, variable TPS enable.

## 3. Wiring/connector and enclosure approach

- Own two-board case with stock-style harness connectors; stock ECU stays in the car box (kept). VERIFIED (AMP 96-97 "no factory parts will be discarded"; MSPNP2 94-95: connectors "reach around the bottom and push down on release tab").
- Install is by plugging the factory connectors into the new case: "no repinning". Rear options connector: 26 pin A + 22 pin B (AMP) with 6 inch pre-crimped wire pigtails. VERIFIED (pinout PNGs `AMP-PNP-MM9900_Rear_Options_Connector_{A,B}_Pinout.png`).
  Connector A (26): spark A-D, injector E-H, DI2 clutch, DI3, DI 12 V, IAT, DFIN1/2, analog 1-8 (EGO input = wideband), CAN H/L with 120 ohm onboard termination, 5 V ref internally fused 0.25 A, sensor ground. Connector B (22): 12 V out 0.25 A relay control only, flex fuel, IAC pins, tach out, high current out 1-3, PWM 2-5, six wideband wires (WB 1-6, colours listed).
- Wideband: internal module in the 48-pin variant, LSU 4.9 cable plugs into rear connector (wires WB1-6, colours brown/green/blue/red/white/black). In MSPNP2/Pro era the wideband was external and the controller output wired to a rear option pin (see blog "wiring a wideband controller").
- MAP: internal 4 bar MAP and one barb on the case; vacuum hose through the firewall; jumper to use external OEM MAP.
- Mounting and no-glue approach: NA via sheet metal screws into the rear firewall; NB via zip ties.
- Debug LEDs through holes in case side: 12 V, 5 V Vref, tach, fuel pump (MSPNP2 manuals). Serial M8-4 tuning cable keyed (MSPNP2) / M8 cable (AMP); USB not mentioned for Miata pages read.

## 4. Documentation and support model
- Per-model, per-PCB-version installation pages (MSPNP2 v1.3 and v2.0, Pro, AMP PNP each separate): 37 pages saved. Content quality: texts are good; AMP pages still contain placeholders "Insert Rear Option Connector pinout image/table here" and "Insert MAF connector and IAT wiring diagram here" in the live 2026 pages (VERIFIED in `amp-pnp-mm9697-installation.txt`, `amp-pnp-mm9093-installation.txt`), with the real data in images and a printable PDF. A pinout error erratum exists for v1.1 PCBs (jumper labels J2/J5 mislabelled, MSPNP-Pro 96-97 page).
- Base tunes and firmware on a public page; "restore original base tune" procedure.
- TunerStudio registration code included. Tuning software is third-party.
- Dealers and refurbishment: opened-electronics return not accepted; dealer diagnostic fee $75 (https://ampenginemanagement.com/policies/refund-policy, fetched 2026-11-16). Shipping policy (DIYAutoTune): same-day shipping before 12 pm EST, worldwide USPS, insurance $1.30 per $100, customs value must not be misrepresented.
- Forum presence: vendor staff answer on miataturbo/megasquirt forums (Matt Cramer "Supporting Vendor"). Typical post-sale problems seen: idle quality after first start (miataturbo thread 2019: car "can't hold idle" at ~500 rpm after changing injectors, base map not matched), tach dropouts at high throttle on a 1.6 and after COP swap (pull-up suspected), A/C compressor not engaging after install (jumper/setting mismatch; 2014 thread), flashing immobiliser lamp. UNVERIFIED (forum anecdotes, one thread each).

## 5. MS3Pro / MegaSquirt hardware practice (circuit notes)
Source: `kb/research/files/R04/docs/ms3pro_manual_1.4.1.pdf` (MS3-Pro manual v1.102, fw 1.4.1, 19 May 2016), text beside it. VERIFIED unless noted.
- Supply 6 V min; input limiting circuit clamps at 22 V; sustained 22 V blows replaceable fuse F1 and shuts the ECU; F2 fuses only the TPS reference. (manual lines 997, 1239-1244, 1338-1339)
- Operating range -30 to +80 C (-40 to +85 C without RTC battery); IP rated waterproof enclosure and AMPSEAL connectors, TXL wire.
- Injector outputs: saturated, 5 A per channel with thermal shutdown; low impedance requires external peak and hold box. High-current outputs: 5 A same FET type, flyback clamped to 36 V. Ignition outputs: 5 V logic, high-side, max 200 mA, must not drive coil directly. Lessons: the vendor itself uses protected smart FET drivers and warns not to feed coils directly.
- Tach output 12 V; stepper H bridge; 2 knock inputs; internal temperature sensor logged.
- V3.57: "mostly SMD V3.0" with removable JP1/J1 jumpers selecting optoisolated vs VR input, pad R57 for 5 V pull-up, PWM idle can be driven directly (article https://diyautotune.com/blogs/technical-articles/inside-the-v3-57-board).
- A 2017 AMP service bulletin for MS3Pro Ultimate units (shipped before 28 Apr 2017) concerns "transient surges on incoming 12 V supply in some installations" (search snippet only, bulletin PDF not retrievable: UNVERIFIED). Suggests an early field failure of supply protection.
- V3.0/V3.57 schematic: not read (see Not checked).

## 6. Implications for this project (goals: errors, free removals, cheaper parts, UX, cost, packaging/shipping)
1. UX / feature completeness: Competitor's documented stock-function coverage is the benchmark; a table like section 2 should be in the product page and manual so buyers do not discover gaps after install (immobiliser lamp, CEL, cruise, automatics, VICS/VTCS, no TPS on 90-93). Change: documentation. Evidence: vendor manuals; confidence high.
2. Immobiliser lamp on 2001-05: the incumbent leaves the dash lamp lit/flashing; if this project already documents "no immobiliser" it matches; consider providing the lamp-terminating resistor/circuit as a free firmware/hardware fix. Confidence medium.
3. Stock-case approach is a differentiator: MSPNP is a separate box zip-tied/screwed in the car (extra drilling, firewall screws, relocated ECU) while this project reuses the stock case and mounting. Market it as "reuses stock mounting, no drilling". Counterpoint: stock case sealing/EMC and connector availability is this project's burden (R24). Confidence high.
4. Mandatory timing verification and base-map warnings must be first-class in install docs (incumbent makes it step 1 of software; wrong map can damage engine). Firmware should ship with a fixed-timing mode that is quick to engage. Confidence high.
5. MAF removal needs GM IAT: if this board expects speed density, installation docs must include the MAF connector IAT splice or an IAT input on the board; incumbents document pins (1 and 6 on 1990-93 AFM; 3 and 4 on 96-97 AMP page). Confidence high.
6. Tach: tach dropouts and COP-swap tach noise are repeated forum themes; check the repo tach driver has pull-up and works up to full throttle/high load. Confidence low (anecdotes).
7. Supply protection: MS3Pro clamps at 22 V (blows fuse on sustained 22 V); a 24 V jump start would kill an MS3Pro; this project's higher-rated TVS/PTC is documented elsewhere, but the 22 V/fuse-blow behaviour is evidence of what happens commercially. Info.
8. A/C and fans: incumbents default fan turn-on 190-200 F; A/C needs jumper/software match; copy default fan thresholds and ship A/C enabled in base tune. Confidence medium.
9. Wideband: incumbent moved from external to internal LSU 4.9 module with a 6-wire cable on the options connector; confirms this project's integrated wideband direction. Info.
10. Documentation placeholders in the live AMP pages show that even a mature vendor ships incomplete docs; keep pinout PDFs complete and printable. Info.

## Sources actually read
- Local copies in `work/R04-megasquirt-mspnp/txt/*.txt` (AMP PNP, MSPNP2 v1.3/v2.0, MSPNP-Pro installation pages for 9093, 9495, 9697, 9900, 0105, MSM0405) from https://ampenginemanagement.com/blogs/amp-pnp-documentation/..., downloaded 2026-11-15. Read in detail: mspnp2-mm9495-v2, amp-pnp-mm9697, amp-pnp-mm0105, amp-pnp-mm9900, amp-pnp-mm9093, pro-mm9900/0105/9697/9093 (jumpers, fan, immobiliser sections), grep over the rest.
- Pinout / table images viewed: MM9900-Aux-Functions-V2, MM0105-Aux-Functions, MM9900-VICS, MM9900/MM0105 cooling fan, MM9697-Aux, MM9495-Aux, MM9093-Aux-Function-V2, ECU connector pinouts for 9093, 9495, 9697, 9900, AMP 9900 rear connector A and B, AMP 9900 jumper image.
- Product JSON (prices, variants, descriptions): `work/R04-megasquirt-mspnp/site/products/*.json`.
- https://ampenginemanagement.com/pages/plug-and-play-ecu-mazda-miata-na and -nb, company-profile, policies/refund-policy, policies/shipping-policy (diyautotune), refurbished MSPNP2 product page.
- MS3-Pro manual 1.4.1 (`docs/ms3pro_manual_1.4.1.pdf`), Inside the V3.57 Board article.
- Forum threads (anecdotes): miataturbo tach 1.6 (2015), first MSPNP2 setup (2019), CEL thread (2009), no A/C after MSPNP2 (2014), MSM immobiliser (2015).

## Not checked
- V3.0 / V3.57 / MS3X schematics (no direct PDF retrievable; msextra link 404). Injector flyback and ignition drivers of those boards not read.
- Used (sold) prices: no eBay/classified data reachable; only new/refurbished list prices.
- 2001-05 and 1996-97 pinout images only partly viewed; Mazdaspeed unit not examined; AMP PNP CEL semantics, VTCS, cruise on NB not confirmed.
- MS3Pro Ultimate TSB (2017 surges) not retrieved; no teardown photos of MSPNP internals.
- Idle-valve type per year not independently verified beyond "IAC (PWM1)" labels.
