# R30: Audit and extension of the repo survey of other Miata plug-in boards

Date 2026-11-16. Primary sources read today: the KiCad netlists (XML) and BOM-replace files of ext/hellen-miata-NA6 (rev d), NB1 (rev c), NB2 (rev f), a shallow clone of rusEFI's 1996-97 board (hellen-miata-NA8 rev A, cloned to work/.../web/na8), ext/hellen-one module BOMs and schematic images (output 0.3, input 0.1), the Speeduino NA6 v1.3 PCB (pcbnew dump) and BOM xlsx, rusEFI's own pin tables (repo/firmware/ext/rusefi .../hellen/hellenMiata*/connectors/main.yaml), the rusEFI wiki pages (raw), the Diodes ZXMS6005SG datasheet, live JLC lookups. Web search for closed boards (MSPNP/AMP, ME221, Link) gave only titles; the maker pages were not re-read (HTTP 403/429, or the page says nothing on the topic) so those survey rows are UNVERIFIABLE today.
Evidence files: kb/research/files/R30/ (net lists na6/na8/nb1/nb2, NA8 bom replace, ZXMS6005SG datasheet, NA96 wiki page). Scratch: work/R30-other-miata-boards-audit/.

## Summary (10 lines)
1. The survey's table row "Hellen output module 0.3: AUIPS2041L" is WRONG for the Miata boards: all four Hellen Miata BOM-replace files swap Q305-Q312 (injector drivers) for ZXMS6005SGTA (C174042; clamp 60/65/70 V, 480 mJ, current limit 3.3-7 A at 5 V gate, 2.2-5 A at 3 V). VERIFIED.
2. "Nobody uses the suffix-7 STM32" is WRONG: Hellen NB1 rev c and NA8 rev A are built with STM32F407ZGT7 (C1337111, -40..105 C, JLC extended, stock 34, USD 27.80 at qty 1 vs 6.26 for the T6). VERIFIED.
3. "Nobody puts two drivers on one wire" is true for the default build but incomplete: the Hellen NA6 frame has DNP 0-ohm footprints R12/R17 that tie INJ1+INJ3 and INJ2+INJ4 outputs together (with R26/R25 to separate pins). VERIFIED.
4. rusEFI has a 1996-97 board (hellen-miata-NA8, "Hellen NA96", rev A only, wiki says "somewhat abandoned"); the survey does not mention it. Speeduino has only an NA6 (1989-95) PNP in its hardware repo; no Speeduino NB board found.
5. Most Hellen/Speeduino/project function circuits are the same topology (idle flyback Schottky to +12 V on the board, 1k pull-up to +12 V on the 1989-95 tach, fan/A-C/CEL/pump low sides). The motherboard pin map of this project follows the rusEFI Hellen pin names (rusEFI "3x" = this project's "2x" on 1989-95).
6. Real deviations from ALL proven boards: per-injector diode+TVS clamp to battery (improvement, cost, thermal/stock risk); level-shifted 5 V gate drive; AEM JST-PUD wideband harness connector; protected ignition outputs (100R + Schottky + pull-down); no tach default on 1989-95 (safer).
7. Deviations where the project is the odd one out and the risk is the project's: tach and alternator outputs on 1996-2005 are open-collector with no pull-up, where Hellen NA8/NB1/NB2 drive them push-pull (12 V) from PP2/PP1.
8. Pull-ups on trigger inputs: Hellen crank 680 k (module) + LED path, cam 4.7 k to 5VA; Speeduino 1 k to +5V, 220R series, SP720; project 1 k to protected 5 V via Schottky pair, 4.7 k series. Project matches Speeduino.
9. Pin-table conflicts between rusEFI's NB1/NA8 tables and the project's maps (1999-2000 1U, 3Q; 1996-97 3M/knock) are unresolved here; they need the Mazda wiring diagram.
10. Nothing was measured; no board built by anyone in this review.

## Part A. Claim-by-claim audit of repo/research/other_miata_pnp_boards.md
Legend: C correct, W wrong, P partly, U unverifiable today.

| # | Statement | Verdict | Evidence |
|---|---|---|---|
| 1 | Hellen64 NA6 uses STM32F407ZGT6 (parts list) | C | ext/hellen-miata-NA6/bom_replace_hellen64_NA6_94-d.csv: `U105,"STM32F407ZGT6","LQFP144","C19156"` (JLC: -40..85 C, ext., stock 389, USD 6.26@1) |
| 2 | Hellen72 NB2 uses STM32F407IGT6 | C | ext/hellen-miata-NB2/bom_replace_hellen72_NB2-f.csv `C33993` |
| 3 | uaEFI uses F429VIT6 on a processor module | U | ext/hellen-one/modules/uaefi has only the carrier BOM (UAEFI_BRD); the MCU module was not opened |
| 4 | Speeduino NA6 PNP: Mega 2560 plugged onto the board | C | BOM XA1 "Arduino_Mega2560 header pins"; PCB XA1 5V pads |
| 5 | "Every STM32 in the open designs is the suffix-6 part ... Nobody found uses suffix-7" | W | hellen-miata-NB1 bom_replace_64_NB1-c.csv and hellen-miata-NA8 bom_replace_64_NA8_96-a.csv: `U105,"STM32F407ZGT7","LQFP144","C1337111"`; tools/lcsc.py C1337111: -40..105 C, extended, 34 in stock, USD 27.80 @1 |
| 6 | Link / ME221 / AMP temperature ratings, "none found" for AMP | U | maker PDFs not re-read today |
| 7 | Speeduino NA6 v1.3: two VNLD5090 (dual), four channels for injectors | C | PCB: U2 = INJ-1/INJ-2-OUT, U4 = INJ-3/INJ-4-OUT. (Four VNLD5090 on the board: U7 = idle + boost, U9 = fan + tach jumper.) |
| 8 | Speeduino: no clamp parts outside the driver; the diodes feed the indicator lights | C | D5/D6/D9/D10 (1N4448WX) from INJ-n-OUT to LED nets (Net-(D3-Pad1)...). Idle/boost/fan have real flyback diodes D15/D16/D17 (NBRS2H100T3G, 100 V 2 A) to 12V-SW |
| 9 | VNLD5090/VNL5090 clamp 41 to 52 V | U | ST datasheet not read today |
| 10 | Speeduino puts 1 k in series with each driver input | C (inferred) | U2 pin1 = Net-(R5-Pad1), BOM R5 = 1k (RC0805FR-071KL) |
| 11 | "Hellen (output module 0.3): AUIPS2041L in SOT-223" for the Miata boards | W (true only of the generic module) | Module BOM output-0.3: Q305-Q312 AUIPS2041LTR C113610, but every Miata board file replaces them with ZXMS6005SGTA (NA6-d, NB1-c, NB2-f, NA8-a). Datasheet (kb/research/files/R30/ZXMS6005SGTA_C174042.pdf): VDS(AZ) 60/65/70 V at 10 mA, clamping energy 480 mJ, ILIM 2.2 (min, 3 V gate) / 3.3 (min, 5 V gate), RDS(on) 150 typ / 200 max mOhm |
| 12 | "the part is listed at 1.4 A, less than two 12-16 ohm injectors draw" | W for the shipped boards | ZXMS6005 limit is 2.2-3.3 A min. Two 12 ohm injectors at 14.4 V = 2.4 A peak: above the 2.2 A minimum at a 3 V gate (INFERRED: the Hellen gates are driven straight from the 3.3 V MCU net with a 10k pulldown, R304-R306 module schematic), below 3.3 A at 5 V. So even Hellen would be near its limit on paired wiring at 3.3 V gate, worst-case part |
| 13 | Freewheel diodes only on general-purpose outputs on Hellen | P | Output module: ULN2003 COM to V12FLYBACK (PSM712 TVS clamp), D301/D302 B5819W on LOW6_DIODE and LOW5_MAIN. NA6 frame: idle has D25 B5819W to +12V_PROT; ECF, pump, CEL have 1N4148 in their LED branches only; injector diodes D12-D15 are LED branches. NB2: idle D36, VVT D35 (B5819W), VICS on NB1 D31 |
| 14 | One injector per driver on Hellen, four outputs to 3U 3V 3Y 3Z | C, with caveat | NA6 nets: OUT_INJ1 -> P2.49 (3U), INJ2 -> 3V (P2.62), INJ3 -> R26 -> 3Y, INJ4 -> R25 -> 3Z. R12 (INJ1-INJ3) and R17 (INJ2-INJ4) are DNP jumper footprints: a paired option exists |
| 15 | "Nobody puts two drivers on one wire" | P | see 14: default no, option yes on NA6 |
| 16 | Hellen wideband: on board LSU 4.9, owner wires connector + 12 V | C | NA6 nets WBO_H-/Ip/Vs/R_Trim to options pads 2C,2F,2H,2E; wiki option port table (2D +12 V) ; NA8 options port 4G-4L |
| 17 | Hellen 1990-95 | C | wiki: "Plug-and-Play for NA6 and 94-95 Miatas" |
| 18 | Speeduino one VNLD5090 channel per pin (2U 2V 2Y 2Z), paired layout 2 squirts | P | channel per injector verified (INJ-1..4-OUT each a channel); base tune and firmware not re-read |
| 19 | AMP/ME221/Link rows, quoted forum posts, "'93 California" statement, MegaSquirt advice | U | not re-fetched (403/429 or no content) |
| 20 | Molex 47219-2001 is the card socket rusEFI boards use (audit A5) | C | ext/hellen-one/modules/sd/0.1 BOM: "Molex MicroSD 47219-2001" C164170 |
| 21 | FOME wideband heater driver has 1 k (audit A1) | P | hellen-one wbo 0.3 BOM: Q600 BTS3028, R600/R601 1k; NB2 replaces Q600 with VND14NV04TR-E (C2649436). mck1117 module not re-opened |
| 22 | Survey omits 1996-97 | gap | hellen-miata-NA8 exists (rev A, Hellen NA96, wiki "somewhat abandoned", issue tracker hellen-NA8-96-issues). Same ZXMS6005 injector part, F407ZGT7, PP2 push-pull tach |
| 23 | Survey says Speeduino board "NA6 PNP" (1989-93 in one search snippet) | note | Speeduino manual title "Miata/MX5 89-95 NA6 PNP"; BOM file "NA 8995 v1.3"; connector 174917-1 (this project: 174917-6, different dash number) |

## Part B. Function by function

Project side from kb/interconnect.md and repo/motherboards/*/README.md. Cavity names: rusEFI table "3x" = project "2x" on 1989-95 (3U=2U injector 1, 3W=2W idle, 3T=2T pump, 3I=2I tach, 3E/3G=2E/2G crank/cam, 3P/3Q=2P/2Q IAT/CLT, 3S=2S condenser fan). Section 1 names are the same. This offset was checked cavity by cavity for 20 functions and agrees; the project says it followed the Hellen NA6 map.

| Function | Hellen (part level) | Speeduino NA6 v1.3 | This project | Deviation? |
|---|---|---|---|---|
| Injector drive | module output 0.3: ZXMS6005SGTA SOT-223 (replace file), 10k gate pulldown, gate from 3.3 V MCU net, no external clamp, LED+1N4148 indicator only. NA6 frame R26/R25 0R to 3Y/3Z; DNP R12/R17 for paired | VNLD5090-E dual, 1k to input, clamp inside, no external clamp; 1 channel per injector | VND7NV04 (DPAK, 150R min series needed; ordered rev 0.9 lacks it), 5 V gate via SN74LVC4245A, per-injector ES1D + 1.5SMC16A to battery (rev 0.10); 1989-93 one driver per wire (JP1/JP2 open) | Yes: clamp and driver are unique. Improvement: turn-off energy 8.8 mJ vs 15.3 mJ in the driver (repo sim); cost: 8 parts + 0.16 ms slower closing; risk: TVS 150 C grade, JLC stock, untested |
| Coil drive | ign8 module 0.2: SN74LVC4245 + 10R in series per channel, logic-level 5 V to the stock coil igniter; no protection | TC4424A + 2.4k pulldown | TC4427 + 100R + B5819W, ZXMS6004FF pulldown, 3.3k pulldown (rev 0.8) | Yes, more protection than either. Improvement for wire-to-battery faults; cost ~12 parts; risk: edge/drive timing never tested on a coil |
| Idle valve | injector-class low side (INJ7) + B5819W (1 A, 40 V) from drain to +12V_PROT on the board (NA6 D25, NB1 D25, NB2 discrete MOSFET Q2 + D36); NB2 idle + from 4AF | VNLD5090 ch + NBRS2H100T3G (2 A 100 V) from 12V-SW to IDLE-OUT | VND/ZXMS low side + SS34 (3 A, 40 V) to VBAT_IN (D1); NB2 adds 2 A fuse F2 on IAC +12 V | No (same topology). Differences: SS34 is stronger than Hellen's 1 A part; the NB2 feed fuse is the project's own (cost: 1 part; risk: nuisance blow or none) |
| Fans | ECF on LOW1 via ULN2003, "For 1994+" jumper R33 to 1L, "For 1990-1993" DNP R58 to 1R; condenser fan on 3S via INJ5 driver (R44) | FAN-OUT on VNLD5090 + D17 | OUT_FAN on 1L; spare low side OUT_LS7 to 1R (90-93) or 2S (94-95) through JP3 | Equivalent. Hellen moves the one fan function between 1L and 1R by jumper; project keeps the fan on 1L and needs firmware to put the fan function on LS7 for 1990-93 (check INSTALL) |
| A/C | request input (1Q) into input module: 4.7k series, SRV05-4 ESD, 10k pull-up to 5VA (PULL_AUX3 via M1.J8 to +5VA), relay output LOW8_HIGH2 with PJM2319 + 4.7k switchable pull-up to 12 V (1J) | "AC-Jump": harness pins J1.9 and J1.29 bridged on the board, ECU does not interpose | IN_SW2 with 4.7k to VBAT, 22k/10k divider to 3.3 V; OUT_AC protected low side | Yes vs Speeduino (no control), differs from Hellen in the input level: project treats the switch as 12 V signal, Hellen 5 V pull-up with clamp. Both read a 12 V high through their divider/clamp (INFERRED). A/C logic is firmware in both |
| Fuel pump | LOW9 ULN2003 channel with LED+1N4148; pull-up options | not traced (U8 VN5160S-E high-side on 12V-SW with ST_Sig; function not confirmed) | OUT_FP protected ZXMS6004FF | Improvement (current limit) vs ULN2003 |
| Tach 1989-95 | NA6: LOW12 ULN2003 channel, 1k (R21) + 0R jumper R27 to +12V_PROT, 0R R48 to 3I; all jumpers fitted by default | VNLD5090 (U9) channel, R53 1k to 12V-SW, jumper JP1 to J1.16 | OUT_TACH low side + R37 1k (2512) to VBAT_IN, JP5 "TACH COP" to 2I; ships with tach off | No deviation in circuit. Hellen drives it by default: if 2I carries the igniter's tach signal it would fight it. Project's default off is safer (improvement); the question of direction is open for all three (rusEFI wiki says input) |
| Tach 1996-2005 | NA8, NB1, NB2: PP2 push-pull (TC4427, VCC_PP from +12V_PROT via R310; R309 removed in every BOM-replace file) | n/a | open-collector low side, no pull-up (no R37 on 96-97 / 99-00 / 01-05 boards) | Yes, RISK: unknown whether the cluster input idles high without a driver |
| Alternator (NB) | NB1/NB2: PP1 push-pull output (NB2 via R23/C21 to 3M) and a separate alternator-lamp low side (LOW12) | n/a | OUT_ALT low side to the NB wire, firmware off; may need pull-up (repo says so) | Yes, risk (same cause as tach); repo already documents the doubt. Hellen's push-pull is the proven choice |
| VVT | NB2: discrete Q1 (IN R28, 4R) + D35 B5819W to the 12 V feed 4D; NB1 pin table also lists 4E VVT | n/a | OUT_VVT low side + SS34 (D2) to OCV_12V (2 A fuse F3) | No. NB1 table conflict, see Part C |
| O2 heaters (front/rear) | NB1: front O2 heater 1U, rear 3V; NB2 rear heater 3P; no driver (pins only in tables); the board's own LSU heater is in the wbo module | none | not driven (open) | None; all leave the stock narrowband heaters to the car (INFERRED from empty rows) |
| Check-engine | LOW6_DIODE ULN2003 channel + 1N4148 in LED branch (1E; NB2 2R) | none/LED | ZXMS6004FF driven from MCU pin directly (rev 0.10) | Improvement (fatal-error lamp), small |
| MAP | NA6: MPX4_MAP + MPXH6400A + LPS25HB baro on the frame; NB: internal MAP option | MPX4250AP (+ KP234 footprint) | MPX5700AP (NRND, documented) | Different range (700 kPa vs 250-400): resolution cost, supply risk. LOW |
| Intake temp / CLT | input module 4.7k pull-up to 5VA (PULL_IAT, PULL_CLT), 4.7k series + ESD | R23 470R + ADC clamps SP720 | 2.7k from the protected 5 V, 5.6k series, Schottky clamp | Different bias value (firmware table must match). Not an error in itself |
| TPS | 680k (module PULL_TPS) i.e. effectively none | direct | none | no |
| Crank / cam | see below | | | |
| Knock | NA6: knock module (MCP6002) on options pad 2P/P1; NB: harness pin 2F (NB1), 4M (NB2) | none | amplifier on daughterboard; harness 2F (99-00), 4M (01-05); no harness pad on 1989-97 | No on NB. 1989-97 has no knock cavity in the project (rusEFI NA8 table lists a knock pin: see Part C) |
| Diagnostics | NB1 3S EGR, NB2 3Q K-line, 3S immobiliser, 4E DTM named in the pin table; no K-line transceiver on the frame netlists | none | pins left open | no |
| Main relay | NB2 LOW5_MAIN output (R48), 12V permanent 4AG (+12V_PERM into power12 module) | n/a | OUT_MAINRLY to J5 only; 4AG not connected | Project documents it |

### Trigger inputs (crank / cam)
- Hellen NA6 (netlist): input module chain per input: 4.7k series (R200..R205 4.7k array), SRV05-4 ESD (C85364), 1 n / 10 n / 100 n filter caps. Pull-ups through solder-jumper nets PULL_x to +5VA: PULL_CRANK to +5VA through module's 680k (R206), PULL_CAM not connected on the module (J17 floating) but the frame fits R3 4.7k from +5VA to IN_CAM. Crank and cam each also have 0R R14/R15 into a white LED + 1N4148 antiparallel pair to a 4.7k array to +5V (indicator, doubles as a clamp to +5V through 4.7k). So: cam 4.7k pull-up, crank 680k. NB1/NB2 frames have the same R3/R14/R15 structure.
- Speeduino: R35/R36 220R series, SP720 ESD/clamp array, R33/R34 1k to VDD (+5 V board rail), JP2 moves crank to a second J1 pin (J1.38).
- Project: 1 k pull-up (protected sensor 5 V through D35 common-anode Schottky pair), 4.7k series, 1N4148 clamp to 3.3 V (README rev 0.7/0.8). Matches Speeduino's 1 k and is stronger than Hellen's. Risk the project already notes: 88 mW in the 1 k on a wire shorted to 14.4 V.

### Idle valve flyback path
All four: low-side switch on the board and a Schottky from the switched node to the +12 V supply, on the board (not through the driver clamp). Hellen's supply is +12V_PROT (after F-fuse and reverse diode), Speeduino's 12V-SW (after reverse Schottky D12), project's VBAT_IN (before F1/F4, after the harness). The project's choice sends the flyback current into the unfused battery side, which is correct (no reverse-protection diode between the harness and the diode); on Hellen the current returns through the same node the valve is fed from.

### Tach on 1989-95
VERIFIED: Hellen NA6 and Speeduino both drive it as output through ~1 k to +12 V; the project does too but ships off. UNRESOLVED: direction (rusEFI wiki lists input). All three share the same open risk; the project's default-off is the only one that is safe by default.

### A/C and fan logic
Hardware only: Hellen uses output module low sides + condenser-fan driver and has an A/C request input; Speeduino hardwires A/C through (AC-Jump); project like Hellen. All logic (compressor lockout, fan on A/C) is firmware in rusEFI; nothing on any board enforces it.

## Part C. Pin-table conflicts to check against the Mazda wiring diagram (UNVERIFIED, both sides are claims)
- 1999-2000 (NB1): rusEFI table: 1U = front O2 heater, 3Q = VICS solenoid, 4E = VVT. Project mb9900: 1U = OUT_VVT, 3Q = OUT_MAINRLY (J5.5). The 1999-2000 engine has no VVT; rusEFI's own NB1 netlist routes VICS (INJ8, D31) to 3Q and VVT (INJ5, D32) to 4E. If rusEFI is right, the project drives the front O2 heater cavity with a VVT output and has the main relay on the VICS wire. Needs the 1999-2000 wiring diagram.
- 1996-97 (NA8): rusEFI table has a knock input at 1S (ts_name "2M - KNOCK"); the project leaves 1S/3M-knock without a pad and routes OUT_VVT to 3M. Project 3M = rusEFI 2M by the offset rule. Needs the 1996-97 wiring diagram.
- 1989-95 fans: Hellen puts the fan relay on 1R for 1990-93 ("For 1990-1993" jumper R58) and 1L for 1994+; project has both reachable via 1L/1R and JP3. Consistent if the firmware maps the fan to the right output.

## Implications for this project
1. (high conf, medium sev) Correct the survey: Hellen Miata boards use ZXMS6005SGTA for injectors; NB1 and NA8 use STM32F407ZGT7. Documentation only; no board change. The "everyone uses the 85 C part" argument for keeping the F407VGT6 is weaker: two proven boards pay USD 21 more for the 105 C part. JLC: VGT7 equivalent not priced here. Decision remains the owner's; the cost of the 105 C grade is about USD 20 per board on the Hellen sibling part.
2. (medium conf, medium sev) 1996-2005 tach/alternator outputs: Hellen drives them push-pull at 12 V; project open-collector without pull-up. Adding a 1k pull-up to VBAT (as R37 on 1989-95) or a push-pull option costs ~USD 0.02 per pad; evidence of the cluster input type missing (UNVERIFIED). Firmware: tach default off on these years would be safer.
3. (medium) Resolve the 1999-2000 and 1996-97 pin conflicts (Part C) before first power-up, since a wrong output on 1U (heater) or 3Q could damage a stock circuit.
4. (medium) Injector drive: proven boards survive on a 60-70 V self-clamping driver with no external clamp; the project's per-injector clamp is its own: keep only if the 8.8 vs 15.3 mJ simulation is trusted. Option: ZXMS6005SGTA is 18 in JLC stock (extended, USD 1.17@1): not a drop-in alternative.
5. (low) Document that rusEFI's NA6 frame has a paired-injector option (R12/R17), correcting "nobody".
6. (low) Pull-up on cam/crank: project 1 k equals Speeduino and is stronger than Hellen: keep.
7. (low) MPX range and IAT bias differ from proven boards: confirm firmware tables.

## Sources actually read
ext/hellen-miata-NA6/{hellen64_NA6_94.xml, bom_replace_hellen64_NA6_94-d.csv, README.md, revision.txt}; ext/hellen-miata-NB1/{hellen64_NB1.xml, bom_replace_64_NB1-c.csv}; ext/hellen-miata-NB2/{hellen72_NB2.xml, bom_replace_hellen72_NB2-f.csv, connector-mapping.txt}; https://github.com/rusefi/hellen-miata-NA8 (shallow clone: hellen64_NA8_96.xml, bom_replace_64_NA8_96-a.csv); ext/hellen-one/modules/{input/0.1, output/0.3, ign8/0.2, sd/0.1, wbo/0.3} BOMs and schematic PNGs; ext/speeduino-hardware/PNPs/Miata NA6/Latest ({NA6 v1.3.kicad_pcb via pcbnew, BOM xlsx}); repo/firmware/ext/rusefi/firmware/config/boards/hellen/hellenMiata{NA6,NA96,NB1,NB2}/ (connectors/main.yaml, board_configuration.cpp); https://raw.githubusercontent.com/wiki/rusefi/rusefi/Hellen64-Miata-NA6-94.md and Hellen-NA96.md; Diodes ZXMS6005SG datasheet (LCSC copy C174042, 8 pp.); tools/lcsc.py for C174042, C1337111, C19156; kb/interconnect.md; repo/daughterboard/README.md, repo/motherboards/{1989-95,2001-05}/README.md, repo/VERIFICATION.md (tach lines).

## Not checked
- Closed boards (MSPNP/AMP, ME221/ME442, Link MX5X): maker pages not re-read (403, 429 or silent on the topic).
- Speeduino NB/other community Miata boards: none found; one search only.
- VNLD5090 clamp voltage and the AUIPS2041L datasheet; Speeduino base tune/firmware squirt settings; rusEFI forum quotes; uaEFI MCU.
- Mazda wiring diagrams for the Part C conflicts; what Speeduino U8/ST_Sig does.
- Whether Hellen's crank pull-up (680k + LED path) works on a real Miata CAS; I could not tell if the NA CAS has its own pull-up.
- No board was built or measured.
