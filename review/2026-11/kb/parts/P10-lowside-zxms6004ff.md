# P10 - ZXMS6004FF protected low-side switches Q9-Q19 (daughterboard)

## Summary
1. Part: C95063 = ZXMS6004FFTA (Diodes), SOT-23F, EXTENDED, stock 13,869, $0.4386 @30 / $0.3846 @100 (live lcsc.py today). 11 per board = $4.82 @30. Manifest matches (VERIFIED).
2. Pinout settled from the Diodes pin drawing (p.1 image) + JEDEC TO-236 numbering: pin1 = IN, pin2 = S, pin3 = D. All 11 instances on cur_db and ord_db: pad1 = *_G / *_SNK, pad2 = GND, pad3 = OUT_* (harness). Schematic netlist pinfunction IN/S/D agrees. CHECKED, CORRECT.
3. Footprint is stock KiCad SOT-23 (pads 0.6 x 1.475, 1.9 pitch, rows 1.875 apart, outer span 3.35); Diodes suggests 0.8 x 1.11, outer span 3.0 -> larger pads, fine.
4. Drive: 5 V (U12 A-port, or 74HCT04 U13 for Q16-19) is inside VIN 0..5.5 (abs max 6 V); CEL (Q13) gets 3.3 V via 1k (R160, rev 0.10) = about 3.15 V at the pin vs VIH min 3.0 V: thin spec margin but part still on (Rds 0.6 ohm max at 3 V). Ordered rev 0.9 drives CEL through U12 (5 V) - no R160.
5. Loads are 0.1-0.4 A: dissipation < 0.15 W, Tj rise < 45 K even with the poor drain copper -> fine at 85 C. Clamp energy of relay coils (about 2-6 mJ INFERRED) vs 90 mJ rating: fine.
6. Ignition: spark (falling) edge is set by R144-147 3.3k + line capacitance (about 1-5 us = 0.04-0.2 deg at 7000 rpm), not by the 5 us td(on); dwell-start (rising) edge is delayed by td(off) 45 us typ + part of 15 us fall = 45-60 us (1.9-2.5 deg at 7000 rpm, but only shortens dwell by 1-2 %; matters only if the igniter fires on a rising edge). Datasheet gives only typical times, no min/max, no temperature data.
7. Output shorted to battery: limit 1-2.2 A -> thermal shutdown cycling (VDS(SC) 36 V OK at 24 V). Datasheet note 9: not for extended overtemperature. Q16-19 are ON in idle, so a shorted ignition wire cycles continuously.
8. Cost: no sensible cheaper drop-in. Only basic candidates are 2N7002 / AO3400A (30 V, no protection). Saving at most about $4.3/board, loses the short-circuit protection the repo added deliberately. Keep.

## 1. Identity
- kb/parts_manifest.md line 47: Q9..Q19, C95063, ZXMS6004FFTA, Diodes, "SOT-23F", EXTENDED. lcsc.py today: JLC stock 13,869, tiers (1,0.6006)(10,0.4926)(30,0.4386)(100,0.3846)(500,0.3535)(1000,0.3371); LCSC similar. VERIFIED.
- Same MPN, correct variant (non-Q, commercial). Q-suffix automotive twin C508259 ZXMS6004FFQTA is $1.16@1 / 309 stock (not worth it). Footprint name in design is SOT-23 (pads identical to SOT-23F land).
- Datasheet in datasheets/C95063_ZXMS6004FFTA.pdf is Diodes DS33609 Rev 9-2 April 2022 (manufacturer, current). No extra download needed.

## 2. Datasheet digest (DS33609 Rev 9-2)
- Function: 60 V self-protected low-side N-MOSFET (IntelliFET), logic-level input, active-clamp overvoltage, current limit in saturation, thermal shutdown with auto-restart, ESD input.
- Abs max (p.3): VDS 60 V; VDS(SC) (short-circuit protection) 36 V; VIN -0.5..+6 V; IIN limited to 2 mA outside -0.2..6 V; IDM 2 A (3.3 V) / 2.5 A (5 V); IS 1 A; EAS 90 mJ (Tj 25 C, 0.5 A, 24 V); ESD HBM 4 kV, CDM 1 kV; PD 0.83 W (15x15 mm 1 oz Cu, RthJA 150 C/W) / 1.5 W (50x50 mm 2 oz, 83 C/W); RthJC 44 C/W (to drain pins); Tj -40..150 C.
- Recommended (p.3): VIN 0..5.5; VIH >= 3 V; VIL <= 0.7 V; TA -40..+125; VP (load supply) <= 36 V.
- Electrical (p.5): clamp 60/65/70 V @10 mA; IDSS <= 0.5 uA @12 V, 1 uA @36 V; VIN(th) 0.7/1/1.5 V; IIN 60 typ/100 max uA @3 V, 120/200 @5 V, 220 uA max in over-temperature; RDS(on) 400/600 mOhm typ/max @3 V 0.5 A, 350/500 @5 V; ID(LIM) 0.7 min / 1.7 typ @3 V, 1.0 / 2.2 @5 V; td(on) 5 us, tr 10 us, td(off) 45 us, tf 15 us (typ, VDD 12 V, 0.5 A, VGS 5 V; no min/max, no temperature data); thermal trip 150 min/175 typ, hysteresis 10 C.
- Pin table SOT23F (p.1 "Top view pin out" image, p.8 outline): single lead on one side = D; two leads on the other side: S and IN. By TO-236 convention (pins 1,2 on the two-lead side, 1 at the end next to... counter-clockwise) -> 1 = IN, 2 = S, 3 = D. The Diodes sheet draws no pin numbers; the convention is the only assumption (INFERRED, high confidence; repo's earlier cross-check with two KiCad symbols agrees).
- Package (p.8): lead span E 2.3-2.5, body 2.9 x 1.65, pitch 0.95, e1 1.90. Suggested pad: C 0.95, X 0.80, Y 1.110, Y1 3.000.
- External parts: none required. Input has no series R requirement; keep input pulled low when driver is Hi-Z (done by RN2/RN3 10k).
- Warnings: current limit only acts in saturation; part "not designed to withstand overtemperature for extended periods" (note 9); linear-mode capable; Rds and power limited by package/board thermals.

## 3. Usage audit
### 3a. Pad table (cur_db and ord_db identical; evidence/*/pcb_pads.csv, pcb_nets.txt; sch_netlist.xml pinfunction IN/S/D; repo/scripts/design.py:268-322)
| Q | pad1 IN | pad2 S | pad3 D (harness) | load | result |
|---|---|---|---|---|---|
| Q9 | FP_G (U12.10, RN2.1) | GND | OUT_FP -> J1.6 | fuel pump relay | OK |
| Q10 | MAINRLY_G (U12.9) | GND | OUT_MAINRLY J1.7 | main relay | OK |
| Q11 | AC_G (U12.8) | GND | OUT_AC J1.8 | A/C relay | OK |
| Q12 | FAN_G (U12.7) | GND | OUT_FAN J1.9 | fan relay | OK |
| Q13 | CEL_G (R160, RN3.1) cur; U12.6 ord | GND | OUT_CEL J1.10 | check-engine lamp | OK |
| Q14 | TACH_G (U12.5) | GND | OUT_TACH J1.11 | tach (89-95: JP5 + R37 1k to VBAT_IN) | OK |
| Q15 | LS7_G (U12.4) | GND | OUT_LS7 J1.12 | spare / FAN2 (JP3.2 on 89-95; J1.1B/1I/2C on others) | OK |
| Q16-19 | IGNn_SNK (U13.2/4/6/8 = 74HCT04 outputs) | GND | OUT_IGNn J1.14-17 (+D3n source Schottky, R144-147 3.3k) | ignition logic outputs | OK |
Motherboard side (evidence/*mb*/pcb_nets.txt): OUT_* nets go only to harness cavities / JP3 / JP5 / J5; no flyback diodes on any motherboard.
Gate drive facts: U12 A-port at +5 V, 74HCT04 at +5 V, VIN max 5 V (abs max 6 V) OK; RN2/RN3 10k pull-downs on every gate; Q16-19 gates have no pull-down but the output R144 3.3k holds the line low if U13 is unpowered; U13 unused inputs 11, 13 tied GND, outputs 10, 12 open (correct).
### 3b. Footprint
KiCad SOT-23: pad 0.6 x 1.475, pad pitch 1.9 mm, row spacing 1.875 mm centre-centre, outer span 3.35 mm. Diodes: 0.8 x 1.11, outer 3.0. Lead span 2.3-2.5 mm lands on the pads. OK, slightly longer toe, narrower pad, fine for reflow. Layout (layers/F_Cu around Q9-19): source pad on a solid GND pour; drain pad on a thin trace to the J1 pin pad - practically no drain copper, so RthJA is probably worse than the 150 C/W datasheet value (UNVERIFIED, guess 200-300 C/W). Pads cannot be improved much, but loads are small.
### 3c. Stress
- Normal 14.4 V / 85 C: loads 0.1-0.4 A (relay coils about 0.1-0.25 A, lamp 0.1-0.3 A, UNVERIFIED typical values from memory; repo's hottest load is 402 mA VICS solenoid, Tj 102 C at 85 C ambient per VERIFICATION.md:569). Check: 0.4 A^2 x 0.5 ohm x 1.5 (hot) = 0.12 W; x 140-300 C/W = 17-36 K -> Tj 102-121 C (<150). OK.
- Cranking 6 V: relay drops out margin is the car's; ZXMS unaffected. 24 V jump start: VDS 24 V < VDS(SC) 36 V and < 60 V. Load dump 35 V suppressed: < 36 V (margin 1 V). Unsuppressed dump >65 V would sink through the coil in the clamp: 90 mJ would be exceeded (INFERRED), same for any similar part; low.
- Inductive kick (no flyback anywhere): coil L about 0.1-0.3 H (UNVERIFIED), I 0.15-0.25 A -> 0.5*L*I^2 = 1-9 mJ vs 90 mJ at 25 C, derated roughly x0.4 at Tj 100 C = 36 mJ. OK. VICS solenoid case 0.4 A, L 50 mH -> 4 mJ OK.
- Reverse battery: GND above the +12 V rail; coils pull current through each Q body diode (about 14 V/80 ohm = 0.17 A < IS 1 A); relays would pull in (same as stock). INFERRED, low.
- Harness pin shorted to battery: off state: drain at 14-24 V, below 60 V, IDSS <= 1 uA. On state: current limit 1-2.2 A at VDS 14 V = 14-30 W -> thermal shutdown at 150-175 C, auto-restart with 10 C hysteresis (cycling). Allowed by the datasheet but note 9 says not for extended periods. Q9-15 are on only when commanded; Q16-19 are ON in idle (CTL low -> HCT04 high), so a shorted ignition wire cycles the whole drive time. Shorted to ground: Q on at start sees no load (benign); R144 etc. out of scope.
- CEL at 3.3 V: ID(LIM) min 0.7 A at VIN 3 V (typ 1.7 A) vs cold-filament inrush of a 1.4-3.4 W lamp (about 1-3 A, UNVERIFIED) - will current-limit for a few ms and possibly thermal-cycle once or twice before the lamp warms; datasheet advertises lamp loads, so acceptable. Input at the pin = 3.3 V - 1 k x 100 uA (0.1 V) = about 3.2 V (at 3.3 V -3 % about 3.1 V) vs VIH min 3.0 V: passes, margin 0.1-0.2 V.
### 3d. External parts
None required. 10k pull-downs present. OK.
### 3e. References
ext/hellen-miata-NB1 uses ZXMS6005SGTA (SOT-223, C174042) x8 (Q305-312), not the FF; no reference design for SOT-23F in ext. Repo cites two public KiCad symbols with the same pin order.

## 4. Ignition-edge timing (7000 rpm = 42,000 deg/s = 0.042 deg/us)
Chain for a falling edge (spark): CTL falls -> 74HCT04 out rises (~10-20 ns) -> Q16 td(on) 5 us + tf 15 us; but the diode D31 already blocks the driver so the output is pulled low by R144 3.3k (parallel igniter input) with tau = 2.8k x C_line (say 100-1000 pF) = 0.3-3 us; threshold crossing about 1-5 us. Error 0.04-0.2 deg. Without R144 it would be 5-20 us = 0.2-0.84 deg. (INFERRED; times typ at 25 C.)
Rising edge (dwell start): Q must switch off: td(off) 45 us typ (+ maybe 5-10 us of the 15 us fall) before the 100 ohm / Schottky source can raise the line: delay 45-60 us = 1.9-2.5 deg at 7000 rpm. For dwell-based coils: dwell shortened by 45-60 us = about 1.5-2 % of a 3 ms dwell (about 3-4 % energy). If an igniter fires on the rising edge the error is 2 deg; the Miata ones fire on the falling edge (UNVERIFIED, standard). Temperature spread: datasheet has no min/max or curve for td; if +-50 % (UNVERIFIED assumption) -> +-22 us rising = +-1 deg, falling +-0.1 deg. The overlap also makes the TC4427 push about 46 mA through 100 ohm + Schottky into the on Q for 45 us each cycle (harmless).

## 5. Cost / simplification
- Needed? Q9-12, Q14, Q15 relay/tach/spare: protection was added deliberately (ULN2003 died on a short to battery). CEL: lamp inrush. Q16-19: the Schottky + 3.3k alone would leave the idle output as a 3.3k-impedance line (susceptible to noise pickup on a long harness near coil), so a hard pull-down is useful. Keep all 11.
- Alternatives (datasheets of these not read; only listing data cited, so NOT recommended): C8545 2N7002 BASIC $0.0158@1, 60 V, 5 ohm @10 V (listing), poor at 3-5 V; C20917 AO3400A BASIC $0.079@1, 30 V, 48 mohm @2.5 V (listing) - 30 V drain rating < 36 V and the clamp spec is absent so relay coils without flyback diodes would avalanche; neither has current limit or thermal shutdown. DMN6075S-7 C155242 EXT 60 V 120 mohm @4.5 V $0.09-0.2: extended, no protection. NCV8402ASTT1G C77755 SOT-223 EXT $0.24-0.49: bigger, same price class. Max theoretical saving about (0.44-0.05) x 11 = $4.3/board and every protection feature lost. Recommendation: no change.

## Sources actually read
the review brief; datasheets/txt/C95063_ZXMS6004FFTA.txt (full), p.1 and p.8 images; kb/parts_manifest.md:47; lcsc.py C95063 and searches; evidence/{cur_db,ord_db}/pcb_pads.csv, pcb_nets.txt, pcb_footprints.csv, sch_netlist.xml (Q9); evidence/*mb*/pcb_nets.txt OUT_* nets; kb/interconnect.md; repo/scripts/design.py:262-335; repo/VERIFICATION.md:569-570, research/rev0.10_design_audit.md:36-42; ext/hellen-miata-NB1 BOM; layer image crops in work dir.

## Not checked
Real Miata relay coil and CEL lamp currents (no web lookup; values from memory); transient thermal impedance curve reading for lamp inrush; actual rev0.9 vs 0.10 U12/CEL timing on hardware; igniter input impedances; thermal imaging of drain copper.
