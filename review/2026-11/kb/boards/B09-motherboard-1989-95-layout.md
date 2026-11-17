# B09 - 1989-95 motherboard rev 0.13: layout and circuit review (cur_mb8995)

STATUS: finished. Scripts and raw output in `work/B09-motherboard-1989-95-layout/` (a01/a02 track graphs, b01_gnd.py pour
solver, c01-c05 reference-board extraction, d01_xtalk.py). Board coordinates below = file coordinates minus (100, 50),
origin top-left, y down (same as the repo README).

## Summary

1. No wiring error found on this board. Every non-connector part, every jumper position (JP1-JP6) and every option link
   (R20-R22, R27-R30, R37, D3/D4) was traced through the netlist (`pcb_nets.txt`, `sch_netlist.xml`, `kb/interconnect.md`)
   and silk labels; they agree with the README jumper table and INSTALL.md. Diode polarity (D1, D2, D5 cathode = pad 1 to the
   +12 V net, D3/D4 TVS cathode to the injector wire) is right.
2. No wrong jumper setting found that can damage the board or engine. Failure modes are malfunction only (table in section 2),
   all but two already documented.
3. Ground pour: ONE connected copper network (both layers, 971 GND vias, every GND pad in it). Solved as a resistor network
   (0.2 mm raster, 35 um copper, 1.2 mOhm per via): the five harness ground pins reach all 17 JD1 ground pins in 0.37 mOhm and
   all 8 JD2 ground pins in 0.66 mOhm; worst single JD pin 1.2 mOhm. The long horizontal tracks do not cut it. Checked, correct.
4. Track widths: all fine except the battery trunk 1B -> first split: 46 mm of 0.6 mm track carries heater + logic + AUX
   current. VERIFICATION.md already says "about 20 C at 2.3 A"; with logic (0.5 A) and a J5-15 load it is 48 C (IPC-2221), and
   103 C at heater hold current plus a full 1.1 A AUX load. Documented item, but worse than stated.
5. Outline and holes: the outline matches the early Hellen NA6 board (154.13 x 161.63 vs 154.0 x 161.5) and five of the six
   M4 holes match its holes to 0.1 mm. That Hellen board has three more bosses ((4.1,19.6), (150.2,19.6), (136.7,156.7)) and
   no counterpart of H2 (137.0,7.3). The Speeduino NA6 PNP is a 100 mm board with no case holes: no hole comparison possible.
6. Connector row spacing and pitch pattern of J1 match both references (lower row y 18.13 vs Hellen 18.2; column pitch
   3.5/3.1/3.0..., 6.2 mm plug gap identical to the Speeduino 48-pin footprint). Absolute x of 1A cannot be checked (Hellen uses
   a 64-pin footprint, 6.41 mm further left).
7. MAP sensor and C1/C2/C3 match NXP's recommended decoupling (1 uF, 0.01 uF, 470 pF); pins 1 Vout / 2 GND / 3 Vs correct; it
   is not under the daughterboard; the barb is at board (108.5, 138.0) pointing -x.
8. Parts under the daughterboard are only D1/D2 (SMA), unfitted D3/D4 (SMC), R20-R22, R27-R30: far below the 11 mm gap; the
   daughterboard bottom side carries only its two 1x40 headers (cur_db `pcb_footprints.csv`: 3 bottom-side footprints).
9. Minor: JP4 puts the PRC solenoid wire on the same net as J5-4 (OUT_ALT); R28 mistake also collapses the CLT/IAT bias
   (documented only as "shorts the 5 V").

## 1. Circuit: every part, purpose, value and placement

Board netlist (VERIFIED, `kb/interconnect.md` lines 237-283, `evidence/cur_mb8995/pcb_nets.txt`).

| Ref | Value / part | Purpose | Verdict |
|---|---|---|---|
| D1 | SS34 SMA, K=VBAT_IN, A=OUT_IACV | freewheel for idle valve into its own +12 V feed | correct polarity (D_SMA pad 1 = K). Valve +12 V is the main-relay net = 1B, so the loop closes locally. Value (40 V, 3 A) ample |
| D2 | SS34, K=VBAT_IN, A=OUT_VVT | same for purge/VVT coil | correct |
| D5 | SS34, K=AUX_VBAT, A=OUT_BOOST | boost valve freewheel to J5-15 | correct if the valve is fed from J5-15 (documented). If the valve is fed elsewhere (JP6 BOOST case) the flyback current returns through F4 (PTC) to VBAT_IN: only a transient, harmless |
| D3, D4 | SMCJ30A, K=OUT_INJ1/2, A=GND, NOT FITTED | clamp only for a rev 0.9 daughterboard | with a rev 0.10 daughterboard (clamps to VBAT_IN at about +18 V) they must stay off; BOM and silk agree. Footprints cost nothing |
| F1 | 3 A hold PTC 2920, VBAT_IN -> HTR_PWR | LSU heater supply | placement fine (1.0 mm track). Datasheet derating at 85 C not re-checked here (other audit) |
| F4 | 1.1 A hold 1812 -> AUX_VBAT | J5-15 | fine; at trip (2.2 A) the 0.5 mm track runs 26 C over (IPC), 5 C at 1.1 A |
| R1 120 / R6 0R | CAN terminator + link | fine (R6 fitted, documented) |
| R2, R3 5.1k | USB-C sink CC1/CC2 | correct, one each to GND |
| R20-R22 4.7k | 12 V pull-up options for IN_SW1-3, NOT FITTED | to VBAT_IN; 48 mW at 15 V. Wrong fitting (switch that drives 12 V) = input stuck on, no damage |
| R27 4.7k | 5 V pull-up IN_AUX1, NOT FITTED | for the stock throttle switch on 2L with R29 fitted |
| R28 0R 0805 | 1N <-> V5_EXT, NOT FITTED | TPS conversion |
| R29 0R | 2L -> IN_AUX1, FITTED | stock |
| R30 0R | 2L -> IN_TPS, NOT FITTED | TPS conversion |
| R35 4.7k | flex pull-up to V5_EXT | fine |
| R36 10k | N2O pull-down | 12 V -> 1.2 mA, fine |
| R37 1k 2512 | VBAT_IN -> OUT_TACH, NOT FITTED | COP tach pull-up; 0.21 W at 14.4 V in a 1 W part. Needs hand fitting: README mentions it, parts list says hand-fit |
| C1 1u, C2 10n (V5_SENS), C3 470p (IN_MAP) | MAP supply decoupling and output filter | exactly NXP Figure 4 (datasheets/txt/C90152_MPX5700AP.txt line 206) |
| U2 MPX5700AP | MAP | pad map 1 Vout, 2 GND, 3 Vs checked against the datasheet case 867B pin list (line 270) |
| U4 USBLC6-2SC6 | USB ESD | pins 1/6 I/O1 (DP), 3/4 I/O2 (DM), 2 GND, 5 VBUS, matches ST pin table (C7519 txt line 14-16); in-line pass-through |
| JD1/JD2 | sockets | mating checked by B02 |

### Jumpers traced through the netlist (VERIFIED)

| Jumper | pin 1 | pin 2 | pin 3 | silk (VERIFIED from drawings) | 1989-93 | 1994-95 |
|---|---|---|---|---|---|---|
| JP1 | OUT_INJ2 (2V) | OUT_INJ3 | HARN_2Y (2Y) | PAIR at pin 1, SEQ at pin 3 | none | 2-3 |
| JP2 | OUT_INJ1 (2U) | OUT_INJ4 | HARN_2Z (2Z) | PAIR / SEQ | none | 2-3 |
| JP3 | HARN_1R | OUT_LS7 | HARN_2S | 90-93 at pin 1, 94-95 at pin 3 | 1-2 | 2-3 |
| JP4 | OUT_ALT | HARN_2R | - | | open | fitted |
| JP5 | OUT_TACH | HARN_2I | - | TACH COP | open | open |
| JP6 | IN_AUX3 | HARN_2O | OUT_BOOST | AFM pin 1, BOOST pin 3 | 1-2 | 1-2 |

All agree with the README table and INSTALL.md lines 93-102, 185, 241.

### Wrong-setting analysis

| Wrong setting | Result | Damage? |
|---|---|---|
| JP1/JP2 left open on 1994-95 | injectors 3/4 never fire: two cylinders unfuelled | no (malfunction; documented as "set before first start") |
| JP1/JP2 SEQ on 1989-93 with the stock two-wire harness | 2Y empty; INJ3/INJ4 fire into nothing, batch pairs still ok | no |
| JP2 SEQ on a 1989-93 automatic | INJ4 low-side pulses onto the A/T control unit wire 2Z | malfunction of the transmission unit; driver is current limited, so no board damage (documented) |
| JP1/JP2 PAIR with a rev 0.10 daughterboard and Sequential mode | each injector wire is pulsed twice per cycle (two drivers, each with its own clamp) | no damage; rich (documented in INSTALL.md "never Sequential with PAIR") |
| JP3 in the wrong position | second fan relay not driven (1R vs 2S) | no damage; overheating risk with A/C only. What 1R does on 1994-95 is UNVERIFIED |
| JP4 fitted on 1989-93 | OUT_ALT drives 2R; README says 2R not connected on 1989-93 (what else it is on the car is UNVERIFIED) | none found |
| JP4 open on 1994-95 | PRC solenoid never driven | malfunction |
| JP5 fitted with the stock igniter | ZXMS6004FF low side (60-70 V clamp, 1-2.2 A limit, design.py:268-275) drives the igniter's 2I signal | no board damage; igniter-side effect UNVERIFIED (2I direction is an open item) |
| JP6 on BOOST with the AFM connected | boost low side pulls the AFM signal wire to ground | AFM output stage tolerance UNVERIFIED; reading lost anyway |
| JP6 on AFM with a boost valve on 2O | valve never driven | none |

### Throttle-switch / TPS links (R27-R30), VERIFIED nets

- Stock: R29 fitted: 2L -> IN_AUX1; R27 (not fitted) adds a 4.7k pull-up to V5_EXT for the switch contact.
- Conversion: R28 fitted (V5_EXT -> 1N), R29 moved to R30 (2L -> IN_TPS). Correct and consistent with README.
- Warning cases traced: (a) R28 with the stock switch: V5_EXT shorted to ground at each idle, TLS115 current-limited
  (VERIFICATION.md 1157). New detail: the CLT and IAT pull-ups (2.7k) hang on V5_EXT (`scripts/design.py:385`), so the
  coolant and air temperature readings also collapse while it is shorted. README says only that the 5 V is shorted.
  (b) R30 fitted on an automatic: 2L (switch contact) and the real sensor on 2M both drive IN_TPS (documented).
  (c) R29 and R30 both fitted: 2L feeds both inputs, harmless. (d) R28 fitted without R30: wiper goes to AUX1, no TPS: harmless.
  (e) R28 fitted and the plug reversed: sensor works inverted ("calibrates the same way", documented).
- 1N/2L tracks are 0.2 mm, 14.9 mm / 129-133 mm long; irrelevant at these currents.

## 2. Track width against current (35 um, IPC-2221 external, no pour assist, VERIFIED widths from `a01_overview.txt`)

R from the track graph (a02_paths.txt) at 20 C; currents are assumptions (injector 2 x about 1.1 A peak).

| Net | width, path | I (A) | dT (C) | R | Verdict |
|---|---|---|---|---|---|
| VBAT_IN 1B trunk | 0.6 mm, 46 mm (B 11.8 + F 14 + B 20.1, series) | 2.3 heater | 21 | 38 mOhm | documented |
|  |  | 3.3 (heater + 0.5 logic + 0.5 AUX) | 48 | 125 mV drop | worse than documented |
|  |  | 4.6 (3 A hold + 0.5 + 1.1) | 103 | 174 mV | 85 C cabin + 103 C: above FR4 Tg; IPC chart is conservative and spreading helps, but there is no margin |
| VBAT_IN rest | 1.2 mm, 100-215 mm | 2.3 | 7 | | ok |
| HTR_PWR / LSU_HTR_N | 1.0 mm, 24 / 134 mm | 3 | 17 | 12 / 66 mOhm | ok (heater drop 0.2 V at 3 A on the return) |
| OUT_INJ1/2 | 0.6-0.8 mm | 1.6 rms, 2.2 max | 9 / 19 | 50 mOhm | ok |
| OUT_IACV, OUT_VVT | 0.6 | 1 | 3 | 30 mOhm | ok |
| OUT_BOOST, OUT_ALT | 0.8, 0.6 | 0.6 | 1 | 70 / 220 mOhm | ok |
| OUT_FAN/FP/AC/MAINRLY (relay coils) | 0.5 | 0.3 | <1 | | ok |
| AUX_VBAT | 0.5 | 1.1 / 2.2 trip | 5 / 26 | 30 mOhm | ok |
| V5_EXT | 0.4, up to 230 mm | 0.1 | - | 0.29 Ohm to J5-14 = 29 mV | ok |
| GND | pour both layers | 8 | - | 0.4-1 mOhm = 3-8 mV | ok |

Mechanical cause of the 0.6 mm trunk: `mb_route.py:90` `BW = min(width, 0.6)` for the escape from the harness header.
Fix idea: tap the heater branch at pad 1B on a 1.2 mm track, or widen the escape (pitch 3.0 mm, pad 1.9 mm leaves room for 1.2 mm).

## 3. Ground pour (VERIFIED by calculation)

- GND copper: 20,139 mm2 F.Cu and 20,531 mm2 B.Cu of 24,870 mm2; 971 stitching vias (0.6/0.3), one per 26 mm2; 6 + 8 small
  islands, all tied by vias into the main network (single connected component of 1,016,757 raster nodes). No GND tracks.
- DRC (KiCad 9) reports 2 `starved_thermal` errors (JD1 pads 38 and 39, F.Cu: spokes land on an isolated island). Both
  pads are still joined on B.Cu and by vias, solver confirms: cosmetic.
- Resistance (35 um, 0.2 mm raster, 1.2 mOhm per via barrel): 5 harness ground pins to all JD1 GND pins 0.37 mOhm, to all
  JD2 GND pins 0.66 mOhm, to one JD pin 0.6-1.2 mOhm, to the M4 holes 0.6-1.1 mOhm, to J5 grounds 2.9 mOhm, to J4 0.95 mOhm.
- Loop areas: the heater loop is large (supply from F1 at (44,143), return on a 134 mm track from JD2.37 at about x 110-126
  to J2 at (22,150)); the ground return is the plane. Crosstalk scan (d01_xtalk.py): no LSU, MAP, knock or VR track
  runs within 0.6 mm of a switching net for more than 6 mm; worst: IN_TPS 42 mm beside OUT_FP (relay coil, slow) at 0.45 mm.

## 4. USB, MAP, connectors, parts under the daughterboard

- USB: DP 58-62 mm, DM 57-58 mm, 0.2 mm, one layer change each; skew 3.8 mm irrelevant for full speed. U4 taps both lines
  5 mm before J4. VBUS 0.4 mm (0.3 at the connector). Shell and A1/A12/B1/B12 on GND.
- MAP U2 (rot 90, at (124,142)): body x 108.6-141.8, y 126.9-157.1; holes (127.8,130.4) and (127.8,153.6); leads at x 140.5.
  Not under the daughterboard (its lower edge is y 118, HD4 crtyd y 110-117; lateral gap 8.9 mm). Barb axis y = 138.0, tip x = 108.5
  pointing -x (INFERRED from footprint polygon rotated by 90 deg). A hose to the case's bottom-edge cut-out must bend 90 deg
  inside x 94-108; J5 (x 59.9-94.1, y 123.5-134.5) and F1 (x 41-47, y 138-148) block a straight run left. INSTALL.md gives no
  cut-out position.
- Edge overhang (courtyards): J1 body y -7.6 (7.6 mm past the top edge, by design), J2 +0.5 mm and J4 +0.3 mm past the bottom
  edge (y 161.5); bottom strip is x 14-140, J2 x 19-30, J4 x 74.6-85.4: inside.
- Under the daughterboard (x 14.5-139.5, y 42-118): D1/D2, D3/D4 (unfitted), R20-R22, R27-R30, JD1/JD2 sockets only.

## 5. Outline and holes against the proven boards (VERIFIED by pcbnew)

| | ours | Hellen NA6 old (a/b) `old/hellen64_miataNA6_94.kicad_pcb` | Hellen NA6 -d / -c |
|---|---|---|---|
| bbox | 154.0 x 161.5 | 154.13 x 161.63 | 154.2 x 159.2 |
| holes (rel. to its own bbox corner) | H1 (17.0,7.3) H2 (137.0,7.3) H3 (4,84) H4 (150,84) H5 (4,143) H6 (150,143) | (17.06,7.36) (4.06,84.06) (150.06,84.06) (4.06,143.06) (150.06,143.06) plus (4.06,19.56) (150.17,19.56) (136.66,156.65) | (5.1,5.2) (5.1,87.2) (5.1,154.0) (149.1,5.2) (149.05,87.2) (149.1,154.0): a different layout |
| harness lower row y | 18.13 | 18.2 | 21.5 |

Header columns: ours 1A at 39.70; Hellen-old pad 1 at 33.29 (64-pin 22+16+26 footprint, 3rd plug 32.9 mm after plug 1).
Ours: 1U -> 2A gap 6.2 mm, same as the Speeduino 48-pin footprint (`NA6 v1.3.kicad_pcb` J1, pads 14.. at 3.1/6.2 mm), and the
3.5/3.1/3.0 pattern matches both. Speeduino NA6 PNP: 100.05 x 100.05 mm, only the three header-post holes and two MAP holes.
H2 provenance (microRusEFI J28) is not in `ext/`: UNVERIFIED. Possible issue: three bosses present on Hellen's board are
unsupported here (no hole); not a fit failure unless the bosses are taller than 1.6 mm FR4.

## Sources actually read

the review brief; repo/motherboards/1989-95/README.md, INSTALL.md (jumper lines), scripts mb_na6.py, mb_y9495.py, mb_route.py lines
25-100, design.py 80-125, 268-300, 330-370, 385, 490; kb/interconnect.md 184-283; evidence/cur_mb8995 pcb_pads.csv,
pcb_footprints.csv, drc_kicad9.json, fab BOMs; mb.json and earlier scratch outputs (a01/a02); datasheets/txt C90152, C7519,
C22446884; ext/hellen-miata-NA6 old and -d PCBs, ext/speeduino-hardware NA6 v1.3 PCB; repo/VERIFICATION.md lines 670-700,
1157; evidence/cur_db pcb_footprints.csv.

## Not checked

- Stock case geometry itself (no CAD): H2 and the three Hellen bosses cannot be confirmed.
- What cavities 1R (1994-95), 2R (1989-93), 2O, 2I do on the real cars; AFM signal-pin source impedance.
- Firmware behaviour for batch mode with JP1/JP2 open (B-firmware audits).
- PTC hold derating at 85 C, TE contact current rating of pin 1B.
- Hose exit position (no case cut-out drawing).
- mb_gnd_islands.py / mb_tvs_copper.py were only skimmed; island result re-derived from the filled zones instead.
