# P02 - Wideband processor STM32F103C8T6 (U102), crystal, REF3033 (U103) and support parts

STATUS: complete (2026-11-16). Tags: VERIFIED / INFERRED / UNVERIFIED as in review brief section 5.

## Summary

1. All 48 U102 pads: PCB net == schematic net for every pad on both cur_db (rev 0.10) and ord_db (rev 0.9); the table is identical on both boards (VERIFIED, work/P02-.../u102_table.py output). No pinout error found anywhere in scope.
2. Every function the firmware uses sits on a pin that has that function in the ST datasheet (ADC IN0/2/3/8, TIM3_CH1 PA6, TIM2_CH3 on PB10 via partial remap 2, USART1 PA9/PA10, CAN PA11/PA12, SWD PA13/PA14).
3. UART link is crossed correctly: F407 PD8 (TX) -> F103 PA10 (RX), F407 PD9 (RX) <- F103 PA9 (TX); BOOT0 <- PD10 with R129 10k pull-down; BOOT1 (PB2) R135 10k to GND; NRST <- PD11 open drain with C116 100 nF. Matches AN2606/AN3155 entry conditions and the flasher (8E1, 0x7F, PID 0x410).
4. REF3033 SOT-23 pinout 1=IN 2=OUT 3=GND matches U103 (VERIFIED TI SBVS032F cover + Fig. 2). No output cap required; 1 uF + 100 nF present is allowed; load ~3 mA of 25 mA.
5. D30 orientation correct (K=+3V3, A=VDDA, BAT54WS pin 1 = cathode band).
6. LQFP48 footprint is the KiCad/IPC standard (0.5 mm pitch, pads 1.475 x 0.3, centre span 8.325 mm); longer than ST's suggested 1.2 mm pads but a normal solderable footprint. Pin 1/numbering direction CCW verified from coordinates.
7. Decoupling: 100 nF within 2-3.6 mm of each of VDD pins 24/36/48 (C113, C121, C112), 4.7 uF C110, VDDA 100 nF C109 (1.9 mm) + 1 uF C107. Good.
8. Real (low) issues: ST limits VDD-pin-to-VDD-pin variation to 50 mV (Table 6), the repo comment says "ST allows 0.3 V"; +3V3 LDO is +-3 % so VDDA/VDD can differ >100 mV in steady state (harmless for function, doc mismatch). HSE has no fallback (blank/failed crystal = wideband never starts), whereas all upstream rusEFI F1 wideband boards run from HSI.
9. Cost: Y101+C119+C120 ($0.26/unit) could be dropped as upstream F1 boards do (risk trade-off, owner's decision); clone MCUs save <= $0.1-0.3 and are not recommended; REF3033 kept.

## 1. Identity (live lookup 2026-11-16, tools/lcsc.py) - VERIFIED

| Ref | BOM value | LCSC | Real MPN / maker | Package | JLC library | JLC stock | Price qty 30-100 |
|---|---|---|---|---|---|---|---|
| U102 | STM32F103C8T6 | C8734 | STM32F103C8T6, STMicroelectronics | LQFP-48 7x7 | Extended (Preferred) | 191k-215k | $1.136 @30, $1.013 @250 |
| U103 | REF3033 | C36658 | REF3033AIDBZR, Texas Instruments | SOT-23-3 | Extended | 27.5k-31k | $0.291 @30, $0.247 @100 |
| Y101 | 8MHz | C115962 | X50328MSB2GI, YXC (8 MHz, CL 20 pF, ESR 80 ohm max) | SMD5032-2P | Basic | 517k | $0.246 @1, $0.183 @100 |
| C119, C120 | 33p | C1562 | 0402CG330J500NT C0G 50 V | 0402 | Basic | 1.85M | $0.0024 |
| D30 | BAT54WS | C124205 | BAT54WS-7-F, Diodes Inc | SOD-323 | Extended | 63.8k | $0.094 @50 |
| R135, R129 | 10k | C25744 | 0402WGF1002TCE | 0402 | Basic | 21M | $0.001 |
| D101-103 | RED/GREEN/BLUE | C2286/C12624/C2288 | KT-0603x | 0603 | basic/ext/ext | 5.7M/255k/65k | $0.01 |

Crystal datasheet C115962 has no text layer (image PDF); CL 20 pF / ESR 80 ohm max taken from the manifest (JLC data), not read on the datasheet page.

## 2. Datasheet digest

### STM32F103x8/xB (DS5319 rev 18, datasheets/txt/C8734_STM32F103C8T6.txt) - VERIFIED lines cited
- Table 6 (l.2118-2127): VDD-VSS -0.3..4.0 V; VIN on FT pin VDD+4.0 (max 4.0); **|dVDDx| variations between different VDD power pins 50 mV**; |dVSSx| 50 mV. Note 1: all VDD/VDDA/VSS/VSSA must always be connected.
- Operating: VDD 2.0-3.6 V; ADC needs VDDA 2.4-3.6 V (Table 46, l.4177); VREF+ internally = VDDA on LQFP48 (l.4226). T6 suffix: ambient -40..85 C (l.2211), TJ max 105 C for the 6 suffix (l.5778).
- ADC (Table 46/47): fADC max 14 MHz; RAIN max 50 kohm; at 14 MHz: 7.5 cyc -> 5.9 k, 13.5 -> 11.4 k, 28.5 -> 25.2 k. Equation 1 scaled to 12 MHz / 7.5 cycles (the port's setting) gives about 7.0 k (INFERRED: 0.625 us /(8 pF*ln 2^14) - 1 k).
- HSE (Table 22): 4-16 MHz, gm 25 mA/V, RF 200 k, recommended C 30 pF for RS 30 ohm, startup 2 ms.
- Max Run current at 48 MHz about 36 mA (Table 13, l.2341) -> 0.12 W; TJ rise a few C at ambient 85 C, inside 105 C (INFERRED).
- LQFP48 recommended footprint (Fig. 63, l.5613): pad 0.30 x 1.20, pitch 0.50, outer span 9.70, inner 7.30.
- Pin table LQFP48 (Fig. 8 / Table 5): 1 VBAT, 2 PC13, 3 PC14, 4 PC15, 5 PD0/OSC_IN, 6 PD1/OSC_OUT, 7 NRST, 8 VSSA, 9 VDDA, 10 PA0 (ADC0), 11 PA1 (ADC1), 12 PA2 (ADC2, USART2_TX, TIM2_CH3), 13 PA3 (ADC3), 14 PA4, 15 PA5, 16 PA6 (ADC6, TIM3_CH1), 17 PA7, 18 PB0 (ADC8), 19 PB1, 20 PB2/BOOT1, 21 PB10 (TIM2_CH3 remap), 22 PB11, 23 VSS, 24 VDD, 25-28 PB12-15, 29 PA8, 30 PA9 (USART1_TX), 31 PA10 (USART1_RX), 32 PA11 (CAN_RX), 33 PA12 (CAN_TX), 34 PA13 SWDIO, 35 VSS, 36 VDD, 37 PA14 SWCLK, 38 PA15, 39 PB3, 40 PB4, 41 PB5, 42 PB6, 43 PB7, 44 BOOT0, 45 PB8, 46 PB9, 47 VSS, 48 VDD.

### REF3033AIDBZR (TI SBVS032F) - VERIFIED
- SOT23-3 DBZ: pin 1 IN, 2 OUT, 3 GND (cover diagram, Fig. 2). Abs max V+ 7.0 V; output short to GND continuous.
- VOUT 3.3 V +-0.2 % (3.2934-3.3066), drift 75 ppm/C max -40..125 C, dropout 1 mV typ / 50 mV max, supply min VREF+0.05 V over temp, max 5.5 V, load 25 mA, ISC 45 mA, Iq 42 uA, noise 14-50 uVpp, startup 120 us. "Does not require a load capacitor"; 0.47 uF supply bypass always recommended (C117 1 uF + C108 100 nF on +5V satisfy). Caution about low ESR + high C applies to the 1.25 V part. SOT-23 theta-JA 336 C/W: load 3 mA * 1.7 V = 5 mW -> +2 C.
- +5V rail is 5.0 V (<5.5 V max). Input needs >= 3.35 V: fine except in a deep crank dip where +5V buck also drops (then +3V3 also drops).

### Boot (ST AN2606, from memory; UNVERIFIED text, but consistent with datasheet BOOT pins)
BOOT0=1, BOOT1=0 at reset -> system memory (ROM) bootloader, USART1 PA9/PA10, 8E1, auto-baud on 0x7F; product ID 0x410 for medium density (the flasher checks it).

## 3. Usage audit

### 3a. Pin table (U102 pad -> net -> firmware -> datasheet capability). Same on cur_db and ord_db. Schematic pin name == ST name for all 48 (sch_netlist.xml) and script `repo/scripts/wideband.py U2_PADS` agrees.

| Pad | Pin | Net (PCB = SCH) | Other nodes | Firmware use | Datasheet capability | Verdict |
|---|---|---|---|---|---|---|
| 1 | VBAT | +3V3 | | - | VBAT supply, tie to VDD | OK |
| 2,3,4 | PC13-15 | NC | | PC13/14 ID_SEL straps not fitted, PC15 pull-up input | GPIO | OK |
| 5 | PD0 OSC_IN | WB_OSC_IN | C119.1, Y101.1 | HSE 8 MHz | OSC_IN | OK |
| 6 | PD1 OSC_OUT | WB_OSC_OUT | C120.1, Y101.2 | HSE | OSC_OUT | OK |
| 7 | NRST | WB_NRST | C116 100n, J102.3, U1.58 (PD11 OD) | reset | NRST | OK |
| 8 | VSSA | GND | | | | OK |
| 9 | VDDA | WB_VDDA | REF3033 OUT, C107 1u, C109 100n, D30.A, R101 | ADC ref | VDDA 2.4-3.6 V | OK |
| 10 | PA0 | WB_UN_SENSE | U101.7 (op-amp out), R107 | ADC_IN0 Nernst | ADC12_IN0 | OK |
| 11 | PA1 | NC | | analog (CRL 0) | ADC IN1 | OK |
| 12 | PA2 | WB_IP_SENSE | R124 3.3k + C111 100n | ADC_IN2 | ADC12_IN2 (TIM2_CH3 default, not used) | OK |
| 13 | PA3 | WB_VM | U101.13/14, R109, R115, R132, D41 | ADC_IN3 | ADC12_IN3 | OK |
| 14,15,17 | PA4,5,7 | NC | | pull-up inputs | | OK |
| 16 | PA6 | WB_IP_DAC | R131 68k | TIM3_CH1 PWM | TIM3_CH1 default | OK |
| 18 | PB0 | WB_VBAT_DIV | R120 100k / R121 10k, C106 1u | ADC_IN8 | ADC12_IN8 | OK |
| 19 | PB1 | NC | | | | OK |
| 20 | PB2 BOOT1 | WB_BOOT1 | R135 10k to GND | - | BOOT1 | OK |
| 21 | PB10 | WB_HTR_PWM | R125-R127 1k | TIM2_CH3 via partial remap 2 (AFIO MAPR in boardInit) | TIM2_CH3 remap (RM0008 table) | OK |
| 22 | PB11 | NC | | | | OK |
| 23,35,47 | VSS | GND | | | | OK |
| 24,36,48 | VDD | +3V3 | | | | OK |
| 25-28 | PB12-15 | NC | | | | OK |
| 29 | PA8 | NC | | | | OK |
| 30 | PA9 | WB_PROG_RX (U1.56 = PD9 USART3_RX) | | USART1_TX, ROM bootloader | USART1_TX | OK |
| 31 | PA10 | WB_PROG_TX (U1.55 = PD8 USART3_TX) | | USART1_RX | USART1_RX | OK |
| 32 | PA11 | WB_CAN_RX | U106.4 | CAN_RX | CAN_RX | OK |
| 33 | PA12 | WB_CAN_TX | U106.1 | CAN_TX | CAN_TX | OK |
| 34 | PA13 | WB_SWDIO | J102.2 | SWD | SWDIO | OK |
| 37 | PA14 | WB_SWCLK | J102.4 | SWD | SWCLK | OK |
| 38,39,40 | PA15,PB3,PB4 | NC | | | JTAG pins, left default | OK |
| 41 | PB5 | WB_ESR_42 | R116 6.8k | ESR drive 4.2 | GPIO | OK |
| 42 | PB6 | WB_ESR_ADV | R119 47k | ESR drive ADV | GPIO | OK |
| 43 | PB7 | WB_ESR_49 | R106 22k | ESR drive 4.9 (default, push-pull) | GPIO | OK |
| 44 | BOOT0 | WB_BOOT0 | R129 10k to GND, U1.57 (PD10) | - | BOOT0 | OK |
| 45 | PB8 | WB_LED_B | D103.A (K via R113 1k to GND) | LED blue | GPIO | OK |
| 46 | PB9 | WB_LED_G | D102.A (K via R130 1k) | LED green | GPIO | OK |

Cross-checks: port register values (board.h) decoded: PA0/1/2/3 analog, PA6 AF-PP, PA12 AF-PP, PB0 analog, PB2/PB5/PB6 floating, PB7 PP, PB8/9 PP 2 MHz with ODR 0 (LED off), PB10 AF-PP, unused pins pull-up input. ODR bit 0 = LED off consistent with anode on the MCU pin (D102/103 pad 2 = A per schematic pin names, pad 1 = K). All 4 ADC channels in SQR3 match the pins (IN0, IN2, IN3, IN8).

Two-terminal parts: D30 pad 1 = K -> +3V3, pad 2 = A -> WB_VDDA (BAT54WS cathode band = pin 1, KiCad SOD-323 K=1). Diode conducts when VDDA exceeds +3V3 by Vf: correct sense for the stated purpose. D101 pad1 K=GND, pad 2 A=WB_LED_H (heater PWM via R127 1k): correct. Y101 non-polarised. REF3033 U103: 1=+5V, 2=WB_VDDA, 3=GND: correct.

### 3b. Footprint / layout
- LQFP-48_7x7mm_P0.5mm (KiCad): pads 1.475 x 0.3, pitch 0.5, centre spans 8.325 mm (pad 1 y=102.6625 vs pad 36 y=94.3375). ST suggests 1.2 mm long pads on a 8.5 mm centre span; the KiCad pad is 0.225 mm longer to the inside and 0.1 mm to the outside; both are normal. Pin numbering CCW starting bottom-left (rot 90): pads 1-12 along the bottom increasing x, 13-24 up the right, 25-36 along the top decreasing x, 37-48 down the left. Matches ST top view (VERIFIED from pad coordinates). ord_db identical.
- Decoupling distances to nearest VDD/VDDA pad (pcb_pads.csv): C109 100n 1.9 mm (VDDA), C112 2.0 mm (pad 48), C121 2.9 (pad 36), C113 3.6 / C110 4.7u 3.2 (pad 24), C107 1u 6.4. Good. Crystal Y101 about 6 mm from pins 5/6 (top view); layer image checked, nothing odd.
- J102 TC2030-IDC-NL on the BOTTOM side: pin 1 +3V3 (VTref), 2 SWDIO, 3 NRST, 4 SWCLK, 5 GND, 6 NC: matches the Tag-Connect NL ARM-10 style assignment (UNVERIFIED from memory of the cable). Not reachable with the stack assembled (INFERRED: it faces the motherboard); documented fallback only.

### 3c. Electrical stress
- MCU pins only see signals referenced to +3V3/VDDA: the op-amp U101 runs from +3V3 and D40/D41 clamp the pump/VM outputs. The only harness-exposed MCU net is WB_VBAT_DIV: R120 100k from VBAT_IN (battery before the protection). At 14.4 V: 1.309 V; 24 V: 2.18 V; ADC full scale (3.3 V) = 36.3 V; reverse -14 V: -140 uA into the pad clamp (limit +-5 mA, Table 7); load dump 100 V: about 1 mA; the divider's 10k to GND holds the pad <= 3.6 V up to 40 V (< 4.0 V abs max). OK (INFERRED from numbers above).
- ADC source impedance: PA0/PA3 op-amp outputs; PA2 3.3 k (+100 nF); PB0 9.1 k Thevenin with 1 uF (charge-sharing negligible, cap >> 8 pF). All below the 7 k @12 MHz/7.5 cycle limit or buffered by a large cap. OK.
- Clock tree: HSE 8 MHz x6 = 48 MHz SYSCLK, APB1 /2 = 24 MHz (CAN, BRP3, 13+2 tq, 500 kbit, sample point 87.5 %), ADC clock = PCLK2/4 = 12 MHz (<= 14 MHz). Same 48/24/12 MHz as upstream f1_rev3 (which uses HSI x12). CAN timing copy matches upstream f1_rev3 (VERIFIED file compare).
- Crystal: CL = 33p*33p/66 + stray = about 20 pF (matches 20 pF crystal). Gain margin: gm_crit = 4*ESR*(2 pi f)^2*(C0+CL)^2 = 4*80*2.53e15*(25 pF)^2 = 0.5 mA/V vs ST gm 25 mA/V -> margin about 50 (INFERRED, C0 assumed 5 pF). Fine.
- Thermal: T6 part, ambient 85 C, 0.12 W max * about 55 C/W (UNVERIFIED theta) = +6.5 C -> TJ about 92 C < 105 C. OK but note that the ECU case interior can exceed 85 C ambient only a little before the 85 C ambient rating is passed.
- Power sequencing: REF3033 (120 us) and LDL1117 both derive from +5V. D30 limits VDDA > VDD to Vf; at the REF's 45 mA short-circuit limit Vf is about 0.5 V, so a transient overshoot above 50 mV is possible but only for the C107/C109 charge time (about 1.1 uF * 0.5 V / 45 mA = 12 us) (INFERRED). Reverse direction (VDD > VDDA) is not clamped by anything; with LDL1117 +-3 % (VERIFIED datasheet l.196-198: +-2 % @25 C, +-3 % over -40..125 C) = 3.20-3.40 V vs VDDA 3.2934-3.3066 (+drift): steady differences up to about 0.1 V, above ST's 50 mV |dVDDx| line. Functionally harmless for ADC (ratiometric to VDDA, firmware uses VCC_VOLTS = 3.3 const) but the repo's comment "ST allows 0.3 V" is not what Table 6 says. Low.

### 3d. Required external parts
VDD/VDDA decoupling OK; NRST 100 nF OK (ST recommendation) with internal pull-up and open-drain driver on PD11 (RC rises in about 4 ms, flasher waits 100 ms); BOOT0 pull-down present; BOOT1 pull-down present; VBAT to VDD; no USB so no 1.5 k; unused pins NC with firmware pull-ups (PC13-15 are weak outputs when output; set as inputs, OK). HSE caps present. Nothing missing.

### 3e. Reference designs
Upstream F1 boards (ext/wideband-rusefi/firmware/boards): f1_dual, f1_rev2, f1_rev3 (F103xB/xE) all use HSI (HSECLK 0, PLLSRC_HSI); f1_dual_rev1 uses an 8 MHz HSE (F103xE); f0_module is STM32F042 (HSI48). This port = HSE like f1_dual_rev1 with xB clock values like f1_rev3. The F103 REF3033/VDDA arrangement is from the FOME mck1117 module (same REF3033 + 1k/1k VM_REF divider, R101/R102 = 1.65 mA from VDDA, well within 25 mA).

### Bootloader chain (firmware/board/wideband_uart_flash.cpp, VERIFIED reading)
BOOT0 high, 10 ms NRST low pulse, 100 ms wait, 0x7F sync (5 tries), Get-ID must be 0x410, Get command list picks erase 0x43/0x44, mass erase, 256-byte writes, read-back verify, then BOOT0 low and reset. USART3 8E1 115200. PD10 high-Z at F407 reset -> R129 pulls low, so normal power-up boots the F103 from flash. A blank new F103 therefore needs "Flash on-board wideband" once (README states it). Genuine ST ROM bootloader v2.2 uses 0x43. The 0x410 check does NOT distinguish clones (CKS32/GD32/APM32 F103 variants also report medium-density IDs; UNVERIFIED).

### Genuine vs clone
JLC C8734 is listed as STMicroelectronics (VERIFIED manifest). Clone alternatives at JLC today (lcsc.py -s F103C8T6): GD32F103C8T6 C77994 $1.04-1.62 (stock 16k), APM32F103C8T6 C393540 $0.78-1.24, CKS32F103C8T6 C556576 $0.87-1.55 (421), CH32F103C8T6 C2687451 $0.69-1.19, FCM32F103C8T6 C3151837 $0.45-0.91 (569), MM32 out of stock. Savings vs ST at qty 100 (about $1.0) are at most $0.2-0.5 and need firmware validation (ADC timing, flash page size, RAM, bootloader); I did not read those datasheets, so NOT recommended.

## 4. Cost / simplification
- Y101 + C119 + C120 = $0.18-0.25 + 0.005 (3 parts, 3 placements): removable if the port used HSI x12 like upstream f1_rev3/f1_rev2/f1_dual (VERIFIED upstream configs). Trade-off: HSI is trimmed to +-1 % (typ.) and CAN tolerance with 16 tq is tight; upstream ships thousands that way (UNVERIFIED field record). The owner/author chose HSE deliberately; flag as an option, with the added benefit of removing the HSE-start-failure mode. The change is a firmware config + not fitting parts (DNP); no board change needed.
- U103 REF3033 ($0.29) + C117/C108 + D30 ($0.094) + R101/R102: not removable without accuracy loss (+3V3 LDO +-3 % would feed the ADC; Nernst 450 mV control and Ip scaling would carry 3 % error). Keep.
- D30: removable in principle if VDDA ordering is not a concern; datasheet-wise the 50 mV rule is violated either way, and the real purpose is only brown-out ordering. Saves $0.094 but risk judgement; low value, keep.
- R129/R135/C116: needed (BOOT control).
- LEDs D101-103 (about $0.03 total) are UX; keep.

## Sources actually read
the review brief; repo/scripts/wideband.py (U2_PADS, parts), design.py (U4, U1 pins 55-58); repo/firmware/wideband/miata_f1/{io/io_pins.h, board.h, board.c, mcuconf.h, port.cpp, f1_port.cpp, port_shared.cpp, wideband_board_config.h, wideband_layout.ld}; repo/firmware/board/wideband_uart_flash.cpp; firmware/README.md flashing section; evidence/{cur_db,ord_db}/{pcb_pads.csv,pcb_nets.txt,pcb_footprints.csv,sch_netlist.xml}; layers/top_all.png crop; datasheets/txt/C8734 (Tables 6, 22, 46, 47, Fig. 63, pinout), C36658 (all key pages), C435835 (accuracy), C124205 (polarity); ext/wideband-rusefi/firmware/boards/{f1_*,f0_module} board.h/mcuconf.h/port_shared.cpp; tools/lcsc.py searches.

## Not checked
- Crystal X50328MSB2GI datasheet (no text layer; C0/ESR/drive level not read).
- ST AN2586/AN2606/AN3155 and RM0008 text were not available locally; bootloader entry and TIM2 remap are from memory plus the code comments (UNVERIFIED), though consistent with ST datasheet pin functions.
- Reading of AFIO_MAPR SWJ_CFG bits in boardInit (write-only bits per RM0008, UNVERIFIED) not examined further.
- Op-amp/heater/ESR analog parts (P03, P04), CAN transceiver (P14), J102 physical access with the stack assembled.
- No tolerance simulation of VDDA vs VDD.
