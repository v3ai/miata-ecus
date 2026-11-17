# R12 How owners really install and tune standalone ECUs on Miatas (community evidence)

Date 2026-11-16. Method: web search (summaries = leads only) then curl of the actual threads into
work/R12-how-owners-tune-miatas/*.html and reading the text. Tags per review brief section 5. A "single forum post" is UNVERIFIED
as a general fact but VERIFIED as "this person said this". Coverage is narrower than intended (see Not checked).

## Summary
1. Dominant MSPNP failure families in threads read: charging (1999-2000), idle/start tuning (all years), wideband wiring/ground, tach (89-95), smog/CEL, immobilizer (2001-05).
2. 99-00 alternator: the stock ECU regulates the alternator; MSPNP2 does it in hardware; overcharge to 16 V+ traced by the vendor's engineer to ground offset between alternator body and battery; fix = ground strap.
3. 2001-05: vendor documents that the MSPNP does not do the immobilizer and the dash light flashes; the Pro has a jumper to allow/ignore the OE immobilizer.
4. Tuning: community quotes for a remote tune are USD 300-400 (typical), 400-1000 (range), 600 first session at 200/h; "start and idle" tune ~400. Many say self-tune with wideband + autotune is enough for a basic tune.
5. Speeduino Miata: community says "mostly user error"; criticism is base-firmware features (idle) and NA-only base map; wrong trigger/base map selection is the commonest no-start.
6. Wideband: erratic readings fixed by moving the signal ground to the ECU sensor-ground pin; sensor/exhaust leaks give false lean.
7. Vendor: repairs reported slow (6 months, one poster) but warranty handled; diagnostics ~USD 50 (one poster, 2023).
8. First-run complaints: no start / needs throttle on 94-95, died after ~10 s on 91 (WUE/VE/injector size wrong).
9. Ten requirements and warning list at the end.

## 1. Why people buy (VERIFIED as statements by posters)
- Turbo/boost, injector upgrade, AFM removal (AMP install guide: AFM not needed, unplug or remove; vacuum line to firewall):
  https://ampenginemanagement.com/blogs/mspnp-pro-documentation/pro-mm0105-installation
- Turbo owner with 2003 car, MS3Pro, 2560 turbo, 640 cc injectors, wants 275 whp: https://www.miataturbo.net/ecus-tuning-54/remote-tuner-recommendation-108939/ (Jan 2024)
- Rule of thumb in forum: put engine management in before the turbo to learn tuning (search summary of miata.net threads; UNVERIFIED, not read in full).
- N/A gain is small: summary of a 2010 test, +7 whp peak with MSPNP (UNVERIFIED, thread not read) https://forum.miata.net/vb/showthread.php?t=399512
- Track/race use is the vendor marketing line (AMP NA/NB pages: "road racing and drifting").
- Hardware prices (listing search results, not read as pages; UNVERIFIED for today): AMP MSPNP Gen2 99-00 USD 829.99; MSPNP-Pro 99-00 USD 1149.99; Link G4X plug-in about USD 1255-1595; UK Link plug-in GBP 975 ex VAT to 1374; EMU Classic NB1 adapter USD 175 plus the ECU (links in search output: diyautotune.com/product/mspnppro-mm9900, xtramotorsport.com/product/linkecu-plugin-for-mazda-mx5, ecumasterusa.com/products/1999-2000-mazda-miata-nb1-pnp-for-emu-classic). Original MSPNP-Pro price USD 1199 and Gen2 USD 799 (2012) per forum summaries.

## 2. Tuning routes and prices
| Route | Evidence | Tag |
|---|---|---|
| Self tune with wideband + autotune | miataturbo e-tune thread 2014: "set AFR targets and let it autotune"; poster said autotune ran badly and needs someone else to drive. https://www.miataturbo.net/megasquirt-18/does-anyone-offer-e-tune-service-mspnp-2nd-gens-80267/ | VERIFIED (posts) |
| Remote tune | "typically 400 to 1000 ... I want 400 to make it start and idle normal" (search-summary quote of https://www.miataturbo.net/wtb-7/remote-tuning-96811/, not re-read); 2024 thread: "some tuners charge about 300, some quoted over 1k", a popular tuner "300-400" https://www.miataturbo.net/ecus-tuning-54/remote-tuner-recommendation-108939/ | VERIFIED for 2024 thread, UNVERIFIED for the 400-1000 |
| Dyno tune | Link UK retailers say professional dyno tuning is required (xtramotorsport page, search summary); generic ranges USD 500-1500 from a pricing site (not Miata-specific, ignore). | UNVERIFIED |
| Base-map workflow | Vendor sends base map per year (e.g. MM9495_Miata_331a); owners then adjust. https://www.miataturbo.net/mspnp-55/9495-mspnp2-start-up-issues-81863/ | VERIFIED |
Note: ND/NC remote tunes at USD 349 (corksport) are a different platform and show the price anchor owners will compare against.

## 3. Recurring problems by model year
| Topic | Evidence |
|---|---|
| 99-00 alternator overcharge | https://www.miataturbo.net/megasquirt-18/id1050x-battery-voltage-correction-factor-alternator-overcharging-99-00-mspnp2-107805/ (2023) and https://www.miataturbo.net/mspnp-55/99-mspnp2-blown-up-battery-voltage-regulation-issues-103610/ (2020): battery 16 V+, boiling battery, lean stall because "battery voltage correction" subtracts pulse width above 13.2 V (0.2 ms/V base map). Vendor engineer quote: ground offset between alternator body and battery negative latches the field on; fix = ground strap alternator body to chassis. VERIFIED (posts, vendor engineer relayed second-hand). |
| NB1 not charging after fit | https://www.miataturbo.net/mspnp-55/ms2pnp-nb1-alternator-control-not-working-what-have-i-done-wrong-84350/ : alternator circuit is hardware on the adapter board, independent of software; vendor: tach output must be enabled or alternator output shuts down; asked for MSQ + log by e-mail. VERIFIED. |
| 94-95 start | Needed throttle to start, settles ~1 k rpm; fix: set base timing with fixed advance + trigger wizard, load vendor base map, set base idle manually. TPS must register. https://www.miataturbo.net/mspnp-55/9495-mspnp2-start-up-issues-81863/ VERIFIED |
| 91 NA idle | Idles 8-10 s then AFR 13-14 -> 21 and dies: warm-up enrichment table and wrong injector cc (600 vs 640) and low idle VE; helpers say raise idle VE a lot. https://www.miataturbo.net/megasquirt-18/mspnp2-91-miata-wont-idle-goes-lean-regardless-103709/ VERIFIED. Hired "real tuner" failed too. |
| A/C idle-up | Many threads of stall with A/C; fixes: idle-up delay/duty, min-rpm threshold, PID delay; "MS1/MSPNP lacks true A/C idle-up" (search summary). https://www.miataturbo.net/megasquirt-18/great-c-faq-20954/ (not read) UNVERIFIED detail, VERIFIED that the threads exist (about 8 found). |
| Tach 89-95 | Gen1 90-93 MSPNP has no built-in tach output (search summary of vendor page, UNVERIFIED); 90-93 with R8 coils: jumper at 4I in case, 1 k resistor B+ to IGN- in diagnostic box https://www.miataturbo.net/megasquirt-18/how-getting-tach-work-90-93-ms3pro-r8-coils-107309/ VERIFIED (single post). 95: tach dead after install; asker had alarm remote-start tach tap on 2I; staff asked "wire on 1F or 2I?" https://www.miataturbo.net/megasquirt-18/mspnp-installed-what-happened-my-tach-18670/ VERIFIED. |
| Immobilizer 01-05 | AMP: "MSPNP does not include functionality for the OE immobilizer; dash indicator will illuminate and/or flash" (VERIFIED, installation page). Forum: "2001-2005 MSPNP Pro has a jumper to allow or ignore the OE immobilizer" and another tuner (Reverant) already emulates it. https://www.miataturbo.net/ecus-tuning-54/immobilizer-system-method-operation-alternative-non-janky-theft-deterrent-107244/ VERIFIED (posts). Stock immobilizer failures on 01-03 cars exist independently (search summary, UNVERIFIED). |
| Fans/CLT | Base map hysteresis typo (200 vs 10 deg) kept fan on; poster blamed base map 99-00. https://www.miataturbo.net/megasquirt-18/ms2pnp-repair-109226/ VERIFIED single post. |
| Cruise control, automatics | No community thread read; UNVERIFIED gap. AMP/DIY pages sell manual-transmission units for 2001-05 (diyautotune product page title "manual trans"). |
| Speeduino NB 1.6 no start | wrong trigger pattern/base map; "no base tune for 99 NB6", fuel pump hum. https://www.miataturbo.net/speeduino-128/diy-efi-99-1-6-nb-no-start-110352/ (2025) VERIFIED |
| Speeduino NA | IAC needs flyback diode and 386 Hz; fuse left in by previous owner killed fuel pump driver; "hundreds out there, issues mostly user error" https://speeduino.com/forum/viewtopic.php?t=4583 (2021) VERIFIED. |
| rusEFI 91 Miata Hellen | USB/DFU trouble after cold-start tuning, ECU lived in OEM box with USB cutout; reflash needed. https://rusefi.com/forum/viewtopic.php?p=42004 VERIFIED |
| rusEFI NB alternator | firmware upgrade stopped alternator charging; "simple on/off mode more successful" (search summary of https://rusefi.com/forum/viewtopic.php?t=1282, not read) UNVERIFIED |

## 4. Installation mistakes
- Wideband signal ground not at ECU sensor ground: erratic readings; fixed by ground to pin 22 + signal pin 21 (95). https://www.miataturbo.net/mspnp-55/99-mspnp2-wideband-install-82322/ VERIFIED. Wideband tapped to stock O2 wire path with factory sensor disconnected (95 post).
- False lean from exhaust leak near sensor (91 thread). Sensor position claims from summaries UNVERIFIED.
- MAP: vacuum line from intake manifold nipple through firewall, not kinked (AMP page, VERIFIED); forum summary warns against throttle-body nipples (UNVERIFIED).
- IAT after AFM removal: forum summary says post-intercooler / pre-throttle, open-element for speed, away from radiator exhaust (UNVERIFIED; threads listed in search results iat-sensor-location-30372 etc.).
- Opening the case: needed for J12 (5 V on serial pin 9), MAP selection jumper J8 and 4I jumper (AMP page; tach thread). VERIFIED.
- Grounding: alternator ground strap (above); battery-to-block strap.
- Setup basics: injector cc mis-entered; trigger angle/base timing never checked with a timing light (AMP page demands timing light check).

## 5. Vendors: praise and resentment
- Praise: staff answer in thread and by e-mail, repair under warranty (search summary of 2 threads, not read).
- Resent: repair took "over 6 months" (poster), slow shipping, "unresponsive" (one poster); repair diag about USD 50 (one poster 2023). Source: search summary of https://www.miataturbo.net/mspnp-55/ms2pnp-repair-... and 18psi thread; only repair thread read. UNVERIFIED for the 6 months.
- Documentation: AMP install page is good but says nothing on alternator ground; base maps contain typos (fan hysteresis) and users do not know where to look.
- Speeduino: "SpeedyEFI is not Speeduino; UA4C is the supported board" (search summary UNVERIFIED); idle features weak (summary).

## 6. Accessories owners buy (inferred from threads read)
Wideband (AEM X-series, PLX, Innovative MTX-L, LC-1), open-element IAT, bigger injectors (flowforce 550/640 cc), coil kits (R8, COP/MaxSpark), bluetooth serial adapter (5 V on DB9 pin 9), tach adapter, alternator ground strap, MAP/boost control. Counts not measured.

## 7. Ten things a new low-cost Miata ECU must get right (INFERRED from the evidence above)
1. Starts and idles on first key turn with a per-year, per-engine (incl. NB 1.6 and NB 1.8) base map; the top thread type is first-start trouble.
2. Alternator control right on 1999-2000 and 2001-05 (ground-offset latching, 14.5 V target, safe default when unconfigured, documented ground strap).
3. Tach works on every year including 90-93 and 94-95 pins; no pass-through of alarm taps surprising users.
4. Wideband: signal ground tied to ECU sensor ground; document placement and no-leak rule; autotune ready.
5. Immobilizer: documented behaviour and a switch/jumper for 2001-05; say how to keep or lose it.
6. A/C idle-up input and idle-up tuned in base map; cold start (WUE) base values sane.
7. CEL lamp behaviour defined (lights at key-on).
8. MAP hose and IAT kit included (AFM-delete accessories), with instructions.
9. Documentation by year with pin table, jumper table, first-start checklist (timing light, trigger angle, injector cc).
10. Responsive support, USB reliability (DFU/USB-C), repair path and fixed lead times.
Mistakes that get a product warned against: base-map typos, hard-to-enter bootloader, silent alternator overcharge, shipping without tune/year support, no repair policy, claiming "plug and play" where tach/immobilizer/CEL need workarounds.

## Implications for this project
- Alternator: ground strap instruction and over-voltage cutoff in firmware default (high-confidence, 3 sources: two MT threads + vendor engineer quote). Changes docs + firmware default.
- Tach 1989-95 pin ambiguity (1F vs 2I) is a real field issue: confirm and document (already an open item in review brief). Confidence medium.
- Immobilizer on 2001-05: competitor documents flashing light, one competitor emulates it; ship a documented jumper/notice. Confidence medium.
- Base maps per year/engine incl. NB 1.6 are the major UX lever; sanity-review base-map hysteresis, WUE, injector size.
- Packaging: users open the case for jumpers; USB access through case cut-out is accepted practice (rusEFI forum).

## Sources actually read (curl, files in work/R12-how-owners-tune-miatas/)
miataturbo threads: 84350, 107805, 103610, 81863, 103709, 82322, 18670, 107309, 58536 (partly), 108939, 80267, 110352, 107244, 109226; ampenginemanagement MM0105 install page; rusefi.com forum p=42004; speeduino.com/forum t=4583.

## Not checked
Reddit (domain blocked for the search tool), YouTube series, UK/Australian forums (only UK shop price listings from search results), Link/ECUMaster forum threads, cruise control, automatics, counts of reports, E85 motive, supercharger kits, vendor wait times today, exact tach-driver fact for Gen1, any Speeduino/rusEFI report on immobilizer. 403 on forum.miata.net and grassrootsmotorsports via curl.
