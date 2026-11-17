# R02 - FOME / rusEFI open wideband controller: design history, known problems, validation; the wider field

Status: complete (final pass 2026-11-16). Files under kb/research/files/R02/.
Date of all reading: 2026-11-15.

## Summary (10 lines)

1. The on-board wideband is mck1117's "wideband" design (MIT, (c) 2023 Matthew Kennedy), shared by rusEFI and FOME; FOME has no separate wideband repo (FOME fw embeds the rusEFI image and CAN updater).
2. Variants: F042 "module" rev A/B/C (1 ch, Hellen/Proteus embedded), F103 single (rev2/rev3) and F103 dual (dual, dual_rev1) boards in rusefi-hardware. The project's F103C8 port is a custom port (no bootloader).
3. **R110 is the wrong part**: LCSC C25341 is 0.62 ohm (620 mOhm), not 62 ohm; this is the pump-current shunt. In the ordered rev 0.9 BOM too.
4. Trim resistor: not read by firmware (grep, no hit); it is in the sensor plug between IP and RT and acts in the analog sense path; nominal 61.9 ohm constant.
5. Heater: preheat 2 V, ramp 7 V +0.4 V/s, closed loop on ESR (7.5 V nominal), PWM duty (Veff/Vbat)^2, off below 8.5 V, start above 9.5 V, hard cut at >=23 V.
6. Documented sensor accuracy is Bosch's (+-0.007 at lambda 1, +-0.01 at 0.8, +-0.05 at 1.7); no published validation of the FOME controller was found (forum bench checks are free air and a flame only).
7. Known field problems: heater never starts without Vbat over CAN (F0), stuck underheat after 12 V loss (issue 348, fixed after the project's pin), lean blip at start (303 open), 65 s to detect no sensor (295 open), unprotected inputs (309 open), F0 rev B boards from JLC that read 1.01 in air (forum, unresolved).
8. Competitors: AEM X-series ~$200-231, Innovate LC-2 $145 (no sensor) to ~$170-250 kit, Spartan 3 Lite V2 ~$82-135; all Bosch LSU 4.9, closed source. Open: OWBC (GPL-3), BL49/NanoLambda (CJ125, one CC BY-NC).
9. Conclusion: a ~12-IC discrete FOME-style controller on a $399 ECU is a sound, cheap way, but unvalidated; bench plan in section 8.

## 1. What the upstream project is (repositories, lineages, licence)

| Fact | Source | Tag |
|---|---|---|
| `mck1117/wideband` (Matthew Kennedy) is the origin: 810 commits, first 2020-09-19, HEAD 307cda8 2026-11-13 "bump image"; tags `first-release` (2023-06-06), `2311-release`, `2508-release`, `2611-release` (2026-11-13) | full-history blobless clone in `work/R02-fome-and-open-wideband/clones/mck1117-wideband-hist`, `git log`, `git for-each-ref refs/tags` | VERIFIED |
| `rusefi/wideband` `master` is the same history (HEAD d14ce8a 2026-11-09, 2 commits behind mck1117); rusEFI's own work lives on branch `prod-2026-01` (HEAD 1b985ab; code head 27e115b 2026-01-24), forked from upstream at acd0463 (2025-12-13): 47 commits not upstream, upstream has 41 commits not in it | clone `clones/rusefi-wideband-hist`; `git merge-base`, `git log A..B`; `CHANGELOG-rusefi.md` at 1b985ab | VERIFIED |
| The project under review builds its wideband image from rusEFI's submodule `firmware/controllers/can/wideband_firmware` = rusefi/wideband **27e115b** (branch `prod-2026-01`) | `repo/firmware/wideband/miata_wbo_f103.txt` ("wideband: 27e115b7..."), `git submodule status` in `repo/firmware/ext/rusefi` (rusEFI 1374bd0) | VERIFIED |
| Licence of hardware + firmware repo: MIT, "Copyright (c) 2023 Matthew Kennedy" (single LICENSE file at repo root, added 2023-01-07 commit 4d8ee93; no separate hardware licence) | `ext/wideband-mck1117/LICENSE`, `ext/wideband-rusefi/LICENSE` | VERIFIED |



## 2. Hardware variants and revisions

| Variant | MCU | Where | Firmware target | Source | Tag |
|---|---|---|---|---|---|
| Module rev A (archived), rev B (2023-02-20 export), rev C (2026-03-22, "just BOM improvements") | STM32F042 | mck1117/wideband `hardware/board_module`; embedded in Hellen/Proteus ECUs and standalone with `board_carrier` (5 V reg, CAN xcvr) | `firmware/boards/f0_module` (readme: also Hellen-one `modules/wbo`) | `ext/wideband-mck1117/hardware/README.md`, `firmware/boards/*/readme.md`, git log of `hardware/` (8b056b7, c2547c1, 9e8c618, ede169c "update to kicad 6, break out SEL pins, add 4.2/ADV support switch, TC2030 programming header") | VERIFIED |
| F103 single rev2 / rev3 | STM32F103 | rusefi-hardware `wideband-F103` | `f1_rev2`, `f1_rev3` (rev3 board config has battery divider 100k/10k, heater low-side sense, Vm sense, AUX out) | boards readmes; `f1_rev3/wideband_board_config.h` | VERIFIED |
| F103 dual (rev0, rev1 "is known to work") | F103 (rev1: F103RCT6, original ST, OpenBLT) | rusefi-hardware `lambda-x2` | `f1_dual`, `f1_dual_rev1` (heater low-side voltage sense per channel; GD32 ADC problems forced -O0 / 48 MHz on early dual) | readmes; mck log a605289, e51dc3b, 2e06719 | VERIFIED |
| This project's board | STM32F103C8 | daughterboard U102 | custom `repo/firmware/wideband/miata_f1` copied from f1_rev3 + f0_module analog constants, no bootloader, no TS port | `repo/firmware/wideband/README.md`, `miata_f1/wideband_board_config.h` | VERIFIED |

Sensor types in firmware: LSU 4.9, LSU 4.9 FAE, LSU 4.2, LSU ADV (SEL pins / CAN "set sensor type"). Source: lambda_conversion.cpp, commit f7d527a/8635989. VERIFIED.
Which ECUs embed it: Hellen boards (F042 module, JST XH or MX120 connector), Proteus/Poly (module powered from 5 V of the ECU, issue 348), FOME uses the same module (FOME wiki `Wideband-Module.md`: "FOME wideband controller", F042 pinout identical to rusEFI doc). VERIFIED (docs); exact list of ECUs UNVERIFIED.
Revision changes that are documented: F103 rev2->rev3 (09872e0 "F103 rev 3"); dual rev1 measures Un_sense and avoids clamping (c7a8365), PWM changes (b1bf9bf); F042 rev B -> C only BOM. No changelog explains why for hardware; only commit titles. INFERRED motive for dual rev1: GD32 ADC problems (commits cited).

## 3. Firmware behaviour that matters for this board (pinned 27e115b)

- Heater (`heater_control.cpp`, `wideband_config.h`): preheat at 2.0 V effective for 5 s (HEATER_PREHEAT_TIME), then ramp starting 7 V (9 V if already hot) at 0.4 V/s up to 12 V cap; closed loop when temperature > target-30 C; PID on ESR around 7.5 V; faults: not hot after 60 s warmup timeout -> SensorDidntHeat, >target+100 C for 0.5 s -> overheat, <target-100 C for 0.5 s -> underheat; all stop heater. Duty = (Veff/Vsupply)^2. Hard cut when supply >= 23 V. Start allowed when supply > 9.5 V for 0.5 s, stops below 8.5 V. VERIFIED.
- Supply-voltage sensing: boards with HEATER_INPUT_DIVIDER measure heater supply on Heater- while FET is off (duty limited every 10th cycle via HEATER_MAX_DUTY); boards with BOARD_HAS_VOLTAGE_SENSE use their battery divider (this project: R120/R121, 100k/10k); otherwise the value sent by the ECU over CAN. `CAN: always trust Vbat from ECU` (9ad50ba) and `validate Vbat even if force-heat command` (6d27ef2) are in rusEFI's prod branch. VERIFIED (source). The project's port has no CAN ECU in the loop for heater allow (the F407 talks to it how? not checked here) so heater allow = Unknown -> local voltage rule.
- The upstream commit 9295698 (2026-04-10 "avoid trying to heat when battery voltage is low") and 91aa7c6 (ignore firmware-update request without an ID) are NOT in the pinned 27e115b. VERIFIED (`master_not_in_pinned_log.txt`).
- ESR (temperature) = ESR_supply_R / (3.3/Nernst_AC - 1) - VM_RESISTOR_VALUE; the project sets VM_RESISTOR_VALUE 11.6 (R109 10 ohm + 1.6 ohm PTC F2 typical); PTC resistance varies with temperature and tolerance; effect on ESR small (1 ohm of about 300 ohm at target) INFERRED; sampling.cpp:75-83.
- Lambda conversion: piecewise linear in pump current, LSU4.9: lambda-inverse = 0.99559 + (-0.28299 rich / -0.44817 lean) * Ip; comment claims 0.5% error 0.8-1.0 vs the Bosch table. Source lambda_conversion.cpp. VERIFIED (claim by author, not independently checked).
- LSU_SENSE_R 61.9 ohm fixed constant (`wideband_config.h:27`); there is no per-sensor trim value anywhere in firmware (grep trim|rcal: no match). VERIFIED.
- CAN: base ID 0x190 (400), +2 per controller index, lambda in bytes 2-3 (0.0001), range 0.5-2.0; the bootloader ID set by `WB_BL_ENTER` with hardware ID; `can: reset heaterAllow if no status message from ECU for 250 ms` (095b507). rusEFI doc `master_rusEFI-Wideband-Controller.md`; commits. VERIFIED.

## 4. How the trim resistor is treated

- Bosch tech info: the trimming resistor (30-300 ohm) is in the connector module, drawn between APE (IP) and IA/RT, with the controller's 61.9 ohm measuring resistance across IP and RT. FOME wiki: "pins 1 and 5 have a laser-trimmed resistor between them". (`kb/research/files/R15/bosch_lsu49_techinfo.txt` lines 61-80; `files/R02/fome_Wideband-Module.md`). VERIFIED.
- FOME circuit: Ip_sense = 10*(LSU_Ip - LSU_Rtrim) across the on-board 61.9 ohm (R10; schematic text in module_revC), driven through a 47 ohm. The project's R110 is the equivalent, joined between LSU_RT and LSU_IP (`evidence/cur_db/pcb_nets.txt`: LSU_RT = J2.34 R108.1 R110.1 R111.2 R134.1; LSU_IP = J2.36 R110.2 R112.2). VERIFIED.
- So the trim is applied electrically by the analog path and the firmware treats every sensor as nominal: there is no sensor-specific calibration and no free-air calibration. INFERRED (and consistent with R15 note 9). The exact electrical interaction (the trim resistor in parallel with the 61.9 ohm shunt or in series with the pump path) I did not resolve from the Bosch drawing alone; a bench test (section 8) settles it.

## 5. Known problems in the field and fixes (primary: GitHub issues of mck1117/wideband read via API 2026-11-16; forum threads)

| Problem | Evidence | Status / fix | Tag |
|---|---|---|---|
| F0 module: lambda stuck ~1.010 in air, pump current 0, PumpDuty 0%, Nernst 0.09 V; ten rev-B boards assembled by JLC | rusefi.com/forum/viewtopic.php?p=49394 (issue 310) | No confirmed fix; suspected pump current source / assembly. A BOM error of this kind would look exactly like this (see section 7) | VERIFIED (thread read), cause UNVERIFIED |
| Bench: heater never starts / green LED fast flash | forum t=1856 p.6 | Early firmware required Vbat over CAN from the ECU; later heater logic uses local sense where available; F0 has none | VERIFIED |
| Brand-new sensor failed to heat, 0.3 V Vbat dip when heater switched on (motorcycle) | issue 299 | Weak wiring/supply; firmware changed to heat more aggressively (3a77efb reduced stabilisation 3 s -> 0.5 s; 982cd32 no preheat on low voltage) | VERIFIED |
| Stuck in underheat after 12 V lost then restored (ECU powered by USB 5 V) | issue 348 (closed 2026-02/04) | Fix upstream 9295698 (2026-04-10), not in pinned image | VERIFIED (fix inferred from timeline) |
| Lean blip at start on both channels | issue 303 (open) | Unexplained; probably real sensor settling INFERRED | VERIFIED existence |
| 65 s to detect no sensor | issue 295 (open) | none | VERIFIED |
| Inputs not protected: heater wire on Vm destroyed F042 | issue 309 (open) | none; relevant to the project's sacrificial resistors | VERIFIED |
| Heater duty oscillation | issue 325 | ms->s conversion bug on master, fixed | VERIFIED |
| Nernst not regulated to 450 mV | issue 312 | user support, forum t=2740 | UNVERIFIED cause |
| Overheat shutdown after 3-4 min on the bench (no exhaust flow) | forum t=1856 p.6 | expected (sensor temp measured by ESR; the bench has no flow) UNVERIFIED | VERIFIED existence |
| Reading wrong at high exhaust pressure/temperature | Bosch ds: pressure <= 2.5 bar, "higher with decreased accuracy"; no rusEFI/FOME correction table or pressure compensation exists in firmware (grep) | not handled (naturally aspirated Miata not affected, turbo cars are) | INFERRED |
| DFU flashing write failures | forum t=1856: use ST-Link | | VERIFIED |
| CAN: bus selection in FOME 2026 (many ECUs run the controllers on CAN2) | FOME release notes (search result), UNVERIFIED | | UNVERIFIED |

Noise: no specific noise issue found in issues; the firmware oversamples (ADC_OVERSAMPLE 24) and low-pass filters (alpha 0.02 pump, 0.002 ESR). VERIFIED (config), field noise reports UNVERIFIED (none found).

## 6. Firmware update path

- Upstream: OpenBLT bootloader in the F042/F103 images; the ECU (rusEFI, FOME) embeds `wideband_image.h` (no bootloader image) and updates the controller over CAN: sends WB_BL_ENTER (DLC 1 with controller index; legacy DLC 0 fallback), waits for ack, then streams the image (`fome-fw/firmware/controllers/can/rusefi_wideband.cpp`, read 2026-11-16 from GitHub raw). The rusEFI doc also mentions SD card update/rollback (rusefi PR 8870). First programming is by SWD (TC2030) or DFU (BOOT0 to 5 V, USB D+/D-; STM32CubeProgrammer, not ST-Link utility) (`files/R02/fome_Wideband-Module.md`, `master_rusEFI-Wideband-Controller.md`). VERIFIED.
- This project: no bootloader; the F407 firmware carries `miata_wbo_f103.bin` and "Flash on-board wideband" (repo README). The mechanism (UART bootloader of the F103 system ROM on BOOT0/NRST?) is not in my scope; the `WB_BOOT0` net goes from U102 pin 44 to R129 and U1 pin 57 (evidence pcb_nets), suggesting the F407 drives BOOT0 to use the ROM UART bootloader. INFERRED, UNVERIFIED.

## 7. Parts check found while reading the circuit: R110

- Schematic value "62", footprint 1206, LCSC C25341 (`repo/scripts/design.py:64` map `'62': 'C25341'`; `wideband.py:153` R10 -> C25341; ordered BOM `repo/ordered-boards/2026-11/daughterboard/fab/miata-ecu-daughterboard-rev0.9_jlcpcb_bom.csv:76`; current `evidence/cur_db/sch_bom_grouped.csv:72`).
- Live lookup today (`tools/lcsc.py C25341`): MPN 1206W4F620**L**T5E, JLC description "620mΩ", LCSC parameter Resistance "620mΩ". The other values of the same family in the same table are written 100J = 10 ohm (C17903), 470J = 47 ohm (C17969), so 620**J** = 62 ohm, and the 62 ohm 1206 part with that family is C17971 (1206W4F620JT5E, 62 ohm, 250 mW, +-1%, stock 123034, $0.0053 at 1). The Uniroyal datasheet's own naming table is for 0603 marking and does not list the L suffix; I rely on the two independent catalogue entries (JLC and LCSC both say 620 mOhm). VERIFIED (catalogue), the MPN-letter reading is INFERRED.
- Consequence INFERRED: pump current sense gain becomes 0.62 ohm instead of 61.9 ohm: Ip_sense (x10 amp) would be ~1/100 of nominal; lambda computed from that current would stay close to 1 (0.9956 + gain*Ip with Ip tiny), the Nernst control would still try to regulate through the DAC, and the pump drive would saturate; the symptoms (lambda about 1.01 in free air, pump current 0, Nernst far from 450 mV) resemble the forum report above.
- Fix: replace R110 with C17971 (or a 61.9 ohm E96 1206 1% part) before power-up on the ordered rev 0.9 boards, and correct design.py/wideband.py. Cost +$0.0010. Also note R108-R110 3x1206 parts keep.
- 62 vs 61.9 ohm: +0.16% gain, small versus 1% tolerance; 800 ppm/C tempco of C25341 would not matter once replaced; the 100 ppm/C part is better. INFERRED.

## 8. The wider field

| Product / design | Approach | Cost / price | Accuracy claim | Source | Tag |
|---|---|---|---|---|---|
| AEM X-Series 30-0300 (gauge) | Bosch LSU 4.9, factory resistor-trim or free-air calibration modes, CAN/analog | $199.95-230.95 (AEM list; retailers 205-231), 2026-11-16 | no numeric accuracy; "fastest responding" (third-party test) | AEM manual (R15 files), search results | VERIFIED for price listing, accuracy none |
| Innovate LC-2 | patented digital control, LSU 4.9, 2 analog outs + serial | controller+8 ft cable $144.99 (maker), kit $170-250 | EU retailer "0.007 lambda up to 1.0" (UNVERIFIED), range 7.4:1-22.4:1 | search results | UNVERIFIED-ish |
| 14point7 Spartan 3 v2 | closed; LSU 4.9 and ADV | $138.99 (discontinued per retailer; superseded by AMP), Lite V2 $82.50-135 | 10 ms response, 0.6-3.4 lambda range | diyautotune and others (search results) | UNVERIFIED (snippets) |
| 14point7 SLC Free | I could not find the page ("SLC Free" returned nothing) | | | | not found |
| fpoussin/OWBC | STM32F3, open hardware, GPL-3.0, 18 commits, no releases | | none | github.com/fpoussin/OWBC | VERIFIED (page) |
| oelprinz BL49 / BL49SP | Bosch CJ125 + ATmega32M1, CAN, analog | | none stated | github | VERIFIED (search snippet) |
| TurboCorse LambdaCtrl (NanoLambda, CJ125) | LSU 4.9 only, CC BY-NC 4.0 (no commercial use) | | | github search result | UNVERIFIED (snippet) |
| rusEFI "DEAD DESIGN" CJ125 add-on | abandoned in favour of the discrete design | | | forum t=1052 title | VERIFIED title |
| RP2040 designs | none found | | | search | negative result |

Why FOME's circuit is not CJ125: the CJ125 ASIC (Bosch) is a single-source part, with supply risk; mck1117's thread title says "Fully Custom, no ASIC!" (forum t=1856). VERIFIED title; motivation INFERRED.

## 9. Is the embedded circuit the cheapest sound way? What would a cheaper / more robust variant look like?

- INFERRED yes, with conditions: the design needs 2 quad/dual op-amps (MCP6004-class and AD8628 per the module BOM), one MOSFET, a few resistors and an MCU; at the $399 ECU price a bought-in AEM unit ($200+) is far more expensive. The F103C8 is in stock at JLC (cost belongs to other audits).
- Cheaper: share the F407's own ADC/DAC/timers to run the loops would remove the F103 (and the REF3033) but would couple the 2.5 kHz pump loop to engine firmware and lose independent heater safety; I advise against it (INFERRED).
- More robust: (1) fit the right R110 (section 7); (2) sensor-side protection against Vm/Ip/Rt shorts to battery (issue 309 destroyed an F042); (3) take firmware from upstream master (heater low-battery fix 9295698, firmware-update guard 91aa7c6); (4) keep the hardware watchdog of the heater on the F103 independent from the F407; (5) consider an upstream-style bootloader or documented ROM-bootloader path so field updates do not need SWD.

## 10. Bench test plan for the first boards (bench, no engine)

1. No sensor: power at 12 V and 9, 14.4 V; check 3.3 V ref, Vm 2.5 V (U101 outputs), heater FET off, LED/CAN status shows "no sensor"; check heater PWM stays 0 with 8 V (below 8.5 V) and with 24 V.
2. Simulated sensor on the connector: resistor network replacing the sensor: Rtrim 61.9 ohm... a dummy load with a Nernst cell model is hard; use (a) 100 ohm between IP and RT (trim equivalent), (b) 300 ohm between Un and Vm (ESR 300 ohm at the target), (c) a lab supply injecting 0 to +-3 mA on IP with 3.3 k load to compare Ip_sense reading vs the CAN `PumpDuty`/pump-current channel at 0, -1, +1 mA. Verify the shunt: V(IP)-V(RT) = 62 ohm x I (measure with a DMM to 0.1%).
3. Heater: 3.5 ohm power resistor 10 W as heater load (LSU 4.9 heater about 3 ohm cold); log duty and supply; check Veff 2 V preheat, 7 V start, and the fault codes at no-load (3 blinks equivalent).
4. Real sensor in free air: lambda reads 2.0 (free air about 20.9% O2 gives lambda ~ 2 saturated range; the firmware maximum ~2.0) within seconds of closed loop (about 780 C reached in 20-30 s), steady; repeat with a second sensor; Nernst at 0.450 V +-5 mV. Heater current 1.0-1.5 A at warm-up (Bosch 7.5 W nominal).
5. Test gases: bottled mixtures (for example 1 % CO + N2 or bottled O2/N2 for 5 and 10 %, calibrated, around lambda 0.8, 1.0, 1.7 per Bosch ds points) through a closed sensor adapter: compare to Bosch table (+-0.01 at 0.8, +-0.007 at 1.0, +-0.05 at 1.7). Cheaper: propane lighter flame (qualitative; the forum used it).
6. Comparison meter: a commercial controller with the same sensor model (AEM 30-0300 or Innovate LC-2, analog or CAN), both sensors side by side in a tee or two sensors in the same exhaust at idle on a running engine; compare after both warm; expect within 0.02 lambda around 1.0 (INFERRED target).
7. Disturbance tests: supply dips 14.4 -> 9 -> 6 V (cranking), +- noise injection, heater PWM on/off effects on Nernst reading, CAN bus error/termination, USB-only power.
8. Update path: flash from the F407, power-cycle, confirm CAN IDs 0x190.

## Implications for this project (tie to review brief goals)

1. (Goal 1 errors, severity critical, confidence high on catalogue, medium on effect) R110 part is 0.62 ohm: replace by C17971 on both the ordered daughterboard rev 0.9 (hand rework: one 1206 resistor) and the current design; fix design.py:64 and wideband.py:153.
2. (Goal 1/4) Pin the wideband firmware to a newer commit or cherry-pick upstream 9295698 (low-battery heating) and 91aa7c6; they are not in 27e115b. Medium.
3. (Goal 1) Trim resistor is not handled in firmware; no free-air calibration exists; document that the sensor and its plug are a pair, and that the pigtail needs no resistor. Low. Add the Rtrim bench check from section 10.
4. (Goal 4 UX) No documented validation of accuracy beyond Bosch's sensor datasheet; the first boards need the bench plan; publish results. Medium.
5. (Goal 1) Input protection: upstream issue 309 shows miswired heater/Vm destroys the F042; the project has sacrificial R108-R110 and PTC (repo-documented). Info.
6. (Goal 5 cost) The discrete-circuit approach is the cheapest option found; AEM/Innovate/Spartan retail at $82-231 without ECU. Info.
7. (Goal 4) Update path: no bootloader in the project image; users need the F407 flash path; document it. Low.

## Sources actually read

- Local: the review brief; ext/wideband-mck1117, ext/wideband-rusefi (README, hardware README, firmware/boards/*/readme.md, LICENSE, kicad_sch text for Rtrim, git logs in work/); `work/R02-.../clones/rusefi-wideband-pinned-27e115b/firmware/{heater_control.cpp,sampling.cpp,lambda_conversion.cpp,wideband_config.h,boards/*}`; repo/firmware/wideband/*; evidence/cur_db pcb_nets and sch_bom_grouped; kb/parts_manifest.md; datasheets/txt/C25341*; kb/research/R15 and files/R15 (Bosch ds, techinfo).
- Web (2026-11-16): github issues API for mck1117/wideband (#295,299,303,309,312,320,325,348 and list); github.com/FOME-Tech org repos list; raw fome-fw rusefi_wideband.cpp; FOME wiki `Wideband-Module.md`, `Wideband.md` (files/R02); rusEFI doc `rusEFI-Wideband-Controller.md` (files/R02); forum rusefi.com t=1856 p.150 and p=49394 (page fetch summaries); github.com/fpoussin/OWBC (page fetch); search results for AEM, Innovate, Spartan, BL49, LambdaCtrl.

## Not checked

- Exact ECUs that embed the module; hardware changelog reasons; Bosch accuracy under pressure and temperature curves beyond the datasheet statement; 14point7 SLC Free; Spartan/Innovate/AEM accuracy numbers (no primary source); AEM X-series BOM cost; parts cost of the FOME circuit (not priced by me; see kb/parts_manifest); rusEFI wiki "Firmware-update-via-CAN" page (not fetched); full read of forum threads t=2314, t=2200; whether the F407 flashes the F103 via ROM UART.
