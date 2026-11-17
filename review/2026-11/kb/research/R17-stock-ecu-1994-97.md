# R17 - Stock 1994-97 Miata 1.8 engine computers (1994-95 "PCME" 48-pin, 1996-97 OBD-II "ECM" 64-site)

Tags: VERIFIED = read today (2026-11-16) in a primary source, cited; INFERRED = reasoning shown; UNVERIFIED = forum / seller / memory.
Primary source used for all pin tables: Mazda workshop manual pages as republished by Operation CHARM (charm.li) and Mitchell (Mitchell pages are 2005-era copies in `work/R17-stock-ecu-1994-97/dl/`). The CHARM pin tables are **images**; saved PNGs are in `kb/research/files/R17/` (names `charm_<year>_<page>.png`). I read each image by eye and transcribed it below (transcription error risk: low, but re-check against the PNG before a design decision).

## Summary (10 lines)
1. 1994-95 PCME connector = two blocks, 1A-1V (22) + 2A-2Z (26) = 48 pins (VERIFIED, CHARM terminal ID drawing 1994/1995). 1996-97 ECM = four sites: 1A-1V (22), an unused 12-position site "2" (empty in the OEM ECU), 3A-3P (16), 4A-4Z (26) = 64 used cavities (VERIFIED, CHARM 1996/1997 drawing; rusEFI wiki agrees).
2. The two connectors/pinouts are unrelated (rusEFI wiki: "pinout is drastically different from the early NA8"); 1996 and 1997 pin tables are the same except small items listed below (4Z rear-O2 heater only in 1997, a few voltage values).
3. 1994-95 **2I is an INPUT from the igniter/ignition control module** in the workshop manual of both years (column "Input" ticked, connection "Igniter" 1994 / "Ignition control module" 1995). The ordered 1994-95 motherboard rev 0.9 wires OUT_TACH straight to J1.2I (no jumper) = ECU output fighting the igniter. Current rev 0.12/0.13 has JP5 (open) - correct.
4. 1994-95 ignition = two igniters in the coil pack, #1,4 on 1G and #2,3 on 1H (wasted spark, 0.2 V idle low-side drive signal); 1996-97 = IGT1 on 4N, IGT2 on 4R. Crank/cam = SGT/SGC (2E/2G; 4F/4G) plus NE+/NE- (4H/4E) crank sensor only in 1996-97. No knock sensor anywhere on the 1.8 in these years (no pin in any table).
5. Injection: four separate injector pins in both (2U,2V,2Y,2Z / 4U-4X); sequential-capable wiring. Idle: single IAC valve duty output (2W / 4Q). Fuel pressure control solenoid ("PRC") 2R / 4J. Purge 2X / 4T. EGR vent+vacuum solenoids 1R,1T / 4O,4P and EGR function sensor 2J / EGR position 3J + EGR boost 3N and barometric 3H (1996-97).
6. Fan control: two relays: coolant fan 1L / 1A, condenser 2S / 1B. A/C relay 1J / 1G. Fuel pump relay 2T / 1U. MIL 1E (1994-95: shared with data-link FEN/buzzer) / 1E. 
7. OBD-II adds: front+rear heated O2 (3C,3D; heaters 3M, 4Z[1997]), MIL 1E, serial K-line to DLC-2 (ECM 1D "KLN"), test-mode pin 1I (TEN). Immobiliser: none in the manual's 1996-97 ECM table; only generic code list mentions it (UNVERIFIED for these years).
8. ECU is under the carpet behind the passenger seat in 1996-97 (Mitchell 1997 locations; AMP install guides give the same for 94-95 and 96-97: 3 nuts 10 mm, connector has a release tab). Mitchell 1994 says "under passenger-side footwell" - disagreement, trust AMP + Mitchell 1997.
9. Case dimensions of the 1996-97 ECU: NOT found. Best lead: rusEFI's Hellen64 NA8-96 board (KiCad, working "good to drive") has outline 154.2 x 159.2 mm, 6 mounting holes; same outline file as their NA6_94 board, so it is a generic template; the repo placeholder (154 x ~162) is close to it.
10. Part numbers: BPE8-18-881 (1994 MT), BPL9-18-881(A/B) (1995 MT), BPS1-18-881A/B (1996), BP3A-18-881A/B (1997) - all UNVERIFIED (seller/forum). 

## 1. Hardware identity, location, mounting
| Item | Fact | Source / tag |
|---|---|---|
| Maker | Mazda ECU; the 94-95 manual calls it PCME, 96-97 "ECM/PCM". Internal maker not established (Mazda ECUs of this era are Mitsubishi/Hitachi-type; not checked) | -- |
| 1994 MT | BPE8-18-881 (also seen "BPE8 188 811") | UNVERIFIED: redlineautoparts / partrequest search snippets, miata.net thread titles (pages blocked 403) |
| 1995 MT | BPL9-18-881, later BPL9-18-881A/B | UNVERIFIED same |
| 1996 | BPS1-18-881A/B (redline listing "bps118881b ... 1996 1997") | UNVERIFIED |
| 1997 (also listed 96-97) | BP3A-18-881 / A / B | UNVERIFIED |
| Auto trans | One thread lists BPE9-series for 94/95 autos; another says 1996 catalogue does not distinguish MT/AT. Hardware difference is pin 1K (94-95; ground = MT, open = AT) and 1O (1996-97: ground = MT, open = AT) | VERIFIED pin behaviour (CHARM tables); part numbers UNVERIFIED |
| Market | Manual covers US 1.8. No California/federal split found for 94-97 (only 1993 CA sequential vs pairs, forum). Non-US 1.6/1.8 NA8 harnesses not covered | UNVERIFIED |
| Interchange | 94 and early-95 PCMEs interchange; a late-95 ECU in a '94 gave "no IGf" code and no tach drive; coil type (4-wire early coils vs later) decides | UNVERIFIED (forum summary via search; thread pages blocked) |
| Location | 1997: "Behind passenger's seat" (Mitchell). 1994: "Under passenger-side footwell" (Mitchell). AMP MSPNP guides for BOTH 94-95 and 96-97: lift carpet behind passenger seat, three 10 mm nuts, "fold the ECU over forward (just enough room)", connector release tab pushed from underneath while prying from opposite side | VERIFIED (read): `dl/m1997_electrical_component_locations.txt:46`, `dl/m1994_..._locations.txt:79`, https://ampenginemanagement.com/blogs/mspnp-pro-documentation/pro-mm9697-installation and ...pro-mm9495-installation (saved in `dl/web/`) |
| DLC | 94-95: DLC (TEN/GND/MEN/FEN) on left rear of engine bay near master cylinder. 96-97: DLC-1 on left inner fender + DLC-2 (OBD-II 16-pin) under left side of dash near console | VERIFIED Mitchell locations |
| Case dimensions | Not found anywhere (see 6). rusEFI NA 48-pin wiki: one mounting screw needs a stack of 3 x M4 washers because the case has a recessed thread; stock ECU has a heat sink at that spot; "Hole J27" | VERIFIED https://wiki.rusefi.com/Legacy-Miata-NA-48-pin-board-for-MRE |

## 2. 1994-95 PCME pinout (48 pins) with wire colours and terminal voltages
Colour = CHARM "Terminal ID" drawing (1995 version, clearer; differences from 1994 drawing noted). Voltages = CHARM/Mitchell "Terminal voltage (reference data)". `*`=unused. B+ = battery.
| Pin | Colour | Function | Voltage / note (1994 | 1995 if different) |
|---|---|---|---|
| 1A | L/R | Battery backup (+B) | B+ constant |
| 1B | W/R | Main relay power | 0 V ign off, B+ on |
| 1C | V | Ignition switch START | ~10 V cranking |
| 1D | W/G | DLC MEN terminal (monitor lamp) | 4.5-5.5 V / B+ |
| 1E | Y/B | MIL / DLC FEN (code + buzzer) | <2.5 V lit, B+ off |
| 1F | * | unused | |
| 1G | BR/Y | Igniter #1,4 (in IG COIL) output | 0 V ign on, ~0.2 V idle |
| 1H | BR | Igniter #2,3 output | same |
| 1I | L/W | Transmission control module (output) | <1.0 V coolant <60 C (AT) |
| 1J | L/B | A/C relay | B+ ign on; <2.5 V A/C on |
| 1K | B/LG (1994 drawing: B) | MT/AT select | ground = MT (<1 V), open = AT (B+) |
| 1L | B/G | Coolant fan relay | <1.0 V when coolant >97 C at idle, else B+ |
| 1M | G/R | Vehicle speed | 2-5 V driving, 1 or 7 V stopped |
| 1N | R | Closed-throttle (idle) switch in TPS | 0 V released, B+ depressed |
| 1O | G/B | Brake (stoplight) switch | 0 / B+ |
| 1P | L/Y | Power steering pressure switch | B+ / 0 V when P/S loaded |
| 1Q | LG/B | A/C switch (1994 manual: "A/C sensor") | <2.5 V on / B+ off |
| 1R | Y (1994 drawing Y/B) | EGR solenoid vent | B+ idle |
| 1S | L/O | Blower/fan switch | ~0 V mid+ / ~12 V off,low |
| 1T | Y/R | EGR solenoid vacuum | B+ idle |
| 1U | R/B | Headlight switch | ~12 V on |
| 1V | BR/W | Neutral/clutch (MT) or P/N range (AT) | MT 0 V neutral/clutch in; AT 0 V (1994) / ~1.0 V (1995) in N,P |
| 2A | B | Ground injector | 0 V |
| 2B | B | Ground output | 0 V |
| 2C | B/LG | Ground ECU | 0 V |
| 2D | B/L | Ground input | 0 V |
| 2E | W | SGT (crank angle; 1995 manual says "camshaft position sensor") | 0 or 5 V ign on; ~2 V idle |
| 2F | B/R | MAF ground? listed "Mass airflow sensor" | <1.0 V |
| 2G | Y/L | SGC | 0 or 5 V; ~1.5 V idle |
| 2H | LG/Y | DLC TEN (test mode) | B+ O2-monitor, 0 V self-test |
| 2I | B/W | **Igniter signal INTO ECU (input)** | 1994: <0.5 V ign on, ~1 V idle; 1995: ~10 V ign on, ~11 V idle (the two manuals disagree) |
| 2J | LG/R | EGR function sensor | ~1.0 V; 0-5 V running |
| 2K | LG/W | Vref output | 4.5-5.5 V |
| 2L | L/R | Rear defroster | B+ off, <1 V on |
| 2M | R/B | Throttle position | 0.1-1.0 V closed, 3.1-4.5 V WOT |
| 2N | R/L | Heated O2 sensor (one sensor only) | 0-1 V |
| 2O | R/W (1994 drawing: R) | MAF signal (VGP) | <1 V key on, 1.0-2.0 V idle |
| 2P | R/B | Intake air temperature (built into MAF) | ~2.5 V at 20 C |
| 2Q | L/W | Coolant temperature | ~2.5 V at 20 C, ~0.4 V warm |
| 2R | Y/G | PRC (fuel pressure regulator control) solenoid | <1 V when coolant>70 C and IAT>50 C for 150 s after start, else B+ |
| 2S | L/W | Condenser fan relay | <1 V >108 C idle |
| 2T | LG | Fuel pump relay | B+ ign on / ~0 V idle (running) |
| 2U | Y | Injector 1 | B+ ign on; ~12 V idle (pulsed) |
| 2V | Y/B | Injector 2 | same |
| 2W | L/O | IAC valve | 1994: ~7 V on / ~9 V idle; 1995: ~1.0 V on / ~10 V idle (disagree) |
| 2X | Y/R | Purge solenoid | B+ |
| 2Y | G/W | Injector 3 | |
| 2Z | G | Injector 4 | |
Sources: `kb/research/files/R17/charm_1994_07/09/12...png`, `charm_1995_07/09/12...png`, ID drawings `charm_199{4,5}_05_...png`. VERIFIED (read). Note 2F and 2O are both listed as "mass airflow sensor"; 2F <1 V constant = presumably MAF ground/return (INFERRED, not stated). The abnormal-voltage variants (pages "1A to 1L", "1M to 1U", ... in CHARM 1994/1995, also saved) are fault-finding versions of the same table.
Observations: single heated O2 (narrowband), no knock input, no second O2, no cam-phase, no alternator control. Barometric sensor: Code 14 "atmospheric pressure sensor" exists in 1994 (internal to the PCME; no pin) (VERIFIED `dl/m1994_tests_with_codes.txt:~233`).

## 3. 1996-97 ECM pinout (cavities 1A-1V, 3A-3P, 4A-4Z)
Wire colours: CHARM 1996 terminal-ID image (`charm_1996_05_...png`); I verified the 1A-1U block by zoom; the 3x/4x block colour reading is from a rotated narrow image (medium confidence) - rusEFI wiki gives some colours: 3B R/W MAF, 3F R/B TPS(?), 3G L/W CLT, 3O B/L, 4B W/R, 4E Y/B, 4F W, 4G G, 4H Y/W, 4N G, 4Q L/O, 4R BR, 4U W, 4V Y (https://github.com/rusefi/rusefi/wiki Mazda-Miata-1996, VERIFIED read). They agree with the image where I could compare.
| Pin | Function (CHARM 1996 / 1997) | Voltage / note |
|---|---|---|
| 1A | Cooling fan control (relay) | <1 V on, B+ off |
| 1B | Condenser fan control | same |
| 1C | (table: unused; ID drawing shows a violet wire there) | -- |
| 1D | Diagnostic code serial output to DLC-2 terminal KLN | serial |
| 1E | MIL | B+ off, <2 V on |
| 1G | A/C relay control | B+ / <2 V on |
| 1H | Headlight | |
| 1I | Test mode TEN (DLC) | B+ open, <1 V grounded |
| 1J | Rear defroster | |
| 1K | A/C switch | ~2 V on, B+ off |
| 1L | Load/no-load (neutral/clutch MT, range switch AT) | |
| 1M | Vehicle speed | ~7 or <1.5 V stopped; ~3 V driving |
| 1O | MT/AT select | ground = MT, open = AT |
| 1P | Blower fan switch | |
| 1Q | Brake switch | |
| 1R, 1T | TCM FAIL, TCM diagnostic test mode (AT only) | |
| 1U | Fuel pump relay | B+ key on, <1 V cranking/idle |
| 1F,1N,1S,1V | unused (*) | |
| 3B | MAF (VGP) | <1 V key on, 1.0-2.0 V idle |
| 3C | Front HO2S signal | 0.1-0.9 V cold; 0.5-1.0 accel |
| 3D | Rear HO2S signal | 0-1.0 V |
| 3F | TPS | 0.1-1.1 V closed, 3.1-4.5 WOT |
| 3G | ECT | ~2.5 V at 20 C |
| 3H | Barometric pressure (from EGR boost sensor) | ~4.0 V at 101.3 kPa |
| 3I | Vref 5 V (TPS, EGR position) | ~5.0 V |
| 3J | EGR valve position | 1996 ~0.8 V; 1997 0.7-0.8 V |
| 3K | IAT | ~2.5 V (1996); 2.3-2.4 V (1997) at 20 C |
| 3L | Closed-throttle switch | <1 V released / B+ |
| 3M | Front HO2S heater | <2 V |
| 3N | EGR pressure (EGR boost sensor) | 1997: 4.0 V on, 1.0-1.5 V idle; 1996: "varies" |
| 3O | Analog sensor ground | |
| 3P | Power steering pressure switch | |
| 3A,3E | unused | |
| 4A | ECM ground | |
| 4B | Power supply from main (FUEL INJ) relay | |
| 4C | Injector ground | |
| 4D | Output device ground | |
| 4E | NE- (crank sensor) | |
| 4F / 4G | SGT / SGC cam (in distributor) | 0 or 5 V; 2.0 / 1.5 V idle (as 1994-95) |
| 4H | NE+ (crank sensor) | |
| 4I | Backup battery | B+ |
| 4J | PRC solenoid (fuel pressure regulator control) | <3 V ~149 s after hot start, else B+ |
| 4L | Engine speed to tachometer | 0 or ~11 V key on; ~6 V idle (average of pulses) |
| 4N / 4R | IGT1 / IGT2 (coil in distributor area) | <1 V on, ~0.2 V idle |
| 4O / 4P | EGR solenoid vent / vacuum | B+ |
| 4Q | IAC valve | 1996: <4.8 V key on, ~10 V idle; 1997: ~10 V key on, ~4.8 V idle (values swapped between years; one is probably a manual error) |
| 4T | Purge solenoid | B+ |
| 4U-4X | Injectors 1-4 (separate) | B+ key on |
| 4Y | Engine coolant temp to TCM (AT) | |
| 4Z | 1997 only: rear HO2S heater (<2 V warm, B+ <70 C); 1996 table: unused | |
| 4K,4M,4S | unused | |
VERIFIED: `charm_1996_06..09`, `charm_1997_06_Engine_Control_Module__{1,3,4}.png` (I viewed 1997 pages 1,3,4; page 2 (1L-3E) not viewed - UNVERIFIED that 3x values equal 1996 except as noted).
Tach in 1996-97: ECM drives it from 4L (output). Wired-through: "Instr Cluster" (rusEFI wiki).
Compare 94-95 -> 96-97: 94-95 tach comes from the igniter itself (2I is its signal into the ECU); in 96-97 ECM 4L sends it. (INFERRED from the pin tables; not confirmed by a wiring diagram.)

## 4. OBD-II, diagnostics, immobiliser, readiness
- 1994-95: no OBD-II; codes via Self-Diagnosis Checker / System Selector or jumper TEN-GND at the DLC; code numbers 1,3,4,8,9,10,12,14,15,16,17,25,26,28,29,34 (VERIFIED `dl/m1994_tests_with_codes.txt:83-100`). Code 1 = ignition signal (IGf), 16 = EGR function sensor.
- 1996-97: DLC-2 = standard OBD-II 16-pin under dash; ECM 1D "KLN" goes to DLC-2 (wire W/B to ECM; DLC-2 shows +B (W/G), K-line wire, ground) (VERIFIED CHARM 1996 data link connector diagram image, `charm_1996_11_weData_Link_Connector_0.png`, and 1996 terminal table row 1D). Protocol ISO 9141-2 K-line, pin 7 - **INFERRED** from "KLN" naming and the standard; not stated in what I read (a search result confirms ISO 9141-2 only for 2003 Miata).
- Mazda-specific codes list (generic list incl. P1000 "OBD II monitor testing not completed") in `dl/mextra_mazda_trouble_codes.txt`; it is a generic Mazda table, not Miata-specific (UNVERIFIED applicability).
- Readiness monitors: not researched beyond P1000 existence (not done).
- Immobiliser: no immobiliser pin in 1994-97 ECM tables; generic code list P1602-1604 is not Miata-specific. NB: Mazda Miata immobiliser was introduced with the 1999+? - NOT verified. Treat 94-97 as having none (INFERRED from the absent pins).
- Computer relearn: battery disconnect loses adaptive memory (Mitchell generic, `dl/m1997_computer_relearn.txt`).

## 5. Functions summary (what a replacement must drive)
Hot-wire MAF with IAT (analog VGP + IAT + a ground) 2F?/2O/2P | 3B/3K; sequential-capable four injectors; two igniters (94-95) / IGT1+IGT2 (96-97) wasted spark; one SGT/SGC pair from the distributor (and NE crank sensor on 96-97); fuel pump relay low side; single IAC duty output; two fan relays; A/C relay + A/C switch; purge, EGR vent/vacuum solenoids, PRC solenoid (pressure regulator control = raises fuel pressure on hot start for 150 s); EGR function / boost sensors; 96-97 adds rear O2 + heaters, DLC K-line. 94-95 -> 96-97 pin counts differ, so firmware needs separate pin maps (already per-year in the repo).

## 6. Case / board outline for 1996-97
- No dimensions/photos with scale found in public sources I could reach. Searches (standard mode) gave only seller listings and vendor install guides.
- rusEFI `hellen-miata-NA8` repository (cloned, `work/R17-stock-ecu-1994-97/repos/na_hellen-miata-NA8/`, file `hellen64_NA8_96.kicad_pcb`): Edge.Cuts bbox 154.2 x 159.2 mm (x 21.0-175.2, y 11.6-170.8), 7 mm corner arcs, six 5 mm (radius 2.5 mm) mounting circles at (26.10,16.81), (170.10,16.81), (26.10,98.81), (170.05,98.81), (26.10,165.61), (170.10,164.81) (mm, KiCad coordinates; footprints MountingHole_4.5mm_Pad), so hole pitch about 144.0 mm in X, 148.8 mm in Y with a middle pair. Connector footprint 178780-1 (TE) is their 76-pin plug on the board - not the stock harness connector. VERIFIED computed with pcbnew (`work/.../repos/outline.py`).
- The rusEFI NA6_94 board (`hellen64_NA6_94.kicad_pcb`) has the identical Edge.Cuts and holes, so the outline is a Hellen64 template, not proof of the stock 96-97 case size. The rusEFI NA8-96 rev A is reported "good to drive, great success" (wiki Hellen-NA96) = it physically fits the stock case with its USB-mini and 3.5 mm jack ports; INFERRED that the stock case internal footprint is >= about 154 x 159 mm. Confidence medium-low.
- 1996-97 and 1994-95 mounting: three 10 mm nuts (AMP guides) vs six holes on the Hellen PCB: the nuts are the car-side studs, the PCB is held in the case.
- Not found: a DXF of the 96-97 case; photographs of the opened 96-97 ECU with scale.

## 7. Known problems (all UNVERIFIED unless noted)
- No-start with no fuel and no spark often traced to the main relay, the CAS (distributor sensors) or coil pack, not the ECU (forum threads via search; grassroots/classic motorsports forums).
- A Mazda tip (miata.net, Oct 1998, "tip_3_1098", only as search snippet; page blocked) describes no-spark when the wire on PCM 2I is shorted at the heater mounting bolt; it says 2I should read about 5 V - which disagrees with both workshop tables (1994 ~1 V, 1995 ~10 V) and with the ID drawing colours (2I is B/W, a light-green/red wire is 2J). Treat as unreliable.
- 1994 vs 95 incompatibility of igniter signal / tach (see section 1).
- Capacitor leakage: only found for other platforms (Lexus); nothing Miata-specific.

## Sources actually read
- CHARM (Mazda 1994-1997 MX-5 Miata L4-1.8L DOHC): Terminal ID, Terminal Voltage (Reference Data), Engine Control Module and Data Link Connector pages, all four years; images saved in `kb/research/files/R17/charm_*.png` (CHARM is itself a copy of the Mazda manual, so the "two independent sources" for the pin tables are CHARM + rusEFI wiki, not two workshop manuals). Also local copies of Mitchell (ALLDATA-style) text in `work/R17-stock-ecu-1994-97/dl/` (component locations, tests with codes, trouble codes).
- https://wiki.rusefi.com/Legacy-Miata-NA-48-pin-board-for-MRE ; https://wiki.rusefi.com/Miata ; raw wiki pages `Hellen-NA96.md`, `Mazda-Miata-1996.md`, `Mazda-Miata-1994.md` (saved `dl/web/`; 1994 page not read in detail); https://github.com/rusefi/hellen-miata-NA8 and ...-NA6 (shallow clones).
- AMP/DIYAutoTune MSPNP install guides 94-95 and 96-97 (saved `dl/web/amp9495.html.txt`, `amp9697.html.txt`).
- Search snippets only (pages blocked 403/Cloudflare): miata.net forum threads on ECU part numbers/94 vs 95, redlineautoparts and partrequest listings.

## Not checked
- Internal teardown of either ECU (board photos, chip makers): no source found.
- Case outer dimensions, 96-97 mounting studs layout, connector part numbers (the 48-pin and 64-site housings), seals.
- Page 2 of 1997 terminal table (1L-3E) not viewed; 1997 wire-colour drawing not viewed; 1994 wiring diagram for the tach path not read (the `dl/m1994_wiring.txt` is text only without that detail).
- Readiness monitors, Mazda OBD-II protocol confirmation, MIL flash code behaviour, market (Europe/Japan/Canada) differences, automatic-transmission TCM interface beyond pin list.
- Part numbers are seller/forum level only (no Mazda parts catalogue).

## Implications for this project
1. **Ordered 1994-95 motherboard rev 0.9: OUT_TACH is wired directly to J1.2I** (`evidence/ord_mb9495/pcb_nets.txt:48`: `OUT_TACH J1.2I JD1.11`). Workshop manuals of both 1994 and 1995 list 2I as an input from the igniter. An ECU output driving that wire fights the igniter (and the TSB note says a short on it causes no-spark). Fix on the ordered board before first power-up: cut the trace/pad to J1.2I or leave tach output unconfigured in firmware; current rev 0.12/0.13 JP5 open is right. Confidence medium-high (manual tables) - voltage ambiguity (1994 ~1 V vs 1995 ~10 V) means do not drive it.
2. 94-95 and 96-97 pinouts are totally different; do not reuse a year module. Pin tables above are ready to be diffed against `repo/scripts/mb_na6.py`/`mb_na96.py` mapping (not done here). Confidence high.
3. 96-97 outline/holes: use 154.2 x 159.2 mm with six holes from the rusEFI NA8-96 board as the better placeholder, but only after measuring a real case. Confidence low-medium.
4. 96-97 needs: rear O2 input (3D), two heater drivers (3M front, 4Z rear in 1997), EGR boost/position sensors and EGR/purge/PRC solenoids (4O,4P,4T,4J), K-line on 1D to DLC-2, MIL on 1E, 4L tach output, IGT1/IGT2 (4N/4R) and NE+/NE- (4H/4E) crank sensor with SGT/SGC cam: the product omits OBD-II (documented). MIL 1E is low-side (B+ = lamp off, <2 V = on), so an unconfigured output leaves the lamp off; document that and that the AT-only lines 1R/1T/4Y are not serviced. Confidence medium.
5. Stock part numbers (BPE8, BPL9, BPS1, BP3A) as donor-core guide: UNVERIFIED; the customer must send/keep their case; list in INSTALL that 94-95 and 96-97 cases have different connectors. Confidence low.
6. ECU location behind the passenger seat (three 10 mm nuts, connector release tab): installation notes in INSTALL.md should say so; a USB-C cutout in the stock lid is how rusEFI's NA adapter does it (8 mm hole) and one case screw needs 3 x M4 washers (recessed thread / heat sink) on the 48-pin adapter. Confidence medium.
