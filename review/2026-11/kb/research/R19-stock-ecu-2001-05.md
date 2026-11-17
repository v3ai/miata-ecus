# R19 - The stock 2001-05 Miata (NB2) engine computer: 2001-02 vs 2003-05, immobiliser, reflash

Status: DONE with gaps (2026-11-16). Scratch: work/R19-stock-ecu-2001-05/ ; files: kb/research/files/R19/ (index there).
Pin tables and cavity naming already exist in repo/research/pinouts_9605.md (built from the 2005 FSM, mellens.net); I did not redo them, I checked the 2002 and 2003 manual voltage tables against them.

## Summary
1. Year differences (VERIFIED, 2002 vs 2003 CHARM manual images): 2001-02 main relay is switched by the ignition switch, PCM terminal 3H is unused and 4S is unused; 2003+ the PCM drives the main relay via 3H (B+ key off, <1 V key on) and 4S is the IG1 key-sense input. 2001-02 has 3E CDCV (canister drain cut valve) output and 4AB FTP (fuel tank pressure) sensor; the 2003 table shows 3E unused.
2. Immobiliser (VERIFIED, 2002 manual): serial link PCM terminal 3S <-> immobiliser unit; PCM and immobiliser unit are paired to each other and to the keys; "cannot be deactivated" (Mazda). Failure mode in the manual: engine starts once and stalls soon, no start after the 3rd crank. Security light (cluster) is driven by the immobiliser unit (unit connector terminal M), not by the PCM.
3. With a standalone ECU: forum/vendor evidence says the engine runs, the security light flashes or lights (MegaSquirt PnP docs say so explicitly; Haltech says its plug'n'play does not support the immobiliser; owners pull the bulb). No source found of an NB2 fuel cut after seconds caused by the stock immobiliser unit when the PCM is gone (the stock PCM is what enforces it; the unit only talks to the PCM). INFERRED, not tested.
4. Reflash (stock ECU) cost: $275-$800 per forum posts 2012-2016, all dated; UNVERIFIED current prices.
5. Cruise control is a separate module with servo (CHARM tree), not in the PCM. Tach, VSS and MIL / generator lamp are PCM terminals (3O, 3T, 2R, 3U).
6. Gaps: maker/teardown/PCB/case dimensions/part-number table by year not found in primary sources; 2004-05 voltage table not downloaded (the 2005 FSM table is already behind repo pinouts file).

## Terminal differences 2002 vs 2003 (VERIFIED, images in files/R19)
| Term | 2002 manual | 2003 manual | 2005 FSM (repo pinouts file) |
|---|---|---|---|
| 3E | CDCV control: B+ key on, <1 V when diagnosis exceeded | not used | not used (Hellen: CDCV) |
| 3H | not used | main relay control, B+ key off / <1 V key on | same |
| 4S | not used | IG1 ignition switch: <1 V off, B+ on | same |
| 4AB | FTP sensor, about 2.5 V at 0 kPa | (page 6 not viewed) | not used in 2005 table |
| 4V / 4Y (TP) | TP on 4V: 0.1-1.1 V closed, 3.0-4.6 V WOT | **TP listed on 4Y, 4V "-"** | TP on 4V |
| 4M knock | (page 4 not viewed) | approx 2.4 V ign on (digital meter) | 4M |
Conflict: the 2003 manual page lists TP at 4Y, whereas the 2002 manual, 2005 FSM and rusEFI wiki (2003-alt: 4V TPS) all say 4V. I trust 4V (3 sources) and suspect a manual typo; not resolved, would need continuity on a 2003 car or the 2003 wiring diagram.
Other entries seen in 2002 (same in 2003): 2K A/C relay <1 V when A/C+fan on, else B+; 2M fuel pump: B+ key on, <1 V cranking/idle (low-side); 2N VTCS solenoid B+ when ECT>60 C idling, <1 V when ECT<60 C at 3500 rpm; 2R MIL <1 V key on, B+ idle (MIL off); 3J front HO2S heater <1 V key on and idle; 3P rear HO2S heater B+ key on, <1 V heater operating; 3U generator warning lamp <1 V key on, B+ idle with no DTC P0111/P0112/P1631/P1633/P1634; 3M generator field coil: waveform, voltage raises with load; 4N IAT 2.3-2.4 V at 20 C, 1.9 V at 30 C; 4P ECT about 3.0 V at 20 C, 0.9 V at 80 C; 4T generator P: <1 V key on, 3-8 V idle no load; 4X MAF 0.9-2.0 V key on, 1.7-2.4 V warm idle; 4R OCV negative: waveform only; 3Q K-line to DLC KLN (DLC-2); 3S immobiliser serial; 3T VSS waveform at 50 km/h (1 V/div, 10 ms/div); 4Z PCM-to-TCM serial (AT), DTC P1601.
Scope test points in the manual (2002): injectors 2A/2D/2G/2J vs 3A; IAC 2P (+) at 25 ms/div; purge 3C vs 4A (conditions ECT>80 C, D range, <7.5 km/h); IGT 3F/3I vs 4A; generator 3M vs 4A at 2.5 ms/div; tach 3O; VSS 3T; SGC 3V vs 4A. Waveform images and the OCV coil resistance value were not captured.

## Immobiliser details
- Years/markets: Mazda manual (US, 2002 CHARM) has an Immobilizer system with reprogram procedure; forum (miata.net, search summary, UNVERIFIED) says US cars 2001-2005; the PCM terminal 3S exists in the 2005 table (VERIFIED earlier by repo file) and 2002 table (VERIFIED here). A retailer listing (Redline, search snippet, UNVERIFIED) names a 2001-2002 ECU "BTT3-18-881" sold with immobiliser unit and key. UK MK2.5 (2001.5+) uses a TRW (ex-Lucas) immobiliser unit; MX5OC forum (VERIFIED read) says it is not possible to reprogram a used unit from another car, units are failing and not available new, an emulator exists/existed.
- Interaction (VERIFIED, 2002 manual Programming and Relearning / Service Precautions): keys with transponder; immobiliser unit + PCM both store key IDs and a code word; "The immobilizer unit and PCM cannot be changed from one car to another... engine will not start"; "The immobilizer system cannot be deactivated"; replacement needs >=1 valid key else both unit and PCM replaced; reprogramming is: ignition ON/LOCK five times within 1 s each, security light behaviour, key start cycles (30 s step limit); a dealer code word (8 digits per a forum guide, UNVERIFIED) is needed with fewer than two valid keys.
- Failure behaviour (VERIFIED, manual DTC page): engine starts once and soon stalls after turning the starter the first three times; cannot start afterwards. Reading DTCs: key START 2 s then ON, wait 2 min, read the security light. Light stuck on with engine OK: check short between security light and immobiliser unit connector terminal M.
- Standalone ECU: MegaSquirtPNP-Pro MM0105 (VERIFIED, AMP page read): "MSPNP does not include functionality for the OE immobilizer. Therefore, the fault indicator on the dashboard will illuminate and/or flash." Haltech (search snippet only, UNVERIFIED) says plug'n'play MX-5 harness does not support the factory immobiliser. MiataTurbo thread (VERIFIED read, 2015): MSM with standalone, immobiliser icon flashes intermittently; others pulled the bulb; one Adaptronic user saw no flashing on an SE; a CAN-enabled MS2 reported to control it (UNVERIFIED hearsay). No source found describing a standalone fuel cut after seconds; engine running with standalone is reported (hence no cut), but the mechanism is that the stock PCM is the enforcer (INFERRED).
- Mazdaspeed / other: not found separately.

## Functions (what is documented)
- Main relay: 2001-02 key-switched, ECU power 4AF, 4S unused; 2003-05 ECU holds the relay via 3H, 4S = IG1 sense (VERIFIED manuals above; rusEFI wiki 2002/2003 pages agree, VERIFIED read).
- OCV/VVT: 4D supply (+12 V from the PCM terminal, not a relay), 4R low-side; rusEFI wiki says flyback diode needed (user-written). Resistance value and PWM frequency NOT found.
- IAC: 2P +12 V supply from PCM, 2Q low side, flyback needed (rusEFI wiki).
- EGR: stepper (2E,2F,2H,2I) per repo pinouts (2005 FSM), boost sensor switching solenoid 3D (B+ always in 2002/2003 tables).
- Fans 2B/2C, A/C relay 2K, fuel pump 2M, HO2S heaters 3J (front, low side) 3P (rear), alternator field 3M, tach 3O (also DLC IG-TCM), VSS 3T, CKP 3Y, CMP 3V (Hall, per repo file).
- OBD-II: K-line serial on 3Q (DLC KLN), no CAN terminals in the 2002/2005 tables (VERIFIED absence, INFERRED conclusion that NB2 uses ISO 9141-type K-line).
- Cruise: separate module + servo + switches in the CHARM tree (VERIFIED tree list).
- ECU location: AMP MM0105 install page (VERIFIED read): under the driver's dash next to steering column, two bolts (one on top of case), three connectors, MSPNP fits between brake and clutch pedals.
- Connector: rusEFI OEM-connectors wiki (UNVERIFIED, user-written): 72 pin = 31+24+17; header TE 353830-5 or 1123038-2; plug sections 353031-1 (31), 353029-1 (24), 353027-1 (17) and 353028-1 (22) appear in a related 94-pin entry; Hellen NB2 README lists compatible case "89661-3T270" (which looks like a Toyota number; treat as unreliable).

## Known problems (forum, UNVERIFIED unless noted)
- Immobiliser unit failures; discontinued; replacement BJ3D675G2L and a Mazda recall/bulletin (forum guide). Mazda Service Alert 3505H cited by a parts site for crank-no-start 2001-02 (UNVERIFIED).
- CMP sensor dying (rusEFI Proteus wiki, user-written): misfires at hot, loss above 4-5k rpm; OEM crank 4-tooth plate swap to 36-1 Protege wheel with no cam.

## Reflash options (cost, all UNVERIFIED search summaries of old forum posts)
Bell Tuning $795 (quoted), Dynotronics about $550-600 (2012), TDR $275-495 (2016 post); posters say limited for heavy mods. Prices not re-checked at vendor sites today.

## Implications for this project
1. Immobiliser/security lamp: customers with the stock immobiliser unit will see flashing/lit security lamp after the swap (VERIFIED for MSPNP docs); repo INSTALL.md line 256 already says so. Docs/product: add the removable-bulb tip and warn that the immobiliser unit remains and must be left connected (pin 3S, 3Q etc. stay undriven, already "never drive"). Confidence medium-high.
2. Two 2001-05 variants: one motherboard serves both only if 3H (main relay) and 4S (IG1) are handled per year. 2001-02: do not drive 3H and do not rely on 4S; 2003-05: 3H must pull the relay low or the ECU loses power on key-off logic. Check repo mb 2001-05 nets for 3H/4S (not done here). Confidence high on facts, tied to firmware/docs.
3. 3E (2001-02 CDCV) and 4AB (FTP) exist only on early years; not driving them is fine, document.
4. TP terminal discrepancy (4Y in the 2003 manual vs 4V elsewhere): do not change the design; flag in docs for 2003 owners to verify. Low-medium.
5. Case outline: no primary dimensions found; still placeholder.

## Sources actually read
- charm.li 2002 and 2003 Miata manuals (pinout value images, OCV inspection page, oscilloscope page, immobiliser service precautions, reprogram procedure, DTC page, tree listing). 
- repo/research/pinouts_9605.md, ext/hellen-miata-NB2/*, wiki.rusefi.com pages: Mazda-Miata-2002, Mazda-Miata-2003-alt, HOWTO-Miata-NB2-on-Proteus, OEM-connectors.
- ampenginemanagement.com MSPNP-Pro MM0105 install page; forum.mx5oc.co.uk immobiliser emulator thread; miataturbo.net threads 84178 and 107833.
- web search summaries only (not verified): miata.net immobiliser threads, reflash price threads, eBay/Redline listings, Haltech.

## Not checked
Maker and board teardown; case/board dimensions; part numbers by year/transmission/market (only forum/seller hints: BP7F-18-881 (2003), BP7V-18-881 (2004 CA MT), BTT3-18-881 (2001-02 MT), BP4W-18-881A/B/C (1999-2000)); OCV resistance and drive frequency; EGR/purge control strategies; VTCS detail; 2004-05 voltage table; wire colours; TE plug part numbers verified at TE; Mazdaspeed differences beyond repo file; EU/Japan immobiliser markets; reflash vendor prices today.
