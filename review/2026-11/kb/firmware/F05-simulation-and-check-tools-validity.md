# F05 - Validity of the project's own simulation, emulation and check tools

Run date 2026-11-16. Work dir: `work/F05-simulation-and-check-tools-validity/` (mirror/ = copy of repo/firmware/tools, sim, scripts with symlinks for daughterboard, motherboards, research, ordered-boards; bin/rsvg-convert = cairosvg shim; logs *.log).
Tools run with `tools/run.sh`; env: `PYTHONPATH=$PYTHONPATH_KICAD` + venv python when both scipy/shapely and pcbnew are needed. Renode not available: run_ecu.py / run_system.py NOT run.

## Summary (10 lines)
1. Strongest tool: `check_mcu_pins.py` (independent reference: ST's own pin XML) and `board_copper.py` (netlist rebuilt from copper geometry, ignores net names). Both reproduced OK today. They test the MCU pin map and copper-vs-design.py, not footprint pinouts or ordered boards.
2. Weakest tools: Renode firmware-in-the-loop (inputs and scale factors come from the same author as the firmware config; CI trigger is manual only), `check_sch_netlist.py`/`check_mb_netlist.py` (design.py compared with a schematic generated from design.py), `circuit_sim.py` (CI-run, hard-coded stale values, static verdicts), `board_checks.py` car-side loads (assumed).
3. Reproduced today: sim_inj_clamp.py (exit 0, 43 rows), circuit_sim.py (25 OK, 3 CHECK/6 REF, exit 0), circuit_sim_full.py (93 OK / 11 CHECK / 1 REF, after a path fix), board_checks.py (1602 OK / 265 CHECK / 4 FAIL; repo says 1606/263/4), board_thermal.py (needs rsvg-convert; shimmed), track_current.py (0 FAIL, worst 7.2 C), check_mcu_pins.py and check_pins.py (OK).
4. Bug (verified): track_current.py never checks the four injector clamp-return nets: the PCB net is `/Outputs/INJ1_CL`, the tool asks for `INJ1_CL`, finds no copper and reports `[OK] 0.0 C 0.00 A`. Low real impact (0.2 A on 0.8 mm), but "no copper found = OK" is the failure mode.
5. circuit_sim.py (run in CI, firmware.yaml:149) does not import design.py despite its docstring; its low-side driver section models NCV8406A / 60 V clamp / 8 mH / SMCJ40A (rev 0.5-0.6), not the VND7NV04 (40-55 V clamp) now fitted. VERIFICATION.md row 96 ("as built") is the rev 0.5 description.
6. circuit_sim_full.py crashes on today's tree (reads `motherboards/1989-93/...`, which exists only in ordered-boards/) - AttributeError: NoneType has no Zones; ran after pointing it at the ordered copy.
7. Thermal model result for the ORDERED rev 0.9 board, 20 mH, sequential 7200 rpm, h=10, no ambient added: driver junctions +78..+86 C above the air (8 mH: +46..+50). Inputs are hard-coded losses (1.2 A at 80 % duty per injector). Documented limitation (8 vs 20 mH) but numbers at 20 mH quantified here.
8. No tool tests: footprint-pad vs part pin mapping, JLC CPL rotation, EMC/SI (CAN, USB, crystal, wideband analog), buck loop stability, real injector L, ESD, real case temperature, mechanical fit, ADC noise/accuracy, tolerances (Monte Carlo).
9. CI runs only: check_pins, check_mcu_pins, check_image, circuit_sim.py, wideband build, unit-test engine sim. NOT in CI: board_checks, board_copper, circuit_sim_full, sim_inj_clamp, board_thermal, track_current, check_*_netlist, Renode (workflow_dispatch only, "while being brought up").
10. All tools are pre-hardware; the best remaining confidence tests are bench tests on the ordered boards (list at the end).

## Per-tool table

| Tool | What it actually checks | Where parameters come from | Independent reference? | Cannot see | Run today |
|---|---|---|---|---|---|
| sim_inj_clamp.py | ngspice transient of one injector wire: driver clamp (DRV, ordered rev 0.9) vs TVS-to-VBAT_IN (BAT, rev 0.10) vs TVS-to-GND; faults; 24-45 V; pairs; TVS sharing | VND7NV04 and TVS datasheet figures (cited in docstring, VERIFIED in code constants), injector 12-16 ohm from Mazda, L swept 5-20 mH (unknown), TVS tempco 0.1 %/C assumed, driver RDS 60 mOhm fixed, ES1D diode model assumed | Datasheet-derived models; no measurement. Tests the circuit idea against datasheet limits, not tautological, but cannot be better than inputs | Real injector L/R/saturation, wire L, VBAT_IN impedance other than 0.05 ohm + 10 uF, TVS pulse-heating/derating, driver clamp behaviour at repetitive rates (EAS is single pulse), TVS tolerance population | exit 0; 43 rows. 20 mH: DRV 15.3 mJ/shot (1.84 W batch @7200), BAT TVS 8.3 mJ (1.0 W batch) |
| circuit_sim.py | Input conditioning (hall, 12 V switch, CLT/IAT, VR, knock) and relay/low-side stages | Hard-coded numbers; NO design.py import (grep: only stdlib imports) although docstring line 3 says values come from design.py | Datasheet limits (STM32 VIH etc.) | Drift from design.py (nothing asserts). Section D simulates NCV8406A + SMCJ40A (old) | 25 OK, 3 CHECK, 6 REF; exit 0 |
| circuit_sim_full.py | Power-up/cold crank/brown-out, every MB output & input per year, wideband front end | design.py + mb_*.py (asserted), datasheet quotes, "assumed" load models (alternator 3 ohm/0.2 H, LSU equivalent) | Part-level datasheet limits; LSU model is an equivalent circuit, not Bosch data | Anything not simulated; thermal inputs come from board_thermal model | needs pcbnew + scipy; 93 OK / 11 CHECK / 1 REF after path patch |
| board_checks.py (+board_copper.py) | Copper netlist vs design; every harness cavity shorted GND/14.4/24 V/open, DC network | Car-side loads assumed (relay coil 80 ohm, injector 13 ohm...), cavity-function table (sim_report.py "independent references") from repo itself | Copper rebuild is independent of net names (good). Cavity table is the repo's own | DC steady state only; no transients, no tolerance spread; footprints vs pinouts; ordered-board revisions not run (uses current mb_* modules) | 1602 OK / 265 CHECK / 4 FAIL (4 = LSU drive resistors, documented) |
| board_thermal.py | 2-D/3-D FD heat map from real copper; per-part rise over air | Fixed loss table (1.2 A 80 % duty, rails 0.25-0.05 A guessed), h=10 (factor 1.5 unknown), laminate k recalled, Rth_jc from maker figures | Self-test: 54 C/W at h=10 vs recalled 40-50 (not re-read) | Ambient (case air), neighbours outside the board, component body cooling, airflow in a sealed case | selftest OK; default board rev0.10: seq D46 junction +51 C, batch1 D46 +116 C, Q1 +72 C |
| track_current.py | Resistor network of each net, IPC-2221 rise | Load cases hard-coded in cases() (assumed currents) | IPC-2221 (conservative) | Pour necks (pours treated as perfect conductors), thermal reliefs, via counts (1 mOhm each), only rev 0.10 netlist (design.py) | 34 nets, 41 cases, 0 FAIL, worst 7.2 C (VBAT_IN inner) |
| check_mcu_pins.py | Pin function/supply/EXTI per ST XML | ST open pin data XML | YES (ST) | Only F407 and only design.py (not the .kicad_pcb, not ordered boards) | OK, 79 pads |
| check_pins.py | firmware defines vs design.py | both repo-authored | partly | whether either matches the car | OK |
| check_image.py | Vector tables, OpenBLT CRC header, merged DFU | image files built in CI | self-consistency vs rusEFI's own verify code | Whether it boots on silicon | not run (needs build) |
| check_sch_netlist.py / check_mb_netlist.py | design.py pads vs KiCad netlist export of the generated schematic | design.py / mb_*.py vs gen_sch*.py output | NO: same source generates both | design errors; wrong symbol pin numbering vs real part | not run (needs export) |
| sim_report.py | firmware function -> pin -> cavity vs reference table | unit-test dump + design.py + table | table from repo | wrong table | not run |
| flash_sim/ + an3155_model.py | wideband flasher vs a model of the F103 ROM bootloader | AN3155 doc, "validated against stm32flash" | stm32flash is an independent client | real ROM bootloader timing/quirks, BOOT0/NRST wiring on the board | not run |
| sim/ (Renode) | real firmware on emulated F407/F103 with bench models | run_ecu.py hard-codes VBATT_DIV=(33+6.8)/6.8, ANALOG_DIV=1.56 etc.; LsuSensor uses firmware's own scale factors | NO for board wiring: stimulus is ideal voltages at named MCU pins | analogue front end, pin-to-connector wiring, EMC, real peripheral behaviour (many Renode gaps patched by the authors' own models: ADC, DMA, NVIC RETTOBASE...) | not run (no Renode) |

## Findings detail

### F1 track_current.py net-name mismatch (VERIFIED)
- `pcb file`: `(net 71 "/Outputs/INJ1_CL")` (also INJ2..4_CL); track_current.py:119/129/131 compares `GetNetname() != name` with name `INJ1_CL` (cases() line `out.append((f'INJ{i+1}_CL', ...))`). Output today: `[OK] INJ1_CL worst 0.0 C: 0.00 A in 0.0 mm on - near (-100.0, -50.0); 4 pour(s)`.
- Real impact: net routing shows 0.8 mm track, 1.41 mm, 0.2 A rms -> no hazard. Tool impact: a net that is not found is passed.
- Checked OUT_VVT (2.0 A) which also prints 0.00 A: it is a 6.9 mm wide pour on 4 layers (zone_neck.py) -> the perfect-conductor assumption holds there (checked, correct). OUT_IACV/BOOST same pattern, not separately checked.

### F2 circuit_sim.py stale/hard-coded (VERIFIED by grep + output)
- Output rows: `NCV8406A gate drive`, `1989-93 wire, two drivers + SMCJ40A (rev 0.6)`, `idle valve ... clamp peak 61 V`. design.py: VND7NV04 drivers, NCV8406A only in comments (design.py:334, 529).
- It runs in CI (firmware.yaml:149) and exits non-zero only on FAIL; the injector/idle/VVT/paired rows no longer describe the fitted driver, so a green run says nothing about it. circuit_sim_full.py and sim_inj_clamp.py cover the current driver.

### F3 circuit_sim_full.py path (VERIFIED)
`tvs_copper_area()` (line ~592) tries `motherboards/1989-93/...` then `mb/release_8993/...`; neither exists in the current tree (1989-95 merged). `pcbnew.LoadBoard` returned None here and the next line crashed. With the ordered-boards path added in my copy: 93 OK / 11 CHECK / 1 REF (repo VERIFICATION.md:861 says 93/11/1/0 FAIL: matches).

### F4 verdict logic in sim_inj_clamp.py is largely static (VERIFIED, code read)
`rec()` default verdict 'OK'. Group A, C, H (2-driver) always OK; F verdict = `vb > 30`, not the result (24 V jump start: driver clamp 50 mJ per shot printed, verdict OK); B: SMCJ15A/16A/18A show 97-100 % of the worst-case heat in the driver clamp yet verdict OK (only typical-case e_drv and reverse-battery tested). Fitted part 1.5SMC16A: worst case driver takes 0 %. No impact on the fitted part, but the verdict column cannot be used as pass/fail evidence.

### F5 Results of sim_inj_clamp today (selected, typical parts 14.4 V, 12 ohm)
- DRV (ordered rev 0.9): peak 42.7-42.8 V; per shot 4.0 / 6.4 / 9.6 / 15.3 mJ at 5 / 8 / 12 / 20 mH; 0.92 W sequential, 1.84 W batch at 20 mH 7200 rpm; current to 35 % in 409 us.
- BAT (rev 0.10): peak 31.9 V; TVS 8.3 mJ at 20 mH; 35 % in 572 us.
- Fault rows: TVS/diode open -> driver clamp (42.7 V); TVS short -> 15.4 V, decay 1.56 ms; diode short -> driver in current limit 5.9 A from battery input (injector gets no voltage). 40-45 V supply: driver clamp 178-225 mJ per shot (> 200 mJ EAS at 45 V) -> CHECK.
- Pair, one driver carrying two injectors, worst case: TVS 19.5 mJ = 1.17 W (one opening per cycle), 2.34 W with two.
- Sharing of unequal TVSs: 1.5SMC16A 20 mH: low part takes 1.95-1.99 W of 2 W until 100 C hotter.

### F6 board_thermal.py results
Rev 0.10 current board (6 layer): seq: 5.9 W, Q1-4 +39..41 C, D46-49 junction +50..52 C, U4 +44; batch1: D46 +116 C, Q1 +72 C.
ORDERED rev 0.9 (4 layer; rev0.10 loss table applied to ordered refs - refs U4, U14, Q1-Q7 exist; clamp D42-49 absent so case rev09 puts clamp energy in the drivers): 8 mH: 5.3 W, Q junction +46..50 C; 20 mH: 7.5 W, Q2 +86 C, U14 +67 C. Tool adds no ambient: in 85 C case air the 20 mH driver junction would be about 171 C (INFERRED, simple addition; model assumes 1.2 A at 80 % duty on every injector at 7200 rpm, a severe case). VND7NV04 junction limit/thermal shutdown not re-read here.
Self-test: 54 C/W (h 10), 71 (h 6), 44 (h 15) vs "40-50 recalled" -> h=10 is slightly pessimistic relative to the recalled DPAK figure; not re-read from a datasheet.
Tool dependencies not in the repo's instructions: rsvg-convert, kicad-cli, scipy and pcbnew together.

### F7 Renode / system sim (not run; read only)
- sim.yaml: `on: workflow_dispatch` only; docs (VERIFICATION.md:594) call it "in CI", but nothing triggers it automatically.
- run_ecu.py:116-156 hard-codes dividers and drives ideal voltages at PA1/PA2/PA4/PA5/PB0/PB1/PC5 from its own pin table; the firmware config uses the same assumptions. A divider placed on the wrong ADC pin on the PCB, or a wrong value, would not be caught (check_pins.py/check_mcu_pins.py cover pin names vs design.py only).
- LsuSensor.cs: "uses the firmware's own scale factors so that what is tested here is the firmware" - admitted; analogue front end only in circuit_sim_full.py with an equivalent circuit.
- Renode models written by the authors to get past Renode gaps (ADC, DMA, NVIC RETTOBASE, F103 ROM bootloader, TIM11 capture) mean a pass shows "firmware runs on these models".
- AN3155 model: validated against stm32flash, but the ROM bootloader of a real F103 (BOOT0/NRST timing, RDP, 9-bit parity frame) is untested on hardware.

### F8 Schematic checks are generator tautologies (INFERRED from code)
check_sch_netlist.py compares design.py pads with the netlist KiCad exports from schematics that gen_sch*.py wrote from design.py. It catches generator bugs (split/merged nets) and is useful for that; it cannot show that design.py matches a part's real pinout. The independent counterpart (check_mcu_pins vs ST XML) exists only for the F407.

### F9 board_checks.py scope
Runs the current scripts' netlists. 1989-93 and 1994-95 columns appear (mb_y8993, mb_y9495 modules) but these modules are the current versions, not necessarily the frozen ordered revisions (ordered rev 0.11/0.9/0.7) - INFERRED, other audits (B17) own the diff. The 265 CHECK rows are mostly: V5_EXT backfeed 24 V, FT pin analog above VDDA at 3.6-3.9 V (abs max VDD+4 = 7.3 V so not damaging, reading error only), ZXMS6004 thermal cycling in a 24 V short, R36/R33 87 % rating at 24 V. FAIL x4 = R108/R110 LSU drive resistors (documented).
Count differs slightly from repo claim (VERIFICATION.md:860: 1606 OK / 263 CHECK / 4 FAIL; today 1602 / 265 / 4): unexplained 2-row drift, likely later edits; low importance.

## Ranked: repo claims whose supporting tool is weakest (1 = weakest)
1. "Firmware-in-the-loop passes for all six model years / ECU + wideband flash, CAN, lambda 0 FAIL" (VERIFICATION.md:594, README of sim): emulator with author-written peripheral models, ideal stimulus at MCU pins, firmware's own scale factors; says nothing about the PCB; not run automatically; never on silicon.
2. "Schematic = design" (check_sch_netlist/check_mb_netlist, ERC): same-source tautology; no human review (review brief); part pinouts/footprints unchecked by any tool.
3. Temperatures (board_thermal, circuit_sim_full thermal inputs): all inputs assumed (loads, h, laminate k), no ambient, injector L unknown; documented as model output but "within rating" statements rest on it. Especially the ordered rev 0.9 at 20 mH.
4. Injector clamp behaviour (sim_inj_clamp, docs line 762): datasheet-built models, L unknown, verdict column static; real-world TVS sharing, wire inductance and VBAT_IN impedance unmodelled; ordered rev 0.9 relies on the VND7NV04's own clamp repetitively (EAS is single-pulse).
5. Wideband analogue front end and heater (circuit_sim_full section W, LsuSensor): LSU equivalent circuit, no real sensor, new layout (documented), no noise/EMC.
6. "CI circuit simulation green" (circuit_sim.py): stale driver models, hard-coded values, FAIL only on a few rows.
7. Track-current check (track_current.py): vacuous on INJ_CL nets, assumed loads, perfect pours, rev 0.10 only (ordered boards not covered).
8. Fault tables (board_checks): good method (DC), assumed car loads, no transients (load dump, ignition spikes, ESD), no tolerance stack.
Strong: copper == design (board_copper), MCU pin functions (check_mcu_pins vs ST), image headers (check_image), AN3155 flasher against stm32flash-validated model.

## Suggested real-confidence tests
Bench on the ORDERED boards before first power (they can still be reworked):
1. Continuity/ring-out of every J1/J2 pin to the harness cavity and to the MCU test pad (DMM, 30 min per board) - covers wiring/footprint errors no tool sees. Compare with kb/interconnect.md.
2. First power on a current-limited lab supply (limit 100 mA, then 1 A): measure +12V_F, +5V, +3V3, V5_EXT/V5_SENS, buck switching node on a scope; test reverse battery with the limit set, 14.4 V, 9 V and 6 V (cranking dip) with a dip generator; 24 V for 1 minute.
3. Injector turn-off bench: real Miata injector (and a 12-16 ohm / known-L dummy), measure L with an LCR meter (resolves 8 vs 20 mH), scope the drain at 14.4 V, 7200 rpm equivalent for 30 min with a thermocouple/IR camera on Q1-Q4 and clamp TVSs (rev 0.9: driver clamp; check 42-45 V peak and case temperature). Run the 1989-93 paired wiring too.
4. Hardware-in-the-loop with a trigger simulator: a small MCU (or a second ECU's output / a signal generator) producing NA CAS and NB crank/cam waveforms with jitter and 5-12 V amplitudes, plus resistor decades for CLT/IAT, pots for TPS/MAF, a 12 V PWM load box (injector coils, idle valve) - compare rusEFI's logged RPM/sync/ADC values and pin timing against the source; run cold-cranking dips through the supply. This is what Renode currently stands in for.
5. Thermal measurement: thermocouples/IR camera on U2, U4, U14, Q1-Q4, D46-49 (or D42-45 area) at 85 C oven ambient inside the stock ECU case (or a mock-up) under the sustained-load case; compare to board_thermal rises (+39..52 C seq at 10 W/m2K) and fix h and the loss table.
6. Wideband: calibrate with a free-air LSU 4.9 (lambda 20.9 reading), heater warm-up current on a clamp meter, ESR injection scope check, short-to-battery on the LSU wires with a limited supply (R108-R110 sacrificial, documented).
7. Flashing: test the F103 programming path on the actual board (BOOT0/NRST) - the only evidence today is a software model.
8. Environmental/EMC quick checks: ISO 7637 pulse-ish ignition coil spark nearby, USB/CAN eye on the scope, ESD gun on USB-C and harness header.

## Sources actually read
firmware/tools/sim_inj_clamp.py (full), circuit_sim.py (parts), circuit_sim_full.py (header, asserts, tvs_copper_area), board_thermal.py (header, losses, main), board_checks.py (header, main tail), board_copper.py (header), track_current.py (cases, Net), check_mcu_pins.py (header), check_image.py/sim_report.py/an3155_model.py/LsuSensor.cs (headers), check_sch_netlist.py, check_mb_netlist.py, .github/workflows/firmware.yaml and sim.yaml, firmware/sim/README.md, run_ecu.py (divider lines), VERIFICATION.md lines 96-101, 594, 860-861. PCB net names from daughterboard/miata_ecu_daughter.kicad_pcb.

## Not checked
Renode runs; run_ecu.py check table in detail; C# models line by line; flash_sim run (needs stm32flash/gcc); sim_report/board_checks `--sim-log` path; check_image on a built image; track_current on the ordered boards (design.py is rev 0.10, would mismatch); board_thermal against motherboards; Monte Carlo/tolerance of any model; whether the 1989-93/94-95 columns of board_checks equal the frozen ordered revisions; datasheet limits for VND7NV04 junction temperature (not re-read today); OUT_IACV/OUT_BOOST pour necks.
