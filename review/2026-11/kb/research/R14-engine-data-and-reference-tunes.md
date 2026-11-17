# R14 Engine data and reference calibrations (Miata 1.6 / 94-97 / 99-00 / 01-05)

Date of work: 2026-11-16. Scratch: `work/R14-engine-data-and-reference-tunes/`. Downloaded files: `kb/research/files/R14/` (index at the end).

## Summary (10 lines)
1. Public base calibrations exist for all four variants, but they DISAGREE strongly. At 100 kPa and 4500-5200 rpm the rusEFI NB table asks for about 28 deg, the Speeduino NA/PNP tunes about 29 deg, but Speeduino's own NB8B tune only 10-11 deg (VERIFIED, files below). Nobody should treat any one of them as "the right base map".
2. Injector dead time: three public sources give 1.25 ms (rusEFI NB, 14 V), 0.90 ms (FOME NB, 14.4 V) and about 1.0 ms (Speeduino, open time 1.0 ms x 100 % at 13.9 V). I found no primary (Denso/Mazda) dead-time or flow-at-pressure datasheet for any of the four stock injectors. A first start on a base tune therefore rests on UNVERIFIED numbers.
3. Stock injector part numbers (miataturbo wiki, rusEFI code comments): 1990-93 195500-1970; 1994-97 195500-2180; 1999-00 195500-3310; 2001-05 195500-4060. Flow figures differ by source: 1.6 230 vs 212 cc; 94-97 265 vs 254; 99-00 260 vs 256; 01-05 265.
4. Trigger decoding is well documented in source code (rusEFI `trigger_mazda.cpp`, Speeduino `miata9905.cpp`). NA: 4-pulse crank (SGT, 70 deg wide) plus 2-pulse cam (SGC). NB: 4 crank teeth (alternating 70/110 deg) plus a 3-pulse cam (1 + 2).
5. The repo's firmware uses the same trigger assignment as rusEFI (checked: `miata_board.cpp:106-109`, `203-207`).
6. Compression ratio conflicts: 1.6 9.4 (Moss, Wikipedia) vs 9.0 (FOME) vs 9.1 (rusEFI default); 2001-05 9.5 (Moss) vs 10.0 (FOME). Low consequence for tuning, but the repo should not copy either blindly.
7. Fuel pressure: Moss spec sheets list 38-46 psi for every year, including NB returnless cars (copy-forward, doubtful). rusEFI/FOME code says 400 kPa (58 psi) for NB2 returnless. Not resolved by a primary source.
8. Base timing 10 +/- 1 deg BTDC at 850 +/- 50 rpm with the TEN test connector jumpered (Moss spec sheets, all years; VERIFIED as published by Moss, secondary to the Mazda manual).
9. Closed-loop lambda is OFF in all Speeduino base tunes ("No correction"); knock is off in the NA6/NA8 tunes. Defaults that ship closed-loop-on would be unusual.
10. Not obtained: MSPNP (jbperf) base maps, rusEFI online tune repository entries, Mazda factory manual PDFs (Cloudflare blocked miata.net and gitea mirrors). See Not checked.

## 1. Engine facts
| Item | 1.6 (1989-93, B6ZE) | 1.8 (1994-97, BP-ZE) | 1.8 (1999-00, BP-4W) | 1.8 VVT (2001-05, BP-Z3) | Source / tag |
|---|---|---|---|---|---|
| Displacement | 1597 cc (78 x 83.6 mm) | 1839 cc (83 x 85 mm) | 1839 cc | 1839 cc | Moss spec sheets m1990/m1994/m1999 (VERIFIED, local copies); rusEFI uses 1.6 / 1.839 |
| Compression | Moss 9.4:1; Wikipedia B-engine page 9.4 (US 1990-93); FOME 9.0; rusEFI default 9.1 | Moss 9.0 (1994, 1996); rusEFI 9.1 | Moss 9.5; Wikipedia NB page "raised from 9.0 to 9.5"; FOME 9.5 | Moss 9.5 (probably copy-forward); FOME 10.0; a parts listing 10 (UNVERIFIED) | conflict; trust Moss/Wikipedia for 1.6, 94-97, 99-00 (two sources agree); 01-05 unresolved |
| Firing order | 1-3-4-2 | 1-3-4-2 | 1-3-4-2 | 1-3-4-2 | Moss all years; rusEFI code (VERIFIED) |
| Redline | 7200 rpm (Wikipedia NA table, UK) | 7000 rpm (Wikipedia, UK) | not found | not found | Wikipedia = secondary. rusEFI `rpmHardLimit` 7200 for all (VERIFIED code). Repo also 7200 (`miata_board.cpp:197`) |
| Idle speed | 850 +/- 50 | 850 +/- 50 (1994) | spec row missing in Moss 96+ sheets | | Moss (VERIFIED as published) |
| Base timing | 10 +/- 1 deg BTDC | same | same | same | Moss all years; check with TEN jumpered. miata.net says 1999+ timing not adjustable (search-result summary only, UNVERIFIED) |
| Fuel pressure (Moss) | 38-46 psi | 38-46 | 38-46 | 38-46 | Moss (VERIFIED as published); doubtful for NB, see 3 |
| Plugs | BKR6E-11 | BKR5E-11 | BKR5E-11 | BKR5E-11 | Moss |

## 2. Stock injectors
| Years | Denso part | Colour | Flow (cc/min) | Sources |
|---|---|---|---|---|
| 1990-93 | 195500-1970 | blue | 230 (miataturbo list; Haltech NA8 page, which wrongly sits on the 94-97 page) / 212 (rusEFI NA6 code) | `files/R14/miataturbo_fuel-injectors.txt`; `rusefi_src/mazda_miata_1_6.cpp` |
| 1994-97 | 195500-2180 | tan | 265 (miataturbo list, rusEFI NA96, FOME NA8) / 254 (miataturbo second table, rusEFI NA94) | same |
| 1999-00 | 195500-3310 | red, thin body | 260 (miataturbo) / 256 (rusEFI NB1, repo) | same + `miata_board.cpp:262-265` |
| 2001-05 | 195500-4060 | purple | 265 (both) | same |
- All are high-impedance ("saturated") injectors (miataturbo, VERIFIED text). Resistance about 14.5 ohm for 195500-3310 (go-parts listing, UNVERIFIED); a no-start guide says 12-16 ohm (UNVERIFIED). The repo documents the 8 vs 20 mH inductance as unknown; I found no inductance data either.
- The pressure at which each flow is quoted is not stated by miataturbo; the page's own formula assumes 43.5 psi (300 kPa) rating. INFERRED: the cc figures are Denso "at 3 bar" values.
- Dead time (ms vs volts), all UNVERIFIED community values:
  - rusEFI NB (identical at 300 and 600 kPa): 6 V 4.0; 8 V 3.0; 10 V 2.0; 11 V 1.7; 12 V 1.5; 13 V 1.35; 14 V 1.25; 15 V 1.20 (`mazda_miata_vvt.cpp`, `setMazdaMiataNbInjectorLag`; same in repo `miata_nb_tune.cpp:120-136`).
  - FOME NB: 8 V 1.97; 9.6 V 1.52; 11.2 V 1.23; 12.8 V 1.04; 13.2 V 0.99; 14.4 V 0.90; 15.3 V 0.85; 16 V 0.73.
  - Speeduino PNP (open time 1.0 ms; correction % at 7/9/12.1/13.9/16.9/20.3 V): 154/117/101-107/100/100/100 for NA and 99-00 tunes; NB8B 110/106/100/100/100/98 at 6.6/9.4/12.1/14.8/16.9/20.3 V.
  - Conflict: at 12 V rusEFI 1.5 ms vs FOME about 1.1 ms vs Speeduino about 1.0 ms. A 0.3-0.5 ms error at idle (pulse around 2.5 ms) is 12-20 % of fuel. I trust none of them; the repo should say "measure on the car (wideband) before relying on the base tune".

## 3. Fuel system
- 1990-97: return-style system with a vacuum-referenced regulator on the rail (regulator listed at 38-46 psi by Moss; miata.net etc. say about 36 psi at idle with vacuum, UNVERIFIED).
- 1999-2005: Radium kit instructions (`files/R14/radium_nb.pdf`, VERIFIED text) show an OEM regulator "next to the fuel pump" (in the tank), the OEM feed line going "to engine and back to OEM FPR", and say that plugging the vacuum port gives "constant fuel pressure like the OEM fuel system". So NB: single line to the engine, regulator in tank, NOT vacuum-referenced. rusEFI and FOME both use `fuelReferencePressure = 400` kPa with `ICM_FixedRailPressure` for NB2 (code comment "400 kPa, 58 psi"). Repo does the same for NB2 only (`miata_board.cpp:276`) and not for NB1. A search-result summary of Radium's page said "60 psi" (UNVERIFIED; the PDF text I extracted contains no psi figure). A grassroots forum thread disputes whether NB routing is truly "returnless" (tee and return into the tank regulator); the practical result (fixed pressure) is the same.
- For NB1 (1999-00) the same single-line in-tank-regulator system applies per the same logic (INFERRED; the Radium kit is titled 01-05, a 99-05 kit exists per search results). The repo's NB1 preset leaves fixed-pressure compensation off; cranking table values (27.5, "return-less NB, higher pressure") are shared.

## 4. Triggers
| Year | Signals | rusEFI / FOME type | Speeduino | MegaSquirt |
|---|---|---|---|---|
| 1989-93 and 1994-97 (CAS in distributor, 1.8 94+ has CAS on cam end) | Outer ring CKP 4 slits per crank rev, inner ring CMP 2 slits (DIYAutoTune page; Haltech "crank 4x, cam 2x") | `TT_MAZDA_MIATA_NA` (`trigger_mazda.cpp:27-57`): primary = 2 pulses/720 deg (SGC), secondary = 4 pulses/720 deg (SGT, each 69.7 deg wide), sync on primary fall at 288.8 deg, `tdcPosition` 5.181, wasted spark | "4G63 / Miata / 3000GT", rising edge, comment "tooth #1 at 355 deg ATDC" (`decoders.cpp:435-441`) | MS2 spark mode "4G63", falling-edge capture (DIYAutoTune) |
| 1999-2005 | 4 crank teeth, alternating 70/110 deg, plus cam with 3 pulses (single then double) | `TT_MIATA_VVT` (crank, rise-only, `tdcPosition` 60+655) with cam `VVT_MIATA_NB`; `vvtOffsets` rusEFI 98, FOME 95 | "Miata 99-05" decoder `miata9905.cpp`: crank angles 710/100/170/280/350/460/530/640, cam pulses 1 and 2, trigger angle 0, wasted spark | MS3 stock: "Miata 99-05" family; aftermarket 36-2 wheel needs "Miata 36-2" |
- rusEFI cam pattern for NB: edges at 325/360, 641/679, 700/720 (deg of 720) (`initializeMazdaMiataVVtCamShape`), consistent with Speeduino's single+double pulse description. Both read from source, VERIFIED.
- Repo assignment matches: NA primary = HALL2 (cam SGC), secondary = HALL1 (SGT); NB crank on HALL1, cam on HALL2 (`miata_board.cpp:106-109, 203-207`). Checked, correct against rusEFI's own NA6 Hellen board (triggerInputPins A6/B1, cam unassigned) and NB1/NB2 Hellen boards (crank input plus cam input).
- Sensor polarity: LinkECU thread (search summary, UNVERIFIED) says some Mazda sensors flip polarity near idle; scope before trusting.
- FOME also sets `globalTriggerAngleOffset = 10` for NB (the rusEFI NB base config does not); that is an offset difference to note when comparing timing with a light.
- Base timing check: ECU TEN connector jumper locks timing at 10 deg BTDC; verify with a timing light on cyl 1 and compare rusEFI "fixed timing" mode (not extracted; UNVERIFIED).

## 5. Reference calibrations (files in `files/R14/`)
Sources downloaded: Speeduino `Tunes/Mazda` (5 files, commit 99b2a62, March 2025), rusEFI engines/mazda (the repo's pinned copy 1374bd0), FOME `firmware/config/engines` (HEAD e628773). Extraction: scripts in `work/.../msq.py`, `pick.py`, `tab.py`.

### 5.1 Ignition advance (deg BTDC), nearest table cell, "load" = MAP kPa
| Calibration | Idle (800-1000 rpm, 36-40 kPa) | Cruise (2300-2700 rpm, 50 kPa) | 100 kPa peak torque (4500-5200) | Redline (7000-7200, 96-99 kPa) | Light load 6500 rpm 50 kPa |
|---|---|---|---|---|---|
| rusEFI NA 1.6/NA94/NA96 base map (`mazda_miata_base_maps.cpp`, load bins 10-250) | 18 at 1000 rpm / 35 kPa; 15 at 800 | 31 (2300 / 55 kPa) | 27 (4300 / 99 kPa) to 29 (4800) | 32 (7200 / 99 kPa) | 36-37 |
| rusEFI NB (VVT) table (`mazda_miata_vvt.cpp`, load bins 25-250; used by repo for NB1 and NB2) | 13 (850 rpm / 34 kPa) | 28 (2146 / 54 kPa) | 28 (4144 and 4884 / 99.5 kPa) | 30 (6787) to 31 (8000) | 32 |
| Speeduino NA6 / NA8 PNP (2025.01.1) | 20 | 24 (2500 / 50) | 29 (4500 / 96) | 29 | 34 |
| Speeduino PNP96-98 | 20 | 24 | 29 | 29 | 34 |
| Speeduino PNP99-00 | 18 | 22 | 29 | 29 | 34 |
| Speeduino NB8B PNP (2022.01) | 20 | 21 (2700 / 50) | **11** (4700 and 5200 / 96) | **9** (7200 / 96) | 20 |
- CONFLICT: Speeduino NB8B at WOT is 17-20 deg below the rusEFI NB table. Both are community base maps with no stated test conditions (UNVERIFIED as to correctness). rusEFI's NB table is an "export of NB2 tune, 2017"; Speeduino's NB8B is probably deliberately conservative. A safe first-start strategy is the lower map; the repo uses the higher one.
- Note: rusEFI NB ignition table loads reach 250 kPa and the VE table is clamped to 80 above 116 kPa; for naturally aspirated cars only the rows up to about 100 kPa matter.
- The rusEFI NB VE table (fuel_rail variant, `mapBased18vvtVeTable_NB_fuel_rail`): VE 35-40 at 20-25 kPa idle rows, 56-62 at 40-54 kPa cruise (1550-2150 rpm), peak 76-78 at 85-99 kPa and 4900 rpm. Speeduino NB8B VE: 29-34 at 700-900 rpm / 20-36 kPa, about 71 at 96 kPa 4700 rpm; NA6/NA8 PNP VE reaches 128-141 at 96 kPa (a different table scaling).

### 5.2 Other base-tune numbers
| Item | Value(s) | Source |
|---|---|---|
| Cranking rpm | 400 | rusEFI NA and NB; Speeduino all tunes |
| Cranking advance | NA 1.6: 10 deg; NA96: 6 deg | rusEFI `crankingTimingAngle` |
| Cranking dwell | 4 ms (rusEFI NB/NA96); Speeduino 4.5-6 ms | `ignitionDwellForCrankingMs`; Speeduino `dwellcrank` |
| Running dwell (Speeduino) | NA6/NA8 4.0 ms, 96-98 and 99-00 3.5 ms, NB8B 3.0 ms; limit 12 ms (NA), 8 ms (NB8B); battery correction table 106% at lowest bin to 85% | Speeduino msq `dwellrun`, `dwellLim`, `dwellRates` |
| Cranking fuel | rusEFI NB: base 27.5 (mg) with clt cranking correction 60 (flat); FOME NB: coefficients 3.36 (-20 C), 2.97 (-10), 2.69 (5), 2.15 (30), 1.78 (40), 1.47 (50), 1.0 (65, 90); Speeduino `crankingPct` 10 % (NA) / 20 % (NB8B) | code, msq |
| Warm-up enrichment | Speeduino WUE (%): NA6/NA8 179 at -40 C, 163 at -4 C, 138 at 19 C, 112 at 48 C, 100 at 77 C; NB8B 180, 175, 168, 154, 134, 121, 112, 104, 102, 100 at -40..80 C; FOME `cltFuelCorr` 1.25 down to 1.0 | msq, code |
| After-start | Speeduino ASE 15 % for 3-15 cycles by temperature | msq |
| Idle target | rusEFI NA clt-idle table 1180 rpm at -40 C down to 950 at 70 C and above; Speeduino closed-loop targets 1200 (-40 C) down to 800 (warm); Moss spec 850 +/- 50 | `mazda_miata_base_maps.cpp`, msq, Moss. CONFLICT 800 vs 950 vs 850 warm |
| Idle valve | 2-wire BAC valve, duty controlled (Haltech page). Speeduino PWM open loop, frequency 160 Hz (NA6/NA8), 170 (96-98), 500 (99-00), 120 (NB8B); FOME NB 500 Hz; rusEFI NA idle PID P 0.01 I 0.00001 (NA6) and P 0.0065 I 0.3 D 0.002 (NA96, NB) with idle timing PID on, RPM deadzone 100, upper limit 350 | msq, code. CONFLICT on frequency |
| Fan | Speeduino PNP96-98 on 93 C (199.4 F) hysteresis 10 F; PNP99-00 on 94 C (201.2 F) hysteresis 7 F (computed from msq values in F); newer tunes 80 C / 3 C; rusEFI NA94 fan1 100/96 C, fan2 95/91 C | msq, `mazda_miata_1_6.cpp`. Stock switching temps not obtained from a primary source |
| Alternator control | rusEFI NB: target 14.0 V (14.2 for NA96), offset 20, P 16, I 8, D 0.1, period 10 ms; FOME P 20; repo ships it off and PWM 250 Hz "as stock ECU" | `mazda_miata_vvt.cpp`, FOME, `miata_board.cpp:232-249` |
| Closed-loop lambda | Speeduino all tunes: algorithm "No correction" (off); narrow-band flag on NB8B; AFR targets idle/cruise 14.7, 13.6 at 70 kPa, 12.6 at 100 kPa (NA6/NA8/NB8B) or 13.0-13.1 (96-98, 99-00); EGO active above 1200 rpm only | msq |
| Knock | rusEFI/FOME knock band 6.8 kHz (1.6), 13.8 kHz (1.8, FOME `knockBandCustom` 13.81/13.8); repo enables software knock; Speeduino knock off (NA) / analog with threshold values in NB8B and 96-98/99-00 | code, msq |
| VVT (NB2) | rusEFI/repo: 8x8 target table in deg of cam advance, load bins 30-85 kPa, rpm bins 700-6500; row at 70-85 kPa: 13-17 deg at 700 rpm, 24-28 at 1000, 31-33 at 2000, 28 at 3000, 30 at 3500, 28 at 4500, 11 at 5500, 5 at 6500; PID P 2, I 0.005, D 0.002, offset 33, min 20, max 90 (FOME min 10, minimum rpm 400, different 8x8 table peaking 29 deg). Speeduino NB8B: PWM 300 Hz, hold duty 41 %, closed loop KP 0.8125 KI 0.09375, duty 20-80 %, max angle 70 | code, msq. CONFLICT between rusEFI and FOME tables |
| MAP at idle | not sourced. INFERRED from where the base tables put idle rows: 29-40 kPa warm idle | tables |
| Rev limit (Speeduino) | NB8B soft 6500 / hard 7000; 96-98 soft 6800 / hard 7100; NA6/NA8 soft 6000 (!) | msq |

## 6. Conflicts between sources (summary)
1. Ignition at WOT: rusEFI NB 28-31 vs Speeduino NB8B 9-11 (above).
2. Dead time: above (up to 2x at 12 V).
3. Injector flows: above.
4. Compression: above.
5. Fuel pressure: Moss 38-46 psi on NB vs 400 kPa in rusEFI/FOME.
6. NB VVT target: rusEFI vs FOME vs Speeduino all different; `vvtOffsets` 98 vs 95.
7. Warm idle 800 / 850 / 950.

## 7. Implications for this project
(Goal numbers from review brief section 1: 1 errors, 2 removable parts, 3 cheaper parts, 4 user experience, 5 cheaper boards, 6 packaging.)
1. UX / firmware (goal 4), confidence medium: the repo's NB presets take rusEFI's NB tables, which carry about 28 deg at 100 kPa, 4000-5000 rpm, while Speeduino's NB8B tune carries about 10 deg. Wording in the install guide should say the base map is a starting point, with first WOT pulls only after a wideband and knock check. Evidence: sections 5.1, `miata_nb_tune.cpp`.
2. Firmware (goal 4), confidence medium: NB1 gets NB2's VE/ignition tables and `injector.flow = 256`; NB2 gets 400 kPa fixed pressure but NB1 does not, although the NB1 fuel system is also a single line with an in-tank regulator (INFERRED). Consider setting fixed-pressure compensation for NB1 too, or document why not. Evidence: `miata_board.cpp:262-277`, Radium PDF.
3. Firmware, confidence medium: the injector lag table in the repo (4.0 ms at 6 V to 1.20 ms at 15 V) is rusEFI's, about 0.3-0.4 ms above FOME's at 14 V. No primary source exists; say so and offer a way to correct it (wideband at idle).
4. Documentation, confidence high: the repo should state source and unit conventions for ignition tables (load = MAP kPa, advance = degrees BTDC) and that the NA/NB tables go to 250 kPa.
5. Firmware, confidence medium: the NA 1.6 preset inherits CR 9.1 and a 212 cc injector; Moss lists 9.4:1 and miataturbo 230 cc. Flow is the number that matters (13 % fuel). Check what `setMazdaMiataNA6` leaves for `injector.flow` (rusEFI sets 212 in the 1.6 common settings) and correct to 230 cc if the owner agrees. Evidence: `mazda_miata_1_6.cpp` (212), miataturbo list (230), Haltech page (230).
6. Firmware, confidence medium: NA94 and NA96 presets differ from each other in flow (254 vs 265) without a reason; both are the same injector 195500-2180. Pick one (265 per miataturbo main list and FOME).
7. Firmware, confidence low: Speeduino tunes keep closed-loop lambda off by default; the repo's own defaults (rusEFI closed loop) should be checked by the firmware reviewer.
8. No hardware change follows from this task; all points are firmware or documentation.

## Sources actually read
- `repo/firmware/ext/rusefi/firmware/config/engines/mazda/*.cpp` (copied to `files/R14/rusefi_src/`), `controllers/trigger/decoders/trigger_mazda.cpp`, `trigger_structure.cpp`, `trigger_decoder.cpp`, `config/boards/hellen/hellenMiataNA6|NB1|NB2/board_configuration.cpp`.
- `repo/firmware/board/miata_board.cpp`, `miata_nb_tune.cpp`, `miata_pins.h`.
- FOME clone `https://github.com/FOME-Tech/fome-fw` (HEAD e628773): `firmware/config/engines/mazda_miata*.cpp` (copied to `files/R14/fome_src/`).
- Speeduino tunes `https://github.com/speeduino/Tunes` folder Mazda (5 msq; copied to `files/R14/speeduino_tunes/`, extract in `key_constants_extract.txt`); Speeduino firmware clone (`src/decoders/miata9905.cpp`, `decoders.cpp` lines 435-441, 644-650).
- `http://miataturbo.wikidot.com/fuel-injectors` (saved as `files/R14/miataturbo_fuel-injectors.txt`).
- Moss spec pages `https://mossmiata.com/miata-1990|1994|1996|1999|2001|2004` (1990 and 1999 HTML copied).
- Radium NB regulator instructions `https://media.bofiracing.com/uploads/2024/01/Radium-Return-Fuel-Line-Pressure-Regulator-Kit-for-Mazda-MX-5-NB-01-05.pdf` (copied).
- Wikipedia Mazda B engine, MX-5 (NA), MX-5 (NB) pages (secondary).
- page fetch summaries (secondary): Haltech NA8 page `https://support.haltech.com/portal/en/kb/articles/93-na8-1-6l-b6-ze`; DIYAutoTune "How to MegaSquirt your Miata".
- Web search summaries only (UNVERIFIED, not read): go-parts injector guide (14.5 ohm), miata.net ignition page, grassroots NB fuel-line thread, LinkECU thread.

## Not checked
- MSPNP (jbperf/DIYAutoTune) .msq base maps and MS3 settings: download pages not reached; no MegaSquirt base-tune numbers in this file.
- rusEFI online tune repository entries (rusefi.com/online): not retrievable by tools here; only the code defaults are covered.
- Speeduino wiki decoder pages (gitea mirror blocked by Cloudflare; wiki.speeduino.com returned titles only), miata.net pages (403).
- Mazda factory service manual: no PDF found; stock fan temperatures, coil dwell, stock rev limit for NB, idle MAP values, stock closed-loop targets, alternator duty strategy for 1999-2005, injector resistance/inductance/dead time from the manufacturer: all UNVERIFIED or missing.
- FOME VVT table row-by-row and rusEFI default closed-loop/knock parameters were not extracted.
