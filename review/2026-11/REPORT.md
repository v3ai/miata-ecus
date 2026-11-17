# Miata ECU boards: review report

Review dates 2026-11-15 to 2026-11-17, of `github.com/v3ai/miata-ecus` at commit `6e346af`. Two design states were reviewed: the **ordered** boards (daughterboard rev 0.9 and five motherboards, already at the fab) and the **current** design (daughterboard rev 0.10, motherboards rev 0.13 / 0.9). Prices and stock are as of 2026-11-16.

## Bottom line

- **One build error was found, and it is on the ordered boards.** R110, the wideband pump-current sense resistor, is fitted as 0.62 Ω (LCSC C25341) where the circuit needs 62 Ω (C17971). The on-board wideband would read lambda near 1.0 whatever the mixture; the sensor is not damaged. A script compared every resistor's schematic value with its LCSC part description on all eleven boards, and R110 was the only mismatch.
- **No wrongly connected harness pin was found in any of the five year ranges.** Each range was audited twice, once from the design outward and once from factory documents inward. Three questions remain that only a car can answer: the direction of cavity 2I on 1989-95, cavity 1B on 1996, and the polarity of the A/C and clutch inputs.
- **The ordered boards are fit for bench bring-up** after the R110 swap, one firmware setting and three free inspections (next section). Their other weaknesses are known, are already fixed in rev 0.10, and need rework only if a bench measurement says so.
- **Very little can be removed for free.** Most removal ideas failed verification because each part protects something. All the cheaper-part options together save about $29 per set (7% of $399), and the two large ones need a bench test or a new footprint.
- **A set costs about $150-155 to make and deliver at a batch of 30** (about $205-210 at 5, $140-145 at 100; each ±$15). The largest lever is organisational: one daughterboard run for all years saves $18-25 per set.
- **The biggest customer-experience gaps are not on the boards.** They are firmware published only as expiring build artifacts, a missing delivery path for the TunerStudio `.ini`, and a base tune that ships with its engine protections off.

## Before powering the ordered boards

Details, part numbers and the staged bring-up sequence are in section S1, Part 1.

1. **Replace R110** with a 62 Ω 1% 1206 resistor (C17971). Mandatory before trusting any wideband reading.
2. **1989-95 only: set the tach output pin to "none"** in the ordered firmware before the board meets the car. The ordered motherboards wire the tach driver straight to cavity 2I and the ordered firmware turns it on. Whether 2I must not be driven is unsettled, so this is the free, safe default.
3. **Check your JLCPCB order confirmation for filled and capped vias** on the 4-layer daughterboard. About 500-660 of its 1,423 vias sit inside SMD pads, including all eight injector-driver tabs. If fill was not ordered, inspect those joints under magnification before power.
4. **Check part orientation** on the SOT-23 diodes, the USB protection part on each motherboard and the three input-protection diodes; the JLCPCB rotation for some of these was never confirmed in a placement preview.
5. **Test-fit a harness header** on the 1996-97 and 1999-2000 boards before soldering: the holes are 1.1 mm against TE's recommended 1.35 mm.
6. Decide the optional rework after the bench stages, not before: battery-sense resistor R11, the logic-supply fuse and inductor, the injector-driver input resistors, an external injector clamp, and the A/C pull-up R21.

## Answers to the six questions

| Question | Short answer | Section |
|---|---|---|
| Errors in the boards | One error (R110). One open risk on the ordered daughterboard (via fill). 27 medium items, mostly firmware defaults, thin margins on the ordered boards, and placeholder outlines for 1996-2005. | S1 |
| Parts to remove for free | Almost none. The VR-sensor conditioner (about 24 parts, no supported Miata uses it) can be left unfitted by default for about $0.35 per set. No change is recommended on the ordered boards. | S2 |
| Cheaper parts JLCPCB stocks | Confirmed drop-ins: TJA1042T/3 for the TCAN1042 ($0.56 per set, fixes thin stock) and C960026 for the 2 A fuse (fixes stock of 57). NCV8401B for the injector drivers saves $8.80 but limits at 25-35 A instead of 6 A and needs a short-circuit bench test. A surface-mount MAP sensor saves about $17 but needs a new footprint and covers 400 kPa instead of 700. | S2 |
| Cheaper overall | One daughterboard run for all years; batch of 30 rather than 5; cut extended-part lines ($3.07 each per order). JLCPCB collects 35% US duty on its invoice. Three of the four harness headers can be bought new; the README's "salvage only" is out of date. | S3 |
| Customer experience | Pre-flash and bench-test every unit; fix the fitment and automatic-transmission text; publish tagged firmware releases with the TunerStudio `.ini`; show the true cost to a running car; turn the protections on in the shipped tune. | S4 |
| Packaging and shipping | Ship the two boards mated, foam against the pins, inside a shielding bag in a 9 × 9 × 4 in box: about $3.30-3.60 in materials. USPS Ground Advantage with signature and cover: plan $19-24 postage per US order. | S5 |

Section S6 is the digest of the background research: other ECU designs and their field failures, the stock Miata ECUs by year, and how owners tune standalone Miatas.

## How the findings were checked

1. **Audit.** 88 independent audit passes each took one scope: 24 part groups (datasheet read, pin-by-pin against the PCB netlist), 18 board and fab reviews, 10 pinout audits, 5 firmware reviews, 31 research topics. They produced 896 findings.
2. **Merge.** The 326 findings rated medium or above, plus every removal, alternate-part and cost idea, were merged into 162 unique claims.
3. **Adversarial verification.** Every claim went to an independent verifier instructed to refute it from primary sources; the 30 rated critical or high got two verifiers each. Of the 162 claims, 13 were confirmed as stated, 142 were narrowed or corrected, 4 were refuted, and 3 cannot be settled without a measurement. 56 turned out to be already documented by the repo.
4. **Fact-check.** Each report section was re-traced by a separate checker: about 470 statements checked, 91 corrected. A final critic compared the sections against each other and its 20 corrections were applied.
5. **Spot-check.** Five of the top claims were then checked directly in the netlists, BOMs and firmware source (R110, tach on 2I, battery sense, the unfitted pull-ups, the idle limits). All five held; one needed a detail corrected.

**What this does not establish**

- No board has been built. Everything here comes from the design files, datasheets and outside documents. The "needs a measurement" list in S1 Part 6 is the real test plan.
- The 570 low and informational findings were not verified. They are in `kb/findings/all_findings.jsonl`.
- Verifiers were told to refute by default, and they downgraded 92 of 112 medium claims to low. The reasoning reads as sound, but treat their severities as the conservative end.
- The pinout audits share one script-generated table for the board side, and in places read the factory diagram for a single model year within a range. S1 Part 3 names the year read.
- Customs and duty points are research, not advice. The shipping section assumes a seller in the United States.

## Where everything is

| Path | Contents |
|---|---|
| `REPORT.md` | This summary followed by sections S1-S6 |
| `kb/findings/clusters.json`, `kb/verify/` | The 162 claims and the verifier notes behind each verdict |
| `kb/parts/`, `kb/boards/`, `kb/pinouts/`, `kb/firmware/`, `kb/research/` | The working notes of the audit passes |
| `kb/followup/` | Four follow-up investigations (IAT harness, processor stock, avoiding filled vias, complete-kit cost) |
| `NEXT-BATCH.md` | Findings and next steps for the next batch of boards, with the register of verified claims |


---

# S1. Errors and risks in the boards, and what to do before powering the ordered boards

Date of review: 2026-11-16. "Ordered" means daughterboard rev 0.9 plus motherboards 1989-93 rev 0.11, 1994-95 rev 0.9, 1996-97 / 1999-2000 / 2001-05 rev 0.7. "Current" means daughterboard rev 0.10 and motherboards rev 0.13 (1989-95) / 0.9 (1996-2005). Confidence tags: [CONFIRMED], [PARTLY], [SINGLE-SOURCE], [NEEDS MEASUREMENT]. Cluster ids (C0xx) point into `kb/findings/clusters.json`; verifier notes are `kb/verify/<cid>-<lens>.md`.

**Bottom line.** One real build error was found: R110 on the daughterboard is a 0.62 ohm part, not 62 ohm. It is on the ordered boards and must be swapped before you trust any wideband reading. Everything else is either free (firmware settings, a few inspections and measurements) or optional rework that you should decide on after the bench stages. We re-checked all resistor values against their LCSC part descriptions across every board's BOM; R110 is the only mismatch. No wiring error was found in any harness-cavity map; where the pinout audits are not independent of the repo, Part 3 says so.

---

## Part 1. Rework and checks before first power-up of the ordered boards

### 1A. Checklist (do in this order)

| # | Item | Mandatory? | Boards | Exact part / setting | Replacement | Test that proves it |
|---|---|---|---|---|---|---|
| 1 | R110 (LSU pump-current sense, between LSU_RT and LSU_IP) is fitted with C25341 = 620 milliohm. Should be 62 ohm. C001 | **Mandatory** before any wideband use | All five (daughterboard rev 0.9; same error is in rev 0.10) | R110, 1206 | C17971, 1206W4F620JT5E, 62 ohm 1%, $0.0053 at qty 1 (JLC, re-checked today, 123k in stock). C25341 and C17971 are the same Uniroyal family; only the part-number letter differs | Unpowered, DMM across R110 reads 62 ohm. Then LSU in free air (stage 8): lambda reads lean, near the sensor's free-air value, not 1.0 |
| 2 | Tach output enabled in default firmware drives J1 pin 2I (OUT_TACH is wired straight to 2I on the ordered 1989-95 boards). Whether 2I is an igniter-side line that must not be driven is not settled: the factory-diagram audits say the tach is fed from igniter terminal D, and nothing reads 2I. C002 [PARTLY] | **Mandatory, free** | 1989-93 and 1994-95 | Firmware: set tach output pin to "none" in TunerStudio (the current repo firmware calls `miataNoTachOutput()` for the NA6 and NA94 presets; the ordered firmware copy has no such function and enables the tach pin) before the board ever sees the car | None. No pull-up is fitted. Do not rework unless a car measurement says the ECU must supply a tach | Before plugging in: TunerStudio shows tach pin unassigned. On the car, measure 2I key-on with ECU unplugged. If about 0 V and the cluster tach is dead after plugging in, cut the OUT_TACH track at 2I and add a jumper or about 1k pull-up from switched 12 V |
| 3 | Check JLC order record for "Via covering: epoxy filled and capped". C005 [PARTLY] | **Mandatory check, free** | Ordered daughterboard | About 500-660 of 1423 vias (0.3 mm) sit inside SMD pads, including all 8 DPAK tabs of Q1-Q8. The gerbers cannot show fill; the repo has no order record. Fill is extra cost on 4 layers | If not filled: no rework of vias. Inspect | Under a microscope or X-ray: solder fillet on each Q1-Q8 tab, no starved 0402/0603 joints. Thermal-camera Q1-Q8 under dummy load (stage 6) |
| 4 | Placement check on the received boards: orientation of SOT-23 diodes D15-18, D35-37 (daughterboard) and U4 (USBLC6-2SC6, SOT-23-6, on each motherboard; the daughterboard's U4 is the SOT-223 LDL1117), and polarity of D6, D7, D12 (daughterboard). C034, C055 [PARTLY] | **Mandatory, free** | Daughterboard and all five motherboards | JLC rotation for SOT-23 (+180 in the repo vs -90 in a community table) is unsettled; the repo's +180 for SOT-23 was read from a JLC placement preview of rev 0.5 and the community table could not be fetched, so which one is right is not known (the SOT-23-6 entry was only assumed) | Rework only if wrong | Compare each marking to pad 1 on the layout. DMM diode test on D6, D7, D12 and D15-18 |
| 5 | Header fit, 1996-97 and 1999-2000. TE drawing 178780 (76-pos) recommends 1.35 mm holes (+-0.10); board has 1.1 mm, so seating is marginal, not shown to fail. No drawing was available for the 64-pos 176122-6 (1999-2000), which has the same 1.1 mm drill. C097 [PARTLY] | **Mandatory test-fit** | 1996-97, 1999-2000 (the 2001-05 footprint was not checked) | Test-fit a real harness-side header before soldering the one you will sell or use | If posts do not seat: open holes with a 1.3 mm drill | Header sits flat on the board without force |
| 6 | Set JP1 (IAT select, motherboard) to STOCK (shunt on pins 1-2) for first tests. B17, PIN-9900-A [SINGLE-SOURCE: two audits, no verifier] | Mandatory for engine run | All five motherboards (all have JP1/J3) | JP1 is a hand-fitted header with shunt, default EXT (pins 2-3 per the motherboard README); nothing is on J3, so the stock IAT is not read | Buy Molex 43650-0200 from Digi-Key/Mouser if you want an external IAT (confirm the part against the board footprint and check live stock first) (C587650 has 0 JLC stock but J3 is hand-fitted, C096) | IAT reads sensible ambient in TunerStudio |
| 7 | Battery-sense wire. C045 [CONFIRMED] | Optional | Ordered daughterboard only (rev 0.10 already puts R11 pad 1 on VBAT_IN) | R11 pad 1 is on +12V after D7 and F1, so VBATT reads about 0.3-0.6 V low and varies with load | Lift R11 pad 1, wire to VBAT_IN (J1 pin 1) or firmware offset | With 12.00 V at J1, TunerStudio battery reading within 0.1 V |
| 8 | 220 ohm series resistors on the eight VND7NV04 inputs (Q1-Q8). C008 [PARTLY] | **Optional.** ST's 150 ohm minimum is a rating; normal 5 V drive is about 0.1 mA. Already documented in the repo | Daughterboard | Lift pin 1 of each Q1-Q8 or cut the input track and bridge | 220 ohm: C25091 (0402) or C22962 (0603), under $0.002 each | Rather than rework blind: scope each gate and drain at stage 6; rework only if edges or glitches look bad. Eight delicate DPAK sites |
| 9 | F1 (0.5 A hold PTC, C70077) and L1 (500 mA, 0.3 ohm, C70960) in the logic supply. C006 [PARTLY] | **Optional, decide after stage 5** | Ordered daughterboard (rev 0.10 already has a 1.1 A BSMD1812-110-33V F1, C883150, and a 7.5 A L1, C177247) | Cranking draw modeled at 0.45 A at 8 V, about 0.6 A at 6 V; at 6 V the +5V rail sags below regulation. Nuisance trip is unlikely; the 6 V / 0.6 A sag is an unmeasured extrapolation | F1 to C48985884 (1206L110/33NR, 1.1 A hold, 33 V, $0.087 at 1, stock 25.6k, re-checked); L1 to a 1 A or larger 1210 inductor or a 0 ohm link | Measure supply current at 6 / 8 / 13.8 V and drops across D7, F1, L1. Hot-soak then crank test |
| 10 | Injector inductance and clamp heat. C007 [PARTLY] | **Optional, measure first** | 1994-2005 ordered (no clamp on daughterboard, none on motherboards). 1989-93 has D3/D4 SMCJ30A | Each VND7NV04 absorbs its own turn-off energy: about 15 mJ per shot at 20 mH, 3-6 mJ at 4-8 mH. Over thermal shutdown only for 20 mH injectors at 85 C air and sustained redline | If above about 12 mH: 4 external 16 V TVS (SMCJ16A or 1.5SMC16A) wired from each injector wire to VBAT at the harness side | LCR meter on one injector (costs nothing); driver case temperature on the dummy-load bench |
| 11 | A/C request and clutch pull-ups R21, R22 (0603 4.7k, C23162, not fitted by default). C003, C039 [PARTLY] | Optional, car-dependent | All five motherboards (R21/R22 are motherboard parts; A/C input: confirmed in the 1989-95 and 2001-05 audits) | Stock A/C signal is ground-switched; with R21 unfitted and `acSwitchMode` at its active-high default the compressor is never commanded. Fitting R21 without the firmware change inverts the request. Clutch needs only R22 (rusEFI already defaults to active-low) | Fit R21 (A/C) and R22 (clutch) by hand; set `acSwitchMode=PI_PULLUP` | Measure 1Q (1989-95) or 4F (2001-05) with the stock ECU unplugged: ground-switched = fit. Then switch A/C on and see the relay output change |
| 12 | Hall sensor input levels (R61/R63 4.7k series, R62/R64 1k pull-ups via D35). C046 [PARTLY] | Optional | Daughterboard | Sensor sinks about 4.7 mA, normal for open-collector Hall outputs; the Mazda CAS/CMP low level is unmeasured | Change R61/R63 or R62/R64 only if the scope shows a problem | Scope the real CAS/CMP at first bench power: clean edges, low level below about 0.8 V at the pin |
| 13 | Header sourcing, 1999-2000: TE 176122-6 (64-pos). C014 [PARTLY] | Procurement | 1999-2000 | No authorised stock, brokers show about 510 at $10-20 | The CURRENT 1999-2000 board (rev 0.9) uses the 76-position 178780-1 (repo/motherboards/1999-2000/README.md line 48), so 176122-6 is needed only for the ORDERED rev 0.7 boards: buy only enough for those (about 10-20; broker prices are stale, so confirm the part against the board footprint and check live stock before buying), or salvage from a stock ECU. Do not substitute the 76-pos header on the ordered board | Fit check |
| 14 | 1996-2005 outline and mounting holes are an NA placeholder. C011 [PARTLY] | Mandatory before closing a case | 1996-97, 1999-2000, 2001-05 | Hellen's 154 x 159 mm / six-hole pattern is a candidate, not measured stock-case data | Measure a real case; mount loose until then; drill new holes by hand | Board seats in the case with header aligned to the window |

### 1B. Staged bring-up (from B03 section 4, B17, B18 and the verified claims)

Equipment: bench supply 0-16 V with current limit, DMM, scope, four 12-14 ohm 10 W resistors (injector dummies), a relay coil as an inductive load, USB-C cable, SWD or DFU path, LCR meter.

| Stage | Action | Expect | Stop if |
|---|---|---|---|
| 0 | Visual and microscope inspection (items 3, 4, 5 above). Carry out item 1 (R110) now, plus whatever of item 2 applies | No bridges, tab fillets present | Voids or bridges at Q1-Q8 or U1 |
| 1 | Unpowered ohms on the bare daughterboard: VBAT_IN-GND, +5V-GND, +3V3-GND. Compare with the second board if you have one | Not below about 100 ohm (no design number exists) | Below 10 ohm |
| 2 | Bare daughterboard, not mated. Supply at 6 V, limit 0.1 A, on J1 pins 1+2 with GND on 4, 5; raise to 12 V. Never judge 12 V rails from USB power alone (back-feeds +12V to about 4 V) | +12V about 0.3-0.5 V below input; +5V 5.0 V; +3V3 3.3 V; V5_EXT and V5_SENS about 5 V; DRV_EN_N about 5 V (drivers off) | Current above 0.3 A at 12 V; any rail off by more than 5 % |
| 3 | Scope the buck: ripple and a 0.2 A to 2 A load step on +5V. C058 [PARTLY] | Ripple under 50 mV (target, inferred); no ringing | Hot buck IC or inductor within 30 s. If ringing, add one 22 uF 1206 X5R 10 V across +5V |
| 4 | Flash. DFU (BOOT button) 5 or more times plus software DFU; scope the 8 MHz crystal start-up. C086 [PARTLY]. Use the frozen ordered firmware. Then connect USB and TunerStudio | rusEFI boots, LED on PD12 runs, DRV_EN_N drops to about 0 V after start and returns to 5 V on reset | Reset loop, current above 0.3 A. If DFU is flaky, lower the crystal load caps or fit a lower-ESR crystal |
| 5 | Mate with the matching motherboard (standoffs first). Supply limit 0.4 A, 12 V at the battery cavity (1B on 1989-95 and 1999-2000, 4B on 1996-97, 4AF on 2001-05). JP1 on STOCK | MAP about 0.85 V at the sensor for 101 kPa; CLT/IAT open about 4.26 V; battery reading low (item 7) | Current above 0.4 A; MAP outside 0.7-1.0 V. Also measure +3V3 current and the U4 tab temperature (C059) |
| 6 | Outputs. Dummy resistors from +12V to OUT_INJ1-4, IACV, VVT. Use TunerStudio output tests. Scope drains and gates. Use a relay coil to see the inductive clamp. Scope IGN1/IGN2 with no coil | Drain below 0.5 V when on, about 1 A per dummy; VND7NV04 clamp threshold 36 V minimum (datasheet VCLTH), 40-55 V at 3.5 A, on 1994-2005 drivers; D3/D4 (SMCJ30A) clamp lower on 1989-93 (breakdown about 33-37 V; exact figure at relay-coil current not checked) | Driver above 100-120 C, output stuck on, edge glitches (decide item 8) |
| 7 | Inputs: signal generator on HALL1/2, VR, SW1-3; knock. Confirm the ISO 16750-2 start profile leaves injector and relay outputs off through a reset if you have a programmable supply. C057 | RPM reads; dividers about 3.7 V at 12 V; MCU pins never above 3.6 V | MCU pin above 3.6 V sustained |
| 8 | Wideband. No sensor first; then a 3-4 ohm dummy heater at 3 A limit; then a real LSU in free air. Use 12 V, not USB. Pinned wideband firmware lacks upstream fix 9295698 (USB-only heater case, C075) | CAN heartbeat; heater PWM only after warm-up logic; UN/VM/IP voltages plausible; free-air reading correct (item 1) | Heater current above 3 A (F1 hold); controller fault |
| 9 | Car. Item 2 done. With the stock ECU unplugged, take the measurements in Part 6. Fan test before first drive on 1994-95 (ECU is the only fan control, C061). Select the right 2001-02 vs 2003-05 preset on 2001-05 cars. Use a spare coil or igniter first (generic precaution, C060 is not a found defect). Cranking with a supply as battery at 9-10 V | Cranks; +5V never below 4.7 V while cranking; no stall when key leaves START | Any brownout; fan fails to start on command |

Stop everywhere on smoke or smell, current limit hit at stage 2, or any rail more than 5 % off.

---

## Part 2. Errors and risks in the CURRENT design (daughterboard rev 0.10, motherboards rev 0.13 / 0.9)

Only one verified claim is still "high"; everything else was corrected to medium or lower. Ranked by the verifiers' corrected severity (verifier verdicts, not the earlier draft ranks). "Fix" gives the generator file where the notes identify it.

| Rank | Id | Item | Severity (corrected) | Tag | Fix |
|---|---|---|---|---|---|
| 1 | C001 | R110 is 0.62 ohm (C25341) | high (one verifier critical, one high; reading only, sensor not damaged) | [CONFIRMED] | `repo/scripts/design.py:64` `LCSC_R1206['62']` and `repo/scripts/wideband.py:153`: change to C17971. Add a script check that each LCSC part's resistance equals the schematic value (it would have caught this) |
| 2 | C003 / C039 | A/C and clutch inputs: pull-ups unfitted and polarity not set | medium (C003); low (C039) | [PARTLY] | Firmware preset: `acSwitchMode=PI_PULLUP` for 1989-95 and 2001-05; leave clutch default (already active-low). Add a polarity line to INSTALL.md |
| 3 | C022 / C106 | Stock: STM32F407VGT6 (C12345) 72-140 pcs at JLC across readings on 2026-11-16 (140 live; the C018 verdict says about 96); TCAN1042VDRQ1 (C485806) 207 | medium (C022); low (C106) | [PARTLY] | Check stock before each batch. Buy franchised stock or split the lot; see S3 lever 8 (consignment terms unverified). F405VGT6 C56621 is a hedge at about $1.8 more at 100 |
| 4 | C015 | F2/F3 PTC SMD1812-200-30 (C46641168) stock 57 | medium | [CONFIRMED] | `mb_*.py` for 1999-2000 and 2001-05: switch to C960026 (BSMD1812-200-30V, 194k stock, $0.0887 at 50). Same 1812 footprint; ordered boards: do nothing unless JLC flags a shortage |
| 5 | C084 | NA6/NA94 idle PID: `idleRpmPid.minValue = 20` is set in upstream `miataNAcommonEngineSettings()` (ext/rusefi/firmware/config/engines/mazda/mazda_miata_1_6.cpp:146), which both NA6 and NA94 setups call (lines 211, 270, 293). The maximum is 10 from this board's defaults (firmware/board/miata_board.cpp:224) or 20 from rusEFI's defaults (controllers/algo/engine_configuration.cpp:525), depending on call order (not traced). Either way the minimum is at or above the maximum, so closed-loop idle has no working range. Effect on a real car unmeasured | medium | [PARTLY] | `miataApplyYearPreset`, NA6/NA94 cases: set `idleRpmPid.minValue=-20`, `maxValue=40`; load the 28 to 20 % idle curve. Reflash only |
| 6 | C078 / C016 / C049 / C085 | Firmware: flat 4 ms dwell, protections off, flat 60 kPa MAP fallback, dead time unmeasured, LTFT compiled in. See Part 4 | medium (C016); low (C078, C049, C085) | [PARTLY] | Firmware only |
| 7 | C082 | Condenser fan (LS7: 1I on 1999-2000, 2C on 2001-05) not commanded with A/C | low | [PARTLY] | Set `fan2AcMode=Relay` in 1999-2000 and 2001-05 presets after confirming on a car which relay the stock ECU uses |
| 8 | C097 | Header holes 1.1 mm vs TE 1.35 mm (drawing seen for the 76-pos header only) | low | [PARTLY] | Layout script: drill 1.3-1.35 mm, pad 1.8 mm |
| 9 | C042 | F3 (VVT) and F2 (IAC) PTC derate below coil current in a hot cabin | low | [PARTLY] | Next revision: 3 A hold part for F3 (C22446884, 2920L300/30GR, is the 2920 used for the motherboard LSU heater PTC F1; it is a 2920 footprint, not a drop-in for the 1812). Fail-safe: a trip costs top-end power only |
| 10 | C038 | Wideband heater PTC F1 on the motherboards (2920L300): hold 1.99 A at 60 C, 1.34 A at 85 C. VERIFICATION.md misquotes 2.4 A | low | [PARTLY] | Fix text; swap to 2920L400/30GR if measured heater inrush trips it. One part per board |
| 11 | C102 | VDDA cap C12 about 9 mm from pin, behind ferrite FB1. Also on the ordered board | low | [PARTLY] | Move C12 to the pin with the ferrite upstream. Ordered boards: optional 100 nF at the VDDA pin |
| 12 | C059 | U4 LDL1117 at Tj about 126 C in 85 C air (at 0.2 A inferred) | low | [PARTLY] | Add +3V3 copper and vias at the U4 tab |
| 13 | C033 | Socket C124412: 65 in stock (about 32 ECUs) | low | [PARTLY] | Buy for the whole run now (confirm the part against the board footprint and check live stock first); qualify Wurth 61304011821 as second source |
| 14 | C107 | If the 159 mm outline is adopted, J2 sits outside the edge and J4's USB-C shield pads on it (current 1996-2005 boards) | low | [PARTLY] | Layout script outline height H; move J2 and J4 up at least 2.5 mm. Only after a case is measured |
| 15 | C043 / C123 | AEM 30-3427 connector fit and single-source supply (current motherboards only; the ordered ones use a Molex Micro-Fit LSU 4.9 header) | low | [PARTLY] | Plug a real 30-3427 into a sample S08B-PUDSS-1 before ordering; INSTALL.md: name a fallback (pigtail or Bosch LSU plug) |
| 16 | C104 | Rotations for U3, U14 (DSO-8), J4 (microSD), new TVS and diodes unconfirmed | low | [PARTLY] | Check in JLC placement preview; record in `JLC_ROT` / `JLC_OFFSET` |
| 17 | C054 / C035 | MAP error up to +-17.6 kPa (+-2.5 % FS), 5 V rail not measured | low | [PARTLY] | Offer MPX4250AP as a hand-fit swap for NA; bench-calibrate; baro from MAP at key-on. A V5_EXT divider to a spare ADC input is a future option |
| 18 | C101 | Rev 0.10 daughterboard F1 (1.1 A BSMD1812-110-33V) holds 0.52 A at 85 C against 0.45 A modeled cranking | low | [PARTLY] | Hot-soak crank test already listed in VERIFICATION.md |

Items that apply to both ordered and current and were checked but need only a document or test: C036 thermal model (run `board_thermal.py` at h = 4-5; measure in a case), C032 load dump (add install note: never disconnect the battery with the engine running), C052 wideband accuracy (side-by-side with a commercial unit), C066/C067 (simulation and netlist checks do not prove the wiring; the owner should hand-check pin 1 and orientation on ordered boards, which Part 1 stage 0 does).

---

## Part 3. Per-year pinout result

Method: audit A walks design to car; audit B starts from factory sources and walks inward. Two limits apply to every year. First, only year-specific factory diagrams that the audits could fetch were read, so each result names the year actually read. Second, both audits use the same repo `kb/interconnect.md` for the board side, so board-side agreement is one check, not two. No audit found a pin the design connects wrongly.

| Years | Primary factory source read | A and B agree | Where they disagree, or disagree with the design | Still needs a diagram or car check |
|---|---|---|---|---|
| 1989-93 (48-pin) | A and B both read the 1991 wiring diagram (mellens.net). Years 1989, 1990, 1992, 1993 not read | Pin map matches for 1B, 1C, 1E, 1G, 1H, 1J, 1N, 1R, 2A-2E, 2G, 2K-2Q, 2U-2X, 2Z. 2T has no wire on the 1991 ECU (pump runs from the AFM contact through the circuit-opening relay). 1L and 1M have no wire on the 1991 ECU (fan relay is on 1R). 2I comes from igniter terminal E and the tach is fed from igniter terminal D, so the stock igniter drives the tach. 1V is clutch (manual) or ignition (automatic) | Both audits disagree with the repo README on labels: 1L "fan relay" and 1M "vehicle speed" are wrong for 1991; fan is 1R. They disagree with the ordered board on 2I (tach driver wired straight to 2I). A low-quality site lists 2I as tach output, and the rusEFI MRE wiki says the stock ECU supplies a pull-up on 2I; A discounts both | 2I direction and level on 1989/1990/1992/1993 and on the car (Part 6 item 1). F/P terminal on the AFM connector for the 2T wire (C004: INSTALL.md already warns; reword README row for 2T) |
| 1994-95 (48-pin) | A read the 1994 Mitchell diagram (PDF page 16) and the 1995 diagram. B could not read the 1994 wiring diagram (blank figure pages) and used the FSM self-diagnosis charts | Every driven function maps correctly: 1E, 1G/1H, 1J, 1L, 1M, 1Q, 1V, 2E/2G, 2K, 2M, 2N, 2O, 2P, 2Q, 2R, 2S, 2T (ECU switches the pump relay on this year), 2U/2V/2Y/2Z, 2W, 2X. Fan: relay coil fed from ENGINE fuse, grounded only through 1L, no thermoswitch (C061 [CONFIRMED]). EGR, DLC, power-steering and A/T lines are unconnected | 2I: A says the igniters' BLK/WHT go to both the cluster tach and ECU 2I (so 2I is an input). B's sources (MSPNP J6, MRE JP54) suggest 1995.5+ cars may expect the ECU to output the tach. These conflict and neither can be settled from a diagram. A also notes 2R (PRC solenoid) is wired to OUT_ALT, harmless while alternator control is off | 2I on a 1994 and a 1995.5+ car; the airflow meter type (vane or hot wire; unused by the speed-density preset); stock fan thresholds |
| 1996-97 (76-pin) | A: 1997 Mitchell diagrams (Fig. 8 and 9). B: 1996 factory ECM diagram. Different model years, same cavities | All connected cavities correct: 1A, 1B, 1E, 1G, 1K, 1L, 1M, 1O, 1U, 3B-3G, 3I, 3K, 3M, 3O, 4A-4D, 4F, 4G, 4L, 4N, 4Q, 4R, 4U-4X. 4I (battery backup) and 4E/4H (crank pulley VR) correctly open. Unconnected stock functions: purge 4T, EGR 4O/4P, PRC 4J, rear heater 4Z (C062: the function names are not FSM-confirmed). The rusEFI wiki colour table is partly wrong (4G, 4N, 4U, 4V, 4E, 4H), documentation only | 1B and 1A: A reads the 1997 fan figure as radiator fan 1A and condenser fan 1B. B's 1996 diagram labels 1B "A/C system"; B marks this unresolved | 1B on a 1996 car; A/C (1P/1Q) and clutch (3I) polarity (R20-R22 unfitted); A/T lines 1R, 1T, 4Y |
| 1999-2000 (64-pin) | B: 2000 Mazda wiring diagram (PCM box). A: no primary source, three secondary sources. 1999 diagram not read by either | Every driven or sensed cavity agrees: 1B, 1E, 1I, 1O, 1P, 1R, 1S, 1U, 2B-2L, 3A-3C, 3E-3J, 3M-3O, 3Q, 3W-3Z. 3M = IAC control, 3O = +12 V (B reads the 2000 diagram; the rusEFI wiki has these swapped; A reached the same by majority). 1U front O2 heater and 3Q VICS use the VVT and MAINRLY driver channels, matching NB1 (C041 [PARTLY]: no pin-table conflict; that the NB1 firmware never drives VICS is true, the torque cost rests on an unverified forum report). Net routing identical between ordered and current except IAT and AUX | None between A and B on pinout. Firmware gaps they both list: VICS never driven, charge lamp 1Q open, alternator 1O/1T open, condenser fan 1I not commanded (C082) | VICS solenoid polarity and rpm threshold; A/C polarity on 1P/1S (B says the active-high default "matches", the 2001-05 and 1989-95 audits say the opposite for those years); immobiliser on non-US cars; 1999 diagram |
| 2001-05 (72-pin) | A and B both read Mazda CHARM PCM terminal-voltage tables 2001-03 (2004-05 same images) | All 72 cavities match the factory drawing exactly. 2001 = 2002; 2003-05 uses 3H (main relay) and 4S (IG1). FSM 2003 table's TP on 4Y is a typo for 4V; both resolve it. Knock is on 4M (rusEFI's alt table says 4K, obsolete) | A/C 4F and clutch 4I are active-low with an ECU-side pull-up (both audits), board ships R21/R22 unfitted. Immobiliser on 3S not supported, dash light flashes (C077: stated in README line 101 and INSTALL.md line 256, missing from the product page) | Tach 3O and alternator 3M level with the ECU unplugged (Part 6); 2003-05 wake path 4S through D8 and F1 (design.py:204) on a car; wire colours (neither audit obtained them) |

---

## Part 4. Firmware defaults that matter (verified items only)

All of these are firmware settings and need a reflash, not board rework, so they apply to ordered and current boards alike.

| Id | Default | Consequence | Fix | Tag |
|---|---|---|---|---|
| C016 | Boost cut 0, lambda protection off, CLT-based rev limit off. MAP-failure fallback table (`mapEstimateTable`) is a flat 60 kPa | NA car: only the fallback matters (about 40 % lean at WOT if the MAP sensor or wire fails). Turbo or supercharged: no protection | Fill `mapEstimateTable` (about 35-45 kPa idle to about 95 kPa WOT); set `boostCutPressure` about 160 kPa as a backstop (never triggers on NA) | [PARTLY] |
| C084 | NA6 and NA94 idle PID limits: min 20 (upstream mazda_miata_1_6.cpp:146); max 10 (board defaults, miata_board.cpp:224) or 20 (rusEFI defaults, engine_configuration.cpp:525), call order not traced. Minimum is at or above maximum, so closed-loop idle has no working range, on a generic open-loop IAC curve | Idle probably far too high and uncorrected; effect on a real car unmeasured | See Part 2 (C084). Test on a car | [PARTLY] |
| C003 | `acSwitchMode` stays active-high; stock A/C request is ground-switched | Compressor never commanded | `PI_PULLUP`; fit R21 | [PARTLY] |
| C082 | Only `fan1AcMode=Relay` set | Condenser fan runs only above 95 C (what the stock ECU does with this fan is unverified) | `fan2AcMode=Relay` on 1999-2005 | [PARTLY] |
| C061 | 1994-95 fan on at 100/96 C, condenser 95/91 C; ECU is the only fan control | A failed output or wrong setting overheats the car | Bench-test both fan outputs; consider about 95 C on. Also check failed-CLT behaviour (not checked; the F02 note says a failed CLT turns the fan on) | [CONFIRMED] |
| C078 | Dwell 4 ms flat, correction 1.0 from 8 to 15 V | Under-charge at low battery; rusEFI does not clamp dwell for GPIO igniters (it only warns when the dwell angle is too long), and a flat 4 ms is not itself over-dwell. Coil data unknown | Set dwell from the coil data or a known Miata tune; add correction above 1.0 at 8-11 V. Scope dwell on the real coil | [PARTLY] |
| C049 | Injector dead time is a community estimate; sources differ 1.4-1.5x | Start and idle fuel error | Add a note; set by wideband at idle | [PARTLY] |
| C085 | LTFT compiled in; learning on, applying learned trims off | Safe as shipped (flash-write behaviour not checked) | One line in the docs, or `#define EFI_LTFT_CONTROL FALSE` in prepend.txt | [PARTLY] |
| C040 / C002 | Tach: 1989-95 enabled in ordered firmware (disable it); 1996-2005 tach driver (3O on 2001-05, 4L on 1996-97, 2K on 1999-2000) has no pull-up | Dead tach possible but unproven | Part 1 item 2; Part 6 item 2 | [PARTLY] |
| C041 | NB1 never drives VICS (3Q) | Possible low/mid torque loss (from an unverified forum report), no damage | Optional GPPWM or rpm-threshold output after polarity is confirmed | [PARTLY] |
| C091 | 2001-02 and 2003-05 need different presets | Wrong preset: 2003-05 car on early preset will not run (relay never closed) | Say so in INSTALL.md | [CONFIRMED] |
| C044 | Boost ignition rows 24-25 deg at 158 kPa | Aggressive for 91 octane under boost | Cap shipped tune above about 120 kPa to 15-18 deg | [PARTLY] |
| C075 / C080 | Pinned wideband firmware lacks upstream fix 9295698; F103 watchdog off; heater can start without CAN allow (both upstream design choices, hang-leaves-heater-on not demonstrated) | USB-only bench use gives wrong heater behaviour | Cherry-pick 9295698 and 91aa7c6 after diff review; enable IWDG in the heater loop | [PARTLY] |

---

## Part 5. Checked and found correct, and checked and dismissed

**Held up under attack (high stakes):**
- All 80 J1/J2 to JD1/JD2 pin nets match on all five ordered motherboards (same offsets 14.5 / 42.0 mm, same orientation; only HTR_GND on GND, intended). B03, B17.
- Every MCU pin used by the frozen firmware matches the ordered daughterboard netlist, including the wideband flash UART crossing PD8-PA10 and PD9-PA9, and the F407 pin table against ST data. B03, F01.
- Harness-cavity rows of all five ordered motherboard READMEs match the PCB (5 of 5). B17.
- MPX5700AP pinout (1 Vout, 2 GND, 3 Vcc) and bypass caps; Molex 43045-0600 footprint against the Molex drawing; SS34 (D1, D2, D7) and SMCJ30A (D3, D4, D6) polarity; USBLC6 pin use; USB-C CC1/CC2 5.1k. B17, P15 (diode audit).
- Non-inverting output chain (3.3 V MCU, 74LVC4245, VND7NV04 or ZXMS6004, active high; ignition TC4427 plus inverter keeps coils off at reset). Drivers stay off through reset and DFU via PA8. F01.
- DRC and ERC re-run: 0 unconnected, 0 clearance, hole or edge errors on ordered rev 0.9. The 199 lib-footprint and 57 net-conflict items are attributed to KiCad 9 without the libraries (not independently traced); the run also reports courtyard, silk and 6 footprint-mismatch items. B18, B01.
- Output copper is not a limit: every drain is a 6.9 mm column on three layers, below 0.5 milliohm (B18's figure, not re-computed in this check).
- LSU pump loop closes on the Nernst voltage, so R110's error cannot burn the sensor (C001).
- Pairing of injector drivers on ordered 1989-93 (R23/R24 fitted): the SMCJ30A D3/D4 clamp first and the NCV8406A drivers take about 0 mW. Keep R23/R24 and D3/D4 (C037).
- Alternator control drives from a VND7NV04 with alternator off by default, so the Hellen TC4427 field failures do not carry over (C047).

**Checked and dismissed (do not worry):**
- C056: the Hellen H72 crowbar that failed short at 22 V. This design has no MOSFET crowbar.
- C095: A/C idle-up stalls are Megasquirt PnP forum reports, not this product.
- C010: 1999-2000 alternator overcharge reports are second-hand and about another vendor's regulator.
- C060: the long-dwell upstream issue was closed as fixed in 2024; the smoke reports are unrelated.
- C064: vane airflow-meter voltage disagreement between manuals does not matter; the AUX3 input accepts any 0-5 V.
- C063: IAC "H-bridge" suspicion. rusEFI's own NB2 board uses the same topology as this design.
- C087, C018: F407VE (512 kB) cannot run the firmware (about 669 kB) and no F407 clone is supported; both are "do not substitute", not defects.

---

## Part 6. Needs a measurement

| # | Question | Measurement | Affects |
|---|---|---|---|
| 1 | Does 2I on 1989-95 need an ECU pull-up or tach drive? (C002) | Key on, ECU unplugged: 2I to ground; then with ECU plugged in and tach output off. Cluster needle works or not on the stock igniter | 1989-93, 1994-95 (ordered: only the firmware setting) |
| 2 | Does 3O (tach) and 3M (alternator) need a pull-up on 1996-2005? (C040, C010) | Key on, ECU unplugged: 3O, 4L, 2K (per car) to ground. About 0 V: add about 1k to switched 12 V; about 12 V: nothing | All 1996-2005 |
| 3 | A/C request and clutch polarity (C003, C039) | 1Q (1989-95), 1P/1S (1996-2000), 4F and 4I (2001-05) with the stock ECU unplugged | All years |
| 4 | Injector inductance (C007) | LCR meter on one injector. 8 mH or less: nothing. Above 12 mH: external TVS | 1994-2005 ordered |
| 5 | Logic supply current and drops (C006) | 6, 8, 13.8 V: supply current; voltage across D7, F1, L1; hot soak and crank | Ordered daughterboard |
| 6 | Case geometry for 1996-2005 (C011, C031) | Measure hole centres, case height, header window on one real case per generation | 1996-2005 |
| 7 | LSU cold heater resistance and J2 contact heating (C038, C103) | Ohm the sensor at 20 C; log heater current and F1 temperature during warm-up | All |
| 8 | U4 and +3V3 load (C059); 5 V rail (C035); crystal start-up (C086) | Ammeter on +3V3; thermocouple on U4 tab; scope HSE; 5-10 DFU entries | Daughterboard |
| 9 | Hall output low level on the real CAS/CMP (C046) | Scope at first bench power with the real sensor | All |
| 10 | VICS solenoid polarity and threshold; alternator 1O/3M duty direction (C041, M5) | Scope the stock ECU outputs on a car | 1999-2005 |
| 11 | Igniter input threshold; loaded IGT swing about 4.1 V into 1k (C053, a computed estimate; verdict unverifiable) | Scope IGT with the real igniter | All |
| 12 | Via fill, thermal truth (C005, C036) | JLC order record; thermal camera on Q1-Q8 at 3 W and 6 W in a case | Ordered daughterboard |
| 13 | JP1/J3 IAT sensor and stock thresholds; 1B function on 1996 | Wiring diagram or car check | 1996-97 |

---

## Part 7. Consolidated change list for the next revision

Built only from Parts 1-6 and S2 / S4. "Where" gives the generator or firmware file only where this report's notes name it; otherwise "not located". Items marked "after bench check" or "after measurement" are not recommended before that.

| Change | Where | Boards | Tag | Source |
|---|---|---|---|---|
| R110: C25341 -> C17971 (62 ohm); add a script check that each LCSC part's resistance equals the schematic value | `repo/scripts/design.py:64` `LCSC_R1206['62']`, `repo/scripts/wideband.py:153` | Daughterboard rev 0.10 (and ordered rev 0.9 by hand) | [CONFIRMED] | S1 Part 1 item 1, Part 2 rank 1 |
| F2/F3 PTC C46641168 -> C960026 (BSMD1812-200-30V, same 1812 footprint) | `mb_*.py` for 1999-2000 and 2001-05 | 1999-2000, 2001-05 motherboards | [CONFIRMED] (S2 B6) | S1 Part 2 C015; S2 B6 |
| TCAN1042VDRQ1 -> TJA1042T/3/1J (C132227), if accepted | BOM / LCSC code, not located | Daughterboard | [CONFIRMED] pin table (S2 B2) | S2 B2 |
| Header holes 1.1 mm -> 1.3-1.35 mm, pad 1.8 mm | layout script, not located | 1996-97, 1999-2000 (2001-05 not checked) | [PARTLY] | S1 Part 2 C097 |
| C12 to the VDDA pin with the ferrite upstream | not located | Daughterboard | [PARTLY] | S1 Part 2 C102 |
| Add +3V3 copper and vias at the U4 (LDL1117) tab | not located | Daughterboard | [PARTLY] | S1 Part 2 C059 |
| Outline and mounting holes; move J2 and J4 if the 159 mm outline is adopted | layout script outline height H (name from S1 C107) | 1996-97, 1999-2000, 2001-05 | [PARTLY]; only after a real case is measured | S1 Part 2 C011, C107 |
| R144-R147 3.3k -> 4.7k (C17936) and FB1 -> C14709 (extended-line consolidations) | not located | Daughterboard | [SINGLE-SOURCE]; only after bench check | S2 A10, A11 |
| F3 (VVT) 3 A hold part (2920, not drop-in for 1812) | not located | Motherboards | [PARTLY] | S1 Part 2 C042 |
| Firmware: `acSwitchMode=PI_PULLUP` for 1989-95 and 2001-05 (clutch stays default); fit R21/R22 by hand | firmware year presets (`miataApplyYearPreset`; file not located) | 1989-95, 2001-05 | [PARTLY] | S1 Part 2 C003 |
| Firmware: idle PID limits (min must be below max) | NA6/NA94 presets; upstream min set at mazda_miata_1_6.cpp:146 | 1989-95 | [PARTLY] | S1 Part 2 C084 |
| Firmware: tach output none on 1989-95 (current repo already calls `miataNoTachOutput()`; ordered firmware does not) | firmware presets | 1989-95 | [PARTLY] | S1 Part 1 item 2 |
| Firmware: `fan2AcMode=Relay` on 1999-2000 and 2001-05, ONLY after confirming on a car which relay the stock ECU uses | firmware presets | 1999-2005 | [PARTLY] | S1 Part 2 C082 |
| Firmware: fill `mapEstimateTable` (about 35-45 kPa idle to about 95 kPa WOT); `boostCutPressure` about 160 kPa; lambda protection and CLT rev limit on | firmware presets | All | [PARTLY] | S1 Part 4 C016 |
| Firmware: dwell from coil data, correction above 1.0 at 8-11 V; LTFT off or documented | firmware presets / prepend.txt | All | [PARTLY] | S1 Part 4 C078, C085 |
| Firmware/doc: say 2001-02 and 2003-05 need different presets | INSTALL.md | 2001-05 | [CONFIRMED] | S1 Part 4 C091 |
| Wideband firmware: cherry-pick upstream 9295698 and 91aa7c6 after diff review; enable IWDG in the heater loop | wideband firmware pin | Daughterboard | [PARTLY] | S1 Part 4 C075/C080 |
| Docs: README row for 2T (INSTALL already warns); README labels 1L "fan relay" and 1M "vehicle speed" are wrong for 1991 (fan is on 1R) | repo/README.md | 1989-93 | [PARTLY] (1991 diagram only) | S1 Part 3 |
| Docs: harness-header sourcing text ("salvage or clone only" is wrong for 174917-6 and 178780-1) | README | All | [PARTLY] (S3 section 5) | S2 "Cheap ways"; S3 section 5 |
| Docs: wideband heater PTC F1 hold figure (VERIFICATION.md says 2.4 A; datasheet gives 1.99 A at 60 C, 1.34 A at 85 C) | VERIFICATION.md | Motherboards | [PARTLY] | S1 Part 2 C038 |

---

## Sources used

Notes: kb/boards B01, B03, B04, B17, B18; kb/parts P15 (diode audit), P16 (PTC fuses) via cluster verdicts; kb/pinouts PIN-8993/9495/9697/9900/0105 A and B (summaries, step 3 and disagreement sections); kb/firmware F01, F02; kb/parts_manifest.md and .json.
Clusters and verdict notes: C001-C008, C010-C011, C014-C018, C022, C031-C067, C075, C077-C080, C082, C084-C087, C091, C095-C097, C101-C104, C106-C107, C123, C135 (corrected statements from `kb/verify/verdicts.jsonl`; C055 and C062 noted `kb/verify/*-both.md`).
Re-checked today (2026-11-16) with `tools/lcsc.py`: C17971 (62 ohm 1206, $0.0053 at 1, 123,034 in stock), C25341 (620 milliohm, confirms the error), C48985884 (1.1 A PTC, $0.0869 at 1, 25,590 stock), C960026 (BSMD1812-200-30V, 194,229 stock, $0.0887 at 50), C70077, C70960; C25091 (220 ohm 0402) and C22962 (220 ohm 0603, basic) from the manifest and a live search. A script over `kb/parts_manifest.md` compared every resistor's schematic value to its LCSC description; R110 was the only mismatch. `evidence/ord_db/fab_*_jlcpcb_bom.csv` contains C25341 (confirmed on the ordered board).

## Fact-check log

Checked 2026-11-16: about 95 claims (every LCSC code, price, stock figure, resistor value, designator and net in Part 1 and 2, every confidence tag against `kb/verify/verdicts.jsonl`, the Part 3-6 statements against verifier corrected statements).

Corrections made
- Item 4: U4 USBLC6-2SC6 (SOT-23-6) is on the five motherboards, not the daughterboard (daughterboard U4 is the SOT-223 LDL1117). Board column fixed. SOT-23 rotation wording narrowed to the verifier's version.
- Item 12: series resistors are R61/R63 (4.7k); R62/R64 are the 1k pull-ups (pcb_nets, footprints). Rework suggestion softened to "only if the scope shows a problem".
- Item 7 (C045): R11 pad 1 is on +12V on the ordered board, but on VBAT_IN in rev 0.10 (interconnect.md). Marked ordered-only.
- Item 9 (C006): rev 0.10 already has F1 C883150 (1.1 A) and L1 C177247; stated. 6 V sag marked an unmeasured extrapolation.
- Stage 5: "harness cavity 1B" is the battery cavity only on 1989-95 and 1999-2000; it is 4B on 1996-97 and 4AF on 2001-05.
- Item 2 (C002): removed the unsupported "2I is the igniter's signal line"; verifiers say direction is unsettled. Ordered firmware has no `miataNoTachOutput()`; current repo firmware calls it for NA6 and NA94 only.
- Item 5 (C097): TE drawing was seen for the 76-pos header only; 1999-2000 (64-pos) has no drawing; "marginal, not shown to fail".
- Item 6: JP1/J3 are motherboard parts; "left two pads" replaced by pins 1-2 (README: EXT is 2-3, STOCK is 1-2).
- Item 11: R21/R22 are motherboard parts.
- Stage 6: clamp wording replaced by datasheet values (VCLTH 36 V min, VCLAMP 40-55 V at 3.5 A); D3/D4 figure marked unchecked.
- Tags downgraded from [CONFIRMED] to [PARTLY] to match verdicts: C084 (also "unstable"/"far too high" softened), C085, C041.
- Part 2: severities and order now follow verdicts (C082, C097, C042, C038, C102, C059, C033, C107, C043/C123, C104, C054/C035, C101 are low; only C003, C022, C015, C084, C016 are medium). C022 stock updated to 74-140 (140 live today). C043 applies to current boards only (ordered use Molex Micro-Fit LSU header). C038 F1 is the motherboard 2920 PTC. C042: C22446884 is 2920, not a drop-in for 1812. C101 is the rev 0.10 F1.
- Part 4: C040 tach cavity is 3O only on 2001-05 (4L 1996-97, 2K 1999-2000); C078 over-dwell wording per verifier; C075/C080 and C082 qualified; C053 marked an unverified estimate; DRC note and copper figure qualified.

Confirmed unchanged: C25341 = 620 mohm 1206W4F620LT5E at R110 on LSU_RT/LSU_IP in ord_db and cur_db BOMs; C17971 62 ohm $0.0053 at 1, 123,034 stock; C48985884 $0.0869, 25,590; C960026 194,229, $0.0887 at 50; C46641168 stock 57 (LCSC 55); C124412 stock 65; C70077 0.5 A, C70960 500 mA 0.3 ohm; C25091 and C22962 220 ohm, under $0.002; C23162 4.7k; TCAN1042 207; F405 C56621 about $1.8 more at 100 ($5.37 vs $3.57); R110 is the only resistor value/description mismatch (re-run over the manifest, 111 lines); DRC counts (0 unconnected, 199 lib-footprint, 57 net-conflict).


## Cross-section pass

- Item 13 (1999-2000 header): added that the current rev 0.9 board uses the 76-position 178780-1 (checked in repo/motherboards/1999-2000/README.md line 48); 176122-6 is needed only for the ordered rev 0.7 boards; added "confirm against footprint, check live stock".
- Part 2 C022: replaced "consign" with buy franchised stock or split the lot (see S3 lever 8); stock reading harmonised to 72-140 with the C018 verdict's 96.
- Part 2 and Part 4 C084: restated with the verified file:line references (mazda_miata_1_6.cpp:146 min 20; miata_board.cpp:224 max 10; engine_configuration.cpp:525 max 20; call order not traced). Minimum is at or above maximum.
- Added "confirm part against footprint and check live stock" to the Molex 43650-0200 and 1x40 socket purchase recommendations.
- New Part 7, consolidated change list for the next revision.


---

# S2. Parts that can be removed for free, and cheaper alternates JLCPCB stocks

Date of all prices and stock: 2026-11-16, JLC assembly library via `tools/lcsc.py`, prices at qty 30 unless stated. "DB" = daughterboard, "MB" = motherboard. The ordered boards (DB rev 0.9, MB 0.11 / 0.9 / 0.7) already carry the parts below, so every change here is for the next order or the next revision. The one exception is hand rework before first power-up, which I do not recommend for any item in this section.

## Summary

The honest answer is that very little on these boards is free to remove. The board is already lean: the verifiers killed or narrowed most "remove" ideas because each part protects something. What is left:

1. Four same-footprint swaps (B2-B5) save about $1.6 per set. Only B2 is [CONFIRMED]; B3 (hot leakage, polarity) and B4 (D6 forward surge, brand data missing) are unproven and B5 is partly verified, so treat the $1.6 as pending a bench check, not as "low risk, no test".
2. One swap needs a short bench test and saves about $8.8 per set: the eight VND7NV04 injector drivers to NCV8401B (same DPAK footprint).
3. The only large saving is the MAP sensor, about $17 per set, and it needs a new motherboard footprint.
4. Everything else is under $1.50 per set, and most of it needs a re-layout.

All of it together is about $29 per set, 7 percent of the $399 price. The supply risk on four parts (STM32F407VGT6, 2 A PTC, 40-pin socket, TCAN1042) matters more than the savings. Two of them have a drop-in fix today.

## Table A. Removals and consolidations

"Saving" is per assembled set (DB plus one MB) at qty 30, including the JLC fee share: $3.07 per distinct extended part per order (feeder loading, economic assembly), about $0.10 per board at 30 boards. The fee figure was confirmed on JLC's pricing page by the C072 verifier. Whether "preferred extended" parts are exempt from the fee is not stated on that page. I treat the exemption as unconfirmed.

| # | Part(s) | Boards | What it does today | What is lost if removed | Saving | Risk | Verdict |
|---|---|---|---|---|---|---|---|
| A1 | VR conditioner: U9 LM2903 (C7549) plus D15-D18, R51-54, R56-59, R73-R80, C48, C49, C60 (about 24 parts) | cur_db; ord_db carries it too | Conditions VR crank/cam signals that reach only AUX box header J5 pins 7-10 | An optional VR trigger input via J5, and a documented README feature ("two inputs for VR sensors"). No supported Miata uses it: NA CAS and NB CKP/CMP are Hall. Frees PE12/PE13 | about $0.25 plus 1 extended line ($0.10 per board) = about $0.35 | Low. Check firmware config for PE12/PE13 first; edit README and J5 labels | Make optional (DNP by default). [CONFIRMED] C116, P13.01 |
| A2 | U3 second TLS115B0EJ tracker (C3743696, $1.26 at 1) | cur_db, ord_db | Feeds only the on-board MAP (V5_SENS, 7-10 mA); no harness wire | Fault isolation between the MAP sensor and the +5V rail, and the USB-only bench behaviour changes (MAP might work on USB power, which today it does not; plausible, not tested) | about $1.1 (the extended line stays because U14 uses it) | Needs a netlist and layout change. Isolation value is untested | Next revision, owner decision. [SINGLE-SOURCE] C152, P07.06, B16.09 |
| A3 | U12 (74LVC4245 relay level shifter, TSSOP-24) | cur_db, ord_db | Drives the ZXMS6004FF relay gates and gates them with DRV_EN_N | The hardware backstop against MCU pins releasing as pull-up in reset. ZXMS6004FF is fully on at 3 V (Rds 600 mohm max, datasheet) so a 3.3 V pin does drive it | about $0.40 (part plus 2 x 100 nF) | Protection then depends on firmware only | Keep for the first build; revisit after bring-up. [PARTLY] C128 |
| A4 | D42-D49 external injector clamp (4 ES1D + 4 1.5SMC16A) | cur_db | Takes inductive-kick energy off the VND7NV04 | 0.3-0.6 W of driver margin at 14 mH or more (P09: keep if 12 mH or more), and the 1989-93 paired-injector case | about $0.86 (parts $0.66 plus 2 extended lines) | Injector inductance is unknown (8 vs 20 mH) | Keep until the inductance is measured. [SINGLE-SOURCE] P09 section 5 |
| A5 | Push-pull ignition stage: U6, U7 (TC4427), U13 (74HCT04), 8 resistors, 3 caps; replaced by open-drain ZXMS plus pull-up | cur_db | Drives IGN1-4 | Hard 5 V edge, noise immunity; the igniter's input behaviour is unknown | about $1.1 and 3 extended lines | Depends on igniter input data not in the repo; the 3.3k pull-downs R144-147 must also go | Keep. Reconsider only with igniter measurements. [PARTLY] C129, C151. Note: verdict C151 scopes the removal to Q16-Q19 and U13 (keeping D31-D34 and the 3.3k pull-downs), saving $1.5-2.6 per board, and warns the "Schottky-free 100 ohm" idea would remove short-to-battery protection; the part list and saving in this row differ from that scope (unsettled; S6 section 1.2 states the C151 scope) |
| A6 | IGN3/IGN4 and BOOST driver channels | cur_db | Only reach the optional AUX header (boost also via JP6 on 1989-95) | Coil-on-plug cylinders 3/4 and the boost solenoid output | about $2.0 + $2.7 at qty 1 (less at 30; sums not recomputed by the verifier) | Feature loss | Make optional by order tier. [CONFIRMED] connectivity only, C155 |
| A7 | Y101 crystal and its 2 caps (wideband F103) | cur_db, ord_db | F103 clock; upstream f1_rev3 runs HSI | CAN timing margin over temperature (HSI is -2/+2.5 percent), needs firmware change | $0.15-0.27 (C147) | Author chose HSE on purpose | Keep for the first build. [SINGLE-SOURCE] C154 |
| A8 | Y1 (F407 crystal) | cur_db, ord_db | USB OTG needs the HSE | USB | n/a | USB fails | Keep. [SINGLE-SOURCE] C147 |
| A9 | R7 + C16 input damper | cur_db, ord_db | Damps the L1/C17/C18 filter | Probably little, but unproven: the author's own Middlebrook estimate gives margin above 10x without it, and the 1-1.3 V ISO 2a figure is from the author's own ngspice model (verifier did not re-run it) | $0.10-0.12 | Hot-plug ringing not measured | Delete on the next spin only if a scope shows no ringing. [SINGLE-SOURCE] C148 |
| A10 | Consolidation: R144-R147 3.3k 1206 (C26032, extended) to 4.7k (C17936, basic, 2.08 M stock) | cur_db, ord_db | Gate pull-downs on the ignition outputs | 1.4x slower pull-down; 122 mW at 24 V | one extended line, about $0.10 | Low, but changes timing | Bench check, then do it. [SINGLE-SOURCE] C146 |
| A11 | Consolidation: FB1 BLM18PG221 (C80165, extended) to BLM18PG121SN1D (C14709, basic, 1.54 M stock) | cur_db, ord_db | VDDA ferrite | Filter changes from 220 to 120 ohm at 100 MHz; datasheet 2 A rating is higher | one extended line, about $0.10 | VDDA noise not measured | Bench check (ADC noise), then do it. [SINGLE-SOURCE] C146, P22 |

No removal on any motherboard turned up. The parts there are connectors, the MAP sensor, USB, PTCs and jumpers, and each is functional.

## Table B. Cheaper or better-stocked alternates

All stock figures and prices were read from `tools/lcsc.py` today. "Drop-in" means same footprint and same pinout.

| # | Current (LCSC, price at 30 / 100, library, stock) | Proposed (LCSC, price at 30 / 100, library, stock) | Saving per set | Differences that matter | Drop-in? | Confidence |
|---|---|---|---|---|---|---|
| B1 | 8 x VND7NV04TR-E, C155605, $2.0619 / $1.8164, extended, 2391 | NCV8401BDTRKG, C604055, $0.9606 / $0.8101, extended, 2500 | $8.8 at 30, $8.0 at 100 | Pins 1 gate, 2 drain/tab, 3 source in the datasheet (R08.01 read the pin table). Clamp 42-50 V; Rds(on) 23 mohm typ at 10 V (34 mohm max at 5 V); ILIM 25-35 A against 6 A, so a short draws 4-5x more current before it limits. I found no board-level protection in the repo sized for that (inference). Gate input current limit differs (0.1-0.5 mA). Applies to the boards that carry the 8 VND7NV04; the ordered 1989-93 board uses NCV8406A drivers with paired injectors and SMCJ30A clamps (S1 Part 5), a case this row did not assess | Yes (DPAK) | [PARTLY] C068, R08.01 |
| B2 | 2 x TCAN1042VDRQ1, C485806, $0.5957 / $0.5155, extended, stock 207 | TJA1042T/3/1J, C132227, $0.3142 / $0.2635, extended, 62,249 | $0.56 at 30, $0.50 at 100 | SO8. TJA1042 datasheet pin table: pin 1 TXD, 2 GND, 3 VCC, 4 RXD, 5 VIO (the /3 variant), 6 CANL, 7 CANH, 8 STB. VIO 2.8-5.5 V. Temperature -40 to 150 C (TCAN: -55 to 125 C). Both are 5 Mbps parts | Yes | [CONFIRMED] C089 |
| B3 | 11 x BAT54WS-7-F, C124205, $0.0937 at 50 | BAT54WS, C7502694 (hongjiacheng), $0.0127, preferred extended, 46,748; second source C3040452, $0.0128, extended, 73,420 | about $0.90, plus possibly one extended fee | I read the hongjiacheng datasheet: VF max 240 / 320 / 400 / 500 / 1000 mV at 0.1 / 1 / 10 / 30 / 100 mA, IR 2 uA at 25 V, CT 10 pF, Tj max 125 C (Diodes: 150 C), cathode line marks the cathode end. Hot leakage and the Fuxinsemi polarity were not verified | Yes (SOD-323) | [PARTLY] C081, P12.02 |
| B4 | D6 SMCJ30A Littelfuse C224048, $0.237 at 50 | MDD SMCJ30A, C408374, $0.1303 at 50, extended, 7064 | $0.11 | Datasheet read: VBR 33.3-36.8 V, Vc 48.4 V at 31 A, 1500 W, DO-214AB. Brand quality untested. MDD forward-surge VF is not documented, and D6 conducts forward in reverse-battery, so this swap is unproven | Footprint yes; D6 forward surge unproven | [PARTLY] C145, P06.10 |
| B5 | D12 SMAJ33A Littelfuse C223988, $0.1117 at 50 | MDD SMAJ33A, C113966, $0.0416, extended, 11,365 | $0.07 | Same VBR and Vc 53.3 V at 7.5 A; IFSM 40 A against 60 A, which should not matter because D12 sits behind D7/F1 | Yes | [PARTLY] C145, P06.11 |
| B6 | F2/F3 SMD1812-200-30 (hongjiacheng), C46641168, $0.1071 at 50, stock 57 (MB 1999-2005 only: 1 or 2 per MB) | BSMD1812-200-30V (BHFUSE), C960026, $0.0887 at 50, extended, 194,229 | $0.02 per fuse; this is a supply fix | I read the datasheet today (p.2 table, p.5 derating): hold 2.00 A, trip 4.00 A, Vmax 30 V, Imax 40 A, Rmin 20 mohm, R1max 100 mohm (one hour after trip or reflow), hold 1.45 A at 60 C and 0.80 A at 85 C. Same 1812 size | Yes | [CONFIRMED] P16, re-checked today |
| B7 | MAP U2 MPX5700AP, C90152, $27.49 at 30, stock 155 (also hand-fitted) | MPXHZ6400AC6T1, C511770, $10.45 at 30, $9.49 at 100, extended, 739 | about $17 at 30, $18 at 100 (assumes the 30-piece MPX5700AP price holds), less the SMT line fee | 20-400 kPa against 15-700 kPa, supply 4.64-5.36 V, SSOP-8 SMD with a different port arrangement. Hellen's NA6 board uses it. I did not read the HZ datasheet (only the MPXH6400A Rev 6 family sheet). The 400 kPa range is lower than the 700 kPa behind the store's "Boost ready" wording (S4), so adopting it would need that claim revisited | No. New MB footprint and hose adaptation | [PARTLY] C117, P20.04. Needs accuracy check against the 5700 and a port fit |
| B8 | U1 STM32F407VGT6, C12345, $4.0353 / $3.5739, extended, JLC stock 140 (LCSC 34) | Stay with ST: buy franchised stock (TME 1162 pcs at USD 9.97 at 1 per R10, 2026-11-16 note). Clone option: GD32F407VGT6 C115906, $2.97 at 90, 20,600 | clone: $0.6-1.0 | rusEFI does not officially support GD32 / APM32 / AT32 on F407; an open issue reports hard faults on APM32 | Footprint yes; firmware no | [SINGLE-SOURCE] R10.04, R10 note items 1-6. Do not ship a clone unvalidated |
| B9 | J / JD 40-pin socket JD1, JD2, C124412 B-2200S40P-A120, $0.3977 at 30, stock 65 | BOOMELE C9811 (1x40, round hole), $0.4648 at 30, 2865 | negative | Insulation height 3 mm against 8.5 mm: it changes the stack height | No | Not recommended (see section on rejected ideas). Buy C124412 elsewhere or order early (confirm the part against the board footprint and check live stock before buying). [CONFIRMED] listing |
| B10 | L1 FXL0530-2R2 (C177247), $0.1208 at 50 | Sunlord MWSA0503S-2R2MT, C408408, $0.1028 at 50, 9837 | $0.02 | Same listed 5.4 x 5.2 mm body (C158); land pattern not compared, Sunlord datasheet not read, LCSC returns no listing for C408408, automotive grade not shown; the cjiang part is labelled consumer grade. Applies to cur_db only (ord_db L1 is C70960) | Probably | [SINGLE-SOURCE] C158 |
| B11 | J5 box header 2x10 (no LCSC code) | BOOMELE C3405 (2x10), $0.1221 at 50, 42,623 | none, a sourcing fix | Same family as the ordered C3406 (2x8); the C3405 sheet was not read (pin length and height unchecked) | Probably (2.54 mm) | [SINGLE-SOURCE] C157 |

Notes on the stock-thin parts: the 2 A PTC and TCAN1042 have the drop-in swaps B6 and B2. MPX5700AP has only two real fixes: the SMD part B7, or buying the through-hole part from a distributor. MPX4250AP and MPX4115AP have 0 stock at JLC, and the MPX5700DP, GP and D variants are gauge or differential parts, not absolute, so they are not substitutes. The F407 has no ST-approved second source; B8 is a purchasing action. The 40-pin socket has no drop-in on JLC, so buy it on the open market (it is self-ordered, not JLC-placed).

## Total realistic saving per assembled set (DB + one MB)

| Group | Items | Per set at qty 30 | At qty 100 |
|---|---|---|---|
| (i) Low risk, BOM swap only (B3, B4 caveats above) | B2, B3, B4, B5 (+ B6, B10 as supply and cost cleanups) | about $1.6 (plus about $0.10 if the BAT54WS fee exemption is real) | about $1.5 |
| (ii-a) Bench test first, no re-layout | B1 (short-circuit and thermal test on all 8 channels), A1 (firmware check), A10, A11 | about $9.3 | about $8.5 |
| (ii-b) Next revision, new footprint or netlist | B7 (about $17), A2 ($1.1), A3 ($0.4) | about $18.5 | about $19.5 |
| All three | | about $29, 7 percent of $399 | about $29 |

If you do B1 on all eight channels, the separate idea of fitting the SOT-223 NCV8406A on Q5-Q8 adds only about $1.8 (the saving on four channels from $0.96 to $0.52), and it needs a new footprint. Do not do both. This corrects the $5.5 figure in P09.06 and C115, which compared against VND7NV04.

## What can be applied at the next JLC order with no re-layout

Savings are per set at qty 30 from the tables above. None of this is a zero-cost change recommended for the ORDERED boards: those are already at fabrication and this report recommends no rework for any item in this section.

| Change | Kind | Saving per set | Tag | Condition |
|---|---|---|---|---|
| B2 TCAN1042 -> TJA1042T/3/1J (C132227) | BOM swap | $0.56 | [CONFIRMED] | none beyond a footprint check; also fixes stock of 207 |
| B6 F2/F3 -> C960026 | BOM swap | $0.02 per fuse (supply fix) | [CONFIRMED] | 1999-2000, 2001-05 only |
| B3 BAT54WS-7-F -> hongjiacheng C7502694 | BOM swap | about $0.90 | [PARTLY] | hot leakage and polarity unverified |
| B4 D6 -> MDD SMCJ30A (C408374) | BOM swap | $0.11 | [PARTLY] | forward surge unproven (D6 conducts in reverse battery) |
| B5 D12 -> MDD SMAJ33A (C113966) | BOM swap | $0.07 | [PARTLY] | IFSM 40 A vs 60 A |
| B1 8 x VND7NV04 -> NCV8401B (C604055) | BOM swap | $8.8 | [PARTLY] | short-circuit and thermal bench test on all 8 channels; not assessed for the 1989-93 paired case |
| A1 VR conditioner DNP (about 24 parts) | DNP | about $0.35 | [CONFIRMED] connectivity | check firmware config for PE12/PE13; README and J5 labels |
| A10 R144-R147 3.3k -> 4.7k (C17936) | consolidation | about $0.10 | [SINGLE-SOURCE] | bench check first |
| A11 FB1 -> C14709 | consolidation | about $0.10 | [SINGLE-SOURCE] | VDDA noise check first |
| B10 L1 -> Sunlord C408408 | BOM swap | $0.02 | [SINGLE-SOURCE] | land pattern and grade unchecked; cur_db only |

Not applicable without re-layout or new footprint: B7 MAP ($17), A2, A3, A4 to A9.

## Checked and dismissed

* "Tracker U3 isolates nothing": [PARTLY] harness isolation is already done by U14; what U3 gives is current limiting and 85 dB PSRR on the MAP supply. A2 is a cost trade only.
* Shunt clamp on +3V3 is not removable: [PARTLY, info] C130 reproduced the injection arithmetic. D40/D41 can push roughly 0.2-0.43 A, far above the rail load. The clamp also protects against an LDO failure.
* C124205 clones with "7-9x cheaper" price: saving is $0.9 per board, not larger. Counted in B3.

## Ideas considered and rejected

| Idea | Why not |
|---|---|
| Clone F103 for the wideband (GD32, CKS32, CH32, APM32) | Saves about $0.2 (APM32F103C8T6 $0.95 against ST $1.14 at 30; C150 range $0.06-0.48); a web report (secondary, not rechecked) says GD32F103 failed an I2C bench test, and the repo flashes through the ST ROM bootloader (ID 0x410) and uses 12 MHz ADC clock and CAN, none tested on a clone (C150, R10.08). The best candidate would be APM32F103C8T6, C393540, $0.95 at 30, but it is untested here |
| Clone F407 | Firmware risk against $0.6-1.0 saving (R10.04) |
| VET6 / 512 KB flash F407 variants | Current firmware is 640-669 kB; will not fit (R10) |
| LMR14020 buck alternates (AP63205, TPS5430, XL1509, AP64200) | The cheaper ones fail 36 V or 85 C or use another pinout; saving at most one fee. Datasheets not read (P05.09) |
| B360A to SS36 | Both are extended at JLC; no fee saved, so no gain |
| ES1D to SS14 (C2480, basic) | Saves one fee but 40 V rating leaves little margin at 35 V load dump (P09 section 5) |
| SMBJ14A for 1.5SMC16A | About $0.5 per board, needs a new footprint and has less copper (P09 section 5) |
| NCV8406A on all injectors or L9826 octal driver | 2 A paired 1989-93 case and weaker protection; L9826 is itself rated "not recommended" (C115) |
| Plain MOSFET for VND14NV04 heater driver | Loses limiting and thermal shutdown; datasheet not read (C159) |
| Replace VND14NV04 | No cheaper equivalent with the same footprint (C159) |
| All status LEDs red or white (basic) | Removes 3 extended lines ($0.31 per set at 30) but loses colour coding. Not worth it (P22) |
| 6-layer to 4-layer | Estimated $3.4 per board at q=10 and $2.4 at q=50, but these come from the author's own price guesses (no JLC quote), and routing may need 6 layers. Quote both (C162) |
| 74HCT245 for the 4245A shifter | Not read, saves little (P11.10) |
| ESD0504F for USB ESD | Refuted (C156): the board already uses USBLC6-2SC6 (C7519); ESD0504F ($0.079, extended) gives no saving |
| Removing the 1N4148WS as clamp | Cannot replace BAT54WS: Vf 0.65 V at 2 mA puts a TTa pin at about 4.0 V, its limit (P12) |
| Non-JLC assembly to avoid extended fees | Out of scope here; see the cost-model note R21 |

## Cheap ways to cut fees that are not parts

* The harness header 174917-6 (48-pin) is buyable at LCSC C592838 ($12.9, stock 32) and elsewhere for $5-10. The "salvage only" statement in the README is wrong (C071), though S3 section 5 notes an unresolved pitch conflict for this part (DigiKey 3.50 mm vs LCSC 4.5 mm): confirm the part against the board footprint and check live stock before buying. It is not a saving but it removes a sourcing worry.
* The J1/J2 headers must be soldered while plugged into the motherboard sockets, so JLC cannot place them (C105).
* Each extended line costs $3.07 per order, and the manifest counts 38 non-preferred extended lines on cur_db and 35 on ord_db: about $117 and $107 per order. Cutting a line saves about $0.10 per board at 30 boards. This is why A1, A10 and A11 are worth doing at all.

## Sources used

* Notes: kb/parts P06, P07, P09, P12, P16, P20, P22; kb/research R08, R10, R21; kb/parts_manifest.md; kb/verify notes for C068, C072, C081, C089, C116, C117, C128, C129.
* Clusters: C068, C071, C072, C081, C089, C105, C115, C116, C117, C128, C129, C130, C145-C152, C154, C155, C157-C162. Findings: P20.04, R08.01, R10.04, B16.07, B16.09.
* Not opened this pass: R29 teardowns, R01, R03 and R30; the comparisons they hold were consumed through the clusters above (C151, C161). Table A reflects that.
* Re-checked today: `tools/lcsc.py` on C604055, C155605, C132227, C485806, C7502694, C3040452, C124205, C511770, C90152, C960026, C46641168, C408408, C177247, C408374, C224048, C113966, C223988, C14709, C80165, C17936, C26032, C3405, C3406, C459816, C54315, C12345, C124412, C9811, C2990873, C115906, C2802676, C3259058; TJA1042 pin table (datasheets/extra/TJA1042_nxp.pdf); NCV8401B ILIM and clamp (datasheets/extra/NCV8401BDTRKG.txt); BAT54WS hongjiacheng sheet; BSMD1812-200-30V sheet (datasheets/extra/C960026_BSMD1812-200-30V_lcsc.pdf, p.2 and p.5).

## Fact-check log

Claims checked: about 75 (all Table B prices, stock, tiers and savings; Table A designators, boards and savings; summary totals; all verdict marks against kb/verify/verdicts.jsonl).

Corrections made:
* Summary item 1 claimed four swaps need no bench test: B3 and B4 are only partly verified. Reworded; group (i) renamed "low risk".
* A3 (U12) listed cur_db only: U12 is also on ord_db.
* A4: driver margin loss is stated at 14 mH or more in P09 (keep if 12 mH or more), not "12 mH or more".
* A6: mark was [SINGLE-SOURCE]; verifier confirmed connectivity only and did not recompute the sums. Reworded.
* A7: saving $0.15-0.27 (C147), not $0.20-0.30.
* A9: "little lost / 1-1.3 V" came from the author's own ngspice model, not re-run, and hot-plug ringing is not simulated. Hedged.
* A2: USB-only MAP operation is untested. Hedged.
* B1: clamp is 42-50 V (datasheet), added 34 mohm max at 5 V; "no protection sized for 25-35 A" marked as inference.
* B4/B5: marks were [SINGLE-SOURCE]; C145 verdict is PARTLY. Added that MDD forward-surge VF is undocumented and D6 conducts forward, so the SMCJ swap is unproven. B5 IFSM 40 A vs 60 A checked in the datasheets.
* B6: "R 100 mohm max" is R1max (post-trip/reflow), Rmin 20 mohm. Derating 1.45 A at 60 C and 0.80 A at 85 C checked in the datasheet.
* B7: the "$18 at 100" figure assumes the 30-piece MPX5700AP price (no 100 tier shown).
* B10: "same land pattern" is not established (C158); cur_db only, since ord_db L1 is C70960. Drop-in changed to "Probably".
* B11: drop-in changed to "Probably" (C3405 pin length/height unchecked).
* Dismissed list: C130 verdict is PARTLY, not CONFIRMED. U3 line reworded per C152.
* Rejected list: F103 clone saving was "$0.15-0.35 at most", now about $0.2 with C150 range; the GD32F103 I2C failure is a secondary web report. ESD0504F row: C156 was refuted (USBLC6-2SC6 already in use). 6-layer to 4-layer figures come from the author's own price guesses.
* Fee source wording adjusted (verifier fetch, not "verified 2026-11-15").

Re-checked live today and found correct: prices, tiers and stock for C155605, C604055, C485806, C132227, C7502694, C3040452, C124205, C511770, C90152, C960026, C46641168, C408408, C177247, C408374, C224048, C113966, C223988, C14709, C80165, C17936, C26032, C3405, C124412, C9811, C115906, C12345, C592838, C3743696, C393540. Also checked: A1 part list (24 parts, design.py), BAT54WS hongjiacheng datasheet values, NCV8401B ILIM and gate current, TME 1162 pcs at USD 9.97 (R10), 38/35 extended-line counts (C072).

Still unverified: TJA1042 vs TCAN pin and temperature details (relied on C089 confirmed verdict); ZXMS6004FF Rds figure (C128); A5 and A3 savings and igniter behaviour; hot leakage and Fuxinsemi polarity (B3); MPXHZ6400 accuracy and port fit; BOOMELE C3405 datasheet; the 3.07 USD fee exemption for preferred parts; the $0.20-0.40 part prices in A3/A5 (from manifest, not re-fetched); qty-100 column of the totals table; P09 section 5 alternates; MPX5700 variants (DP/GP/D) not substitutes.

## Cross-section pass

- Summary item 1: B3/B4/B5 no longer described as low risk; $1.6 is pending a bench check.
- A5: noted that verdict C151 scopes the ignition-stage removal differently (Q16-Q19, U13, $1.5-2.6); marked unsettled.
- B1: added that the ordered 1989-93 board uses NCV8406A with paired injectors (S1 Part 5), not assessed here.
- B9 and the 174917-6 bullet: added "confirm part against footprint and check live stock", and the S3 pitch conflict.
- New block "What can be applied at the next JLC order with no re-layout"; states no zero-cost change is recommended for the ordered boards.


---

# S3. What a board set costs to make, and how to make it cheaper

Prices as of 2026-11-16. USD. A "set" is one daughterboard plus one motherboard, built and hand-finished, ready to ship in the customer's own stock case (no enclosure included). Every figure is an estimate unless marked as a quote or a live lookup. No JLCPCB quote could be obtained for bare PCBs, so the PCB lines carry about +-40 % uncertainty. They are small lines, so the totals do not move much (about +-$4 per set at 30).

## 1. Bottom line

- A set costs about **$208 to make and deliver at batch 5, $153 at 30, and $142 at 100**. These headline totals carry about +-$15 per set: the PCB lines (+-40 %), freight (a guess) and whether the 35 % duty applies to JLC-bought parts (a $13-17 swing) are all unverified. Outbound postage uses S5's 2 lb row (the packed parcel is about 1.2 lb, calculated not weighed); the earlier figures were $207 / $152 / $141.
- Three costs dominate: the JLC-built SMD part of the daughterboard (parts plus fixed fees), the MAP sensor, and the US duty JLC collects. The bare PCBs are only about $6 to $12 per set.
- The cheapest large saving is organisational, not a part swap: **order one daughterboard batch for all four years and buy one daughterboard run, not four**. That saves roughly $18 to $25 per set against four small per-year runs.
- Three of the four harness headers appear to be buyable from Newark/Farnell and RS in cut quantities (distributor stock and prices are aggregator snapshots, not live-checked; see section 5). Only the 64-position 176122-6, used on the ORDERED 1999-2000 board (rev 0.7), has no good source; the CURRENT 1999-2000 board uses the 76-position 178780-1, so buy 176122-6 only for the ordered boards. Salvage is not worth it.

## 2. Cost table per assembled set

Design assumed: current daughterboard rev 0.10 (6 layers, 330 placements, 38 non-preferred Extended lines) plus motherboard 1989-95 rev 0.13 (2 layers, 17 SMD parts, 4 Extended lines). Batch = number of sets, one year variant, one order of each board, JLC Economic assembly (Standard at 100, forced by the 50-board Economic limit).

| Line (per set) | Batch 5 | Batch 30 | Batch 100 | How it is derived |
|---|---|---|---|---|
| Bare PCB, DB 6-layer ENIG + MB 2-layer | 12.2 | 8.0 | 6.3 | ESTIMATE. One JLC anchor only (6-layer 100x100 5 pcs "from $35.1"); rest scaled. R21 A10 |
| SMT assembly: setup, stencil, Extended-part fees, joints | 30.8 | 6.6 | 5.7 | Computed from JLC fee page of 2026-10-22. DB fixed fees about $123-128 per order (setup $8.18 + stencil $1.53 + $3.07 x 37-38 lines) + MB $22 per design, + $0.0016 x 1094 joints |
| SMD parts bought by JLC | 49.3 | 42.3 | 37.8 | JLC library tier prices. STM32F407VGT6 $5.05 (1), $3.57 (100) live today. No attrition added; real cost is a few % to a few dollars per order higher |
| Hand-fitted through-hole parts | 40.9 | 37.7 | 36.7 | MAP sensor $29.12 (5) / $27.49 (30+), sockets $0.6-1.1, 48-pin header $5.7-7.7, DB 1x40 pins, JST, box header, shunts, M3 hardware about $2 (hardware is a guess) |
| Inbound freight, JLC to you | 7.0 | 2.5 | 1.8 | GUESS from forum reports, no JLC rate table is public |
| US duty prepaid at JLC (35 %) | 32.3 | 19.9 | 17.4 | 35 % x PCB + assembly + SMD parts. Section 4 |
| Payment fee | 11.9 | 11.9 | 11.9 | 2.9 % + $0.30 of $399. From memory of Shopify US card rates, NOT verified; excludes monthly plan fee |
| Packaging | 3.3 | 3.3 | 3.3 | S5 bill of materials, $3.3-3.6 per unit at 25-100 units (the earlier $3.0 was an assumption) |
| Outbound shipping, US (postage + signature + cover, no packaging) | 20.7 | 20.7 | 20.7 | S5: USPS Ground Advantage commercial, 2 lb row (parcel about 1.2 lb) $8.39-13.42 + Signature Confirmation $4.15 + $6.05 cover = $18.6 (zone 1) to $23.6 (zone 8), $20.7 at zone 5. The earlier $20 used the under-16 oz row ($7.33-8.95, verifier C119 $18-21); that parcel weight is not achievable per S5 unless the packed unit is under 16 oz (saves about $1-4.5). Weight is calculated, not measured: weigh the first packed unit |
| **Cost per set** | **208** | **153** | **142** | Zone 1 to zone 8 postage moves each total by about -$2 to +$3 |

Variants and what changes:

| Variant | Change per set vs the table | Why |
|---|---|---|
| ORDERED daughterboard rev 0.9 (4 layers, 302 placements, 35 Extended lines) | about -$11 / -$6 / -$5 at 5 / 30 / 100 | Lower PCB and fee cost, same duty rate. R21 model 74.5 / 47.6 / 41.6 per board |
| 1996-97 motherboard (76-pin 178780-1) | +$7 / +$6 / +$5 | Header $15.0 / $12.2 / $10.9 instead of $7.7 / $6.5 / $5.7 (Newark CAD at 0.72, which is an assumption) |
| 1999-2000 motherboard (76-pin, 5 Extended lines) | +$8 / +$6 / +$5 | Same header plus one more Extended line |
| 2001-05 motherboard (72-pin 353830-5) | +$2.4 / +$2.2 / +$2.3 | Header $10.1 / $8.7 / $8.0 |
| ORDERED 1999-2000 board (64-pin 176122-6) | header $12-18 (broker) or $29.99 (Ballenger) | Section 5 |

**Before / after the S2 changes (batch 30, one year variant).** Savings are S2's per-set figures at qty 30, subtracted from the revised $153 and not adjusted for duty (if the 35 % duty applies to JLC-bought parts, S3 assumption 3, the true saving on those parts is up to about 35 % higher).

| Case | Savings (S2) | Cost per set at batch 30 | Needs |
|---|---|---|---|
| Today (current design) | 0 | about $153 | |
| After S2 group (i): B2, B3, B4, B5 (B6, B10 as supply cleanups) | about $1.6 | about $151 | B3 and B4 unproven; BOM-only |
| After (i) + (ii-a): B1, A1, A10, A11 | about $9.3 more | about $142 | B1 needs a short-circuit and thermal bench test; A1 a firmware check; A10/A11 a bench check; no re-layout |
| After all, incl. (ii-b): B7 MAP, A2, A3 | about $18.5 more (about $29 in total) | about $124 | New motherboard footprint (B7) and netlist/layout change (A2, A3); B7 changes the pressure range |

What is not in the table: the Bosch LSU 4.9 sensor, AEM harness 30-3427, TPS kit, vacuum hose and any case (the self-order BOM treats them as customer or car items); returns and warranty; the monthly Shopify plan; customs broker fees (none expected at this volume, C021).

## 3. Assumptions you may want to change

1. DB parts and fees come from R21's model, rebuilt against the live manifest. The verifier counted 38 (rev 0.10) and 35 (rev 0.9) non-preferred Extended lines, not 37 and 34 (C072). That adds $3.07 per order, which is under $1 per set at batch 5.
2. One batch means one order per board design. Four motherboard designs each pay about $22-25 in fixed JLC fees.
3. Duty is charged on the JLC invoice lines for PCB and assembly. Whether JLC also taxes the parts it buys is not stated by JLC [NEEDS MEASUREMENT: read the DDP line on a real checkout]. I assumed yes for the SMD parts. If it does not, subtract about 35 % of the SMD-parts line ($17 / $15 / $13).
4. Stock risk at batch 100: STM32F407VGT6 C12345 has 140 pieces at JLC today (readings across today ranged 72-140), the TCAN1042 about 207, the 1x40 socket 65, the MAP 155. A 100-set run is not buildable from JLC stock without consignment or a second lot (C022, C106).

## 4. US duty on 2026-11-16: why R21 and R26 disagree, and what to budget

R21 says 35 %; R26 says about 15 % (2.7 % + 12.5 %), possibly 40 % or more. They are answering different questions.

- **35 % is what JLCPCB charges you.** JLC pre-collects duty on US DDP orders at a flat 35 % on PCB and assembly lines (stencil 90 %), as an average with no later true-up. Individuals must use DDP. The source is JLC's own tariff FAQ (updated 2026-10-29) and the rate image Tariff-us.png. The verifiers re-read both [CONFIRMED as JLC's charge].
- **15.2 % is R26's statutory stack for a finished ECU**: 2.7 % MFN (HTS 8537.10.91.60, CBP ruling N275130; USITC lookup) plus the 12.5 % forced-labor Section 301 duty in force since 2026-07-24. It omits the older China Section 301 25 %. R21 adds that 25 %, giving about 40 %. Whether 8537.10.91 is on the legacy Section 301 lists is **not verified by anyone**; my search today did not settle it either [SINGLE-SOURCE, unresolved]. JLC treats assembled boards as "intermediate products", which also means the exemptions for finished electronics do not apply.
- De minimis is gone (CBP, Federal Register: non-postal 2026-06-24, mail 2026-07-24; verified in R26). The IEEPA end (notes disagree: 2026-02-20 or 02-24) and the end of Section 122's 10 % on 2026-07-23 are secondary-source only [UNVERIFIED]; they do not change the 35 % budget.

**Budget 35 %.** It is the amount that will actually appear on the checkout, so it is the planning number. Real liability if you became importer of record (a company can choose CPT and pay actual duty) could be anywhere from about 15 % to 55 %. At batch 30 each 10 points is about $5.7 per set. Do not rely on the repo's own "at least 15 %" figure as a ceiling. Do not move parts to the US to avoid duty until JLC shows which lines are taxed. The MAP sensor and other through-hole parts are already outside the JLC invoice in my table, which is why they carry no duty.

## 5. Harness header sources (3 of 4 apparently buyable)

Prices are from Findchips/aggregator snapshots of 2026-11-16 (secondary) and live LCSC lookups today. Newark is in CAD; I converted at 0.72, an assumption. TE's own pages say all four are "Active but not currently available", so TE is not a source. Stock moves daily: re-check before ordering. Live-checked today: LCSC/JLC stock and prices of C592838 and C5166246. Newark, RS, DigiKey and marketplace stock and prices are aggregator snapshots [SINGLE-SOURCE]; the verifiers did not re-check them, and 353830-5 was not checked by any verifier. The pitch of 174917-6 is described differently by DigiKey (3.50 mm) and LCSC (4.5 mm); R24 did not resolve it from the TE drawing, so confirm the part against the board footprint before buying 12-15.

| Part | Used on | Best source and stock | Price | Fallback |
|---|---|---|---|---|
| 174917-6, 48-pos | 1989-95 | Newark/Farnell 471 | CAD 10.66 (1), 9.36 (10), 7.90 (100) = about $7.7 / 6.7 / 5.7 | LCSC/JLC C592838, 32 in stock, $12.92 (1) to $12.16 (100). Marketplace Greenchips 2,929 at about $4.47, unknown provenance. RS UK GBP 7.41 |
| 178780-1, 76-pos | 1996-97, 1999-2000 current | Newark 160; DigiKey NL 1,887 at EUR 16.05, 27-week lead (P19b note, not re-checked) | CAD 20.85 / 18.60 / 15.09 = about $15.0 / 13.4 / 10.9 | LCSC C5166246, 18 in stock, $24.98 |
| 353830-5, 72-pos | 2001-05 | Newark 153; RS 14 at $5.67 | CAD 14.03 / 13.03 / 11.05 = about $10.1 / 9.4 / 8.0 | Alternate 1123038-2 (Avnet MOQ 2520, footprint not checked) |
| 176122-6, 64-pos | ORDERED 1999-2000 (rev 0.7) only; the CURRENT 1999-2000 board uses 178780-1 (repo/motherboards/1999-2000/README.md line 48), so buy only enough for the ordered boards | No authorised cut stock; reel MOQ 1600 | Sager min 160 at $12.61; brokers about $10-20 for about 510 units (stale data) | Ballenger CONN-100747, $29.99, identity unverified. Do not substitute the 76-pos header without a fit check; the footprint is reported different (about 20.7 mm shift, not re-derived by verifiers, C014) |

Salvage: used ECUs cost $150-190 (NA6/NB1) and $285-450 (NB2). A header is $6-15 new. Salvage only gets you a case. Clone headers (Kinkong etc.): no price, no quality data, do not use without a tested sample. The repo's "not available, salvage or clone" wording looks wrong for 174917-6 and 178780-1 (verifier-confirmed purchasable, C071) and probably 353830-5 (aggregator only).

## 6. Levers ranked by saving per set

Basis: batch 30 unless stated. "Duty" counts the 35 % that rides on JLC-invoiced lines.

| Rank | Lever | Saving per set | Cost in risk or work | Confidence |
|---|---|---|---|---|
| 1 | One DB run for all four years instead of four small runs (e.g. 30 DB + about 8 of each motherboard instead of four 8-set runs) | $18-25 (DB falls from about $73 to $52 per board; MBs rise about $2.7) | Cash tied up in 30 DBs; you hold stock across years | [PARTLY] model, PCB lines estimated |
| 2 | Batch size 5 to 30 of one year | $55 on SMT side, $12 duty, $4.5 freight | About $3.4k cash at 30 (DB $1.6k, MB $140, duty $600, hand parts $1.1k). Needs a design that works | [PARTLY] fee table verified, PCB estimated |
| 3 | MAP sensor from Mouser instead of JLC/LCSC | $8-10 | Aggregator figures from the writer's web search (Mouser 1,761 at $19.61, DigiKey 0 at $21.96) are not in any note, and R-notes recorded Mouser stock 74 on 2026-10-31. NRND status is unconfirmed (P20). Check live and buy a reserve | [UNVERIFIED] |
| 4 | Cut Extended lines (38 now; merge three BAT54 variants, three LED colours, three 1206 resistor values, TVS families) | $3.07 per line per order, x1.35 with duty. 10 lines = $1.4 at 30, $8 at 5 | Part changes need datasheet checks by the alt-part section | [CONFIRMED] fee rate (C072, live price page); line count 38 verified from manifest |
| 5 | 6 layers to 4 | about $3.6 including duty (PCB estimate, unverified) | Rev 0.10 is routed for 6 layers; 4-layer needs relayout. The 4-layer needs epoxy via fill, which is free only at 6 layers, price unknown. Not recommended for $3.6 | [NEEDS MEASUREMENT]: one JLC quote of both stackups |
| 6 | Order a bigger lot only to reach Standard at 100 | $0 | Standard needs edge rails. Two 50s on Economic cost about the same in the R21 model; the Standard edge-rail fee is unknown | [PARTLY] model |
| 7 | JLC fits motherboard through-hole parts | Saves 10-20 min labour, costs $3.1 per board + $3.58 per order | Header 174917-6 stock 32, 178780-1 stock 0, so only partly possible. DB headers must be soldered in the sockets and stay with you (C105) | [PARTLY] |
| 8 | Consign MCU or other scarce parts | negative: HK warehouse, 2 % fee (min $10), refundable duty deposit | Only to cover stock outages. MCU at JLC ($3.6-5.05, live) is cheaper than the distributor prices quoted in the notes (TME $8.70-9.97, not re-checked). The HK warehouse, 2 % fee and duty-deposit terms were not re-verified | [UNVERIFIED] |
| 9 | Panelisation, board area, double-sided placement | $0 | Fees are per design and per joint. MB cannot panelise (250x250 limit). DB cannot get under 100x100. All parts are top-side | [PARTLY] fee structure per R21; not quoted |
| 10 | Ordering in multiples of 5 | not shown | No source on JLC's price steps. Quote it | [NEEDS MEASUREMENT] |
| 11 | S2 B1: 8 x VND7NV04 -> NCV8401B (C604055) | $8.8 at 30, $8.0 at 100 (S2; not duty-adjusted) | Short-circuit and thermal bench test on all 8 channels; current limit 25-35 A vs 6 A; not assessed for the ordered 1989-93 paired-injector board. See S2 B1 | [PARTLY] |
| 12 | S2 B7: MAP MPX5700AP -> SMD MPXHZ6400AC6T1 (C511770) | about $17 at 30, $18 at 100 (S2), less the SMT line fee | New motherboard footprint and hose fit; 400 kPa vs 700 kPa range; HZ datasheet not read. See S2 B7 | [PARTLY] |

Via-in-pad: current rev 0.10 on 6 layers gets the epoxy fill and cap by default at no charge (JLC capabilities page, read by B08; the C005 verifiers did not re-check this default). So the expensive-process worry only applies to the 4-layer ORDERED boards, where fill is an optional paid extra. **Check the JLC order confirmation for "epoxy filled and capped" on ordered rev 0.9 now.** It is free to check; it cannot be fixed later. If it was not filled, expect solder voids or starved joints (not necessarily open joints) on the eight DPAK tabs (about 25 vias each) and on some of the roughly 250 or more vias in small pads; counts of vias in pads range 500-660 by counting rule.

## 7. Recommended plan for the next batch

1. **Do not order a production batch yet.** No board has been built. Build and bring up the ordered boards (4 DB + 5 MB) first. Cost of finding a layout error after a 30-board run is $2k+.
2. After bring-up, order **one 6-layer rev 0.10 daughterboard lot of about 30** on JLC Economic (stays under 50, 255 C reflow fixed, check heat-sensitive parts). Hold the stock lot for all years. Bring-up covers the ordered 4-layer rev 0.9, not rev 0.10 (6-layer stackup, new F1/L1, new routing), and R110 is wrong in rev 0.10 too, so a rev 0.10 fix list must precede the order: see S1 Part 7 (consolidated change list for the next revision).
3. Order motherboards **per validated year at about 8-10 each**. Each design costs $22-25 fixed plus about $2.5-3 per board, so over-ordering a little is cheap. Do not order 1996-2005 until the outline and mounting holes are measured from real cases (documented as placeholders).
4. Use JLC **Combine Shipping** to merge the DB and four MB orders into one parcel. Check the DDP line and freight at checkout; replace my freight guess and the unconfirmed duty-on-parts assumption with those numbers.
5. Buy harness headers from **Newark/Farnell/RS** in lots of 12-15 per year now (about $90-200 total; the stock and prices are aggregator snapshots and the 174917-6 pitch conflict is unresolved, so confirm each part against the board footprint and check live stock before buying). Buy MAP sensors after a live price and stock check (LCSC/JLC C90152 is $27.5-29.1 live; a Mouser price is unverified), plus 20 % spares. Buy 1x40 sockets in one LCSC cart (stock 65 limits runs above about 30).
6. Re-check STM32F407VGT6 stock the day you order (140 today). If short, split the lot or consign. STM32F405VGT6 C56621 (1,050 in stock, $1.8 dearer at 100) is a pin-compatible hedge but rusEFI build support is unconfirmed.
7. Before batch 100: ask a customs broker or CBP for an HTS ruling on 8537.10.91 and the legacy Section 301 status. Each 10 points of duty is about $5.7 per set.

## Checked and dismissed

- "A 100-board run needs JLC Standard and costs much more": Standard at 100 costs about the same as two Economic lots of 50 (R21 model: $4.16 vs $4.13 per board assembly; edge-rail fee unknown). No saving either way.
- "The DB is about 430 parts": it is 330 (302 on the ordered board). Overstates SMT joint cost by about 30 % only, a few cents per board.
- "Hand-assemble the motherboard SMD parts": loses beyond about 5 boards (B05).
- "Harness headers are unobtainable": wrong for 174917-6, 178780-1, 353830-5 (C071).
- J1 header stock of 32 does not limit a JLC run because the header is hand-fitted (C106 corrected).

## Sources used

Notes: kb/research/R21-jlcpcb-cost-model.md, R22-alternative-manufacturing.md, R24-harness-connectors-and-enclosures.md, R26-shipping-and-customs.md; kb/boards/B04, B05, B08; kb/parts_manifest.md. Clusters (verifier versions): C005, C014, C021, C022, C024, C071, C072, C105, C106, C119, C162. Self-order BOMs in evidence/cur_db and cur_mb8995 and repo/additional-parts/order_all_boards.csv.

Re-checked today (2026-11-16): tools/lcsc.py live for C12345 (stock 140, $5.05 / $3.57), C56621, C90152 (stock 155, $29.12 / $27.49), C592838 (32, $12.92), C5166246 (JLC 0, LCSC 18), C124412 (65), C2977586, C412098, C3405, C5305, C49257. Web search for MPX5700AP prices (aggregator, SINGLE-SOURCE) and for Section 301 listing of 8537.10.91 (not resolved). Model script: work/report/S3-cost-model/m.py.

## Fact-check log

Checked 2026-11-16, about 60 claims (live lcsc.py lookups, parts_manifest, R21/R24/R26/P19b/B08 notes, verdicts for C005, C014, C021, C022, C024, C071, C072, C105, C106, C119).

Verified: LCSC/JLC stock and prices for C12345 (140; $5.05 to $3.57), C56621 ($5.37 at 100, so $1.8 dearer), C90152 ($29.12 / $27.49), C592838 (32; $12.92 to $12.16), C5166246 (JLC 0, LCSC 18, $24.98), C124412 (65). Cost-table arithmetic reproduced with m.py (207.3 / 151.9 / 140.6; margins 48 / 62 / 65 %). Fee rates and Extended-line counts (38 / 35), USPS rate arithmetic, the 35 % JLC duty and the 15.2 % statutory stack match the sources.

Corrections:
- Bottom line and section 5 title said the headers are buyable; Newark/RS/DigiKey figures are aggregator snapshots, so reworded to "appear buyable" and the [CONFIRMED] tag was replaced by what was actually live-checked.
- 353830-5 was claimed as confirmed; no verifier checked it. Marked aggregator-only.
- Added the unresolved 174917-6 pitch conflict (DigiKey 3.50 mm vs LCSC 4.5 mm) from R24.
- "Do not substitute the 76-pos header: footprint is different" narrowed to "without a fit check; reported different, not re-derived".
- IEEPA and Section 122 dates: stated as fact; sources disagree (02-20 vs 02-24) and are secondary. Marked UNVERIFIED. De minimis dates given as verified.
- MAP sensor lever: Mouser/DigiKey prices and "Part is NRND" appear in no note (notes say Mouser stock 74 on 10-31 and NRND unconfirmed). Downgraded to UNVERIFIED and removed "buy from Mouser" as a firm step.
- Consignment terms and TME prices: no source in the notes; marked UNVERIFIED.
- Lever 6 "[CONFIRMED]" downgraded to [PARTLY] (edge-rail fee unknown).
- Via fill: "verified by B08 and C005" corrected (C005 verifiers did not check the default); consequence narrowed to voids or starved joints, with the 500-660 via-count range.
- Parcel weight under 16 oz noted as an unmeasured assumption.

Still unverified: all PCB lines (about +-40 %), freight, packaging, the Shopify fee, the 35 % duty on JLC-bought parts, legacy Section 301 status of 8537.10.91, the DigiKey NL, RS and Greenchips figures, the CAD to USD rate of 0.72, 12-15 header lots costing $90-200, and the 1996-2005 header deltas that use interpolated batch-30 prices.

## Cross-section pass

- Outbound shipping line raised from $20.0 to $20.7 (S5 2 lb row, zone 5; range $18.6-23.6) and packaging from $3.0 to $3.3 (S5); totals moved from 207/152/141 to 208/153/142 (about +$1.0; arithmetic: +0.7 + 0.3 on the earlier table sum 207.3/151.9/140.6). Weight caveat added (1.2 lb is calculated, near the 16 oz line). Headline totals now stated as +-$15.
- Added a before/after table using S2's group totals (not duty-adjusted).
- Added levers 11 (S2 B1) and 12 (S2 B7).
- Section 5 / plan step 5: current 1999-2000 board uses 178780-1, 176122-6 only for ordered rev 0.7; added "confirm against footprint, check live stock".
- Step 2: rev 0.10 fix list must precede the order (S1 Part 7).


---

# S4. The customer experience, from unboxing to living with the ECU

Date: 2026-11-16. Confidence tags: [CONFIRMED] survived verification or was re-checked today, [PARTLY] verifier narrowed it, [SINGLE-SOURCE], [NEEDS MEASUREMENT].

## The short version

The hardware is a prototype, and what a customer meets after the box arrives is thin. Firmware reaches the customer only as an expiring CI download. The TunerStudio ini has no automatic delivery path. The first-start steps do not tell the customer to check injector size before cranking.

Almost all of this is cheap to fix: copy edits, a release workflow step and a bench step before shipping. The two expensive items are the case cutting and the wideband lead on the ordered boards. Both have cheap workarounds, listed below.

Step 1 (finding and buying) is not part of this published copy; the steps below keep their original numbers.

The competitors are far more expensive. Prices as the AMP PNP Miata product JSON gave them on 2026-11-16 (R04): $1,349.99 with the internal wideband and $1,199.99 without, one unit. A separate R32 page read showed the wideband version at $1,199.99 struck down from $1,349.99, so the real price may be a sale price; re-check. That is about three times the $399 board (3.0 to 3.4x), but the competitor boxes hold more. A fair comparison needs the $399 plus the add-ons below.

## Step 2. Unboxing and install

**What a customer meets.** INSTALL.md is richer than AMP's pages: header pin maps, a "What you need" list, and year-specific steps. Most of it is marked unchecked because no board has been fitted (R28). The box contents are not listed anywhere. The customer must open the stock case, move the board in, cut three to four openings in the case edge the board's bottom-edge parts face (INSTALL step 3), and reach the MAP hose, wideband plug and USB-C through them (B13).

**Specific points:**

- **Case washers.** The rusEFI wiki says one hole of the NA case (a recessed thread at the stock heat sink, on the MRE board) needs a stack of three M4 washers; INSTALL does not say so, and it was not verified that one of this board's six holes is at that spot. Check on the first case, then add washers and one line. [PARTLY, C098]
- **Drill template.** INSTALL gives hole centres only on paper. Print a 1:1 template as the first insert in the box, but only after one case has been measured. The 1996-2005 outline is a placeholder, so say "1989-95 only" until then. [PARTLY, C137, B13]
- **Fewer holes.** B13 proposes one drilled 16 mm hole with a grommet for the wideband lead, USB extension and hose. Another option is a printed replacement end plate. Both need measured case geometry first. [SINGLE-SOURCE, B13]
- **Reversibility.** AMP and BMM leave the stock ECU untouched and sell that as a feature (R28). Here the customer's own case is modified. The way back is a refit of the stock board, but the one-wire-per-injector conversion on 1990-93 cars cuts the stock paired joints and makes INSTALL's "your way back to stock" untrue. Add a warning and suggest splice connectors. [PARTLY, C100]
- **Jumpers per year.** The 1989-95 board needs per-year shunts: 90-93 sets JP3 and JP6; 94-95 sets JP1, JP2, JP3, JP4 and JP6. A 94-95 car with JP1/JP2 open has injectors 3 and 4 undriven. INSTALL already has per-year jumper tables; the gap is only a seller-side assembly checklist. Ship it set for the ordered year and put the setting on a label. [PARTLY, C121]
- **Wideband sensor mounting.** INSTALL section 6 has no mounting rules. Add four lines: at least 10 degrees incline with the connector up, 40-60 Nm with high-temperature grease, cover the sensor during underbody sealing, power the heater only after the engine is running. These come from Bosch's data sheet (Y 258 E00 015e). [PARTLY, C136]
- **IAT.** Removing the airflow meter or airbox takes out the stock intake-air sensor. The README documents the open-element replacement. Put the IAT in the starter kit. [PARTLY, C131]
- **Ordered boards and the wideband lead.** All five ordered motherboards have a Micro-Fit 2x3 at J2, so the AEM 30-3427 will not plug in. The ordered INSTALL says only "a 6-wire lead". A seller-made lead needs a Bosch plug kit, a 43025-0600 housing and crimped contacts, pin n to pin n, about $9-20 in parts (R15 estimate, unchecked). No board rework. Document the recipe and sell the lead (confirm the housing against the board footprint and check live stock before buying parts). [PARTLY, C013, ordered boards affected]
- **Kink-free MAP hose.** About 14 mm is free beside J5 and F1 before the hose must turn. Use a 90-degree silicone elbow on the barb. [SINGLE-SOURCE, B13]

## Step 3. First power-up and first start

**What a customer meets.** INSTALL section 8 has six steps: key on, throttle calibration, crank, timing light, watch the wideband, light-throttle drives. The firmware README has the long form. The base tune is loaded by the "Popular Vehicles" year button, which resets the tune (F04).

**What is missing:**

1. **The ini.** The firmware build passes `uploads: ''` and `EFI_EMBED_INI_MSD` is false, so TunerStudio's Detect cannot fetch the ini and the ECU cannot serve it. The ini exists only in the CI bundle. INSTALL's bench check never tells the customer to load it. Publish the ini beside each release, name it by version, and add a "Create Project, Browse, pick .ini" step with screenshots. This is a documentation gap common to custom rusEFI boards, not a design defect. [PARTLY, C019]
2. **Firmware delivery.** The workflow runs on pushes touching `firmware/`, sets no retention (GitHub's default expiry, 90 days from memory, unchecked, applies), and the files are CI artifacts needing a GitHub login. There is no release, tag, checksum or version note. Make a GitHub Release per shipped batch with the bin, DFU file, ini, SHA-256 sums and the pinned rusEFI commit (1374bd0). The pinned rusEFI commit (dated 2026-10-30) is 239 commits behind master on 2026-11-16 (GitHub compare API, F04); pin and keep it pinned. [PARTLY, C025]
3. **Pre-flash it.** The seller knows the year at sale. A bench step of a few minutes per unit removes the DFU, driver and wrong-NB2-button steps from the customer: flash the bin, press the year (on ordered 1989-93 and 1994-95 boards also set the tach output pin to none before shipping or mating: S1 Part 1 item 2, because the ordered firmware enables it and OUT_TACH is wired to 2I), run "Flash on-board wideband", confirm lambda on CAN, run `wbo_uart_status`. The wideband MCU ships blank, so the wideband does nothing until it is flashed once. [CONFIRMED, C114; PARTLY, C079: the flasher has only been simulated, and a failed flash leaves the wideband MCU blank]
4. **Injector size and fuel pressure before cranking.** The year button loads one injector set per year (212, 254, 265, 256, 265 cc/min). INSTALL has no pre-crank checklist for injector size, dead time, fuel pressure or engine size; it matters mainly for non-stock injectors, and the base tune itself is documented. Add four lines. Near-zero cost. [PARTLY, C026]
5. **Timing check order.** INSTALL puts the timing-light check (step 4) after the first crank and start (step 3), and no Miata preset sets the trigger offset, so the first start runs on unverified timing. The rusEFI book's sequence is to disable injection, pull the injector fuses and the plugs, set fixed 10 degrees, then crank and adjust Trigger Angle Advance; INSTALL instead uses a running-engine check, and neither INSTALL nor the firmware README has the fuel-off steps. Consider moving the check ahead of the first start and adopting the rusEFI sequence. The claim that the docs never say to restore dynamic timing was refuted: they do. [PARTLY, C023, C126]
6. **Safe defaults.** Boost cut, lambda protection and the CLT limit are off in the shipped tune, and a failed MAP sensor falls back to a flat 60 kPa estimate, so a wiring fault would run about 40% lean at wide-open throttle. These are stock rusEFI defaults; for the stock naturally aspirated car only the MAP fallback matters, and boost cut matters on boosted cars. The fixes are firmware settings and reflash, with no rework (F02, C016 [PARTLY]). The verifier lowered the severity to medium. Turn them on before shipping, or put the warning on the product page.
7. **Wrong year.** The base tune differs per year. A blank board defaults to NA6, and a wrong NB2 button gives no fuel or spark. If the seller pre-presses the year, the failure moves to the seller. Label the unit. [PARTLY, F04]

**Brick recovery.** BOOT (SW1) and RESET (SW2) are on the daughterboard inside the case with no access hole (OpenBLT recovery behaviour unverified). First flash can happen at the desk, and pre-flashing removes the need. Recovery then means opening the case. Say so in INSTALL, or add one hole. [PARTLY, C139]

**Benchmark.** AMP preloads a base map, ships a TunerStudio code and tells the customer to check engine size, injector size and wideband before starting, with timing-light verification (R04, R28). Haltech documents a first-start training course (R28, search summary only, UNVERIFIED).

## Step 4. Tuning

**What owners do.** R12 read forum threads. Self-tuning with a wideband and autotune is common, though one poster said it ran badly. Remote tuning runs $300-400 typically and up to $1,000. A "start and idle" tune runs about $400. Vendors send a base map per year, and owners then adjust. The first-run failures are no start on 94-95 until the throttle position registers, a 91 car that died after 10 seconds from wrong warm-up enrichment and injector size, and wrong trigger or base map on Speeduino cars (R12, forum posts [SINGLE-SOURCE]).

**Software.** rusEFI now ships a free Windows app, "rusEFI tuner", with tune editor, firmware update, log viewer, gauges and engine sniffer (R11, book.pdf). It is Windows-only. TunerStudio's free edition tunes manually; autotune (VE Analyze Live) needs the registered edition, about $70-100 on sale (R11, F04; the efianalytics page lists conflicting figures, so check before quoting). Link, ECUMaster, MaxxECU and Haltech tuning software is free (R11). The project's INSTALL says only "a laptop with TunerStudio" and does not say what is free.

**Gaps and fixes:**

- Tell the customer the free tuner exists, what TunerStudio adds, and that it costs extra. Effort: 1 hour. [CONFIRMED, R11]
- LTFT (learned long-term fuel trim) is compiled in by default in the pinned rusEFI; learning is on but applying learned trims is off by default, so the shipped state is safe. The repo does not mention it. Describe it, or turn it off. [PARTLY, C085]
- Idle on NA6 and NA94: the idle PID min and max are both 20, so closed-loop output is a constant +20 percent on a generic open-loop base, with no RPM feedback; the on-car effect is unmeasured. Fix in firmware before telling people it is closed loop. [PARTLY, C084; F02]
- Ship a tested microSD with a one-page README. TunerStudio's integrated log viewer is Ultra only; the rusEFI tuner has a free one. [SINGLE-SOURCE, F04]
- SD logging: if USB has power at key-on, rusEFI switches the SD card to mass-storage mode and stops logging. INSTALL tells owners to leave a USB-C cable in place without saying this; it only triggers if the far end supplies VBUS at key-on (a powered laptop or phone), not a bare cable. Add one line: start the car before connecting the laptop, or enable `alwaysWriteSdCard`. [PARTLY, C138]
- No autotune result for rusEFI is documented anywhere in the notes. [SINGLE-SOURCE]

## Step 5. Living with it

| Topic | Customer meets | State | Fix | Tag |
|---|---|---|---|---|
| Check-engine light | Lights at key-on (OUT_CEL wired) | The "no CEL" claim from forums does not apply to this design | none; tell owners | [PARTLY, C074] |
| Immobilizer 2001-05 | Dash lamp lights or flashes | Documented in README, not on the product page | one line on the page; test on a car | [PARTLY, C077] |
| A/C condenser fan | Second fan comes on only above 95 C (not with A/C) | `fan2AcMode` not set for 99-00 and 01-05; the stock A/C fan behaviour is unverified | one-line firmware change after checking the stock behaviour on a car | [PARTLY, C082] |
| Alternator, 1999-2005 | Control ships off; the NB charge lamp pin (1Q on 1996-2000, 3U on 2001-05) is unconnected, so the lamp never lights | Forum evidence of overcharge with ground offset on a competitor's unit | ground strap instruction; keep it off by default | [PARTLY, C069; R12 SINGLE-SOURCE] |
| USB drop-outs | USB-C under engine EMI | upstream rusEFI reports on other ECUs (VFD, charger ground loop); no evidence of a defect here | note a recovery path | [PARTLY, C140] |
| Firmware updates | OpenBLT console update | Ini changes with each build; settings may be lost | release notes saying which ini, backup the tune first, pin to a release | [PARTLY, C025; F04] |


**Production tests.** C141 and C099 note there are no test points or fiducials; the F103 SWD pads (J102) are on the bottom but matter only for recovering a blank wideband MCU (J3, the F407 SWD, is on top). Add a bench check list as part of the pre-ship step. [PARTLY]

**Not answered in this report.** Customer install time, tools list and case-cutting effort were not established (INSTALL gives steps, no time or tool estimate that the review checked), and the TPS kit for 1989-93 manual cars is not priced (R05 and R15 give no figure).

## Checked and dismissed

- C094: a fuel-pump driver killed by an ST_SIG fuse on Speeduino NA6 is a Speeduino issue, not this board's.
- C095: recurring A/C idle-up stalls are an MSPNP problem, not shown here. (The A/C fan issue above is separate.)
- R12's claim that INSTALL never says to restore dynamic timing is false.

## Top UX changes, in priority order

1. Pre-flash every unit at the bench with the year pressed, wideband flashed and lambda verified, and record the result on a label: a few minutes per unit.
2. Publish a tagged GitHub Release per batch with bin, DFU, ini, checksums and the rusEFI commit, and add the "Create Project, Browse .ini" step to INSTALL: 3-4 hours.
3. Add a pre-crank checklist (injector size, dead time, fuel pressure, displacement) and move the timing-light check before first start with injection disabled: 1 hour.
4. Turn on boost cut, lambda protection and the CLT limit in the shipped tune, and give the 99-00 and 01-05 presets `fan2AcMode` only after confirming on a car which relay the stock ECU uses (S1 C082; the stock A/C fan behaviour is unverified): 2-3 hours firmware plus a reflash.
5. Document the seller-made wideband lead for the ordered boards (Bosch plug, 43025-0600, crimps) and stock it: about 9-20 dollars in parts per lead (estimate), plus an afternoon to test.
6. Put three M4 washers and a printed drill template in the box after one real case has been measured: a few dollars, plus the measuring session.

## Sources used

Notes: kb/research/R32, R28, R04, R05, R11, R12, R15, R13, R27, R14; kb/firmware/F02, F04; kb/boards/B13, B14. Clusters: C012, C013, C016, C019, C020, C023, C025, C026, C027, C028, C029, C030, C069, C074, C077, C079, C082, C084, C085, C098, C100, C108, C109, C111, C114, C121, C124, C126, C131, C136, C137, C138, C139, C140, C141. Dismissed: C094, C095.

Re-checked today by the fact-checker: `repo/INSTALL.md` ("What you need", section 8), `repo/README.md` (limitations, status), `repo/.github/workflows/firmware.yaml` (no release step, no retention setting), AMP PNP Miata product JSON in `kb/research/files/R04/products_json/` (variants 134999 and 119999 cents). A live fetch of diyautotune.com failed (not JSON), so the AMP price comes from the stored R04 file. Prices for sensors, harness and TunerStudio come from R15, R11 and F04 and move often; re-check before publishing.

## Fact-check log


Corrections:
- "Two to three times" the $399: AMP's $1,199.99-1,349.99 is 3.0-3.4 times. Added that an R32 page read showed $1,199.99 as a sale price on the wideband version.
- AEM 30-3427 row: "fits the current boards" was an inference never tried on a board; price and stock kept, fit marked UNVERIFIED.
- Seller-made lead cost: $10-22 became about $9-20 (R15 estimate, JST-ended version, Micro-Fit parts unpriced).
- Hose and tee price: not in INSTALL; relabelled as a review estimate. Total $530-620 relabelled UNVERIFIED estimate.
- TunerStudio price: now 69.95 registered and 99.95 Ultra on sale (R11), with the inconsistency noted.
- Case washers: the 3 x M4 washer rule is from the rusEFI wiki for another board; not shown for this board's holes.
- Case openings "opposite the harness": not in INSTALL; replaced with "bottom-edge parts" per INSTALL step 3.
- Timing check: INSTALL uses a running-engine check; the verifier called the "disable fuel" framing misframed; wording narrowed.
- Safe defaults: added that these are stock rusEFI defaults and only the MAP fallback matters on a stock NA car.
- LTFT: learning is on, applying learned trims is off; the draft said "on by default".
- Idle: constant +20 percent offset, on-car effect unmeasured, not simply "pinned".
- SD logging: triggers only when the far end supplies VBUS.
- Alternator row: lamp pin is unconnected on NB boards (1Q on 1996-2000, 3U on 2001-05), not just 1999-2000.
- SWD: only J102 (F103) is on the bottom; J3 is on top.
- USB drop-out row: evidence is upstream reports on other ECUs, not on this design.
- Pre-flash and GitHub retention: added that the flasher is only simulated and the 90-day default is from memory.


## Cross-section pass

- Pre-flash routine: added tach output pin to none on ordered 1989-95 boards (S1 item 2).
- Sensor kit price: R15 shows the 119.20 figure (R05, S6) was the earlier price, 111.20 on sale today; S4 numbers stand.
- Added "confirm part, check live stock" to the seller-made wideband lead; added a "Not answered" sentence (install time, tools, case cutting, TPS kit price).


---

# S5. Packaging and shipping the assembled two-board set

Date of figures: 2026-11-16. Seller assumed to be in the United States (the notes assume this; the owner's location was not given). None of this touches the ordered boards: packaging is independent of board revision, and it applies to all five motherboard years plus the daughterboard.

## Bottom line

Ship the stack as one assembled unit (daughterboard on the motherboard, standoffs fitted) in a metallised shielding bag, inside a pink foam pouch, in a 9 x 9 x 4 in stock corrugated box. Materials cost about 3.3 to 3.6 USD per unit at 25 to 100 units. Ship domestic by USPS Ground Advantage at commercial (label-platform) rates with Signature Confirmation and cover to 399 USD. Plan about 19 to 24 USD of postage per order, not the 14 to 18 USD the notes first estimated, because the packed parcel is over 1 lb.

## 1. Pack-out for one set [SINGLE-SOURCE for the design; prices CONFIRMED]

Source: R25 (kb/research/R25-packaging-design.md), the "Spec B" recommendation. The design logic is one audit's reasoning and was not tested. The box and bag prices below were re-read today from Uline's pages (listed price data in the page source, valid to 2027-03-07). Nobody has built a board, so the weight and fit are calculated, not measured.

**Steps**

1. Leave the daughterboard on the motherboard. Ship the 154 x 162 mm stack as the customer will install it. Separate boards would put the 2 x 40-pin headers at risk of bending and add a mating step for the buyer.
2. Slide the stack into a 9 x 12 in pink anti-static foam pouch (1/8 in PE). The through-hole pins under the motherboard (harness header, sockets) puncture a bare metallised bag, so the foam goes inside the bag, against the pins.
3. Put the foam-wrapped stack in a metal-in static shielding bag and close it. A pink antistatic bag only stops the bag itself charging; it does not shield against an outside discharge. The stack has an MCU, USB-C and exposed harness pins, so use a shielding bag. [SINGLE-SOURCE: vendor and distributor pages agree; the standard text was not read.]
4. Put the bag on a corrugated cradle (scrap or die-cut) that carries the load at the four standoff positions and the board rim, with a relief cavity under the pins. Do not let foam load the harness header latch, the MAP barb or the microSD lid. Fit a small vacuum-hose cap (or a foam pocket) over the MAP barb so a drop cannot push it into the board. Ship with the microSD lid closed and no card fitted.
5. Add 3 ft of pink bubble wrap (or kraft paper in a first run) around the bag, then the printed quick-start card on top.
6. Close the 9 x 9 x 4 in box, tape it, and put one tamper-evident label across the flap seam. Skip desiccant for US delivery. A shielding bag is not a moisture barrier. Add a 1/6 unit desiccant (about 0.13 USD) only for sea or long-storage routes.

**Fit caution (added by fact-check).** The listed sizes do not nest as written: the foam pouch is 9 x 12 in inside, the shielding bag is 9 x 12 in inside (10 x 13 in outside, Uline page), and the box is 9 x 9 in inside. The pouch cannot go inside a bag of the same inside size, and a 10 x 13 in bag must be folded to fit the box. The 154 x 162 mm stack itself (about 6.1 x 6.4 in) fits the box. Try the real stack with these items, and check live stock, before buying 100 bags and 150 pouches; a 6 x 9 or 8 x 10 in bag and pouch may be the right size (not checked).

**Quick-start card.** One printed sheet, roughly 0.30 USD (estimate): which year board it is, stock-case cutting template reference, first-power checklist, support address, and the statement "you supply your stock ECU case; openings must be cut" (C109 verifier: the storefront copy "fits the stock ECU case" omits the cutting). The MRE NA case needs 3 M4 washers at the recessed thread hole (C098, [PARTLY]: not checked that this repo's holes land there). Add four M4 screws and washers to the bag: a few cents.

**Bill of packaging materials (per unit, USD)**

| Item | Source / part | Unit price | Basis | Check |
|---|---|---|---|---|
| Shielding bag, 9 x 12 in reclosable | Uline S-3753 | 0.57 | 57.00 per 100 | re-read 2026-11-16 |
| Cheaper alternative bag, 210 x 240 mm, 7.5 mil silver | LCSC C7543868 | 0.056 | 100 pcs, 0.0557 each | re-read 2026-11-16, stock 14,000; no certification wording; JLC does not stock it, LCSC only |
| Pink foam pouch, 9 x 12 in | Uline S-12583 | 0.39 | 59.00 per 150 | re-read 2026-11-16 |
| Box 9 x 9 x 4 in, 200 lb test | Uline S-4595 | 0.68 | 17.00 per 25 | re-read 2026-11-16 |
| Same, 32 ECT (lighter, cheaper) | Uline S-21587 | 0.57 | 14.25 per 25 | re-read 2026-11-16 |
| Tamper label | Uline S-8326 | 0.36 | 36.00 per 100 | re-read 2026-11-16 |
| Corrugated cradle + 3 ft pink bubble (Uline S-13053, 47 USD per 300 ft roll at 1) | | 0.62 | R25 estimate at 25 units | not re-checked |
| Tape, shipping label, card | | 0.16 | estimate (the card is estimated at 0.30 above, so this line may be low by about 0.15) | |
| **Total at 25 units (with 0.80 amortised box stamp)** | | **3.58** | R25 | |
| **At 100 units** | | **about 3.0 to 3.3** | die-cut EPE insert (Alibaba listings, 0.10 to 0.60 each at 100+, unquoted) could cut it; without a quote, assume 3.3 | [SINGLE-SOURCE] |

First-run outlay is higher than the per-unit figure because of minimums: 100 bags 57 USD, 150 pouches 59 USD, 25 boxes 17 USD, 100 labels 36 USD. Buy the LCSC bags with a JLC/LCSC parts order to avoid separate freight (R25). US-stock ESD pick-and-pluck foam (about 7 to 8 USD per kit) is the expensive trap; avoid it.

**Finished box and weight**

| Quantity | Value | Basis |
|---|---|---|
| Outside size | 9 3/8 x 9 3/8 x 4 5/8 in (238 x 238 x 117 mm), about 406 in3 | Uline listing |
| Bare stack | about 180 g (range 170 to 260 g) | calculated: motherboard 154 x 162 x 1.6 mm FR-4 about 74 g (upper bound, outline is smaller than the box); daughterboard 125 x 76 x 1.6 mm about 28 g; 4 standoffs 5 g; headers and sockets 12 g; harness header about 35 g (guess); MAP sensor about 7 g (guess); other parts about 20 g |
| Box | 181 g (32 ECT) or 218 g (200 lb) | Uline bundle weights divided by count |
| Packed | about 0.55 kg (1.2 lb) | estimate, 0.45 to 0.7 kg |

Weigh the first real packed unit. Spec A (32 ECT box, paper fill) comes to about 0.45 kg, right at the 16 oz line that changes the postage price (section 2).

## 2. Carriers and rates

**Domestic: USPS Ground Advantage, commercial price [CONFIRMED].** Notice 123 effective 2026-10-04, checked today against the saved copy of pe.usps.com. The tables cannot show whether they include the holiday increase that runs to 2027-01-17 (R26 assumes they do, from a secondary news page); if so, expect roughly 0.40 to 0.75 USD less afterwards (inference).

The notes (R26, C119) priced a parcel under 16 oz. The real packed parcel is about 1.2 lb, so the 2 lb row applies:

| Zone | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8-9 |
|---|---|---|---|---|---|---|---|---|
| GA commercial, over 16 oz to 2 lb | 8.39 | 8.48 | 8.66 | 8.91 | 10.50 | 12.13 | 12.55 | 13.42 |
| GA commercial, under 16 oz (for comparison) | 7.33 | 7.34 | 7.70 | 7.86 | 8.24 | 8.41 | 8.62 | 8.95 |
| GA retail, 2 lb row | 11.30 | 12.00 | 12.70 | 13.50 | 14.85 | 15.85 | 17.20 | 19.80 |

Commercial prices come from label platforms (Pirate Ship, Shippo, ShipStation, EasyPost). Their own discount claims are marketing and were not checked.

Insurance approach for a 399 USD item: Ground Advantage includes 100 USD of cover (usps.com page, via a fetch summary; whether it is credited against the fee is not stated, so treat 6.05 as the full cost). Buy full cover and Signature Confirmation:
- Signature Confirmation, electronic: 4.15 USD (Notice 123, confirmed).
- USPS merchandise insurance, 300.01 to 400 USD tier: 6.05 USD (confirmed). Third-party cover (ShipStation ParcelGuard) is claimed at about 2.20 USD; that is a vendor claim [SINGLE-SOURCE].
- Result: postage plus signature plus cover about 18.6 USD (zone 1) to 23.6 USD (zone 8), about 20.7 USD at zone 5, plus 3.3 USD packaging. Budget 22 to 27 USD all-in, about 6 percent of 399. The C119 verifier's 18 to 21 USD was for a sub-16 oz parcel.
- Keeping the packed parcel under 16 oz (about 454 g) saves about 1 to 4.5 USD per order depending on zone (1.06 at zone 1, 2.26 at zone 5, 4.47 at zone 8-9). Do not strip protection to get there.

**UPS and FedEx are not worth quoting [PARTLY].** At the 139 divisor the packed box bills about 3 to 4 lb against 1.2 lb actual; USPS only applies dimensional weight above 1,728 in3 (DMM 283, confirmed). The UPS divisor and all UPS/FedEx prices are secondary-source (the carrier PDFs blocked automated access). Get one live quote only if USPS fails you (C120).

**International (USPS, Notice 123 retail, 2 lb row, confirmed).** First-Class Package International carries no insurance, so a 399 USD item should go Priority Mail International (PMI), which includes 200 USD cover; 300.01 to 400 USD tier adds 17.55 USD.

| Destination | PMI 2 lb retail | + cover to 399 USD | FCPIS 17-32 oz (no cover) | Notes |
|---|---|---|---|---|
| Canada | 47.05 | 64.60 | 29.05 | DDP available (optional; per R26, not independently checked) |
| UK | 76.90 | 94.45 | 35.70 | DDP for 135 to 900 GBP (R26) |
| Germany | 85.50 | 103.05 | 32.85 | DDP required for dutiable goods (R26 from Postal Bulletin 22707; the verifier corroborated only the Canada/Germany/UK launch) |
| France | 73.65 | 91.20 | 32.85 | DDP required (R26, as Germany) |
| Australia | 77.95 | 95.50 | 46.05 | no DDP |

These are 2 lb figures. The notes quoted 1 lb figures (for example Canada 43.55); they do not apply above 1 lb. Charge international shipping at checkout, calculated, and state that the buyer pays import tax (C024, [PARTLY]: the USPS prices and 17.55 cover fee were confirmed against Notice 123; VAT thresholds and per-country DDP status were not re-verified; policy text only, no hardware effect). Delivery times (FCPIS and PMI 6 to 14 business days) are unverified.

**Not answered in this report.** Non-US sellers: the seller is assumed to be in the US and no non-US outbound or inbound route is priced. The packed weight is calculated, not measured (it sits near the 16 oz line). Inbound freight from JLC to the seller is unsourced (S3 uses a guess).

## 3. Customs paperwork

| Item | Value | Confidence |
|---|---|---|
| US HTS | 8537.10.9160, "programmable controllers", 2.7 percent. Supporting ruling: CBP NY N275130 (2016, engine ECU; it cites the older number 8537.10.9060, the current statistical line is 8537.10.91.60). | HTS rate [CONFIRMED] (USITC API); classification [SINGLE-SOURCE], R26 notes an argument for 8708 exists |
| UK commodity code | 8537 10 91 99, third-country duty 2 percent, VAT 20 percent | [CONFIRMED] (UK Trade Tariff API) |
| EU | 8537 10 98 99 likely; duty about 2.2 percent | [SINGLE-SOURCE], EU TARIC not queried |
| Description for forms | "engine control unit, programmable controller for automobile" | R26 |
| Country of origin | Probably China (boards fabricated and assembled by JLCPCB; hand-fitting through-hole parts in the US is unlikely to change origin). Declare China unless a customs adviser says otherwise. | inference, not verified |
| Dangerous goods | None. No coin cell, battery or battery holder appears in any board's BOM (grep of all evidence BOMs for CR1220, CR2032, coin cell, battery holder returned nothing). No lithium, no magnets, no liquids. | [CONFIRMED] for the BOMs; confirm on the first built unit |

What the buyer pays on arrival, on 399 USD plus shipping (arithmetic on the rates above, not quotes):

| Region | Tax / duty | Roughly, for a 399 USD item | Confidence |
|---|---|---|---|
| UK | 2 percent duty, 20 percent VAT at the border (seller point-of-sale VAT covers only consignments up to 135 GBP) | about 95 to 100 USD, plus carrier handling fee (8 to 12 GBP, secondary); USPS DDP removes the surprise | rates [CONFIRMED]; fees [SINGLE-SOURCE] |
| EU | 19 to 25 percent national import VAT, duty about 2 percent; the 150 EUR schemes do not apply | about 90 to 120 USD | [SINGLE-SOURCE] |
| Canada | 5 percent GST plus provincial tax, about 9.95 CAD handling | about 25 USD (GST only) to 70 USD (HST provinces); duty depends on origin | [SINGLE-SOURCE] |
| Australia | 10 percent GST; goods under 1,000 AUD duty-free (unverified) | about 40 to 48 USD | [SINGLE-SOURCE] |

US inbound from China is a separate cost: JLCPCB pre-collects a flat 35 percent on PCB and assembly lines for US orders (C021, [PARTLY]); the 8537.10 plus Section 301 stacking is inferred. De minimis is suspended for all countries (confirmed, Federal Register 2026-12669/12670). Use JLC's checkout figure.

## 4. The case

The product reuses the customer's stock ECU case, so there is **no core to collect and no core deposit**. The buyer opens the stock case, lifts out the stock board and cuts the case for the wideband plug, USB-C, MAP hose and add-on header (INSTALL.md section 3; C109, [PARTLY]: the cutting and the unchecked fit are already documented in README and INSTALL; the missing part is the storefront wording). The stock board is the buyer's way back to stock.


## Checked and dismissed

- R26's domestic budget of 14 to 18 USD and its 9 x 7 x 3 in, under-16 oz parcel: wrong for this product. The board is 154 x 162 mm, so the box is 9 x 9 x 4 in and the parcel is about 1.2 lb.
- Pink antistatic bags alone, bubble mailers and loose peanuts: not adequate (R25).
- Consignment, 3PL and a company-run enclosure: not needed for packaging; home fulfilment to about 100 units is the notes' advice (C112: the JLC consignment and 3PL fee figures were confirmed, the advice itself is judgement; consignment also has a 3-year use-or-abandon limit and a 30 percent retrieval fee, min 30 USD).

## Sources used

Notes: kb/research/R25-packaging-design.md, R26-shipping-and-customs.md, R28-support-and-ownership.md, R22-alternative-manufacturing.md. Clusters: C009, C020, C021, C024, C027, C051, C098, C109, C110, C112, C119, C120, C127. Re-checked today: pe.usps.com Notice 123 (effective 2026-10-04; GA commercial and retail rows, signature and insurance fees, international PMI and FCPIS tables from the saved copy kb/research/files/R26/usps_notice123_2026-10-04.txt); Uline pages S-21587, S-4595, S-3753, S-12583, S-8326 (list prices from page data); LCSC C7543868 via tools/lcsc.py; BOM grep for batteries across evidence/*/sch_bom_grouped.csv. Not re-checked: UPS and FedEx rates, EU duty, AU/CA customs, Alibaba prices.

## Fact-check log

Date 2026-11-16. About 70 claims checked.


Corrections:
- Fit: added a caution that the 9x12 in pouch, 9x12 in bag (10x13 in outside) and 9x9 in box do not nest as listed.
- C109 marked [CONFIRMED] -> [PARTLY] (verifier said partly).
- Holiday increase: "this includes" -> not shown by the tables, assumed from a secondary source.
- Savings for staying under 16 oz: 1 to 3.5 -> 1 to 4.5 USD (zone 8-9 is 4.47).
- HTS ruling cites the older 9060 number; card cost (0.30) versus the 0.16 table line flagged.

Unverified: UPS/FedEx divisors and prices; EU duty and import VAT rates; Canada and Australia customs figures; UK carrier handling fees; Alibaba die-cut prices; delivery times; the 100 USD included GA cover; whether Notice 123 tables include the holiday increase; the shielding-bag standard (vendor pages only); all weights other than the bare-stack sum (guesses for harness header and MAP sensor); the case washer fit (C098); S-3753 "certified wording" not re-read.

## Cross-section pass

- AMP $75: reworded so it is not attributed to AMP (verifier found DIYAutoTune's only).
- Added 'check live stock' to the bag and pouch purchase and a 'Not answered' paragraph (non-US seller, unmeasured weight, unsourced inbound freight).
- S3 now uses this section's 2 lb postage row ($20.7 at zone 5, $18.6-23.6) and $3.3 packaging.


---

# S6. What the background research found, and what it means for this design

Date of this section: 2026-11-16. Confidence tags: [CONFIRMED] survived adversarial verification or was re-checked today; [PARTLY] the verifier narrowed it and only the narrowed version is stated; [SINGLE-SOURCE] one research audit, not independently verified; [NEEDS MEASUREMENT] needs a bench or car measurement. "ORDERED" means the boards already sent to fabrication in November 2026.

Nobody built or ran any board in this review. Everything below comes from documents, source code, vendor pages and forum threads, so the field-failure evidence is "a report exists and says this", not a failure rate.

---

## Part 1. Other ECU designs, commercial competitors, field failures

### 1.1 Where $399 sits

Prices read on 2026-11-16 (notes R05, R04, R03). GBP converted at an assumed 1.30. "Sensor" means the Bosch LSU 4.9 wideband sensor, which every onboard-wideband product needs.

| Product | Fits | Price (1 unit) | Wideband | Notes |
|---|---|---|---|---|
| This product | 1989-2005 (manual; automatics untested per README, while the draft store FAQ says swapped autos are covered, C012) | 399 USD | on board | sensor and IAT extra |
| DIY-EFI CORE4 Speeduino (UK) | 2001-05 | GBP 400 ex VAT (about 520 USD) | option GBP 70 plus sensor | fits factory case |
| Speeduino NA6 plug-in via resellers | 1989-93 kit (SpeedyEFI NA8 1994-95 kit 399 USD, shown out of stock); Alex Eng. NA 93-94, NB | 449-489 USD (SpeedyEFI NA6); EUR 325 (Alex Eng., single forum post by the maker) | no (EUR 70 option) | no knock, no CAN |
| Beer Money Motorsports (BMM) | NA, 96-97, NB1, NB2 | 749 / 775 USD | internal | backordered, "up to 30 days" |
| AMP PNP (MS3Pro, MSPNP successor) | all five Miata ranges | 1,199.99 / 1,349.99 with wideband | optional internal | own case; stock case not reused |
| ECUMaster EMU Black plus NB1 adapter | 1999-2000 only | 1,169 + 224 = 1,393 USD | internal | no NA or NB2 adapter found |
| Link G4X MX5Link | NB1 or NB2 | 1,595 USD | not listed | NB1X (1998-2000) and NB2X (2001-05) variants, manual only |
| Haltech Nexus S2 / S3 | NA, NB | 2,130 special / 2,520 special | internal | S3 also sold; excludes 1996-97 US |
| rusEFI uaEFI plus Tindie Miata breakout | universal | 275 + 20 USD | on board | DIY, no MAP fitted |

[SINGLE-SOURCE: vendor pages read by R05 on 2026-11-16; not re-fetched in this fact-check. Verifier outcome on the cost claims is C028, C029 PARTLY, see below. Alex Eng. price rests on one forum post; Haltech S3 regular price is 2,800.]

**What this design should take from it.**
- The defensible claim is "lowest-priced assembled plug-in with onboard wideband", not "most affordable Miata EFI": a self-built uaEFI plus breakout is 295 USD (C028, PARTLY: the repo already documents part of this; the number and the wording fix are new).
- Cost to a running car is about 530-620 USD, not 399: add sensor (R15: 119.20 USD was the earlier ECUMaster kit price, 111.20 on sale today, 139 list; S4 row), IAT sensor if the airflow meter is removed (about 15-25 USD, unverified), and optional TunerStudio (see 3.2) (C029, PARTLY: the range is an unsourced sum of mixed-quality prices; the INSTALL and README already list the IAT, TPS and TunerStudio, so the gap is storefront copy only). State it on the store page.
- Haltech names only manual cars. Copy that precision (supported years, manual only, 1.6 car TPS caveat). Not every competitor says "manual only" (R05 shows it for Haltech, Link NB1X, ECUMaster adapter).
- No stock-ECU reflash tool for 1999-2005 was found, so standalone is the only route on NB [SINGLE-SOURCE, absence of evidence].
- rusEFI no longer sells or stocks any Miata Hellen board and calls the NB2 and NA96 pages "somewhat abandoned" (R01). The open-source Miata competitor is dormant. [SINGLE-SOURCE]

### 1.2 What rusEFI, Speeduino and others converged on

| Practice | Evidence | Meaning for this design |
|---|---|---|
| Hellen Miata boards: 2-layer (NA8-96 layer count inferred), injector drivers swapped to ZXMS6005SGTA (SOT-223, about 60 V self-clamp per R01; datasheet not read) on every Miata BOM | R01, R30 [SINGLE-SOURCE per audit, file read directly] | A cheap driver is used in the field (context only, not support for the NCV8401B swap: ZXMS6005 clamp from R01, datasheet not read) (JLC stock only 18 pcs on 2026-11-16, so not a drop-in answer). The review's cheaper-driver options (NCV8401B in the same DPAK footprint saves about 8.0 USD per board at 100 pieces (re-checked today: 1.82 vs 0.81 USD each), but its current limit is 25-35 A against 6 A on the VND7NV04; NCV8403A in SOT-223 saves more but needs a re-layout and thermal rerun) are in C068 [PARTLY, no on-car test]. |
| Current uaEFI (rev F3, Sept 2026): F407VGT6, 4 layers, VNLD dual low sides, series resistors added in front of driver inputs | R01 | Same MCU as this design. Supports C008 (see below). |
| Open designs buffer coil outputs with a TC4424/TC4427-class gate driver (Hellen uses an SN74LVC4245 level shifter plus 10 ohm instead); none adds a Schottky plus FET plus 74HCT04 stage | R06, R09, R01 | The extra ignition parts (Q16-Q19, U13, B5819W) go beyond proven practice. Verdict C151 [PARTLY] scopes a removal to Q16-Q19 and U13 ($1.5-2.6 per board, slower spark edge, lower noise margin; not the short-to-battery protection), while S2 A5 says keep; unsettled until igniter measurements exist. |
| Hellen and Speeduino fit a tracked or protected 5 V sensor supply after a shorted TPS bricked a Hellen NA6 | R31, R01 (C118, no verifier verdict [SINGLE-SOURCE]) | This design has a protected harness 5 V (U14), so it is ahead of the field here. |
| Speeduino v1.3 added a 40 V TVS, 100 V flyback Schottkys, a baro sensor | R03 | Covered by this design's TVS and clamps. |
| Production-ECU teardowns | R29 | Public teardowns of aftermarket ECUs are essentially absent. The stock Miata 1990 ECU is fully discrete (2SD1415 Darlingtons); the 1999 NB1 uses a 160-pin semi-custom CPU, CPU and flash coated. The only multi-channel injector drivers found in open designs are dual VNLD5090 parts (Speeduino, uaEFI); quad or larger injector ICs appear only in expensive designs and none is stocked at JLC (R29). |

Per injector channel this design spends about 3 USD (VND7NV04, ES1D, 1.5SMC16A, resistors) against 0.5-1 USD for shipped open designs (R29). That is the main place where the BOM is heavier than the field practice.


### 1.3 Field failures logged by comparable projects

All items are "reports exist" (R31); none is a failure rate.

| Failure class | What was logged | Applies to this design? |
|---|---|---|
| Unprotected 5 V sensor output | Shorted TPS 5 V bricked a Hellen NA6 | No: protected supply fitted. |
| TC4427 alternator or tach output killed MCU pins (Hellen NB1/NB2 #23) | Fixed upstream with 100 ohm plus Schottky | No: this design drives the alternator from a VND7NV04 and fits 100 R plus B5819W on the ignition TC4427. Alternator control ships off. C047 [PARTLY, no rework needed]. |
| Hellen H72 load-dump crowbar MOSFET failed short at 22 V | hellen-one #47 | No: this design has no MOSFET crowbar. C056 REFUTED for this board. Only the general advice to bench-test 24 V and 35 V with a current limit remains. |
| Injector-driver input without series resistor | rusEFI added resistors in uaEFI rev F | Yes for the ORDERED daughterboard rev 0.9: no 150-220 ohm resistors on the VND7NV04 inputs. C008 [PARTLY], already documented; the current rev 0.10 has them. The review's rework list covers the ordered boards. |
| F407 would not enter DFU: HSE start-up slower than the ROM bootloader waits | Hellen issue 79, seen on 144/176-pin parts | C086 [PARTLY; NEEDS MEASUREMENT]. This board uses an 8 MHz, 80 ohm ESR crystal with 33 pF loads. Test: on the first built board, enter DFU from cold and hot ten times. Fallback is a different crystal. |
| JLC assembly faults on Hellen boards | one poor joint, diode-polarity queries, a substituted op-amp | Single anecdotes (C055 PARTLY). Inspect the first boards. |
| USB dropouts and FATAL near a 3-phase VFD; long dwell at sync loss | rusEFI issues; long-dwell issue was closed as fixed in April 2024 | C060 PARTLY: not open upstream. Generic risk, not a defect of these boards. |
| Speeduino fuel-pump driver killed when the start-signal fuse is left in | Speeduino NA6 wiki | Different circuit; C094 no verdict. Worth one line in INSTALL if the pump output is used. [SINGLE-SOURCE] |

### 1.4 Processor and parts supply (checked today)

STM32F407VGT6 (LCSC C12345), run with `tools/lcsc.py` on 2026-11-16: JLC stock 140, LCSC stock 34, 5.05 USD at 1, 3.57 USD at 100. R10 logged 72 on the same day earlier (the C018 verdict says about 96), so the figure moves by the hour. Either way, a run of 100 boards would exhaust JLC stock (C022, C106 [PARTLY]). Actions:
- Do not switch to a GD32 or APM32 clone for this batch. rusEFI supports none, and an open issue (#8396) reports a hard fault on APM32F407 (R10, C018 [PARTLY]).
- STM32F407VET6 (512 kB) cannot hold the current image (669 kB build); do not buy it as a substitute (C087 [PARTLY]).
- Keep the F103C8 for the wideband. Clones save 0.15-0.35 USD each and behave differently (C150, no verdict, [SINGLE-SOURCE]).

---

## Part 2. The stock Miata ECUs and engine electrics

### 2.1 What each generation does and where this design differs

| Years | ECU connector | Ignition | Facts that change design or documentation | Source |
|---|---|---|---|---|
| 1989-93 | 48 pins: 1A-1V and 2A-2Z | external igniter; ECU 1G and 1H drive igniter bases (about 659 ohm to ground); 2I is read as an input from the igniter (direction unsettled, see 2.2); the stock igniter drives the tach per the 1991 diagram | Many cavities carry no wire on a manual car (1I, 1L, 1M, 1T, 2F, 2J, 2M, 2R, 2S, 2T, 2Y, 2Z). Fuel pump is not ECU-driven (a circuit-opening relay is fed from the airflow-meter switch); the fan is thermoswitch-driven, ECU only monitors it on 1R. The throttle "sensor" is a two-contact switch. | R16 [CONFIRMED against 1990 US manual; 1991-93 manuals not read] |
| 1994-95 | 48 pins, different table | same igniter arrangement; 1G and 1H; 2I direction unsettled (S1 Part 3) | Automatic differs on pin 1K. Late-95 ECU in a 94 car gave "no IGf" in one forum report. | R17 [CONFIRMED manual; part numbers SINGLE-SOURCE] |
| 1996-97 | 64 cavities in four sites (1, 3, 4 used; unused site 2) | coil packs, IGT1 on 4N, IGT2 on 4R | Extra crank-pulley NE sensor (4H/4E, 500-600 ohm, magnetic) left unconnected by the design. OBD-II lamps and K-line exist. | R17, R20 |
| 1999-2000 | 3 plugs, 22 + 16 + 26 | coil packs, 3G and 3H | Alternator: 1O drives field duty, 1T senses output, 1Q drives the charge lamp. 1H is constant battery supply and 3K is the tank-level signal (the repo calls both "unclear"). 2K is the tach output, not "unused". 3-wire Hall CKP/CMP fed 12 V from the main relay. | R18 [CONFIRMED against 2000 wiring manual] |
| 2001-05 | 4 sites | coil packs 3F and 3I | 2001-02: main relay switched by the key, 3H and 4S unused. 2003-05: PCM drives the main relay on 3H and reads key-on on 4S. The shared board handles this with two firmware presets (C091 CONFIRMED, not a defect). Immobiliser serial link on 3S. | R19 |

**Signals that differ by year, market or transmission.** Automatic-transmission cars use lines (1R, 1T, 4Y, 1I, 1N, 1V, 3L) the design does not serve (C012 [PARTLY]). The store should say "manual only" (the draft FAQ and Fits rows currently say swapped autos are covered); serving the A/T lines would need board changes (not assessed here). The 1V clutch input reading is harmless by default in rusEFI; the real risk is the unconnected TCM lines (unverified). 1.6 NA cars with a throttle switch need a full-range TPS fitted if you want rusEFI throttle logic (Haltech says the same).

### 2.2 Ignition: the one place to act on the ORDERED boards

- On ORDERED 1989-93 and 1994-95 motherboards the tach driver (ZXMS6004) is wired straight to harness 2I, and the frozen ordered firmware enables the tach output by default. the R17 workshop manual notes read 2I as an igniter-side input on these years, but its direction is UNSETTLED (S1 Part 3: audit A says input, audit B's sources suggest the ECU may need to output the tach; verdict C002: not settled without a car measurement). C002 [PARTLY]: it is true and the repo's docs already warn about it; what is NOT shown is that the stock ECU pulls 2I up or that the cluster tach depends on 2I, and nothing in the firmware reads 2I. The FSM-based notes say the cluster tach comes from igniter terminal D (R16, R20). Action (as S1 Part 1 item 2): before first power-up, disable `tachOutputPin` in the flashed config; rework only if a car measurement shows the ECU must supply the tach (then cut OUT_TACH at 2I and add a jumper or about 1k pull-up). The current revisions have jumper JP5 (open), which is right.
- On 1996-2005 boards the tach is a ZXMS6004 low side with no pull-up, where rusEFI's Hellen boards drive 3O push-pull from a 12 V stage. Whether the cluster needs a driven-high idle level is unmeasured. C040 [PARTLY; NEEDS MEASUREMENT]. Measure with the stock ECU in the car: tach terminal voltage (3O on 2001-05, 2K on 1999-2000, 4L on 1996-97) with the ignition on and the engine off.
- Dwell: rusEFI ships a flat 4 ms with a voltage-correction table that is all 1.0. A flat 4 ms is not over-dwell; the real problem is under-charge at low battery voltage. C078 [PARTLY]. The coil's correct dwell is unknown; ignition inputs on the NB switch below 3 V (2005 manual bench test).
- Ignition inputs rest LOW in this design, which matches the stock ECU (0 V key on, about 0.2 V average at idle) (R09, [CONFIRMED against the 1990 manual]).

### 2.3 Sensor and actuator numbers to reuse (R20)

| Item | Value | Notes |
|---|---|---|
| Injectors | 12-16 ohm at 20 C, high impedance, 1990-96 | 1999-2005 value not found |
| IAC solenoid | 10.7-13 ohm | 2P/2Q naming exists, but rusEFI Hellen NB2 wires 2P to 12 V and 2Q to a low side; the design follows that (C063 PARTLY). |
| ECT/IAT | 2.21-2.69 kohm at 20 C; ECT 0.29-0.35 kohm at 80 C | 1994-2005 |
| Coil primary | 0.78-0.94 ohm | 1994 manual |
| Knock sensor | piezo, about 560 kohm to body; signal on 2F (1999-2000), 4M (2001-05) | none on the 1.8 NA |
| CKP/CMP 2001-05 | 3-wire Hall, 12 V from main relay, signal pulled up to about 5 V | C093 no verdict; read from Mitchell 2005 |
| Alternator (1999-2005) | PCM 3M field duty, 4T output sense. The manual contradicts itself on the idle voltage (3-8 V vs about 14 V). | Do not design from one table alone. |

### 2.4 Immobiliser and alternator

- 2001-05 immobiliser: PCM and immobiliser unit are paired by serial link on 3S, "cannot be deactivated" (2002 manual). With a standalone ECU the engine runs and the dash light flashes or stays on (AMP documents this) [CONFIRMED for AMP's statement; not tested on a car with this product]. No report was found of a fuel cut after seconds. The repo already documents it (README line 101, INSTALL line 256). New: the product page does not say it, and the owner should add that the immobiliser unit stays connected and that pulling the bulb is a user choice (C077 PARTLY).
- 1999-2000 alternator overcharge reports belong to the MSPNP2's own regulator circuit (a vendor engineer blamed a ground offset; another case was a repaired unit with the regulator set to maximum). Alternator control ships off in this design, so the reports are not evidence against it (C010 [PARTLY], severity corrected to low). The charge lamp (1Q/3U) is never driven, so the dash lamp behaviour on 1999-2005 is untested (C069, no verifier verdict [SINGLE-SOURCE]).
- Check-engine lamp: not driven by the MSPNP either. Inspection states that read OBD-II readiness will fail (C074, C134, no verifier verdict). [SINGLE-SOURCE]

### 2.5 Still uncertain (do not state as fact)

| Open question | Why it matters | What would settle it |
|---|---|---|
| Does the 1989-95 stock ECU pull up 2I? | decides whether tach or "code 01" works | meter on 2I in a car with a stock ECU [NEEDS MEASUREMENT] |
| Is there a load-dump clamp in the Miata alternator? | decides TVS sizing | scope on B+ while disconnecting the battery on a running car [NEEDS MEASUREMENT]. R07 says the SMCJ30A and SMAJ33A suit a clamped supply; for a 35 V suppressed dump the verifier's worst-case simulation puts about 5-18 J through D6, outside the datasheet pulse curve, and the 80 V unsuppressed figure is speculation (C032 [PARTLY]). |
| Stock ECU case dimensions and mounting for 1996-2005 | the 1996-2005 outlines and holes reuse the NA 1989-95 outline as a documented placeholder; rusEFI's Hellen NA8-96/NB1/NB2 use a 154 x 159 mm template (NB1 targets a Camry donor case), not proven to match the Miata case | measure an actual case (C011 [PARTLY]) |
| Injector dead time and flow | public tables differ about 1.4-1.5x (rusEFI 1.5 ms vs FOME about 1.1 ms at 12 V); no Denso or Mazda source (C049 [PARTLY]). Public ignition maps disagree by up to 18 degrees, but the Speeduino NB map is a conservative placeholder (C044 [PARTLY]). | flow-bench data or a dyno/wideband sweep |
| Hall sensor output level into the 1 k pull-up | 4.7 mA sink is normal for open-collector Hall parts; the stock sensor's Vol is unmeasured (C046 [PARTLY]) | scope on the first car |

---

## Part 3. How people tune standalone Miatas

### 3.1 Practice

Owners load a vendor base map for the year, start the car, check base timing with a timing light and the diagnostic jumper (10 degrees BTDC at 850 rpm, all years per Moss, secondary to the Mazda manual), then either self-tune with a wideband and autotune or buy a remote tune (R12, R14). Reported remote-tune prices: 300-400 USD typical, 400-1,000 USD range (forum quotes seen via search summaries, not re-read [SINGLE-SOURCE]). There is no source for how many hours tuning takes; R11's 3-10 drive hours over several sessions is an inference [SINGLE-SOURCE, labelled INFERRED in the note].

Common failure families in owner threads (R12): no-start from the wrong base map or injector size; idle and warm-up tuning; wideband erratic readings fixed by moving the signal ground to the ECU sensor ground (C132, no verdict) or by exhaust leaks; 1989-95 tach; the immobiliser light. Speeduino users call the failures "mostly user error". C026 [PARTLY]: "base map missing" is false here (INSTALL step 1.2 loads the year tune), but INSTALL has no pre-crank checklist of injector size, fuel pressure and engine size for non-stock injectors, and the base tune rests on unmeasured injector numbers.

### 3.2 Software and what it costs the owner

- rusEFI ships a free Windows tuner. TunerStudio is optional; the registered edition is needed for VE Analyze Live autotune (per the TunerStudio manual as read by R11; the verifier did not re-check this): 69.95 USD on sale (79.95 normal), Ultra 99.95 (129.90 normal), read 2026-11-16 from the EFI Analytics store (C113 [PARTLY]). Competitors include their tuning software free.
- C019 [PARTLY, medium]: this build's CI uploads no .ini to rusefi.com (`uploads: ''`) and the F4 build does not embed the .ini, so "Detect" cannot find the file. The .ini ships in the release bundle. Add an INSTALL step: "create a TunerStudio project from the .ini in the bundle". This is an owner-facing fix that costs a paragraph.
- C085 [PARTLY, low]: long-term fuel trim is compiled in. Learning is on, applying learned trims is off. Defaults are safe; the docs do not mention it.
- C023 [PARTLY]: the timing check (INSTALL step 4) comes after the first start (step 3), and `globalTriggerAngleOffset` is 0. Swap the order. rusEFI's plugs-out cranking method has fire-safety steps (disable injection, pull plugs, extinguisher at hand); the repo instead uses a running-engine fixed-10-degree check, so whether to add them is a judgement call. The review's claim that "restore dynamic timing" is undocumented is false; it is documented. No Miata preset sets the offset except the 36-1 NB2 variant.
- Selling pre-flashed boards removes the riskiest customer steps (drivers, DFU, wideband flashing) (C114, no verdict [SINGLE-SOURCE]).

### 3.3 Checked and dismissed

| Claim | Why it fails |
|---|---|
| Load-dump crowbar failed short at 22 V (C056) | This board has no crowbar. |
| A/C idle-up stalls recur (C095) | The reports are about MSPNP; this design has its own A/C input and sets `acIdleExtraOffset`. |
| 1999-2000 pin table conflict on 1U/3Q (C041) | No conflict; mapping matches rusEFI's NB1 table. VICS solenoid undriven is already in the README. |
| TC4427 killed MCU pins (C047) | Different topology here. |
| Vane-meter voltage conflict between manuals is a board risk (C064) | The AUX3 input takes any 0-5 V level. |

---

## Sources used

Notes: kb/research/R01, R02, R03, R04, R05, R06, R07, R09, R10, R11, R12, R13, R14, R15, R16, R17, R18, R19, R20, R29, R30, R31 (R08 for the driver prices in 1.2).
Clusters (verifier versions where they exist): C002, C008, C010, C011, C012, C018, C019, C022, C023, C026, C028, C029, C032, C040, C041, C044, C046, C047, C049, C055, C056, C060, C063, C064, C077, C078, C085, C086, C087, C091, C095, C113.
Clusters with no verifier verdict, so [SINGLE-SOURCE]: C069, C074, C093, C094, C108, C114, C118, C124, C125, C132, C134, C150, C151.
Re-checked today: STM32F407VGT6 stock and prices with `tools/lcsc.py C12345` on 2026-11-16 (JLC 140 pcs, LCSC 34 pcs, 5.05 USD at 1, 3.57 USD at 100). No other price in this section was re-fetched; competitor and TunerStudio prices are as recorded by R04, R05 and R11 on 2026-11-16.

## Fact-check log

Date: 2026-11-16. About 95 claims checked against research notes R01, R03, R05, R09, R13, R16-R20, R29, verdicts.jsonl, evidence/ nets and live `tools/lcsc.py` (C12345, C604055, C155605, C174042).

Re-checked live and found correct: STM32F407VGT6 C12345 (JLC 140, LCSC 34, 5.05 USD at 1, 3.57 at 100); NCV8401B vs VND7NV04 saving (about 8.05 USD per 8 at 100); OUT_TACH ties J1.2I to the tach driver on ord_mb8993 and has JP5 on cur_mb8995.

Corrections made:
- Table row "This product": "not automatic" -> automatics untested per README; draft store FAQ says swapped autos are covered (C012).
- SpeedyEFI 449-489 USD is the 1989-93 NA6 kit, not 1989-95 (NA8 1994-95 is 399 USD, out of stock); Alex Eng. price is a single forum post.
- The "[CONFIRMED against R05 pages]" tag on the price table downgraded to SINGLE-SOURCE (not re-fetched).
- ZXMS6005 clamp "60-70 V" -> about 60 V per R01, datasheet not read; JLC stock 18 pcs; NA8-96 layer count inferred.
- NCV8401B option: added the 25-35 A vs 6 A current-limit trade-off the verifier named.
- "Every open design uses TC4424/TC4427-class" -> Hellen uses an SN74LVC4245 level shifter.
- "No public design uses a multi-channel injector IC" -> contradicted by dual VNLD5090 in Speeduino and uaEFI; reworded. "Coated board" -> coated CPU and flash.
- C002: added that nothing in the firmware reads 2I; "cluster tach from terminal D" attributed to FSM-based notes.
- Outline placeholder (C011): design reuses the NA outline; the 154 x 159 mm template belongs to rusEFI's Hellen boards and is unproven for the Miata case.
- C032: "neither survives an unclamped test A pulse" removed; replaced with the verifier's simulated 5-18 J figure and the speculation note.
- C023: fire-safety steps belong to rusEFI's plugs-out method; the repo uses a running-engine check; added that no preset sets the offset (36-1 NB2 excepted).
- Knock sensor: 2001-05 also has one (4M, about 560 kohm); "1999-2000 only" was wrong.
- Remote-tune prices: not "VERIFIED"; search-summary quotes.
- Autotune needs registered TunerStudio: attributed to the TunerStudio manual via R11; verifier did not check.
- Tach terminal list: added 4L on 1996-97.

Remains unverified: ZXMS6005 clamp voltage; 1994-97 NE sensor 500-600 ohm and "1996-97 four sites" beyond R17's statement; R10, R29, R31, R30 individual claims taken from notes; C118, C125, C151 and other no-verdict clusters; competitor prices other than R05's recorded values; TunerStudio sale prices (79.95 vs 89.95 list conflict between notes); no web page was re-fetched.

## Cross-section pass

- 2I (sections 2.1, 2.2): direction marked unsettled to match S1 Part 3 and verdict C002; action changed to firmware setting first, rework only after a car measurement (S1 Part 1 item 2).
- Sensor kit price: R15 shows 119.20 was the earlier price; 111.20 on sale today (139 list).
- Ignition-stage removal (1.2): C151's actual scope stated; S2 A5 says keep; marked unsettled.
- NCV8401B row: ZXMS6005 flagged as context only.
- F407 stock: noted the C018 verdict's 96.
