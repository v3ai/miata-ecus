# B13 - Mechanical stack and case fit

Status: complete (2026-11-16). Tags: VERIFIED / INFERRED / UNVERIFIED as in review brief section 5. No stock case was ever measured by
anyone in this workspace; every case dimension below is second-hand (forum posts of the rusEFI "Frankenso" project, which
targeted the stock NA Miata case). Treat case verdicts as "likely / unknown", never as measured.

## Summary
1. Stack height above the motherboard (MB) top surface: 11.0 mm standoff (8.5 mm socket + 2.5 mm header plastic; repo
   additional-parts) + 1.6 mm daughterboard (DB) + tallest SMD 3.0 mm (inductor FXL0530, datasheet "3.0MAX") = **15.6 mm**.
   M3 pan screw heads on the DB top (about 2.4 mm, ISO 7045 nominal, UNVERIFIED) reach 15.0 mm. INFERRED.
2. 1990-95 case: rusEFI admin posts (2014/2016): 23 mm from top of the shield PCB to the underside of the cover, and "close
   to 4 mm" below the board. If that is the same case, margin above = 23 - 15.6 = **7.4 mm**; harness shell 13.0 mm above MB
   top fits; below the board 4 mm vs worst pin stub 3.0 mm (TE housing pegs, viewer model) leaves 1.0 mm. Verdict: **likely fits (INFERRED, medium/low)**;
   deciding dimension is the 23 mm headroom (unmeasured on a real case) and the case floor features below the board (unknown bosses; one
   hole has a recessed thread, see 4).
3. 1996-97 / 1999-2000 / 2001-05 cases: **unknown**. Hellen's own issue thread (via B11) says the OEM NB case "does NOT look like
   the NA6" case, and the repo's 1996-2005 boards use the NA outline/holes as placeholders (documented). No height source found.
4. rusEFI wiki (VERIFIED, local copy work/.../web/mre_na48.html): one NA case mounting hole has a recessed thread (stock ECU
   has a heat sink there) and needs a stack of **3 M4 washers**; INSTALL.md step 4 ("six M4 holes, stock screws") does not
   mention it. Doc finding.
5. MPX5700AP: datasheet case 867B-04 (p.7 drawing) shows body thickness 7.75-8.26 mm from seating plane; viewer models 6.8 mm
   above the board. So the MAP top is about 8.3 mm above MB top (9.9 above MB bottom): not stack-critical (beside DB, under the cover with 23 mm).
   The AP part has straight leads (only the GP1 variant is 90-degree lead form, datasheet p.1 ordering note); the footprint says "lying flat, leads
   bent 90 deg", so someone must hand-bend 6 leads of an NRND part. Assembly/UX note.
6. All customer exits (J2 wideband x 19-30, USB-C x 75-85, ribbon, MAP hose) are on the edge opposite the harness: the stock
   case has no opening there, so the customer cuts 3-4 holes. Proposals in section 6 (best: one drilled hole or a pre-cut
   plate; or move everything to the harness end if the harness window has spare width: unknown).
7. Mass (INFERRED): DB about 47 g (6-layer), MB 1989-95 about 120 g, assembled stack with hardware about 175 g (1989-95) to 195 g (1996-97); packed
   about 0.4-0.5 kg. No case is shipped (customer's own).

## 1. Case data found (all second-hand)
| Fact | Source | Tag |
|---|---|---|
| "close to 4 mm of vertical space on the back of the board inside this case" (Frankenso, May 2014) | rusefi.com forum t=569 (local f_t569.html) | VERIFIED (post exists); applies to the NA case: INFERRED |
| "vertical space inside the case: from top of red board to bottom of top cover - 23 mm; from top of brain board to bottom of top cover - 10 mm" (Dec 2016) | same thread, p.10 (f_t569start270.html) | VERIFIED text; "red board" = Frankenso shield, "brain" = Discovery stacked on it: INFERRED |
| Mazda 929 case "maybe 8 mm taller", only two holes line up; 89661-32590 "is a taller case"; Australian MX-5 case same size, holes differ | same thread / p=30099 | VERIFIED text; shows case variants differ by hole pattern and 8 mm in height: check the customer's part number |
| Frankenso micro-USB case hole: d = 12 mm, 7 mm from top, 46 mm from right | same thread, first post | VERIFIED text |
| Hellen NA6/NB1/NB2 KiCad: 154.2 x 159.2 board, six 4.5 mm pads (5.0 mm drill) | ext/hellen-miata-NA6/hellen64_NA6_94.kicad_pcb (pcbnew) | VERIFIED. Already compared by B09 (5 of 6 holes match) and B11/B12 |
| Hellen NA6: "Case cover bolts: M4/0.7 countersunk Philips, 9 mm thread" | ext/hellen-miata-NA6/README.md | VERIFIED |
| Hellen NB2 README "Compatible cases 89661-3T270"; "M4 x 10 mm good for NB external case and internal board to case" | ext/hellen-miata-NB2/README.md | VERIFIED text |
| 1996-2005 OEM case dimensions, connector window width | not found | UNKNOWN |

## 2. Stack computation (heights above MB top surface; MB thickness 1.6 mm all boards, DB 1.6 mm both revs: pcbnew)
| Layer | mm | Basis |
|---|---|---|
| MB pin stubs below MB bottom | viewer: J1 TE 3.0, JST J2 2.6, MPX 2.0, sockets 1.45, headers 1.35 | UNVERIFIED (viewer pcb3d.py model values; TE drawing not read). TE housing pegs 3.5 mm per B11 |
| M3 x 6 pan screws on MB bottom | about 2.4 head | UNVERIFIED nominal |
| Case floor to MB bottom (seat) | about 4 | Frankenso statement, second-hand |
| Socket 8.5 + header plastic 2.5 = standoff 11.0 | 11.0 | repo additional-parts (VERIFIED as claim); socket "8.5mm" in BOM C124412 |
| DB bottom side: J1/J2 header pins (viewer -8.59 below DB bottom, i.e. through the sockets), Tag-Connect footprint (no part) | nothing taller than the gap | VERIFIED geometry, only headers on bottom |
| DB 1.6 | 1.6 | pcbnew |
| Tallest DB top parts (viewer box top minus 1.6): L1 FXL0530 3.0 max (datasheet C177247 table: "3.0MAX" VERIFIED; viewer 2.85), L2 MWSA0603S-100MT 2.85 viewer (datasheet not in pack: UNVERIFIED), F1 BSMD1812 2.55, 9x TO-252 (Q1-Q8, Q101) 2.37, 5x SMC TVS (D6, D46-49) 2.36, SMA diodes (D7,D9,D12,D42-45) 2.27, microSD J4 1.9 (Molex SD-47219-001 p.1: 1.90 VERIFIED), U2/U3/U14 DSO-8-EP 1.9, SOIC-8 U6/U7/U9/U10/U106 1.8, SOT-223 U4/Q20 1.75, 1206 caps 1.65 | ten tallest: L1, L2, F1, Q-series (TO-252), SMC TVS, SMA, J4, U14/U2/U3, ... | viewer values INFERRED from viewer/parts.json box tops |
| Top of stack incl. 3.0 mm inductor | 11 + 1.6 + 3.0 = 15.6 above MB top; 17.2 above MB bottom | INFERRED |
| MB parts above MB top: J1 TE shell 13.0 (viewer 14.6 minus 1.6), J5 IDC 9.15, USB-C 3.4, JST 7.3, MAP about 8.3 (datasheet 8.26 max) | all below 15.6 | INFERRED |
| Headroom vs Frankenso 23 mm | +7.4 mm | INFERRED |
| Fixed hardware heads on DB top (4 standoff screws) | about 15.0 | UNVERIFIED |

microSD J4 (DB x 114.7, y 28.3): closed 1.9 mm; hinged lid is 10.85 mm long (SD-47219-001 p.1) so open it stands about 11-13 mm above
the DB (about 25-27 mm above MB top; exceeds the 23 mm headroom): the card can only be changed with the cover off.
INFERRED. The socket is rated -20..+85 C (documented).

## 3. Verdict per year
| Year | Verdict | Deciding dimension |
|---|---|---|
| 1990-95 | likely fits (INFERRED, medium-low) | 23 mm headroom vs 15.6 mm stack; 4 mm underside vs 3.0 mm stubs; hole pattern per B09; the recessed-thread hole needs washers |
| 1996-97 | unknown | NB-style case: hole pattern, connector window width (76-pin housing 130 mm per B10/B11) not known; stack height likely similar but no source |
| 1999-2000 | unknown | as above; 64-pos stock header vs 76-pos fitted |
| 2001-05 | unknown | Hellen NB2 outline 154 x 159 (B12: J2 and J4 overhang 3 mm past a 159 mm edge) |
All verdicts need one real stock case measured: height (cover underside to board seat), hole centres, connector window width, floor bosses.

## 4. Specific mechanical items
- Recessed-thread boss (wiki): needs 3 x M4 washers (about 2.4 mm, INFERRED 0.8 mm each); add to INSTALL step 4 and to the kit.
- Standoff stack: 4 x M3x11 F-F at DB corners (MB x 19/135, y 46.5/113.5). 8 M3x6 screws; the lower ones protrude under the MB bottom
  (about 2.4 mm) into the 4 mm underside gap: check the case floor at those four spots (ribs/heat-sink boss unknown).
- USB-C J4 (GCT USB4105-GF-A, 16-pin, 3.4 mm tall): receptacle body flush with the MB edge (0.3 mm overhang, B09). Needs a hole in the
  wall about 9.5 mm wide x 4 mm tall minimum for the receptacle, in practice 14 x 8 mm for a plug overmold (UNVERIFIED typical).
  A plugged cable tug loads the SMD pads (the 4 shell pegs are THT). Leave-it-plugged advice in INSTALL: needs strain relief
  (zip tie to a case hole, or a panel-mount extension).
- MAP U2 barb: axis y = 138, tip x = 108.5 pointing -x (B09 INFERRED). Hose 3-4 mm ID silicone, OD about 7-8 mm; kink-free bend radius
  about 20-30 mm (UNVERIFIED rule of thumb), but only about 14 mm free beside J5/F1 before the hose must turn to the bottom wall (B09):
  use a 90-degree silicone elbow (3 mm ID) on the barb, or route the hose over J5 (J5 top 9.15 mm, barb axis about 4-5 mm above
  seating plane: no).
- JST J2: right-angle to the bottom edge, plug housing about 12 x 8 mm (UNVERIFIED) plus AEM harness; opening 14 x 9 mm at x = 24.5.
- Ribbon J5: vertical IDC 2x10, 9.15 mm tall, 33 mm in from the bottom edge: the ribbon leaves upward, then bends 90 degrees under
  the cover: needs about 5 mm bend + the 23 mm headroom is fine; a flat cable needs a slot 25 x 2 mm in the wall, or a lid-side pass.
- JP headers on MB (JP1-JP6 1989-95: 8.6 mm tall jumpers) are within headroom.

## 5. Mass (INFERRED; FR4 1.85 g/cm3 plus copper; parts masses are typical, UNVERIFIED)
| Item | Basis | g |
|---|---|---|
| DB (cur 6-layer, 9497 mm2, 1.6 mm) | 94.97 cm2 x 0.16 x 1.85 = 28.1 + Cu about 5 | 33 |
| DB parts: STM32, 2 headers (about 3.4 each), 9 TO-252, SMC TVS, L1/L2, microSD, 300 passives | | 14 |
| DB total (ord rev 0.9 4-layer: about 31 + 14) | | about 47 (45) |
| MB bare (24363 mm2, 2-layer) | 243.6 x 0.16 x 1.85 = 72.1 + Cu 3.8 | 76 |
| MB parts 1989-95: TE 48-pin about 20, 2 sockets about 9, MPX about 6, J5 2, JST 1.5, USB 1, jumpers/PTC 4 | | 43 |
| MB parts 1996-2005: 76/72-pin TE about 32-35 instead of 20 | | 56-59 |
| Hardware: 4 standoffs about 1.6, 8 screws about 0.4 | | 10 |
| Assembled 1989-95 | | about 175 |
| Assembled 1996-2005 | | about 190-195 |
| Shipping with foam/box (UNVERIFIED) | | 0.4-0.5 kg |

## 6. UX: avoiding case cutting (proposals)
Current exits: J2 (x 19.5-29.5), J4 (x 75.5-84.5), MAP hose (barb at x 108, y 138), ribbon J5 (y 125-134).
| Option | Customer work | Board change |
|---|---|---|
| A. One round hole (about 16 mm, drilled, not sawn) in the bottom wall; JST pigtail, USB-C extension and hose all pass through a single grommet | 1 drill hole, 1 grommet (ship in kit) | none for USB/hose if flying leads are used; J2 and J4 would need to be within about 25 mm of each other: move J4 from x 80 to about x 35, or use a USB-C panel-mount pigtail on a 5-pin JST-SH header |
| B. Pre-cut replacement end plate (laser-cut or printed) that screws on with the case lid screws | no cutting | none, but needs measured case geometry first |
| C. Exit through the harness connector window (the car's own cables leave there already): put J2, J4, MAP barb, J5 on the J1 edge | none if the window has spare width (UNKNOWN: housing 91.5 mm wide vs window) | re-layout of all four motherboards; J1 occupies y 0-26 of the top edge, so the strip beside it is narrow |
| D. Leave the lid off or notch only the lid edge | none | none (rusEFI wiki itself suggests running without the lid for USB) |
| E. Ship a printed paper drill template with measured centres (INSTALL already gives x for J2/J4) | 3 holes | none |
Recommendation: A with a flying-lead USB-C (strain relief inside, one grommet) or B once one case is measured; board changes are only needed to make
J2 and J4 adjacent (move J4 to x about 35-40, B09 says the strip x 14-140 is free).

## Sources actually read
- the review brief; repo/INSTALL.md section 3; repo/README.md; repo/additional-parts/order_all_boards.csv, shopping_list.html lines 120-124
- repo/viewer/parts.json, mb8995_parts.json, mb0105_parts.json (box heights); work/.../geom/*.csv; pcbnew outline/area on work/.../pcb copies
- datasheets/txt/C177247_FXL0530-2R2-M.txt (table), C90152_MPX5700AP.pdf p.7 and p.1 table (pdftotext), C164170_472192001.pdf p.1 drawing
- ext/hellen-miata-NA6, NB1, NB2 (pcb, README); kb/boards/B09, B11, B12
- https://wiki.rusefi.com/Legacy-Miata-NA-48-pin-board-for-MRE ; https://rusefi.com/forum/viewtopic.php?t=569 (also start=270 and p=16133, p=30099 via fetch)

## Not checked
- Any real stock case (no CAD, no photos analysed); 1996-2005 heights and hole patterns; actual part masses; TE housing drawings; Sunlord MWSA0603S height; USB plug
  overmold sizes; silicone hose min bend radius (rule of thumb only); whether the stock cover splits at board level; which Hellen hole is "J27".
