# P11 - Level shifters U11/U12 (SN74LVC4245A), U13 (74HCT04), U6/U7 (TC4427) and ignition output stage

Date 2026-11-16. Status: complete (see Not checked).

## Summary
1. All five ICs are wired correctly on cur_db (pcb_pads.csv + schematic/design.py + datasheet pin tables agree). The ordered rev 0.9 db is pad-for-pad identical for U6/U7/U13/R15-18/R144-147/D31-34/RN1 (diff of pcb_pads.csv = empty), so every ignition conclusion holds for both.
2. 4245A: A port = 5 V (VCCA pin1 = +5V), B port = 3.3 V MCU side (VCCB pins 23,24 = +3V3), DIR (pin2) = GND = B->A, OE (pin22) = DRV_EN_N = PA8 (U1.67) pulled to +5V by R71. Channel pairing A8/B8 .. A1/B1 correct (A1=3..A8=10, B8=14..B1=21). Unused channels: U11 none; U12 A1(3) open + B1(21) GND, A5(6) open (CEL, rev 0.10) + B5(18) GND. Correct per datasheet note (unused inputs to VCC or GND).
3. Power-up: matches TI "Power-Up Considerations" (OE tied to VCCA through pull-up, VCCA first, DIR low). Outputs stay off through reset/DFU. Firmware opens PA8 open-drain (board_configuration.cpp:41,110) so no 3.3 V-drives-5 V-pull-up issue.
4. Ignition: all reset/boot states give a LOW line (RN1 10k pull-down on CTL -> TC4427 low, HCT04 high -> ZXMS on; plus R144-147 3.3k). No sequencing hazard found. Shoot-through TC4427 vs ZXMS is only about 43 mA for ~50 us at each rising edge (ZXMS tD(OFF) 45 us + tF 15 us typ).
5. Stage is much more complex than rusEFI Hellen ign8 (74LVC4245A + 10 ohm only, no protection). Cost of the stage about $2.9 per board at qty 100; a cheaper protected variant is proposed below but depends on unknown igniter input data (UNVERIFIED), so it is a proposal, not a claim.
6. No hard error found in scope. Small risks: R15-18 dissipation in a short to ground at 85 C; igniter drive level unknown.

## Datasheet digests (VERIFIED, datasheets/txt)
SN74LVC4245A (TI SCAS375H): pins 1 VCCA(5V), 2 DIR, 3-10 A1-A8, 11/12/13 GND, 14-21 B8..B1, 22 OE (active low), 23/24 VCCB. Abs max VCCA 6.5, VCCB 4.6 V, pins VCC+0.5. Rec: VCCA 4.5-5.5, VCCB 2.7-3.6; control VIH 2 V / VIL 0.8 V referenced to VCCA; IOH/IOL 24 mA; VOH 3.7 V @24 mA (VCCA 4.5). Function: OE L, DIR L = B->A. Power-up note p.5: ground first, VCCA first, OE to VCCA pull-up.
74HC04/74HCT04 (Nexperia rev10 combined sheet; table 6 first block is 74HC04, HCT block is separate): HCT VIH 2.0 V, VIL 0.8 V at VCC 4.5-5.5 -> 3.3 V logic OK. Pin order 1A,1Y,2A,2Y,3A,3Y,GND,4Y,4A,5Y,5A,6Y,6A,VCC matches U13 pads (5Y/6Y open, 5A/6A GND).
TC4427A (Microchip): pins 1 NC, 2 INA, 3 GND, 4 INB, 5 OUTB, 6 VDD, 7 OUTA, 8 NC; VDD 4.5-18 V (abs 22); VIH 2.4 V min, VIL 0.8 V max, hysteresis ~0.3 V; Ro 7-9 ohm; 1.5 A; Iq 0.1 mA (inputs low) / 1 mA. SOIC-8 theta-JA 155 C/W. Matches U6/U7 pads. Note the sheet is the "A" version of TC4426/7/8.
ZXMS6004FF (for the pull-down, see P10): VIN(th) 0.7/1/1.5 V; tD(ON) 5 us, tR 10, tD(OFF) 45, tF 15 us (VDD 12 V, ID 0.5 A); RDS(on) 350 mohm max 500 @5 V; ID(lim) 1.0-2.2 A @5 V; clamp 60-70 V; IIN 120 uA @5 V.

## Pin-by-pin (cur_db pcb_pads.csv; ord_db same)
U11: 1 +5V, 2 GND, 3-10 ALT,BOOST,VVT,IACV,INJ4,INJ3,INJ2,INJ1 _DRV (A1..A8), 11-13 GND, 14-21 INJ1..ALT _CTL (B8..B1), 22 DRV_EN_N, 23/24 +3V3. All OK.
U12: 1 +5V, 2 GND, 4 LS7_G, 5 TACH_G, 7 FAN_G, 8 AC_G, 9 MAINRLY_G, 10 FP_G; B: 14 FP_CTL, 15 MAINRLY, 16 AC, 17 FAN, 19 TACH, 20 LS7; 3,6 open; 18,21 GND; 22 DRV_EN_N. OK (A-B pairing 10/14, 9/15, 8/16, 7/17, 5/19, 4/20 correct). Ord_db: pin 6 = CEL_G, pin 18 = CEL_CTL (CEL behind enable, documented).
U13: 1 IGN1_CTL, 2 IGN1_SNK, 3 IGN2_CTL, 4 IGN2_SNK, 5 IGN3_CTL, 6 IGN3_SNK, 7 GND, 8 IGN4_SNK, 9 IGN4_CTL, 10/12 open, 11/13 GND, 14 +5V. OK.
U6: 2 IGN1_CTL, 7 IGN1_DRV, 4 IGN2_CTL, 5 IGN2_DRV, 3 GND, 6 +5V, 1/8 NC. U7 same for IGN3/4. OK.
Footprints: KiCad standard TSSOP-24 4.4x7.8 P0.65, TSSOP-14 4.4x5 P0.65, SOIC-8 3.9x4.9 P1.27 (pads 1.475x0.4 / 1.95x0.6); not re-checked against drawings beyond name/pitch.

## Power-up / fault analysis
- 5 V rises first (3V3 derived from it, P05/P08). OE rises with VCCA via R71 -> A outputs Hi-Z; R19-26 (10k) + RN2/RN3 hold ZXMS/VND gates low. MCU pins floating in reset do nothing. PA8 is an FT pin; reset state floating -> OE high.
- Ignition: CTL pins PE1/PE0/PB9/PB8 float in reset; RN1 pulls low (TC4427 VIL max 0.8 V, typical threshold much higher). If rusEFI releases an unused ignition pin to input+pull-up (the firmware comment says rusEFI does this): 3.3 V * 10k / (10k + 30..50k) = 0.55-0.83 V, still below typical thresholds (INFERRED); IGN3/4 are unused on stock harnesses and not parked by firmware (only the 15 low-side pins are). Low risk.
- Short to battery on OUT_IGN: D31-34 (40 V, reverse 14.4/24 V) block, TC4427 sees nothing; Q (ZXMS) is on in the idle state and current-limits 1-2.2 A with thermal cycling (datasheet protected). R144-147 3.3k: 63 mW at 14.4 V, 175 mW at 24 V (<250 mW).
- Short to ground with driver high: I = (5 - 0.35 - ...)/107 ohm = about 43 mA, R15-18 dissipate about 0.185 W; 1206 250 mW rating applies to 70 C, derates to about 0.2 W at 85 C ambient (INFERRED, derating curve not read) -> 90 %: marginal, fault-only.
- Edge timing: rising dwell edge delayed about 50 us by ZXMS tD(OFF)+tR (constant, firmware compensates; irrelevant); falling edge (spark) line decays through R144 and igniter input RC; Q takes over after 5-15 us.

## Igniter levels (UNVERIFIED)
High level = 5 V - Vf(B5819W about 0.3-0.4 V at tens of mA) - I*100 ohm, loaded further by R144 3.3k (1.4 mA). Stock NA igniter / NB coil input current and threshold could not be found (searches gave no numbers; Haltech says NB coils with internal igniter wire directly to an ECU output). If the igniter input is an LED/optocoupler-like or a pull-up type, 100 ohm + diode (about 0.5-1 V drop) may leave margin short. Needs a scope/meter on a stock coil pack, or the Mazda FSM. rusEFI Hellen drives these inputs push-pull with 4245A + 10 ohm (ext/hellen-one/modules/ign8/0.2/ign8-BOM.csv).

## Cost / simplification
Ignition stage today (qty 100 JLC): U6+U7 2 x 0.476 = 0.95; U13 0.15 (qty 150); Q16-19 4 x 0.385 = 1.54; D31-34 4 x 0.014; R15-18 + R144-147 about 0.04; RN1, C34, C35, C66 about 0.02 -> about $2.75 + 3 extended-part loading fees per order (U6/7, U13 and ZXMS are all "extended"; fee amount UNVERIFIED).
Option A (drop Q16-19 + U13, keep TC4427 + 100 + D + 3k3): saves about $1.7. Low state then = 3.3k only (high impedance, less noise immunity against ground offset between ECU and coil pack); short-to-battery still survives (diode). Not recommended without knowing igniter input.
Option B (open-drain with pull-up): ZXMS gate driven directly from the MCU pin with 10k pull-UP to +5V (reset = Q on = line low, safe), line pulled up through 1k + Schottky from +5V, firmware inverts ignition polarity (rusEFI ignition pin mode is invertible). Removes U6, U7, U13, R15-18 (1206), R144-147 (1206), C34, C35, C66, changes RN1 to pull-ups: saves about $1.1-1.3 + two extended parts; keeps short-to-battery survival (Schottky blocks, ZXMS clamps) and gives a hard low edge at the spark. Costs: slower, weaker-high edge (1k pull-up) and the high level depends on igniter input resistance -> only after measuring a stock igniter. UNVERIFIED proposal; the MCU FT pin with a 5 V pull-up and VDD=0 also needs the STM32 datasheet check.
4245A alternatives: 74HCT245 TSSOP-20 (e.g. C52140501 $0.10 @1k, C53436288 $0.085) would remove the 3.3 V rail dependency (HCT VIH 2 V) and save about $0.13-0.2 each, but needs new pinout/layout and its datasheets were not read -> not recommended now. Current C7859 is JLC "extended (preferred)", stock 36862, $0.3928 @30 / $0.3437 @100.

## Sources actually read
design.py lines 255-350, 455-475, 535-550; evidence/cur_db and ord_db pcb_pads.csv, pcb_nets.txt, pcb_footprints.csv; kb/interconnect.md IGN rows; datasheets C7859, C131317, C20551, C95063 (txt); firmware/board/board_configuration.cpp:30-135, miata_pins.h; ext/hellen-one/modules/ign8/0.2 BOM + schematic text; tools/lcsc.py lookups (C7859, C131317, C20551, C95063, 74HCT245/74LVC4245/74HCT541/74AHCT245 searches); one web search (no numbers).

## Not checked
Stock NA/NB igniter input current and threshold (no source found). 4245A/74HCT04/TC4427 package drawings vs KiCad lands (names and pitch only). ZXMS/UNI-ROYAL resistor derating curves. Layer images/loop area. Hellen NB/NA6 ignition schematics (only ign8). STM32 FT pin behaviour at VDD=0 with a 5 V pull-up. Whether JLC charges a per-part extended fee for these today.
