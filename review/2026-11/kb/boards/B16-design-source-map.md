# B16 - design source map (generator scripts -> circuit description) and source-level errors

STATUS: complete (2026-11-16). Scratch: `work/B16-design-source-map/` (`dump_design.py`, `mcu_pins.py`, `cmp_db.py`, `cmp_mb.py`, `map_mb.py`, `blocks.py`; outputs in `out/`: `db_nets.txt`, `db_parts.txt`, `blocks.md`, `cavity.md`, `mb_map.txt`). Scripts in `work/.../scripts/` are a verbatim copy of `repo/scripts/` (used only so Python can import them).
Tags: VERIFIED = read or computed from design files / datasheet text today; INFERRED = reasoning shown; UNVERIFIED = memory.

## Summary
1. Source == PCB == fab BOM for the CURRENT designs (VERIFIED): `design.py` rev 0.10 gives 338 parts / 230 nets; every net and every pad of `evidence/cur_db/pcb_nets.txt` is identical to the source netlist (cmp_db.py: 0 differences), footprints, values and LCSC fields of all 338 footprints match, and the JLC BOM refs + self-order refs + 6 no-BOM refs (H1-4, J3, J102) = 338. The four current motherboard modules (mb_na6, mb_na96, mb_nb1, mb_nb2) also reproduce `cur_mb*` `pcb_nets.txt` exactly (cmp_mb.py: 0 differences). So the generator is a faithful description of the boards; errors are in the source itself, not in source-vs-board drift.
2. **Real error found: R110 (wideband pump-current shunt, 62 ohm 1206) is built with LCSC C25341 = UNI-ROYAL 1206W4F620LT5E = 0.62 ohm, not 62 ohm.** On the ordered rev 0.9 daughterboard as well as rev 0.10 (both fab BOMs: `62,R110,R_1206_3216Metric,C25341`). Correct part: C17971 (1206W4F620JT5E, 62 ohm, extended, 123k in stock). Cheap hand rework before first power-up. It is the only value/LCSC disagreement among all 6 db + 10 mb BOMs (script check against kb/parts_manifest.json).
3. `scripts/mpn.json`, which `bom.py` calls the record that "every LCSC number was looked up ... nothing left to flag", has no entry for 14 LCSC codes the boards use (incl. C25341, C155605, C95063, C485806, C70065); that is how item 2 slipped through.
4. Dead / stale code: `mb_na8.py` calls `base.build_parts(HARNESS, paired_injectors=False, ...)` but `mb_na6.build_parts` has no such argument (TypeError if run) and its harness is obsolete (HARN_IAT/JP1, 1N/2P/2R wiring differ); it is only copied by mb_make.sh. `mb_common.trigger_select()` is never called. `bom.py` GROUPS/DESC/BASIC are from rev 0.4 (U5, NCV8406, ULN2003, AMS1117, SN65HVD230; 20 codes missing from BASIC or wrong) and feed `parts_xlsx.py`.
5. Spare resources: 21 MCU pins unused (list below); NO spare J1/J2 pin (all 80 allocated; J1 has 17 GND pins, J2 has 6 GND + 2 HTR_GND). The AUX header J5 is the only expansion path and uses 17 of 20 pins for signals.
6. Parts for features no supported car needs: VR comparator block (27 parts, $0.27), IGN3/IGN4 channels (10 parts, $2.03 + half of U13/RN1), BOOST driver (Q7 $2.69), U3 second 5 V tracker ($1.26), AN_AFR chain (4 parts). Details in section 7.
7. Checked and correct (not findings): TL431 pin order (DBZ: 1 cathode, 2 REF, 3 anode, datasheet C23892 p.1 pinout), BAT54S/BAT54A/ES1D/TVS orientation, SN74LVC4245A direction/enable/unused channels, 74HCT04 unused gates, TC4427 NC pins, LM2903/LMV321/TCAN1042V/F103 pin maps, CAN termination, jumper position labels vs SHUNTS, VIGN-only-single-pad nets (see 6.4).

## 1. Method and parity checks (all VERIFIED)
- `work/.../dump_design.py` imports `repo/scripts/design.py` (wideband.py is imported by it) and writes parts/nets. `cmp_db.py` compares to `evidence/cur_db/pcb_nets.txt` (net name = text after the last "/"): 230 vs 230 nets, 0 pad differences.
- `cmp_mb.py` imports each year module, calls `build_parts()` and compares to `evidence/cur_mb8995|9697|9900|0105/pcb_nets.txt`: 68/59/60/61 nets, 0 differences. Single-pad nets: none in the db; mb 96-97 and 99-00: `VIGN_IN` (only JD1.3) - see 6.4.
- Footprint/value/LCSC parity of db: `pcb_footprints.csv` vs `design.parts` 338/338 identical; JLC BOM LCSC per ref identical.
- Ordered boards (rev 0.9 / 0.7-0.11) come from earlier source states and are NOT reproduced by today's scripts; B03 has their delta. The R110 error is present in their fab BOMs (VERIFIED, `evidence/ord_db/fab_*jlcpcb_bom.csv`).

## 2. Daughterboard: block by block (parts, nets, how it works)
Full ref/value/MPN/LCSC table per block is in section 8 (auto-generated from the source + kb/parts_manifest.json). Block descriptions:

**Headers J1/J2** (1x40, C2977586, hand-fitted bottom side). J1 = power + outputs, J2 = inputs + comms + LSU. Pin allocation in section 4.

**MCU core.** U1 STM32F407VGT6 (LQFP-100, C12345 - the code really is the F407, mpn.json note, manifest). VDD x7 on +3V3 with C1-C6 100n (C4 is 0402) + C7/C8 4.7u; VDDA/VREF+ via FB1 BLM18PG221 (+3V3A) with C11 1u/C12 100n; VCAP1/2 2.2u (C9/C10); 8 MHz Y1 with 33p C13/C14; NRST C15 100n + SW2; BOOT0 R1 10k to GND with SW1 to +3V3 (DFU), BOOT1 (PB2) R72 10k GND; SWD only as Tag-Connect pads J3 (no part). 

**Power.** VBAT_IN -> D6 SMCJ30A TVS to GND; D7 SS34 (VBAT_IN -> +12V_IN); D8 B5819W from VIGN_IN (ignition wake) -> +12V_IN; F1 BSMD1812-110-33V 1.1 A PTC -> +12V; D12 SMAJ33A TVS; R7 1 ohm + C16 10u/50V damping; L1 2.2 uH (FXL0530-2R2-M, footprint MWSA0503S; LCSC C177247) -> +12V_F with C17/C18 10u/50V + C71 100n; U2 LMR14020 (C187824) buck 12 V -> 5 V (R8 10k RT, C19 boot, C20 soft-start 10n, D9 B360A catch, L2 10 uH MWSA0603S, FB divider R9 68k / R10 12k + C21 220p, C22/C23/C59 10u); D10 B5819W +5V <- USB_VBUS (bench power, one-way). U4 LDL1117S33R 3.3 V LDO (C26/C27 10u). U3 TLS115B0EJ ("tracker", short-to-battery protected) makes V5_SENS from +5V (feeds only the MAP sensor on the motherboard via J2-1), U14 (same part) makes V5_EXT (J1-13: harness sensor 5 V, hall pull-ups, CLT/IAT bias, AUX header). C24/C62 1u on its +12V input, C25/C61 1u on its output. +3V3 shunt clamp: U15 TL431 + Q20 BCP53 PNP + R141 1k/R142 5.1k/R143 12k (trip 3.56 V) + C63/C68 100u 1206 (6.3 V X5R, see 6.6).
Battery/ignition sense: R11 33k (VBAT_IN, since rev 0.10; ordered boards: +12V after D7/F1), R12 6.8k, C28; R13/R14/C29 from VIGN_IN; BAT54WS clamps D38/D39 to +3V3.

**Status LEDs.** D1 green RUN (PD12), D2 blue COMM (PC8), D3 yellow WARN (PC9), D4 red ERR (PD15), each 1k; D5 green power LED from +3V3 via R6 1k.

**Relay/lamp low sides (7).** Q9-Q15 ZXMS6004FFTA (IN pad1, S pad2 = GND, D pad3 = OUT_*): FP, MAINRLY, AC, FAN, CEL, TACH, LS7. Gates driven at 5 V by U12 SN74LVC4245A (A side 5 V = VCCA pin 1, B side 3.3 V = pins 23/24, DIR pin 2 = GND => B->A, OE pin 22 = DRV_EN_N). RN2/RN3 4x10k pull-downs on the gates. CEL (Q13) is NOT through U12 since rev 0.10: R160 1k from CEL_CTL (PE4) straight to the gate (U12 pin 6 open output, pin 18 tied GND). The U12 channel 1 (pins 3/21) is unused (A open, B tied GND). No flyback diodes on the daughterboard (relay coils are on the car's relays; the ZXMS6004FF clamps).

**Ignition (4).** U6/U7 TC4427 (5 V, 1.5 A) -> R15-R18 100 ohm 1206 -> D31-D34 B5819W (anode on the 100 ohm, cathode on OUT_IGNn: blocks a short to battery); Q16-Q19 ZXMS6004FF pull the output down, gates from U13 74HCT04 (inverted control line; inputs 9/11/13 = unused gates tied GND); RN1 4x10k pull-downs on the control lines (so the sink is ON and the output low in reset); R144-R147 3.3k 1206 output pull-downs. Net result: IGNn_CTL high = output pulled high through 100 ohm + diode.

**Smart low sides (8).** Q1-Q8 VND7NV04TR-E (DPAK, 1 IN, 2/tab drain, 3 source=GND): INJ1-4, IACV, VVT, BOOST, ALT. U11 SN74LVC4245A shifts 3.3 -> 5 V (all 8 channels used, DIR GND, OE = DRV_EN_N shared with U12, R71 10k pull-up to +5V); R19-R26 10k pull-downs on the driver inputs; R152-R159 220 ohm in series with each input (rev 0.10; absent on the ordered rev 0.9). D42-D45 ES1D + D46-D49 1.5SMC16A: per-injector clamp (drain -> ES1D -> TVS -> VBAT_IN) on INJ1-4 only; IACV/VVT/BOOST/ALT are clamped by the VND7NV04 itself and the motherboard freewheel diodes.

**Analog inputs (8) + knock.** TPS, MAP, CLT, IAT, AFR, AUX1-3: 5.6k series, 10k to GND, 10n, BAT54WS clamp to +3V3 (D19-D26); CLT/IAT also 2.7k pull-up to V5_EXT (R33, R36). Knock: R138 2.2k, C44 100n coupling, U8 LMV321 (gain 1 + 47k/10k = 5.7, bias 1.65 V from R45-R47/C45), R50 330 + C47 10n to PA3.

**VR inputs (spare).** U9 LM2903 (A = VR2, B = VR1), 2 x 5.1k per leg, 1n across, BAT54S clamps D15-D18, 100k to VR_BIAS (R79/R80 divider 1.65 V), 1M hysteresis, 10k pull-ups to +3V3 into PE12/PE13. No Miata year uses it; reaches only J5-7..10.

**Hall / switch / flex / nitrous inputs.** HALL1/2: 4.7k series, 1k pull-up from V5_EXT through D35 BAT54A (common anode), 1n, D13/D14 1N4148WS clamp to +3V3 (PE7/PE8). SW1-3: 22k/10k divider, 10n, D27-D29 clamp (PE9-PE11). FLEX/N2O: R139/R140 10k + BAT54S clamp D36/D37 + C72 1n/C73 10n into PC6/PC7; pull-up/pull-down lives on the motherboard (R35/R36).

**CAN.** U10 TCAN1042V-Q1 (CAN2 PB12/PB13, VCC 5 V pin 3, VIO 3.3 V pin 5, STB pin 8 GND); C56 100n; U106 (same part) is the F103's transceiver on the same CAN_H/CAN_L. Termination on the motherboard (R1 120 + R6 0R link).

**microSD (rev 0.10).** J4 Molex 47219-2001 (C164170) on SPI2: PB10 SCK, PB14 MISO, PB15 MOSI, PD13 CS; 47k pull-ups on CS/MISO/MOSI/DAT1/DAT2; C69 100n, C70 10u.

**Wideband (module refs + 100).** Copy of the FOME/mck1117 module with an F103: U102 STM32F103C8T6, U101 MCP6004 (virtual ground/pump driver/Nernst), U103 REF3033, U105 AD8628 (shunt amp, gain R117/R111 = 100k/10k = 10), Q101 VND14NV04 heater low side (R125 1k gate), U106 CAN transceiver, Y101 8 MHz, D101-D103 LEDs, J102 SWD pads. LSU nets: LSU_UN (J2-33, via R137 22k into the Nernst buffer), LSU_RT (J2-34), LSU_VM (J2-35 -> F2 nSMD010 PTC -> WB_VMS -> R109 10 ohm), LSU_IP (J2-36), LSU_HTR_N (J2-37/38 = Q101 drain), HTR_GND (J2-39/40, tied to GND on the motherboard). R110 = pump-current shunt between LSU_RT and LSU_IP (see finding 1). D40/D41 B5819W and D30 BAT54WS clamp the pump / VM / VDDA nodes to +3V3. Programming link from the F407: USART3 PD8/PD9 -> F103 PA10/PA9, PD10 -> BOOT0, PD11 -> NRST. F103 spare pins: PC13-15, PA1, PA4, PA5, PA7, PB1, PB11-15, PA8, PA15, PB3, PB4 (net NC).

## 3. MCU pin allocation (U1, LQFP-100) - VERIFIED from design.py:126-168 and the pin-name table `scripts/stm32f407v_lqfp100_pins.txt`
| pin | name | net | function |
|---|---|---|---|
| 1 | PE2 | LS7_CTL | U12 -> Q15 OUT_LS7 |
| 2 | PE3 | TACH_CTL | U12 -> Q14 OUT_TACH |
| 3 | PE4 | CEL_CTL | R160 -> Q13 gate (OUT_CEL), no shifter |
| 4 | PE5 | FAN_CTL | U12 -> Q12 OUT_FAN |
| 5 | PE6 | AC_CTL | U12 -> Q11 OUT_AC |
| 6 | VBAT | +3V3 | power |
| 7 | PC13 | MAINRLY_CTL | U12 -> Q10 OUT_MAINRLY |
| 8 | PC14 | FP_CTL | U12 -> Q9 OUT_FP |
| 9 | PC15 | **unused** | |
| 10 | VSS | GND | power |
| 11 | VDD | +3V3 | power |
| 12 | PH0 | HSE_IN | Y1 8 MHz |
| 13 | PH1 | HSE_OUT | Y1 8 MHz |
| 14 | NRST | NRST | SW2, J3, C15 |
| 15 | PC0 | **unused** | |
| 16 | PC1 | **unused** | |
| 17 | PC2 | **unused** | |
| 18 | PC3 | **unused** | |
| 19 | VDD | +3V3 | power |
| 20 | VSSA | GND | power |
| 21 | VREF+ | +3V3A | power |
| 22 | VDDA | +3V3A | power |
| 23 | PA0 | **unused** | |
| 24 | PA1 | AN_VBATT | ADC, VBAT_IN divider |
| 25 | PA2 | AN_VIGN | ADC, VIGN_IN divider |
| 26 | PA3 | AN_KNOCK | ADC, knock amp U8 |
| 27 | VSS | GND | power |
| 28 | VDD | +3V3 | power |
| 29 | PA4 | AN_TPS | ADC (J2-4) |
| 30 | PA5 | AN_MAP | ADC (J2-5) |
| 31 | PA6 | AN_CLT | ADC (J2-6) |
| 32 | PA7 | AN_IAT | ADC (J2-7) |
| 33 | PC4 | AN_AFR | ADC (J2-8) |
| 34 | PC5 | AN_AUX1 | ADC (J2-9) |
| 35 | PB0 | AN_AUX2 | ADC (J2-10) |
| 36 | PB1 | AN_AUX3 | ADC (J2-11) |
| 37 | PB2 | BOOT1 | R72 to GND |
| 38 | PE7 | HALL1 | digital in crank (J2-13) |
| 39 | PE8 | HALL2 | digital in cam (J2-14) |
| 40 | PE9 | SW1 | 12 V switch (J2-15) |
| 41 | PE10 | SW2 | 12 V switch (J2-16) |
| 42 | PE11 | SW3 | 12 V switch (J2-17) |
| 43 | PE12 | VR2_OUT | LM2903 A out |
| 44 | PE13 | VR1_OUT | LM2903 B out |
| 45 | PE14 | **unused** | |
| 46 | PE15 | **unused** | |
| 47 | PB10 | SD_SCK | SPI2 SCK |
| 48 | PB11 | **unused** | |
| 49 | VCAP_1 | VCAP1 | power |
| 50 | VDD | +3V3 | power |
| 51 | PB12 | CAN_RX | CAN2 RX (U10) |
| 52 | PB13 | CAN_TX | CAN2 TX (U10) |
| 53 | PB14 | SD_MISO | SPI2 MISO |
| 54 | PB15 | SD_MOSI | SPI2 MOSI |
| 55 | PD8 | WB_PROG_TX | USART3 TX -> F103 PA10 |
| 56 | PD9 | WB_PROG_RX | USART3 RX <- F103 PA9 |
| 57 | PD10 | WB_BOOT0 | F103 BOOT0 |
| 58 | PD11 | WB_NRST | F103 NRST |
| 59 | PD12 | LED_RUN | D1 green |
| 60 | PD13 | SD_CS | GPIO CS |
| 61 | PD14 | **unused** | |
| 62 | PD15 | LED_ERR | D4 red |
| 63 | PC6 | FLEX_M | R139 10k + D36 + C72 (J2-24) |
| 64 | PC7 | N2O_ARM_M | R140 10k + D37 + C73 (J2-25) |
| 65 | PC8 | LED_COMM | D2 blue |
| 66 | PC9 | LED_WARN | D3 yellow |
| 67 | PA8 | DRV_EN_N | active-low enable of U11/U12 (R71 pull-up +5V) |
| 68 | PA9 | **unused** | |
| 69 | PA10 | **unused** | |
| 70 | PA11 | USB_DM | OTG_FS DM (J2-30) |
| 71 | PA12 | USB_DP | OTG_FS DP (J2-31) |
| 72 | PA13 | SWDIO | J3 |
| 73 | VCAP_2 | VCAP2 | power |
| 74 | VSS | GND | power |
| 75 | VDD | +3V3 | power |
| 76 | PA14 | SWCLK | J3 |
| 77 | PA15 | **unused** | |
| 78 | PC10 | **unused** | |
| 79 | PC11 | **unused** | |
| 80 | PC12 | **unused** | |
| 81 | PD0 | **unused** | |
| 82 | PD1 | **unused** | |
| 83 | PD2 | **unused** | |
| 84 | PD3 | **unused** | |
| 85 | PD4 | **unused** | |
| 86 | PD5 | ALT_CTL | U11 -> Q8 OUT_ALT |
| 87 | PD6 | BOOST_CTL | U11 -> Q7 OUT_BOOST |
| 88 | PD7 | VVT_CTL | U11 -> Q6 OUT_VVT |
| 89 | PB3 | IACV_CTL | U11 -> Q5 OUT_IACV |
| 90 | PB4 | INJ4_CTL | U11 -> Q4 |
| 91 | PB5 | INJ3_CTL | U11 -> Q3 |
| 92 | PB6 | INJ2_CTL | U11 -> Q2 |
| 93 | PB7 | INJ1_CTL | U11 -> Q1 |
| 94 | BOOT0 | BOOT0 | R1 10k to GND, SW1 to +3V3 |
| 95 | PB8 | IGN4_CTL | U7 + U13 -> Q19 |
| 96 | PB9 | IGN3_CTL | U7 + U13 -> Q18 |
| 97 | PE0 | IGN2_CTL | U6 + U13 -> Q17 |
| 98 | PE1 | IGN1_CTL | U6 + U13 -> Q16 |
| 99 | VSS | GND | power |
| 100 | VDD | +3V3 | power |

Unused (21): PC15(9), PC0-PC3(15-18), PA0(23), PE14/PE15(45/46), PB11(48), PD14(61), PA9/PA10(68/69), PA15(77), PC10-PC12(78-80), PD0-PD4(81-85). (Alternate functions below are from memory of the F407 datasheet: UNVERIFIED.) PC0-PC3 and PA0 are ADC inputs (5 possible extra analog channels; PA0 also WKUP); PD0/PD1 = CAN1 (a second bus would need only a transceiver); PA9 = OTG_FS VBUS sense, so the firmware must run USB without VBUS sensing (INFERRED, PA9 is open); PC10-PC12 + PD2 are the SDIO pins but PC8/PC9 are taken (LEDs), so the microSD uses SPI2. No header pin exists to bring any of these off the board: all 80 J1/J2 pins are allocated (section 4); only the AUX header J5 (motherboard) could carry them, and it is full.

PC13/PC14 (MAINRLY_CTL, FP_CTL) are on the backup-domain switch (3 mA total; comment design.py:133). PB3/PB4 are JTAG pins at reset (outputs INJ4/IACV drivers are held off by DRV_EN_N then; INFERRED).

## 4. J1 / J2 allocation (daughterboard, mates 1:1 with JD1/JD2 on every motherboard; VERIFIED design.py:91-116, parity with kb/interconnect.md)
J1 (top edge, power + outputs): 1,2 VBAT_IN; 3 VIGN_IN; 4,5 GND; 6 OUT_FP; 7 OUT_MAINRLY; 8 OUT_AC; 9 OUT_FAN; 10 OUT_CEL; 11 OUT_TACH; 12 OUT_LS7; 13 V5_EXT; 14-17 OUT_IGN1-4; 18 GND; 19 OUT_INJ1; 22 OUT_INJ2; 25 OUT_INJ3; 28 OUT_INJ4; 31 OUT_IACV; 34 OUT_VVT; 37 OUT_BOOST; 40 OUT_ALT; GND on 20,21,23,24,26,27,29,30,32,33,35,36,38,39 (17 GND pins in total: 4,5,18 + those 14). Every VND7NV04 output sits on every third pin flanked by two GND pins (current return/spacing).
J2 (bottom edge, inputs + comms + LSU): 1 V5_SENS; 2 GND; 3 IN_KNOCK; 4 IN_TPS; 5 IN_MAP; 6 IN_CLT; 7 IN_IAT; 8 IN_AFR; 9-11 IN_AUX1-3; 12 GND; 13,14 IN_HALL1/2; 15-17 IN_SW1-3; 18 GND; 19 VR2_N; 20 VR2_P; 21 VR1_P; 22 VR1_N; 23 GND; 24 IN_FLEX; 25 IN_N2O; 26 GND; 27 CAN_L; 28 CAN_H; 29 GND; 30 USB_DM; 31 USB_DP; 32 USB_VBUS; 33 LSU_UN; 34 LSU_RT; 35 LSU_VM; 36 LSU_IP; 37,38 LSU_HTR_N; 39,40 HTR_GND (the motherboard's JD2 ties these to GND).
Spare pins: none unassigned. Candidates that could be given another job without a new pin: J1 GND pins 4/5/18 and the 14 GND pins between injector outputs (but they carry return current / isolation), J2 GND 2/12/18/23/26/29 (sensor ground; used as shield between the analog groups), the duplicated J2 pins LSU_HTR_N 37/38 and HTR_GND 39/40 (2 + 2 pins for about 3 A of heater current: both pairs are needed for the current rating, INFERRED).
Mating: J2-1 V5_SENS goes only to the on-board MAP sensor U2 + C1/C2 on every motherboard (VERIFIED map_mb.py: V5_SENS reaches U2.3, C1.1, C2.1 on all four) - see removal candidate R4.

## 5. Motherboards: harness cavity -> signal (header pad name = cavity label, VERIFIED from the HARNESS dicts; the pad->PCB-pin geometry is in kb/interconnect.md) and options
Common to all four (mb_common.py): JD1/JD2 sockets C124412 (HTR_GND -> GND); R1 120 + R6 0R CAN terminator on CAN_H/CAN_L; J5 AUX 2x10 IDC box header (optional, hand-fitted): 1 OUT_IGN3, 2 OUT_IGN4, 3 OUT_BOOST, 4 OUT_ALT, 5 OUT_MAINRLY, 6 IN_KNOCK, 7 VR1_P, 8 VR1_N, 9 VR2_P, 10 VR2_N, 11 IN_AFR, 12 IN_FLEX, 13 IN_N2O, 14 V5_EXT, 15 AUX_VBAT (F4 1.1 A PTC from VBAT_IN), 16-18 GND, 19 CAN_H, 20 CAN_L; D5 SS34 (AUX_VBAT -> OUT_BOOST freewheel), R35 4.7k (V5_EXT -> IN_FLEX), R36 10k (IN_N2O -> GND), D1 idle-valve freewheel to its +12 V feed; U2 MPX5700AP (IN_MAP, GND, V5_SENS) + C1 1u/C2 10n/C3 470p; J4 USB-C + R2/R3 5.1k CC + U4 USBLC6-2SC6; J2 JST S08B-PUDSS-1 (1 LSU_RT, 2 LSU_HTR_N, 3 LSU_VM, 5 LSU_IP, 6 LSU_UN, 8 HTR_PWR; 4, 7 empty); F1 2920L300 3 A PTC VBAT_IN -> HTR_PWR; R20-R22 4.7k VBAT_IN -> IN_SW1-3 (NOT fitted, no LCSC); HD1-4 standoffs, case holes. Signals reaching no harness cavity on any year: IN_AFR, IN_FLEX, IN_N2O, OUT_IGN3/4, VR1/VR2 (J5 only), CAN (J5), USB (J4), V5_SENS (MAP).

### 1989-95 (mb_na6.py rev 0.13, 48 pins, harness HARNESS dict)
1B VBAT_IN; 1C VIGN_IN (the START signal, not ignition-on; firmware does not use it as ignition sense); 1E OUT_CEL; 1G OUT_IGN1; 1H OUT_IGN2; 1J OUT_AC; 1L OUT_FAN; 1M IN_SW1; 1N HARN_1N (-> R28 only); 1Q IN_SW2; 1R HARN_1R (-> JP3); 1V IN_SW3; 2A-2D GND; 2E IN_HALL1; 2F GND; 2G IN_HALL2; 2I HARN_2I (-> JP5); 2K V5_EXT; 2L HARN_2L (-> R29/R30); 2M IN_TPS; 2N IN_AUX2; 2O HARN_2O (-> JP6); 2P IN_IAT; 2Q IN_CLT; 2R HARN_2R (-> JP4); 2S HARN_2S (-> JP3); 2T OUT_FP; 2U OUT_INJ1; 2V OUT_INJ2; 2W OUT_IACV; 2X OUT_VVT (purge); 2Y HARN_2Y (-> JP1); 2Z HARN_2Z (-> JP2). Open: 1A, 1D, 1F, 1I, 1K, 1O, 1P, 1S-1U, 2H, 2J.
Option links (all VERIFIED mb_na6.JUMPERS/SHUNTS): JP1 (1 OUT_INJ2, 2 OUT_INJ3, 3 HARN_2Y): 1-2 PAIR (INJ3 in parallel on 2V), 2-3 SEQ (INJ3 on 2Y, 94-95). JP2 (1 OUT_INJ1, 2 OUT_INJ4, 3 HARN_2Z): same for INJ4/2U/2Z; never SEQ on a 1989-93 automatic. JP3 (1 HARN_1R, 2 OUT_LS7, 3 HARN_2S): 1-2 = 1990-93 fan 2 on 1R, 2-3 = 94-95 on 2S. JP4 (OUT_ALT - HARN_2R): fit for 94-95 pressure-regulator solenoid. JP5 (OUT_TACH - HARN_2I): open with the stock igniter, fit only for COP (tach driven through 2I, R37 1k 2512 pull-up VBAT_IN -> OUT_TACH). JP6 (1 IN_AUX3, 2 HARN_2O, 3 OUT_BOOST): 1-2 AFM signal, 2-3 boost valve on the AFM wire. R28 0R 0805 (HARN_1N - V5_EXT) NOT fitted, TPS conversion; R29 0R 0805 FITTED (HARN_2L - IN_AUX1); R30 0R (HARN_2L - IN_TPS) NOT fitted; R27 4.7k (V5_EXT - IN_AUX1) NOT fitted (stock idle switch pull-up). D3/D4 SMCJ30A (OUT_INJ1/2 -> GND) NOT fitted (fit only with a rev 0.9 daughterboard). Fitted by year: 1989-93 JP3 1-2, JP6 1-2, JP1/JP2 open; 1994-95 JP1/JP2 2-3, JP3 2-3, JP4 1-2, JP6 1-2. Both mb_y8993/mb_y9495 wrappers (checking tools) reproduce these.
Note: the unused default of JP5 leaves OUT_TACH (J1-11) connected to nothing but the R37 and JP5 pads on the current board; the ordered boards wire OUT_TACH straight to 2I (B03).

### 1996-97 (mb_na96.py rev 0.9, TE 178780-1 76 pins)
1A OUT_FAN; 1B OUT_LS7; 1E OUT_CEL; 1G OUT_AC; 1K IN_SW2; 1L IN_SW3; 1M IN_SW1; 1O GND; 1U OUT_FP; 3B IN_AUX3 (MAF); 3C IN_AUX2 (front HO2S); 3D IN_AUX1 (rear HO2S); 3F IN_TPS; 3G IN_CLT; 3I V5_EXT; 3K IN_IAT; 3M OUT_VVT (front HO2S heater PWM); 3O GND; 4A GND; 4B VBAT_IN; 4C,4D GND; 4F IN_HALL1; 4G IN_HALL2; 4L OUT_TACH; 4N OUT_IGN1; 4Q OUT_IACV; 4R OUT_IGN2; 4U-4X OUT_INJ1-4. 2A-2L open (no plug). Options: none (no jumpers); D1 idle freewheel to VBAT_IN; no D2. VIGN_IN not wired.

### 1999-2000 (mb_nb1.py rev 0.9, TE 178780-1 NB1 footprint)
1B VBAT_IN; 1E OUT_CEL; 1I OUT_LS7; 1O OUT_ALT; 1P IN_SW2; 1R OUT_FAN; 1S OUT_AC; 1U OUT_VVT (front HO2S heater); 2B IN_IAT; 2C IN_AUX2; 2D IN_SW1; 2E IN_CLT; 2F IN_KNOCK; 2H IN_HALL2; 2I V5_EXT; 2J IN_HALL1; 2K OUT_TACH; 2L IN_AUX3 (MAF); 3A-3C GND; 3E IN_TPS; 3F GND; 3G OUT_IGN1; 3H OUT_IGN2; 3I IN_SW3; 3J IN_AUX1; 3M OUT_IACV; 3N OUT_FP; 3O IAC_12V (F2 2 A PTC from VBAT_IN, D1 freewheel); 3Q OUT_MAINRLY (VICS solenoid); 3W-3Z OUT_INJ1-4. Bay "X" (12 pos) unused. VIGN_IN not wired.

### 2001-05 (mb_nb2.py rev 0.9, TE 353830-5 72 pins)
2A OUT_INJ1; 2B OUT_FAN; 2C OUT_LS7; 2D OUT_INJ2; 2G OUT_INJ3; 2J OUT_INJ4; 2K OUT_AC; 2M OUT_FP; 2P IAC_12V (F2, D1); 2Q OUT_IACV; 2R OUT_CEL; 3A,3B GND; 3F OUT_IGN1; 3H OUT_MAINRLY (2003-05); 3I OUT_IGN2; 3M OUT_ALT; 3O OUT_TACH; 3T IN_SW1; 3V IN_HALL2; 3Y IN_HALL1; 4A GND; 4D OCV_12V (F3 2 A PTC, D2 freewheel); 4F IN_SW2; 4I IN_SW3; 4L V5_EXT; 4M IN_KNOCK; 4N IN_IAT; 4O GND; 4P IN_CLT; 4R OUT_VVT; 4S VIGN_IN (IG1, 2003-05); 4V IN_TPS; 4W IN_AUX2; 4X IN_AUX3 (MAF); 4AA IN_AUX1; 4AF VBAT_IN. GND_TIES: 3B tied to 3A on B.Cu.

Cavity -> net -> every other pad on the net for the whole board: kb/interconnect.md (sections `harness connector J1`). Net pad-level equality with the source is VERIFIED (section 1).

## 6. Findings from the source (detail)
6.1 **R110 wrong LCSC (error, high).** design.py:64 `LCSC_R1206 = {... '62': 'C25341'}` and wideband.py:153 `{'R8': 'C17969','R9': 'C17903','R10': 'C25341'}` (module R10 -> R110, value '62' via VALUE_RC). kb/parts_manifest.json: C25341 = 1206W4F620LT5E "620 mohm" (UniOhm code letters: ...J = x0.1, K = x0.01, L = x0.001: 620L = 0.62 ohm; the LCSC description in the manifest says 620mΩ; datasheet C25341_1206W4F620LT5E.txt). `tools/lcsc.py -s 1206W4F620JT5E` finds C17971 = 62 ohm 250 mW 1 % 1206, extended, 123,034 in stock, $0.0053. Role: R110 joins LSU_RT and LSU_IP (pcb_nets: LSU_RT = J2.34 R110.1 R111.2 R134.1 R108.1; LSU_IP = J2.36 R110.2 R112.2); the AD8628 stage U105 (R111/R112 10k in, R117 100k feedback = gain 10) measures the pump current across it. With 0.62 ohm the signal is 1/100 of the designed 62 ohm (62 mV/mA x10 = 0.62 V per mA designed; 6.2 mV per mA built): about 8 ADC counts per mA instead of about 770 on a 3.3 V, 12-bit ADC (INFERRED, arithmetic from the netlist values), so the lambda computation in the unmodified wideband firmware would be nonsense/very coarse. In the repo's own record the part was 62 ohm 0603 C23222 until rev 0.8 (VERIFICATION.md line 273 row R110) and the 1206 change introduced the code. Affects ordered rev 0.9 AND rev 0.10 (fab BOMs of both, VERIFIED). Rework: replace R110 by a 62 ohm 1 % 1206 (C17971, or any 62 ohm 1206). Source fix: LCSC_R1206['62'] = 'C17971' and wideband.py R10 -> 'C17971'.
6.2 **mpn.json is not the complete lookup record.** 14 LCSC codes used on current boards are not in it: C131317, C15008, C155605, C17901, C17903, C17969, C23892, C25341, C26032, C485806, C70065, C85085, C916423, C95063 (all SMD, JLC-placed; mpn.json is read by order_bom.py only for self-ordered/hand parts, so nothing breaks). bom.py:7 "every LCSC number was looked up on 2026-10-28 (scripts/mpn.json); nothing left to flag" is therefore not true as written. Conversely 44 mpn.json entries are not used by any current board (stale alternates, e.g. C25770 which is the documented 270k vs 2.7k mismatch; C14709; C540242; C25885 replacement present).
6.3 **Dead / duplicated code that could produce a wrong board.** (a) mb_na8.py (ordered 1994-95 board module): `build_parts()` calls `base.build_parts(HARNESS, paired_injectors=False, idle_pullup=False, tps_links=False)`; mb_na6.build_parts(harness=None, idle_pullup=True, tps_links=True) has no `paired_injectors` -> TypeError. It still references HARN_IAT/JP1 and 1N '' wiring that the merged board no longer has; mb_make.sh:22 only copies the file. Not reachable by the release scripts for the current boards (no importer other than mb_make.sh), so low risk, but a future "build 94-95" would fail or (if the kwarg were added) silently revive the pre-0.12 wiring. (b) `mb_common.trigger_select()` (hall/VR link selector) is unused since the AUX/VR move. (c) bom.py `GROUPS`/`DESC`/`BASIC`/`VERIFY`: 'Relay / lamp drivers' = `r == 'U5'` (no such part), every Q lands in 'Injector / solenoid drivers' (first rule `r.startswith('Q')` matches Q9-Q20, Q101), descriptions still name NCV8406A/ULN2003/AMS1117/SN65HVD230; BASIC contains C25917 (6.8k 0402, actually extended) and omits 20 codes the manifest shows as basic (C1562, C1620, C1663, C2128, C8598, C13167, C15008, C17477, C17901, C17903, C22787, C23189, C25091, C25741, C25768, C25792, C25890, C26083, C52923, C115962), 16 listed codes are no longer used. Consumer: parts_xlsx.py -> `daughterboard/miata_ecu_daughterboard_parts.xlsx` (Basic/Extended column and groups; not the JLC order). (d) `wideband.LCSC['R0603']['62'] = 'C23222'` is dead since R110 was moved to 1206 (the VALUE_RC path still selects it before the override). (e) daughterboard/README.md "What changed in rev 0.5" still describes NCV8406A / ULN2003 COM-TVS D11 / SN65HVD230 U106 (history section, superseded by rev 0.8 notes; doc only, B14 scope).
6.4 **Single-pad nets / floating inputs.** db: none (230 nets, all >= 2 pads). Unconnected pads (33 in the db, all deliberate: J3.6, U3/U14 NC pins 2/4/6, U12.3/U12.6, U6/U7 pins 1/8, U13.10/12, and 21 F103 pins). mb 1996-97 and 1999-2000: `VIGN_IN` has one pad (JD1.3): the car harness has no ignition-sense cavity wired, so AN_VIGN reads 0 V and D8 (wake-on-ignition) never conducts; harmless because the main relay powers VBAT_IN, but firmware that checks ignition voltage must not depend on it (INFERRED). No floating CMOS input found: U12 channel 1 B input tied GND, U13 unused gates' inputs tied GND, U11 fully used.
6.5 **Outputs tied together:** only the intended ones: CAN_H/CAN_L (U10, U106 bus transceivers, J2/R1/R6), WB_VM (U101 pins 13/14 are one follower: in- and out), WB_UN_BUF (U101 8/9 same). No two push-pull outputs share a net otherwise (checked from db_nets.txt).
6.6 **Capacitor derating (low, UNVERIFIED magnitude).** C63/C68 are 100 uF 6.3 V X5R 1206 (C15008, CL31A107MQHNNNE) on a 3.3 V rail; the shunt-clamp rationale (design.py:538-541, simulated 3.93 V peak) assumes the nominal value. X5R large-value MLCCs at 52 % of rated voltage typically lose a large fraction of capacitance (UNVERIFIED, from memory; not looked up in the Samsung curve). Only matters for the fault-step simulation.
6.7 Supply (from manifest, VERIFIED today): STM32F407VGT6 C12345 JLC stock 126; JD1/JD2 socket C124412 stock 65 (two per motherboard); TLS115B0EJ 556; TCAN1042V 257. 44 of 92 db JLC BOM lines are extended parts (7 of them "preferred"): 37 non-preferred extended lines (JLC charges a per-unique-extended-part setup fee; the fee amount is UNVERIFIED).

## 7. Candidate part removals (feature each would cost)
| # | Parts | Saves (JLC qty-1 price, manifest) | Feature lost | Evidence |
|---|---|---|---|---|
| R1 | VR comparator block: U9 LM2903, D15-D18, R51-R60, R73-R80, C48-C50, C60 (27 parts); frees PE12/PE13 and J2-19..22 | $0.27 + 1 extended part + placement | VR crank/cam input on AUX header J5-7..10 only. No supported car uses it: 1989-2005 harness cavities map crank/cam to IN_HALL1/2 on all four boards (HARNESS dicts), rev 0.10 comment design.py:402 "no Miata year uses a VR sensor" | map_mb.py: VR1/VR2 reach only J5 |
| R2 | IGN3/IGN4 channels: U7, R17, R18, D33, D34, Q18, Q19, R146, R147, C35 (+ half of U13, RN1) | $2.03 (Q18/Q19 $0.60 each) | Coil-on-plug / sequential ignition on cylinders 3/4 via J5-1/2; stock Miatas use IGN1 (1&4) and IGN2 (2&3) wasted spark on every year (HARNESS dicts) | OUT_IGN3/4 reach only J5 |
| R3 | BOOST driver Q7 + R25, R158 (and mb D5) | $2.69 + 2 passives | Boost solenoid output (J5-3, or JP6 2-3 on 89-95 AFM wire); no harness cavity uses OUT_BOOST | OUT_BOOST: J5/JP6 only |
| R4 | U3 TLS115 (V5_SENS tracker) + C25: join V5_SENS to +5V (or feed the MAP sensor from V5_EXT through a ferrite) | $1.26 (qty 1), $0.87 (qty 1000), extended part | Per-sensor short protection of the MAP supply. V5_SENS leaves the daughterboard only to U2/C1/C2 on the motherboard (on-board sensor, no harness wire), so the short-to-battery case U3 was added for cannot occur; a failed MAP sensor would then load the +5V buck (2 A) instead of a 150 mA tracker. Also needs motherboard/ordered-board J2-1 net unchanged. Design intent not stated in the repo for keeping both | map_mb.py; design.py:243-247, 488-492 |
| R5 | AN_AFR chain R37, R38, C40, D23 | $0.12 | External analog AFR input (J2-8 / J5-11): the on-board LSU wideband already supplies AFR over CAN | OUT of harness cavities |
| R6 | R6 0R CAN link, R36/R35 (if J5 not fitted), F4/D5 if J5 not fitted | about $0.08 | Selectable CAN termination; flex/nitrous pull options only matter when J5 is fitted | mb_common.py |
| R7 | Wideband LEDs D101-D103 + R113/R127/R130 | $0.03 | Wideband status LEDs (redundant with ECU LEDs) | trivial |
Keep-listed (looked at, NOT recommended): U15/Q20 clamp (protects 3V3 rail), U13+Q16-19 (needed IGN1/2), ALT/VVT drivers (used on 89-95 JP4/2X, NB1 1O, NB2 3M/4R), knock amp (used on 1999-2005), AN_VIGN chain (used on 1989-95 starter signal and 2003-05 IG1), D10 (USB bench power).

## 8. Per-block parts table (ref, value, MPN, LCSC) - generated by blocks.py from design.py + kb/parts_manifest.json (current rev 0.10)

**Headers** (2 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| J1 | Mezz_Power_Out (PinHeader_1x40_P2.54mm) | 2.54-1*40 | C2977586 |
| J2 | Mezz_Signal_In (PinHeader_1x40_P2.54mm) | 2.54-1*40 | C2977586 |

**MCU core/clock/boot/SWD** (23 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| U1 | STM32F407VGT6 (LQFP-100_14x14mm_P0.5m) | STM32F407VGT6 | C12345 |
| C1,C2,C3,C5,C6,C12,C15 | 100n (C_0603_1608Metric) | CC0603KRX7R9BB104 | C14663 |
| C4 | 100n (C_0402_1005Metric) | CL05B104KO5NNNC | C1525 |
| C7,C8 | 4.7u (C_0603_1608Metric) | CL10A475KO8NNNC | C19666 |
| C9,C10 | 2.2u (C_0603_1608Metric) | CL10A225KO8NNNC | C23630 |
| FB1 | BLM18PG221 (L_0603_1608Metric) | BLM18PG221SN1D | C80165 |
| C11 | 1u (C_0603_1608Metric) | CL10A105KB8NNNC | C15849 |
| Y1 | 8MHz (Crystal_SMD_5032-2Pin_) | X50328MSB2GI | C115962 |
| C13,C14 | 33p (C_0603_1608Metric) | CL10C330JB8NNNC | C1663 |
| R1 | 10k (R_0603_1608Metric) | 0603WAF1002T5E | C25804 |
| SW1 | BOOT (SW_Push_1P1T_XKB_TS-11) | TS-1187A-B-A-B | C318884 |
| SW2 | RESET (SW_Push_1P1T_XKB_TS-11) | TS-1187A-B-A-B | C318884 |
| J3 | SWD (Tag-Connect_TC2030-IDC) |  |  |
| R72 | 10k (R_0402_1005Metric) | 0402WGF1002TCE | C25744 |

**Status LEDs** (10 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| R2,R3,R4,R5,R6 | 1k (R_0603_1608Metric) | 0603WAF1001T5E | C21190 |
| D1,D5 | GREEN (LED_0603_1608Metric) | KT-0603G | C12624 |
| D2 | BLUE (LED_0603_1608Metric) | KT-0603B | C2288 |
| D3 | YELLOW (LED_0603_1608Metric) | KT-0603Y | C2287 |
| D4 | RED (LED_0603_1608Metric) | KT-0603R | C2286 |

**Input power / protection / 5V buck / LDO / sensor 5V** (33 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| D6 | SMCJ30A (D_SMC) | SMCJ30A | C224048 |
| D7 | SS34 (D_SMA) | SS34 | C8678 |
| D8,D10 | B5819W (D_SOD-123) | B5819W SL | C8598 |
| F1 | BSMD1812-110-33V (Fuse_1812_4532Metric) | BSMD1812-110-33V | C883150 |
| D12 | SMAJ33A (D_SMA) | SMAJ33A | C223988 |
| R7 | 1 (R_0603_1608Metric) | 0603WAF100KT5E | C22936 |
| C16,C17,C18 | 10u/50V (C_1206_3216Metric) | CL31A106KBHNNNE | C13585 |
| L1 | 2.2uH (L_Sunlord_MWSA0503S) | FXL0530-2R2-M | C177247 |
| C71,C19 | 100n (C_0603_1608Metric) | CC0603KRX7R9BB104 | C14663 |
| U2 | LMR14020 (SOIC-8-1EP_3.9x4.9mm_P) | LMR14020SDDAR | C187824 |
| R8 | 10k (R_0603_1608Metric) | 0603WAF1002T5E | C25804 |
| C20 | 10n (C_0603_1608Metric) | 0603B103K500NT | C57112 |
| D9 | B360A (D_SMA) | B360A-13-F | C94193 |
| L2 | 10uH (L_Sunlord_MWSA0603S) | MWSA0603S-100MT | C132141 |
| R9 | 68k (R_0603_1608Metric) | 0603WAF6802T5E | C23231 |
| C21 | 220p (C_0603_1608Metric) | CL10B221KB8NNNC | C1603 |
| R10 | 12k (R_0603_1608Metric) | 0603WAF1202T5E | C22790 |
| C22,C23,C59,C26,C27 | 10u (C_0805_2012Metric) | CL21A106KAYNNNE | C15850 |
| U3,U14 | TLS115B0EJ (Infineon_PG-DSO-8-27_3) | TLS115B0EJ | C3743696 |
| C24,C25,C61,C62 | 1u (C_0603_1608Metric) | CL10A105KB8NNNC | C15849 |
| U4 | LDL1117S33R (SOT-223-3_TabPin2) | LDL1117S33R | C435835 |

**Battery / ignition sense** (8 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| R11,R13 | 33k (R_0402_1005Metric) | 0402WGF3302TCE | C25779 |
| R12,R14 | 6.8k (R_0402_1005Metric) | 0402WGF6801TCE | C25917 |
| C28,C29 | 100n (C_0402_1005Metric) | CL05B104KO5NNNC | C1525 |
| D38,D39 | BAT54WS (D_SOD-323) | BAT54WS-7-F | C124205 |

**+3V3 shunt clamp** (7 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| U15 | TL431AIDBZR (SOT-23) | TL431AIDBZR | C23892 |
| Q20 | BCP53-16 (SOT-223) | BCP53-16,115 | C85085 |
| R141 | 1k (R_0603_1608Metric) | 0603WAF1001T5E | C21190 |
| R142 | 5.1k (R_0603_1608Metric) | 0603WAF5101T5E | C23186 |
| R143 | 12k (R_0603_1608Metric) | 0603WAF1202T5E | C22790 |
| C63,C68 | 100u (C_1206_3216Metric) | CL31A107MQHNNNE | C15008 |

**Relay/lamp low sides (FP,MAINRLY,AC,FAN,CEL,TACH,LS7)** (13 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| Q9,Q10,Q11,Q12,Q13,Q14,Q15 | ZXMS6004FFTA (SOT-23) | ZXMS6004FFTA | C95063 |
| U12 | SN74LVC4245APWR (TSSOP-24_4.4x7.8mm_P0.) | SN74LVC4245APWR | C7859 |
| RN2,RN3 | 4x10k (R_Array_Convex_4x0603) | 4D03WGJ0103T5E | C29718 |
| R160 | 1k (R_0402_1005Metric) | 0402WGF1001TCE | C11702 |
| C64,C65 | 100n (C_0402_1005Metric) | CL05B104KO5NNNC | C1525 |

**Ignition drivers (IGN1-4)** (23 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| U6,U7 | TC4427 (SOIC-8_3.9x4.9mm_P1.27) | TC4427AEOA713 | C20551 |
| R15,R16,R17,R18 | 100 (R_1206_3216Metric) | 1206W4F1000T5E | C17901 |
| RN1 | 4x10k (R_Array_Convex_4x0603) | 4D03WGJ0103T5E | C29718 |
| C34,C35 | 1u (C_0402_1005Metric) | CL05A105KA5NQNC | C52923 |
| D31,D32,D33,D34 | B5819W (D_SOD-123) | B5819W SL | C8598 |
| Q16,Q17,Q18,Q19 | ZXMS6004FFTA (SOT-23) | ZXMS6004FFTA | C95063 |
| R144,R145,R146,R147 | 3.3k (R_1206_3216Metric) | 1206W4F3301T5E | C26032 |
| U13 | 74HCT04PW (TSSOP-14_4.4x5mm_P0.65) | 74HCT04PW,118 | C131317 |
| C66 | 100n (C_0402_1005Metric) | CL05B104KO5NNNC | C1525 |

**Smart low sides (INJ1-4,IACV,VVT,BOOST,ALT) + shifter + clamps** (36 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8 | VND7NV04TR-E (TO-252-2) | VND7NV04TR-E | C155605 |
| U11 | SN74LVC4245APWR (TSSOP-24_4.4x7.8mm_P0.) | SN74LVC4245APWR | C7859 |
| R19,R20,R21,R22,R23,R24,R25,R26 | 10k (R_0603_1608Metric) | 0603WAF1002T5E | C25804 |
| R152,R153,R154,R155,R156,R157,R158,R159 | 220 (R_0402_1005Metric) | 0402WGF2200TCE | C25091 |
| D42,D43,D44,D45 | ES1D (D_SMA) | ES1D | C116492 |
| D46,D47,D48,D49 | 1.5SMC16A (D_SMC) | 1.5SMC16A | C1973780 |
| C57,C58 | 100n (C_0402_1005Metric) | CL05B104KO5NNNC | C1525 |
| R71 | 10k (R_0402_1005Metric) | 0402WGF1002TCE | C25744 |

**Analog inputs TPS/MAP/CLT/IAT/AFR/AUX1-3** (34 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| R27,R29,R31,R34,R37,R39,R41,R43 | 5.6k (R_0603_1608Metric) | 0603WAF5601T5E | C23189 |
| R28,R30,R32,R35,R38,R40,R42,R44 | 10k (R_0402_1005Metric) | 0402WGF1002TCE | C25744 |
| C36,C37,C38,C39,C40,C41,C42,C43 | 10n (C_0402_1005Metric) | CL05B103KB5NNNC | C15195 |
| R33,R36 | 2.7k (R_0603_1608Metric) | 0603WAF2701T5E | C13167 |
| D19,D20,D21,D22,D23,D24,D25,D26 | BAT54WS (D_SOD-323) | BAT54WS-7-F | C124205 |

**Knock amp** (12 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| C44,C47 | 100n (C_0603_1608Metric) | CC0603KRX7R9BB104 | C14663 |
| R45,R46,R47 | 100k (R_0603_1608Metric) | 0603WAF1003T5E | C25803 |
| C45 | 1u (C_0603_1608Metric) | CL10A105KB8NNNC | C15849 |
| R48 | 47k (R_0603_1608Metric) | 0603WAF4702T5E | C25819 |
| R49 | 10k (R_0603_1608Metric) | 0603WAF1002T5E | C25804 |
| R50 | 330 (R_0603_1608Metric) | 0603WAF3300T5E | C23138 |
| C46 | 10n (C_0603_1608Metric) | 0603B103K500NT | C57112 |
| U8 | LMV321IDBVR (SOT-23-5) | LMV321IDBVR | C7972 |
| R138 | 2.2k (R_0402_1005Metric) | 0402WGF2201TCE | C25879 |

**VR comparators (spare)** (27 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| U9 | LM2903DR (SOIC-8_3.9x4.9mm_P1.27) | LM2903DR | C7549 |
| D15,D16,D17,D18 | BAT54S (SOT-23) | BAT54SLT1G | C19726 |
| R73,R74,R75,R76 | 100k (R_0402_1005Metric) | 0402WGF1003TCE | C25741 |
| R77,R78 | 1M (R_0402_1005Metric) | 0402WGF1004TCE | C26083 |
| R79,R80 | 10k (R_0402_1005Metric) | 0402WGF1002TCE | C25744 |
| C60 | 100n (C_0402_1005Metric) | CL05B104KO5NNNC | C1525 |
| R51,R52,R53,R54,R56,R57,R58,R59 | 5.1k (R_0805_2012Metric) | 0805W8F5101T5E | C27834 |
| C48,C49 | 1n (C_0805_2012Metric) | CL21B102KBCNNNC | C46653 |
| R55,R60 | 10k (R_0603_1608Metric) | 0603WAF1002T5E | C25804 |
| C50 | 100n (C_0603_1608Metric) | CC0603KRX7R9BB104 | C14663 |

**Hall / 12V switch inputs** (21 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| R61,R63 | 4.7k (R_0603_1608Metric) | 0603WAF4701T5E | C23162 |
| R62,R64 | 1k (R_0603_1608Metric) | 0603WAF1001T5E | C21190 |
| C51,C52 | 1n (C_0402_1005Metric) | 0402B102K500NT | C1523 |
| D13,D14,D27,D28,D29 | 1N4148WS (D_SOD-323) | 1N4148WS | C2128 |
| R65,R67,R69 | 22k (R_0402_1005Metric) | 0402WGF2202TCE | C25768 |
| R66,R68,R70 | 10k (R_0402_1005Metric) | 0402WGF1002TCE | C25744 |
| C53,C54,C55 | 10n (C_0402_1005Metric) | CL05B103KB5NNNC | C15195 |
| D35 | BAT54A (SOT-23) | BAT54A | C916423 |

**CAN** (3 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| U10 | TCAN1042VDRQ1 (SOIC-8_3.9x4.9mm_P1.27) | TCAN1042VDRQ1 | C485806 |
| C56 | 100n (C_0603_1608Metric) | CC0603KRX7R9BB104 | C14663 |
| C67 | 100n (C_0402_1005Metric) | CL05B104KO5NNNC | C1525 |

**Flex / N2O inputs** (6 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| R139,R140 | 10k (R_0603_1608Metric) | 0603WAF1002T5E | C25804 |
| D36,D37 | BAT54S (SOT-23) | BAT54SLT1G | C19726 |
| C72 | 1n (C_0402_1005Metric) | 0402B102K500NT | C1523 |
| C73 | 10n (C_0402_1005Metric) | CL05B103KB5NNNC | C15195 |

**microSD** (8 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| J4 | microSD (microSD_HC_Molex_47219) | 472192001 | C164170 |
| C69 | 100n (C_0402_1005Metric) | CL05B104KO5NNNC | C1525 |
| C70 | 10u (C_0805_2012Metric) | CL21A106KAYNNNE | C15850 |
| R150,R151,R161,R162,R163 | 47k (R_0402_1005Metric) | 0402WGF4702TCE | C25792 |

**Mounting** (4 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| H1,H2,H3,H4 | M3 (MountingHole_3.2mm_M3) |  |  |

**Wideband (LSU) controller** (64 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| C101,C117,C104,C106,C107 | 1u (C_0402_1005Metric) | CL05A105KA5NQNC | C52923 |
| C110 | 4.7u (C_0603_1608Metric) | CL10A475KO8NNNC | C19666 |
| C111,C112,C113,C114,C116,C102,C105,C108,C109,C122,C118,C121 | 100n (C_0402_1005Metric) | CL05B104KO5NNNC | C1525 |
| C103 | 33n (C_0402_1005Metric) | CC0402KRX7R9BB333 | C106862 |
| D101 | RED (LED_0603_1608Metric) | KT-0603R | C2286 |
| D102 | GREEN (LED_0603_1608Metric) | KT-0603G | C12624 |
| D103 | BLUE (LED_0603_1608Metric) | KT-0603B | C2288 |
| J102 | SWD (WBO) (Tag-Connect_TC2030-IDC) |  |  |
| Q101 | VND14NV04 (TO-252-2) | VND14NV04TR-E | C2649436 |
| R101,R113,R102,R125,R126,R127,R130 | 1k (R_0402_1005Metric) | 0402WGF1001TCE | C11702 |
| R110 | 62 (R_1206_3216Metric) | 1206W4F620LT5E | C25341 |
| R111,R112,R121,R129,R103,R133,R134,R104,R135 | 10k (R_0402_1005Metric) | 0402WGF1002TCE | C25744 |
| R114 | 62k (R_0603_1608Metric) | 0603WAF6202T5E | C23221 |
| R115,R117,R120 | 100k (R_0402_1005Metric) | 0402WGF1003TCE | C25741 |
| R116 | 6.8k (R_0402_1005Metric) | 0402WGF6801TCE | C25917 |
| R119 | 47k (R_0402_1005Metric) | 0402WGF4702TCE | C25792 |
| R124 | 3.3k (R_0402_1005Metric) | 0402WGF3301TCE | C25890 |
| R131,R132 | 68k (R_0402_1005Metric) | 0402WGF6802TCE | C36871 |
| R105,R107 | 27k (R_0402_1005Metric) | 0402WGF2702TCE | C25771 |
| R106,R137 | 22k (R_0402_1005Metric) | 0402WGF2202TCE | C25768 |
| R108 | 47 (R_1206_3216Metric) | 1206W4F470JT5E | C17969 |
| R109 | 10 (R_1206_3216Metric) | 1206W4F100JT5E | C17903 |
| U101 | MCP6004 (TSSOP-14_4.4x5mm_P0.65) | MCP6004T-I/ST | C50282 |
| U102 | STM32F103C8T6 (LQFP-48_7x7mm_P0.5mm) | STM32F103C8T6 | C8734 |
| U103 | REF3033 (SOT-23) | REF3033AIDBZR | C36658 |
| U105 | AD8628 (SOT-23-5) | AD8628ARTZ-REEL7 | C29309 |
| U106 | TCAN1042VDRQ1 (SOIC-8_3.9x4.9mm_P1.27) | TCAN1042VDRQ1 | C485806 |
| Y101 | 8MHz (Crystal_SMD_5032-2Pin_) | X50328MSB2GI | C115962 |
| C119,C120 | 33p (C_0402_1005Metric) | 0402CG330J500NT | C1562 |

**UNASSIGNED** (4 parts)

| refs | value | MPN | LCSC |
|---|---|---|---|
| D30 | BAT54WS (D_SOD-323) | BAT54WS-7-F | C124205 |
| F2 | nSMD010 (Fuse_1206_3216Metric) | nSMD010 | C70065 |
| D40,D41 | B5819W (D_SOD-123) | B5819W SL | C8598 |
(Wideband: the 4 parts listed under UNASSIGNED are the wideband protection parts D30, F2, D40, D41.)

## 9. Motherboard parts (all four years, from mb_common.py / year modules; MPN from manifest)
JD1/JD2 B-2200S40P-A120 (C124412); J4 USB4105-GF-A (C3020560); U4 USBLC6-2SC6 (C7519); U2 MPX5700AP (C90152, hand); F1 2920L300/30GR (C22446884); F4 BSMD1812-110-33V (C883150); D5, D1, D2 SS34 (C8678); R1 120 0603 (C22787); R6 0R 0603 (C21189); R2/R3 5.1k (C23186); R35 4.7k (C23162); R36 10k (C25804); C1 1u (C15849); C2 10n (C57112); C3 470p (C1620); F2/F3 SMD1812-200-30 2 A (C46641168, NB1/NB2); J2 JST S08B-PUDSS-1 (hand, no LCSC); J1 TE header (hand); J5 AUX 2x10 (hand, optional); 1989-95 only: JP1-JP6 1x3/1x2 pin headers (C49257 for the 3-pin ones), R29 0R 0805 (C17477), R28/R30/R27/R37/D3/D4 not fitted. Option/links per board: section 5.

## Sources actually read
- repo/scripts: design.py (all 575 lines), wideband.py (all), daughter_rev10.py (all), mb_common.py (all), mb_na6.py (all but the long CHANGES strings), mb_na8.py (header + HARNESS), mb_na96.py, mb_nb1.py, mb_nb2.py, mb_later.py, mb_y8993.py, mb_y9495.py (all), bom.py (all), order_bom.py (all), mpn.json (parsed, not read line by line), placement.py (not read; only referenced).
- evidence/cur_db/pcb_nets.txt, pcb_footprints.csv, fab_*jlcpcb_bom.csv; evidence/cur_mb8995/9697/9900/0105/pcb_nets.txt and fab BOMs; evidence/ord_db fab BOM (R110); kb/parts_manifest.json; kb/interconnect.md (headings only); kb/boards/B03 (read).
- datasheets/txt: C7859 (SN74LVC4245A recommended conditions, VIH 2 V), C23892 (TL431 DBZ pinout), C25341 listing text; `tools/lcsc.py -s` for 1206W4F620JT5E.
- daughterboard/README.md rev 0.5 section lines 155-190, 243-248.

## Not checked
- placement.py (geometry only; not needed for the netlist), mb_build/mb_route/mb_export and the release shell scripts (so which modules the release scripts actually import was found by grep only: mb_na8 appears only in mb_make.sh).
- Footprint pad numbering/pin-1 conventions of the custom `ecu_mb` footprints (TE headers, MPX5700, USB4105): other audits (B09-B12).
- Whether ordered rev 0.9 / 0.7-0.11 netlists differ from today's source beyond B03's delta (they are not reproducible from the current scripts).
- Alternate-function claims for unused MCU pins (memory only). Real firmware use of spare pins not checked beyond B03.
- Effective capacitance of C63/C68 under DC bias (no curve read).
- Verification of every VERIFICATION.md/README claim against the source (B14/B15 scope); only the points listed in section 6 were compared.
