# B12 - 2001-05 motherboard (rev 0.9, CURRENT): layout and circuit review

Status: COMPLETE (2026-11-16). Scratch/scripts: work/B12-motherboard-2001-05-layout/ (scripts/, out/).

## Summary
1. Outline/holes/header are the NA placeholder. The Hellen NB2 KiCad board (ext/hellen-miata-NB2/hellen72_NB2.kicad_pcb, Edge.Cuts + footprints, read with pcbnew) gives: board 154.000 x 159.000 mm, four R7.0 corners, no notches, 6 holes dia 5.0 mm. VERIFIED (numbers); that this is the real 89661-3T270 case geometry is INFERRED (Hellen README "Compatible cases 89661-3T270", "M4 x 10mm ... NB external case").
2. Header position cross-check: repo J1 footprint (TE 353830-5) has the same pad pitch and row spacing as Hellen's P2, and its two shell holes (spacing 56.8 mm) equal Hellen's last two holes; with a constant shift of (+26.05, +11.29) mm every one of 22 common pin names (2C ... 4AF) lands exactly on Hellen's pad, and both shell holes land on Hellen's (74.5, 14.45) and (131.3, 14.45). VERIFIED (computed).
3. After the outline change J2 (wideband) and J4 (USB-C) overhang the new bottom edge by about 3 mm and must move up; nothing else conflicts with the new corners/holes (checked by bounding boxes). INFERRED.
4. F2/F3 (SMD1812-200-30: hold 2.0 A at 25 C, 1.45 A at 60 C, 0.80 A at 85 C, trip 4 A, 30 V) feed a VVT valve of 6.9-7.9 ohm (20 C) = 1.8-2.1 A at 14.4 V DC: little margin when hot (see circuit). INFERRED.
5. Wrong year preset (2001-02 vs 2003-05): electrically harmless both ways, the car simply does not start. INFERRED.
6. Ground: one continuous GND net on both layers, 3A/3B/4A/4O to the daughterboard sockets 1.6-4.1 mOhm (my raster model, 1 oz assumed). No GND island problem found.
7. Docs: README calls the first header terminal "1A" at (40.95,16.60); there is no plug 1, that pin is 2A.

## 1. Mechanical: Hellen NB2 geometry vs repo (all mm, origin = board top-left corner, y down)
Sources: ext/hellen-miata-NB2/hellen72_NB2.kicad_pcb (Edge.Cuts graphics, footprints J11..J17 MountingHole_4.5mm_Pad, P2 8-5353015-1); repo: work/.../mb/miata_mb_0105.kicad_pcb (copy of the board), repo/motherboards/2001-05/README.md lines 34-47. Scripts: scripts/hellen_geom.py, repo_geom.py, fit.py; data out/hellen_geom.json, out/hellen_P2_pads.txt.

| Item | Repo (placeholder) | Hellen NB2 (proposed) | Delta (Hellen - repo) |
|---|---|---|---|
| Board W x H | 154.0 x 161.5 | 154.000 x 159.000 (x 21.098..175.098, y 11.705..170.705 in its file) | 0 / -2.5 |
| Corners | 3 mm radii plus NA notches (x 12.5..141.5 at top, bottom notch 11.5..) | 4 x R7.000, straight edges | outline must be redrawn |
| Hole dia | 4.5 plated, 7 pad | Edge.Cuts circle R2.5 (dia 5.0), pad drill 5.0, pad 7.0 (footprint is named 4.5 but its drill is 5.0) | +0.5 |
| H1 top-left | 17.0, 7.3 | 5.0, 5.1 | -12.0, -2.2 |
| H2 top-right | 137.0, 7.3 | 149.0, 5.1 | +12.0, -2.2 |
| H3 mid-left | 4.0, 84.0 | 5.0, 87.1 | +1.0, +3.1 |
| H4 mid-right | 150.0, 84.0 | 148.95, 87.1 | -1.05, +3.1 |
| H5 bottom-left | 4.0, 143.0 | 5.0, 153.9 | +1.0, +10.9 |
| H6 bottom-right | 150.0, 143.0 | 149.0, 153.9 | -1.0, +10.9 |
| Header pin 2A (row 3, pin A) | 40.95, 16.60 | 66.995, 27.89 | +26.05, +11.29 |
| Header row y (2C / 2B / 2A rows) | 8.6 / 12.2 / 16.6 | 19.89 / 23.49 / 27.89 | +11.29 |
| Header shell holes (3.5 mm NPTH) | 48.45 / 105.25 at y 3.15 | 74.5 / 131.3 at y 14.45 (Hellen P2 holes 41.3/95.6/152.4 less 20.2... see json; the last two) | +26.05, +11.3 |

Hellen's P2 is the 122-position 8-5353015-1 (sections 1(22), 5(28), 2, 3, 4); the repo's 72-position OEM header is the right-hand 72 positions of it (physical order 2|3|4), which is why one constant shift fits.

Hole count differs: Hellen has 6 holes, but the rev 0.9 repo also has 6. Daughterboard standoffs (HD1..4) and JD1/JD2 do not need to move relative to each other; the daughterboard mounting is independent of the case holes, but the whole assembly must be checked: the harness header moves 26 mm right and 11.3 mm down, so the top-left region (F2/F3 at x 8) and the JD1 area need a recheck/reroute (not done).
Mouse-bite check: the stock board (not Hellen's) was never measured; ask the owner to measure one stock PCM board or case (hole centres) to confirm; Hellen's own file is the best available evidence.
Cutouts: Hellen places USB at the right edge (x~140, y 51..63) and MAP at the right (x~141, y 107..130); repo has USB-C, J2, MAP on the bottom edge. Whether the stock case lets these be reached is UNVERIFIED (no case drawing).

Bottom-edge fit with the 159 mm height: J2 bbox y 148.3..162.0 and J4 bbox y 152.8..161.8 (rel) exceed 159.0 by about 3 mm (fit.py). Move both up about 3.5 mm (or drop the board's lower part).

## 2. Circuit review (non-connector parts, from pcb_pads.csv / pcb_footprints.csv)
| Ref | Part | Nets | Purpose / verdict |
|---|---|---|---|
| F1 | 3 A hold 2920 PTC | VBAT_IN -> HTR_PWR | LSU heater feed (J2.8). OK |
| F2 | SMD1812-200-30 (C46641168) | VBAT_IN -> IAC_12V (2P) | idle valve +12 V, protects 0.8 mm track from a shorted harness |
| F3 | same | VBAT_IN -> OCV_12V (4D) | VVT valve +12 V |
| F4 | 1.1 A hold 1812 | VBAT_IN -> AUX_VBAT (J5.15) | add-on header +12 V |
| D1 | SS34 | pad1 (K) IAC_12V, pad2 (A) OUT_IACV | freewheel for idle valve, polarity correct (KiCad D_SMA pad 1 = cathode; INFERRED) |
| D2 | SS34 | K OCV_12V, A OUT_VVT | same for VVT valve; correct |
| D5 | SS34 | K AUX_VBAT, A OUT_BOOST | boost valve freewheel |
| R1/R6 | 120 / 0R | CAN_H - CAN_T - CAN_L | termination, R6 is the link |
| R20-22 | 4.7k (DNP option) | VBAT_IN -> IN_SW1..3 | optional pull-ups, correct direction |
| R35/R36 | 4.7k / 10k | V5_EXT-IN_FLEX; IN_N2O-GND | flex pull-up, nitrous pull-down |
| R2/R3 | 5.1k | CC1/CC2 -> GND | USB-C sink |
| U4 | USBLC6-2SC6 | D+/D-/VBUS | ESD, pin map matches USBLC6 convention |
| C1/C2/C3 | 1u, 10n, 470p | V5_SENS, IN_MAP | MAP supply decoupling and output filter |
No part is year-specific; there are no solder links for 2001-02 vs 2003-05.

Alternator output OUT_ALT (3M): 0.6 mm track, no motherboard part; load is a logic-level input (about 5 mA per repo firmware/README line 232, UNVERIFIED), pull-up question documented by the repo. Main relay OUT_MAINRLY (3H): 0.5 mm track, relay coil about 0.1-0.2 A (typical, UNVERIFIED), driver on the daughterboard. Not checked further.

### VVT valve current vs driver and fuse
- Coil resistance: Mazda manuals for later engines (2008 MX-5 LF engine, MZR 1.6) give 6.9-7.9 ohm at 20 C; no NB 1.8 figure found. UNVERIFIED for the NB2 (web search, workshop-manuals.com 2008 MX-5 page; repo circuit_sim.py:330 assumes about 7.5 ohm / 6 mH "typical").
- Current: 14.4 V / 6.9..7.9 = 2.09..1.82 A cold at 100 % duty; 16 V: 2.3 A; 9 V: 1.3 A. Hot coil (+100 C, copper +0.39 %/K): 1.4-1.6 A.
- Driver: VND7NV04 Ilim 6 / 9 / 12 A (min/typ/max, datasheet C155605 table at line 404, VIN=5 V), clamp 40-55 V: not a limit.
- F3: SMD1812-200-30 (datasheet C46641168 thermal derating table): hold 2.00 A @25 C, 1.80 @40, 1.45 @60, 1.09 @70, 0.80 @85 C; trip 4.0 A. A PWM valve heats the fuse with I_rms = V/R * sqrt(duty): about 1.1 A rms at 50 % duty, 14.4 V. In a 60-85 C case that is above hold: nuisance trips possible during hot soak with high VVT duty (the valve defaults to the no-advance position, engine still runs; the fuse resets). Margin is fine at 25 C. Same reasoning for F2: idle valve 11 ohm (repo assumption, UNVERIFIED) = 1.3 A at 100 %, typical idle duty lower. Fix: a 2.6-3 A hold part (SMD1812-260/-300) in F3 (and F2), the trip is still low enough to protect 0.8 mm tracks (IPC-2221 external 1 oz: 0.8 mm about 2.0 A at +10 K, 2.8 A at +20 K), or keep and accept.
- D2 SS34: 3 A average, IFSM 80 A (datasheet C8678), VF 0.55 V at 3 A; freewheel current <= 2.3 A: fine. VRRM 40 V vs load-dump clamp of D6 on the daughterboard (SMCJ30A, clamp roughly 48 V at full surge, from memory, UNVERIFIED) is a theoretical overlap only while the driver is on; not reported.
- The stock car has no such fuse (valve fed from the main relay circuit); F2/F3 exist to protect the PCB. Purpose correct.

### Wrong year preset (firmware only; same motherboard)
Facts: 2001-02 key-switched main relay, 3H unused, 4S unused; 2003-05 PCM pulls 3H low to close the main relay and reads IG1 on 4S (repo research/pinouts_9605.md lines 205-217, firmware/README.md 55-63; per rusEFI wiki, not re-verified). Daughterboard wake path: VIGN_IN -> D8 -> +12V_IN (design.py:204); VBAT_IN -> D7 -> +12V_IN.
- 2003-05 preset on a 2001-02 car: firmware drives 3H (open pin, nothing connected) and expects 4S high; 4S is not connected, so VIGN reads about 0 V (divider R13 33k / R14 6.8k) and rusEFI cuts fuel and spark. No stress to any part; documented in firmware/README.md line 62.
- 2001-02 preset on a 2003-05 car: 3H is never pulled low, so the main relay never closes: 4AF (VBAT_IN) stays dead, so injectors, IAC, VVT, wideband heater and (via main relay) CKP sensor feed are unpowered. The logic still wakes via 4S -> D8 (battery sense reads about 0 V). No damage; the engine does not start. INFERRED.
- Risk is customer confusion only. Suggest the firmware shows a "main relay output 3H not driven / VBATT low while VIGN high" warning (cheap check: VIGN > 9 V and VBATT < 4 V for 2 s on 2001-02 preset -> TunerStudio message).

## 3. Layout
Track widths (pcb_net_routing.csv; 2-layer, copper weight not stated in the evidence, 1 oz assumed UNVERIFIED; IPC-2221 external, 10 K / 20 K rise: 0.5 mm 1.4/2.0 A, 0.8 mm 2.0/2.8 A, 1.0 mm 2.4/3.4 A, 1.2 mm 2.7/3.7 A):
- VBAT_IN min 1.2 mm: carries everything behind 4AF (logic about 0.5 A, heater up to 3 A at warm-up, F2 up to 1.3 A, F3 up to 2 A, F4 1.1 A: worst-case sum about 8 A, realistic simultaneous about 4 A). The 1.2 mm track runs 410 mm in total. About 4 A is already 3.7 A @ +20 K territory; a pour or 2 mm would be safer. INFERRED, low/medium; the F1/F2/F3 PTCs limit sums only per branch.
- IAC_12V, OCV_12V, OUT_IACV, OUT_VVT, OUT_INJ1: 0.8 mm, adequate for 1-2 A. LSU heater 1.0 mm for <= 3 A: ok. AUX_VBAT 0.5 mm for 1.1 A hold: ok. OUT_ALT 0.6, OUT_MAINRLY 0.5: ok for 0.2 A.
- Ground (scripts/gnd_dump.py + gnd_solve.py, raster 0.2 mm, 1 oz = 0.49 mOhm/sq, via 1.5 mOhm, 974 GND vias): GND forms ONE connected component incl. 3A, 3B, 4A, 4O, JD1/JD2, J4, U2, J5 (KiCad DRC also reports no unconnected items). Resistance from the four J1 GND pins tied together: JD1 0.87 mOhm, JD2 1.07, J4 0.95, U2 1.6, J5 1.6 mOhm. Single pins to JD1: 3A 4.1, 3B 1.9, 4A 1.6, 4O (sensor ground) 3.2 mOhm. 1 A injector pulse = about 4 mV on that path, i.e. 3 ADC LSB shared with the sensor ground: minor. VERIFIED (model) / copper weight assumed.
- DRC: starved-thermal warnings (14, "spoke connected to isolated island") present; each such pad still connects elsewhere (no unconnected reports).
- USB: USB_DP/USB_DM 0.2 mm, 62.8 / 58.7 mm, with layer changes, D+/D- length difference 4 mm; full-speed 12 Mbit/s (rise time much longer than the skew), no impedance control needed. USBLC6 at the connector. VBUS 0.3 mm. Adequate.
- MAP: IN_MAP 0.2 mm, 135 mm long, C3 470 pF at the sensor, V5_SENS 0.4 mm 142 mm with 1 uF+10 nF at the sensor. Long but filtered; crosstalk from nearby switching/CAN not analysed. Adequate for a 1 kHz-bandwidth sensor signal.

## Sources actually read
the review brief; evidence/cur_mb0105 (pcb_pads.csv, pcb_footprints.csv, pcb_nets.txt, pcb_net_routing.csv, pcb_stats.json, drc_kicad9.rpt, layers/top_all.png); repo/motherboards/2001-05/README.md; repo/scripts/mb_nb2.py, design.py (D6-D8, drivers); repo/research/pinouts_9605.md (NB2 section); repo/firmware/README.md; repo/VERIFICATION.md H2 and reverse-battery text; ext/hellen-miata-NB2 (hellen72_NB2.kicad_pcb, README.md, connector-mapping.txt); datasheets/txt C46641168_SMD1812-200-30, C155605_VND7NV04TR-E, C8678_SS34; web search (OCV resistance).

## Not checked
- Real stock NB2 board/case measurement; case cutouts for USB/MAP/J2.
- Copper weight (1 oz assumed); fab stackup not read.
- Mutual crowding of the moved header with F2/F3/JD1 area (needs reroute).
- Main relay / alternator driver circuit on the daughterboard (other audits).
- Crosstalk on the MAP trace; D1/D2 reverse rating in a true load dump.
- NB-specific OCV and IAC coil resistance values.
