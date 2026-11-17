# B03 - Ordered boards (Nov 2026): delta vs current design, carried problems, consistency, bring-up plan

STATUS: complete (2026-11-16). Scratch: `work/B03-ordered-boards-delta-and-bringup/` (delta*.txt = machine diffs of the PCB pad/net lists, `mate.py`, `u1map.py`, `vip.py`).
Tags: VERIFIED = read/computed from design files today; INFERRED = reasoning shown; UNVERIFIED = memory/secondary.

## Summary
1. Ordered hardware = daughterboard rev 0.9 (4 layers, 310 parts) + 5 motherboards. All five ordered motherboards mate with the ordered daughterboard: all 80 J1/J2 pins match JD1/JD2 by net (only exception: HTR_GND on J2-39/40 lands on GND, an intentional tie), same 14.5/42.0 mm offset, no rotation (VERIFIED, mate.py). 
2. Every MCU pin the frozen firmware uses matches the ordered daughterboard netlist (VERIFIED, u1map.py vs miata_pins.h / board_configuration.cpp / knock_config.h / wideband_uart_flash.cpp, incl. the F103 flash UART crossing PD8->PA10, PD9->PA9).
3. Reworks worth doing BEFORE first power-up: (a) 220 ohm in each of Q1-Q8 inputs; (b) decide the 1989-93 R23/R24 pairing; (c) decide tach on 1989-95; (d) battery-sense wire R11.1 -> VBAT_IN (optional); (e) F1/L1 only if hot-soak shows trips.
4. NOT recorded anywhere in the repo: whether the 4-layer order used epoxy-filled vias. 664 of 1423 vias sit inside SMD pads (404 in the Q1-Q8 tabs). Check the JLC order confirmation; if not filled, expect wicking/tombstoning risk and inspect/X-ray the DPAKs. On 4-layer JLC charges extra for fill (free only 6+ layers).
5. Ordered db has NO per-injector clamps (D46-49/ES1D absent): on 1994-2005 the injector turn-off energy goes into the VND7NV04 clamps (VCLTH 36 V); on 1989-93 the mb D3/D4 SMCJ30A take it.
6. Ordered CEL is behind the shared driver enable and battery sense is after D7/F1 (both VERIFIED from netlist), as the repo already admits.
7. Ordered tach (OUT_TACH) goes straight to 2I with no jumper on 1989-93 and 1994-95 (VERIFIED). Firmware default tach output ON (miata_board.cpp:86).
8. Staged bring-up plan in section 4 (bare daughterboard first, current limit 0.3 A).

## 1. Delta ordered vs current (from netlists/PCB, not changelogs)

### 1.1 Daughterboard (ord_db rev 0.9 -> cur_db rev 0.10)  [work/.../delta_db.txt]
| Item | Ordered 0.9 | Current 0.10 |
|---|---|---|
| Copper layers | 4: F.Cu / In1 GND / In2 +3V3 / B.Cu (pcb_stats: copper_layers 4; vias 1423 all 0.6/0.3 mm) | 6 |
| Parts | 310 | 338 |
| Added in current | microSD J4 (Molex 47219-2001) + C69-C73, R150/151/160-163 (SD pull-ups, 47k) | J4: MCU PB10/PB14/PB15/PD13 now SD_SCK/MISO/MOSI/CS (U1 pads 47,53,54,60 are unconnected in ordered) |
| Input series R | none: U11 pins 3-10 (4245 outputs) connect directly to Q1-Q8 inputs (nets /Outputs/*_IN contain U11.x and the driver pin) | R152-R159 220 ohm in each driver input (nets *_DRV) |
| Injector clamps | none on db | D42-D45 ES1D + D46-D49 1.5SMC16A per injector, returned to VBAT_IN |
| CEL | Q13 gate from U12.6 (level shifter output, enabled by DRV_EN_N: CEL_G net = Q13.1 RN3.1 U12.6) | R160 1k from CEL_CTL (U1.3) direct to gate; U12.18 tied GND |
| Battery sense | R11.1 on net +12V (after D7 SS34 and F1) | R11.1 on VBAT_IN |
| F1 / L1 | nSMD050-33V 1206 0.5 A hold (C70077) / CMI322513U2R2KT 1210 2.2 uH 500 mA, 300 mohm (C70960) | BSMD1812-110-33V 1.1 A (C883150) / Sunlord MWSA0503S (C177247) |
| Flex / nitrous | J2-24/25 = UART_TX/UART_RX; MCU PC6/PC7 via R139/R140 10k + BAT54S (D36/D37) | J2-24/25 = IN_FLEX / IN_N2O, with RC filters C72/C73, nets FLEX_M / N2O_ARM_M |
| Moved | C61, C62, U14 (second TLS115), F1, J3 (SWD), D1-D5/R2-R6 (wideband, 1.5 mm), D36/37 R139/140 | |
J1 (VBAT 1-2, VIGN 3, GND 4-5, FP 6, MAINRLY 7, AC 8, FAN 9, CEL 10, TACH 11, LS7 12, V5_EXT 13, IGN1-4 14-17, INJ1-4 19/22/25/28, IACV 31, VVT 34, BOOST 37, ALT 40, GND between) is identical in both. J2 differs only in pins 24/25. Full ordered J2: 1 V5_SENS, 3 KNOCK, 4 TPS, 5 MAP, 6 CLT, 7 IAT, 8 AFR, 9-11 AUX1-3, 13-17 HALL1/2 SW1-3, 19-22 VR2_N/P VR1_P/N, 24 UART_TX, 25 UART_RX, 27 CAN_L, 28 CAN_H, 30-32 USB, 33-38 LSU wires (UN, RT, VM, IP, HTR_N x2), 39/40 HTR_GND (VERIFIED, pcb_pads.csv).

### 1.2 Motherboards (ordered -> current)
Common to all five ordered boards (VERIFIED, pcb_footprints/pads):
- J2 wideband = Molex Micro-Fit 43045-0600 2x3 (1 LSU_IP, 2 LSU_VM, 3 LSU_HTR_N, 4 HTR_PWR, 5 LSU_RT, 6 LSU_UN: matches Bosch LSU 4.9 connector numbering, UNVERIFIED from memory) vs current JST S08B-PUDSS-1 2x8-pin for AEM 30-3427 (pin order differs). IAT: ordered J3 = Micro-Fit 43650-0200 1x2 (C587650) (1 IAT_EXT, 2 GND) + JP1 IAT SEL 1x3 (shunt HARN_IAT | IN_IAT | IAT_EXT); current removed J3/JP1 on 1996-2005 (IN_IAT straight from harness).
- J5 AUX = 2x8 (16 pin): 1 IGN3, 2 IGN4, 3 BOOST, 4 ALT, 5 MAINRLY, 6 KNOCK, 7-10 VR1/VR2 P/N, 11 AFR, 12 UART_TX, 13 UART_RX, 14 V5_EXT, 15 AUX_VBAT (via F4), 16 GND. Current: 2x10, adds GND 17/18 and CAN_H/CAN_L 19/20, pins 12/13 = IN_FLEX/IN_N2O with 4.7k/10k pull-up options (R35/R36), SS34 D5 on AUX_VBAT/OUT_BOOST (flyback for boost valve).
- Fuses: F1 LSU heater 3 A hold 1206 PTC (same), F4 AUX 0.5 A hold 1206 nSMD050-33V (current 1.1 A BSMD1812). Net jumpers vs fixed: ordered has no jumpers except JP1 and (8993) fitted 0R links; harness wires are fixed links to nets.
- R20-R22 4.7k pull-ups to VBAT_IN on SW1-3 are NOT fitted by default (no LCSC, hand options).
Per board:
| Board | Ordered specifics (netlist) | vs current |
|---|---|---|
| 8993 rev 0.11 (48-pin 174917-6) | D3/D4 SMCJ30A (C224048) clamps on OUT_INJ1/OUT_INJ2 to GND; 0R links R23 (INJ1-INJ4), R24 (INJ2-INJ3) FITTED (C17477), R25/R26 (INJ3->2Y, INJ4->2Z) not fitted; R29 (2L -> IN_AUX1) fitted; R27 4.7k, R28 (1N->V5_EXT), R30 (2L->IN_TPS) not fitted. Harness 2I = OUT_TACH direct; 2R = OUT_ALT; 2S/1R OUT_LS7 (J1.1R) | current 8995 is one merged 1989-95 board with JP1-JP6 jumpers (INJ3/INJ4/FAN2/TACH COP/94-95 2R/2O), HARN_xx nets, SS34 D5, R35-R37 (R37 1k 2512) |
| 9495 rev 0.9 (48-pin) | no D3/D4, no links: INJ3->2Y, INJ4->2Z direct (J1.2Y = OUT_INJ3), 2L = IN_AUX1, 2I = OUT_TACH, 2R = OUT_ALT, 2S = OUT_LS7; JP1 IAT SEL, J3 IAT | as above |
| 9697 rev 0.7 (76-pin 178780-1) | IAT via JP1/J3 (J1.3K = HARN_IAT) | current: no JP1/J3, J1.3K=IN_IAT, +D5 R35 R36, JST AEM connector |
| 9900 rev 0.7 | J1 = TE 176122-6 64-pin (ecu_mb:TE_176122-6_64P, 68 pads) | current 1999-2000 board uses TE 178780-1 76-pin "76P_NB1" footprint (80 pads) i.e. a different header |
| 0105 rev 0.7 | IAT J1.4N = HARN_IAT via JP1/J3 | as 9697 |
Not done: per-pin harness-cavity comparison of ordered vs current (the nets differ only as above in the diffs; cavities not listed in diffs are identical).

## 2. Problems documented for later revisions that apply to the ordered hardware
| # | Problem | Applies to ordered? | Rework | Verification |
|---|---|---|---|---|
| P1 | VND7NV04 input needs >=150 ohm series (ST abs-max RIN MIN); none fitted | YES, Q1-Q8 (U11.3-10 wired directly to Q inputs) | Per repo audit: lift Q pin 1 and bridge to its pad with 220 ohm 0603, or cut track U11->Q input and bridge with 220 ohm 0402. Q101 (VND14NV04 wideband heater) has 1k already, not affected. Rework is delicate (DPAK pin 1 lead, 8 parts); the consequence of omitting is unquantified by ST | VERIFIED netlist; consequence UNVERIFIED |
| P2 | Fuse 0.5 A hold F1 + L1 500 mA, 300 mohm | YES (F1 C70077, L1 C70960) | 1206 PTC ~1 A hold + matching 1210 inductor fit the pads (repo); otherwise hot-soak/cranking test (buck ~0.45 A at 8 V). Ordered F1 700 mohm max + L1 300 mohm = ~0.45 V drop at 0.45 A | VERIFIED parts; trip risk INFERRED |
| P3 | AUX fuse F4 0.5 A hold; boost valve takes most; no flyback diode D5 on ordered mb | YES, all five | Do not hang a boost solenoid on J5-3 without own diode and external fuse; replace F4 with 1 A 1206 only if wiring allows (F4 pad is 1206; J5 pin and 12 V trace width unchecked) | VERIFIED netlist (no D5) |
| P4 | Battery sense after D7 and F1 (reads 0.4-0.6 V low, load dependent) | YES: R11.1 on +12V | Move R11 pin 1 to VBAT_IN (e.g. D7 pad 2 or J1 pin 1). Optional; firmware could instead add an offset/trim. Do not forget the reverse-battery path: R11 33k limits current into the ADC clamp to ~0.4 mA at -14 V (INFERRED) | VERIFIED netlist |
| P5 | CEL behind shared driver enable (cannot light when drivers are off, e.g. fatal error) | YES: Q13.1 net = U12.6 | Cut track U12.6 -> Q13 gate and wire U1 pin 3 (CEL_CTL, PE4) to Q13 gate (repo says ZXMS6004FF switches from 3 V); U12.18 would then float: tie to GND. Cosmetic/safety nicety; skip unless you want a lamp on fatal error | VERIFIED netlist; rework INFERRED |
| P6 | Tach output vs igniter on 1989-95 (2I) | YES 8993 and 9495: OUT_TACH on J1.2I with no jumper | Set tach output = none in TunerStudio BEFORE first connection to a stock-igniter car (firmware default sets tachOutputPin, miata_board.cpp:86). Hard rework: remove link? there is none, only cutting the 2I track | VERIFIED |
| P7 | 1989-93 paired injector drivers with D3/D4 | YES: R23/R24 fitted by default (INJ1||INJ4 on 2U, INJ2||INJ3 on 2V) | Current policy is one driver per wire with no pairing: remove R23 and R24 (0805 0R) so INJ1 drives 2U and INJ2 drives 2V alone; firmware needs no change (INJ3/INJ4 switch into nothing). Keep D3/D4. Per repo's calc one clamp then takes both injectors: 2.0 W at 7200 rpm, 20 mH (repo model) and driver 0.55 W. Sequential conversion: remove R24/R23, fit R25/R26 (never R26 on automatics) | policy VERIFIED (VERIFICATION.md "one driver per injector wire"); benefit INFERRED |
| P8 | Injector turn-off energy on 1994-2005 ordered boards: no clamp on db, no D3/D4 on mb | YES | Driver clamps (VCLTH 36 V) take 15 mJ/shot at 20 mH (repo sim); measure injector inductance and driver case temperature on a bench with 12-14 ohm loads before the car; add external TVS from OUT_INJx to VBAT_IN only as a wired option | repo-documented, UNVERIFIED sim |
| P9 | Via-in-pad on a 4-layer order | 664/1423 vias are inside SMD pads of the same net (404 Q1-Q8, ~260 under C/R/U/D/RN parts) (VERIFIED, vip.py: via centre inside pad bbox) | README says "order epoxy-filled and capped" but no order record exists in the repo. JLC: epoxy-filled & capped is free only on 6+ layers; 4-layer costs extra (JLC news/quote page, web search 2026-11-16, https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv). If NOT filled: open 0.3 mm holes in pads wick solder (starved joints on DPAK tabs and 0402/0603). Inspect: reflow-check DPAK tab fillet, thermal image drivers under load; reflow/hand-add solder paste on suspicious pads. Open vias on the tabs may also be tented/covered on one side, unknown | counts VERIFIED; fill status UNKNOWN |
| P10 | PTC fuse voltage ratings, SD socket, AEM connector | n/a: ordered has no SD, Molex wideband connector | - | - |
| P11 | Wideband R120 sense far from J1 (153 mm 0.25 mm track) | YES | Move R120.1 to J1 (optional) | repo note |
| P12 | Buck input caps 4.6-7.5 mm from VIN, 100 nF missing | YES | Add 100 nF 50 V across U2 VIN/GND by hand if ripple/EMI is seen | repo note |
| P13 | CAN not on a connector, no microSD | by design | - | ABOUT.md |
| P14 | Flex/nitrous inputs: J5-12/13 = PC6/PC7 with 10k + BAT54S, no pull-up, no RC | YES | Flex sensor needs a 4.7k pull-up to J5-14 (V5_EXT) externally. In rusEFI flexSensorPin is EXTI based (init_flex.cpp:25): PC6 = EXTI line 6 (no other EXTI user seen); nitrous on PC7 shares line 7 with HALL1 PE7: use it as a polled switch only, not an interrupt input (INFERRED) | VERIFIED pins; EXTI conflict INFERRED |

## 3. Consistency
- JD1/JD2 vs J1/J2 for all five ordered motherboards: identical nets, offsets (14.5, 42.0) mm on both connectors (VERIFIED, mate.py). Pin 1 same orientation (all offsets equal).
- MCU pin map: miata_pins.h vs ord_db U1: IGN1 PE1, IGN2 PE0, IGN3 PB9, IGN4 PB8, INJ1-4 PB7-PB4, IACV PB3, VVT PD7, BOOST PD6, ALT PD5, FP PC14, MAINRLY PC13, AC PE6, FAN PE5, CEL PE4, TACH PE3, LS7 PE2, DRV_EN PA8, HALL1/2 PE7/PE8, SW1-3 PE9-PE11, VIGN PA2, KNOCK PA3, TPS PA4, MAP PA5, CLT PA6, IAT PA7, AFR PC4, AUX1 PC5, AUX2 PB0, AUX3 PB1, CAN PB12/13, LEDs PD12/PC8/PC9, WB flash PD8-PD11: all match (VERIFIED). PA1 VBATT not individually re-read (grep filter excluded it; INFERRED ok).
- Ignition pin order in firmware: [0]=IGN1,[1]=IGN3,[2]=IGN2,[3]=IGN4: with wasted spark rusEFI uses [0] and [2] (comment, miata_board.cpp:66). INFERRED fine; verify on a coil by scope (stage 5).
- Firmware header comment "rev 0.8" is stale (cosmetic).
- Frozen firmware does not configure PC6/PC7 flex/nitrous: user must set pins in TunerStudio.
- Ordered motherboards are NOT compatible with the current daughterboard (J2-24/25 meaning, no J4) and vice versa (ABOUT.md says so).

## 4. Staged bring-up (bench supply, current limited)
Equipment: bench supply 0-16 V with limit, DMM, scope, 12-14 ohm 10 W resistors x4 (injector dummies), USB-C cable, SWD/DFU. Never power from USB alone to judge the 12 V rails (back-feed gives ~4 V on +12V, repo-documented).
| Stage | Action | Expect | Stop if | Why |
|---|---|---|---|---|
| 0 | Visual/microscope: Q1-Q8 tabs, U1, U2, U102, polarity of D12/D7/D6; confirm J1/J2 headers soldered square; confirm via fill from JLC order | no bridges, fillets at tabs | solder voids at DPAK tabs, bridging | P9 |
| 0b | Apply reworks P1 (and decisions P7/P6/P4) now | - | - | cheaper than after power |
| 1 | Unpowered ohms on bare daughterboard: VBAT_IN-GND, +5V-GND, +3V3-GND | not < ~100 ohm (no hard number in design; compare with second board) | <10 ohm | shorts before power |
| 2 | Bare daughterboard (not mated): supply 6 V, limit 0.1 A on J1 pins 1+2 / GND 4,5; raise to 12 V | +12V = Vin minus ~0.3-0.5 V (SS34+F1); +5V = 5.0 V (68k/12k, LMR14020 ref 0.75 V, INFERRED 4.99 V); +3V3 3.3 V; V5_EXT/V5_SENS ~5 V; DRV_EN_N ~5 V (pull-up, drivers off) | current >0.3 A at 12 V (F1/L1 hold 0.5 A), any rail wrong by >5 % | rails and the drivers-off default |
| 3 | Reverse-polarity quick check optional skip; measure buck switching node, rail ripple with scope | 5 V ripple < 50 mV (INFERRED target) | hot buck inductor/IC within 30 s | LMR14020 layout is new |
| 4 | Flash via DFU (BOOT button) or SWD J3, connect USB, TunerStudio | rusEFI boots, LEDs run (PD12), no fatal error; DRV_EN_N goes to ~0 V after start, back to 5 V on reset | reboot loops, current >0.3 A | MCU supply, firmware identity (frozen ordered-boards firmware) |
| 5 | Mate with the matching motherboard (standoffs first), supply limit 0.4 A, 12 V at harness 1B (VBAT) | idle current dominated by logic; no heat; MAP reads ~0.85 V at the sensor for 101 kPa (INFERRED from firmware 0.2-4.7 V = 0-700 kPa), ADC pin 0.55 V; CLT/IAT open = 4.26 V at the node, 10k to GND = 3.46 V (INFERRED from 2.7k/15.6k); VBATT reading ~0.4-0.6 V low (P4) | current >0.4 A; MAP out of 0.7-1.0 V | sensor supply and dividers |
| 6 | Outputs: dummy resistors from +12V to OUT_INJ1-4, IACV, VVT; TunerStudio output tests; scope drain waveform and measure case temp. Ignition: scope OUT_IGN1/2 with no coil | injector drain pulls to <0.5 V when on, ~1 A per 12-14 ohm load; clamp visible with a real inductive load (a relay coil) at ~36-37 V (D3/D4 on 1989-93 SMCJ30A, VBR 33.3-36.8 V) | driver >100 C, output stuck on | verifies P1/P7/P8 and DRV_EN |
| 7 | Inputs: signal generator on HALL1/2 (5 V logic through 1k pull-up), VR inputs, SW1-3 12 V; knock test | RPM reads; 22k/10k dividers give ~3.7 V at the MCU pin at 12 V? INFERRED 12*10/32 = 3.75 V, check clamp to 3.3 V | MCU pin >3.6 V sustained | logic input protection |
| 8 | Wideband: no sensor, then a 3-4 ohm dummy heater at 3 A limit; then real LSU in free air | CAN heartbeat (J2-27/28 via USB/CAN), heater PWM only after warm-up logic, UN/VM/IP voltages plausible | heater current >3 A (F1 3 A hold), controller fault | wideband layout is new (README) |
| 9 | On the car: unplug igniter-tach conflict check (set tach none), measure 1O/3M, cranking test with supply as battery 9-10 V | cranks, no stall when key leaves START (1C only live in crank) | any brownout of +5V <4.7 V while cranking | P2, P6, firmware fixes |
Conditions to stop everywhere: smoke/smell, current limit hit at stage 2, any rail >5 % off, USB-only supply confusion, any driver >120 C on bench.

## Sources actually read
the review brief; repo/ordered-boards/2026-11/ (ABOUT.md, README.md, VERIFICATION.md lines 583-735, daughterboard/README.md, motherboards/1989-93/README.md, firmware/board/miata_pins.h, miata_board.cpp, board_configuration.cpp); repo/research/rev0.10_design_audit.md; repo/VERIFICATION.md "one driver per injector wire"; evidence/ord_* and cur_* pcb_pads.csv, pcb_footprints.csv, pcb_nets.txt, pcb_stats.json; repo/research/st pin XML; kb/parts_manifest.md (L1, F1); rusEFI init_flex.cpp; web search JLC via-in-pad.

## Not checked
- Actual JLC order options (via fill, finish, thickness): unknown, not in repo.
- Physical rework feasibility (DPAK pin 1 geometry), PTC/inductor replacement part numbers.
- Idle current of the real board (no value in repo; limit chosen from F1/L1 ratings).
- Cavity-by-cavity ordered vs current harness diff beyond the pad/net diff.
- PA1 VBATT pin row; Bosch LSU connector numbering from memory.
- LSU heater dummy load value.
