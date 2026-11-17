# F01 - rusEFI board configuration vs hardware

Status: COMPLETE (partial, see Not checked). Scratch: work/F01-board-config-vs-hardware/ (u1.txt = U1 pad->net, chk.py = yaml vs PCB cross-check).

## Summary
1. VERIFIED: every MCU pin in miata_pins.h matches the PCB (cur_db and ord_db U1 pads, LQFP100 numbering; table below). connectors/daughterboard.yaml J1/J2 ids also match the PCB nets (script chk.py, 0 real mismatches; the "ADC_n" ids are names, they map to the right pins).
2. VERIFIED: dividers. Analog 5.6k + 10k = 1.56 (R27..R44 values read from pcb_footprints.csv); VBATT/VIGN 33k + 6.8k = 5.853 (R11-R14). rusEFI does not apply the 1.56 divider to vbatt (init_vbatt.cpp: adcVoltsPerVolt 1.0) so using separate coefficients is right.
3. VERIFIED: MPX5700AP: Vout = Vs(0.0012858 P + 0.04) gives 0.2 V at 0 kPa and 4.70 V at 700 kPa at Vs = 5 V; firmware uses 0.2/4.70 V and 0/700 kPa, sensor-side volts (rusEFI multiplies the ADC volts by 1.56 first). ADC sees at most 3.01 V. Correct.
4. VERIFIED: CLT/IAT: 2.7k pull-up to V5_EXT with 15.6k of divider on the node = 4.262 V behind 2.30k; firmware passes bias 2.30k and supply 4.262 V to rusEFI (init_thermistors.cpp:51 uses the board override). Correct.
5. Output chain polarity checked: MCU 3.3 V push-pull -> SN74LVC4245A (DIR pin 2 = GND = B->A, A side 5 V) -> VND7NV04 / ZXMS6004 inputs, all non-inverting and active high; ignition TC4427 non-inverting plus 74HCT04 inverter to the ZXMS pull-down, so idle/reset state is coil input low. rusEFI default OM_DEFAULT push-pull non-inverted is right. No inverted flags are needed.
6. PA8 enable (OM_OPENDRAIN_INVERTED, R71 10k pull-up to 5 V, OE of U11/U12 = pin 22): code and hardware agree; drivers stay off through reset/bootloader/DFU; released after 4 slow ticks, dropped on every Burn (documented, firmware/README.md:132).
7. EXTI: trigger/flex/VSS use EXTI in this rusEFI (digital_input_exti.cpp, init_flex.cpp:25, frequency_sensor.cpp:40), not timers or ICU. Lines in use by default: 7 (PE7), 8 (PE8), 9 (PE9; VSS). Flex PC6 = line 6, N2O PC7 is polled (nitrous_controller.cpp:143 efiReadPin) so it does not collide with PE7 (line 7). No conflict in any preset; a conflict would only appear if a user sets the N2O pin as an event input.
8. CAN2-only: rusEFI's ChibiOS fork enables the CAN1 clock when CAND2 starts and sets default accept-all filters in init (hal_can_lld.c lines 662-694 of rusefi/ChibiOS master; fetched today, not the pinned submodule, the ChibiOS submodule is empty in this checkout). Holds.
9. Findings of substance (details in the table): A/C-switch and clutch polarity never set (F-1, F-6); ordered firmware drives the tach output into 2I on 1989-95 (F-2); CEL dark on fatal error on ordered boards (F-3).

## Pin table: firmware constant -> MCU pin -> U1 pad -> PCB net (cur_db; ord_db identical except as noted)
| Constant | MCU | U1 pad | Net -> circuit | Result |
|---|---|---|---|---|
| IGN1/2/3/4 | PE1/PE0/PB9/PB8 | 98/97/96/95 | IGNn_CTL -> TC4427 + 74HCT04 + ZXMS pull-down, RN1 10k pull-downs | ok |
| INJ1..4 | PB7/PB6/PB5/PB4 | 93..90 | INJn_CTL -> U11 B7..B4 -> VND7NV04 | ok |
| IACV, VVT, BOOST, ALT | PB3, PD7, PD6, PD5 | 89, 88, 87, 86 | U11 B3..B0-side | ok (PB3 is JTDO at reset; gated by PA8) |
| FP, MAINRLY, AC, FAN, TACH, LS7 | PC14, PC13, PE6, PE5, PE3, PE2 | 8, 7, 5, 4, 2, 1 | U12 -> ZXMS6004 | ok |
| CEL | PE4 | 3 | cur: R160 1k to Q13 gate (outside enable); ord: U12.18 | differs cur/ord |
| DRV_EN | PA8 | 67 | DRV_EN_N: R71 to 5 V, U11.22, U12.22 | ok |
| HALL1/HALL2 | PE7/PE8 | 38/39 | R61/R63 4.7k, C 1n, clamp, 1k pull-up to harness 5 V | ok, non-inverting |
| SW1/SW2/SW3 | PE9/PE10/PE11 | 40/41/42 | 22k/10k + clamp | ok |
| FLEX/N2O_ARM | PC6/PC7 | 63/64 | FLEX_M/N2O_ARM_M (cur only) | ok |
| ADC VBATT, VIGN | PA1, PA2 | 24, 25 | 33k/6.8k | ok |
| ADC TPS, MAP, CLT, IAT | PA4, PA5, PA6, PA7 | 29..32 | 5.6k/10k | ok |
| ADC AFR, AUX1, AUX2, AUX3 | PC4, PC5, PB0, PB1 | 33..36 | 5.6k/10k | ok |
| Knock | PA3 (ADC3_IN3) | 26 | AN_KNOCK | ok |
| CAN RX/TX | PB12/PB13 | 51/52 | U10 TCAN1042V (not SN65HVD230 as the code comment says) | ok, comment stale |
| USB | PA11/PA12 | 70/71 | J2.30/31 | ok |
| SD SCK/MISO/MOSI/CS | PB10/PB14/PB15/PD13 | 47/53/54/60 | J4 (cur only; ord: not connected) | ok |
| WB UART | PD8 TX/PD9 RX | 55/56 | -> F103 PA10 RX (U102.31) / PA9 TX (U102.30); 8E1 as AN3155 | ok |
| WB BOOT0/NRST | PD10/PD11 | 57/58 | U102.44 (R129 10k) / U102.7 | ok |
| LEDs run/comm/warn/err | PD12/PC8/PC9/PD15 | 59/65/66/62 | R2/R3/R4/R5 | ok |
| VR1/VR2 (spare) | PE13/PE12 | 44/43 | VRn_OUT | ok, unconfigured |

Harness function per year was audited by the PIN-* notes (kb/pinouts); I did not repeat it. Firmware-relevant points from the interconnect tables: 1989-95 OUT_LS7 reaches 1R (89-93) or 2S (94-95) via JP3; OUT_ALT reaches 2R only via JP4; 1996-97 VVT driver on 3M (O2 heater); NB1 VVT driver on 1U (O2 heater), NB2 on 4R; MAINRLY on 3H (2001-05) / 3Q (NB1, VICS, unused); VIGN_IN on 4S (2001-05) and 1C (1989-95 starter signal, firmware leaves ignition sense unassigned there: correct).

## Findings (full)
F-1 A/C switch polarity never set (medium, INFERRED). firmware never sets acSwitchMode (miata_board.cpp has no such line; rusEFI default 0 = PI_DEFAULT). ButtonDebounce (hw_layer/debounce.cpp:109-115) only inverts for PI_PULLUP, so the switch is active-HIGH. R16 (kb/research, FSM voltage table) gives 1989-93 pin 1Q "below 2.5 V = A/C on", i.e. active-LOW; the 1989-95 motherboard fits R21 4.7k to VBAT, so the pin sits HIGH with the A/C off. Result: rusEFI sees "A/C requested" with the A/C off: fan1 (acMode Relay) runs, idle-up applies, the A/C relay output is energised (the stock compressor circuit still goes through the dash switch). Polarity on 1994-2005 is not established by any source read (PIN-9900 also says cannot verify). Fix: set acSwitchMode = PI_PULLUP (active low) for the years with grounded-when-on switches after verifying, or document the TunerStudio setting.
F-2 Ordered firmware drives the tach output into harness 2I on 1989-95 (medium, VERIFIED mechanism, effect INFERRED). ordered-boards/2026-11/firmware/board/miata_board.cpp has no miataNoTachOutput() (diff against current firmware); ord_mb8993 and ord_mb9495 wire OUT_TACH directly to 2I (kb/interconnect.md lines 1071-1123, 1257-1309); PIN-8993/PIN-9495 show 2I is the igniter signal INTO the ECU (FSM). So after pressing a 1989-93 or 1994-95 preset the ECU pulls 2I low twice per revolution with no pull-up. Tach reading and igniter tach signal are disturbed; no damage expected (ZXMS6004 60 V clamp). Owner must set "Tach output" to none in TunerStudio after pressing the year button (the preset reapplies it each time), or the preset must be updated before the car is started.
F-3 Ordered boards: CEL stays dark on a fatal rusEFI error (low, VERIFIED). ord_db CEL_CTL goes through U12.18 (behind DRV_EN); the current firmware lights the lamp directly (board_configuration.cpp:83-93) but the ordered firmware has no such code, and rusEFI drives outputs off on a fatal error. The customer sees no lamp; only the internal red LED.
F-4 Ordered firmware has no SD/flex/N2O settings and the old VBATT comment (info): rev 0.9 VBATT is read after D7 + F1, 0.3-0.4 V low; target 14.0 V (alternator control off by default anyway). Current firmware on a rev 0.9 board would enable SPI2 and SD logging on unconnected pins (README says harmless; not run).
F-5 Every Burn drops all 15 low-side outputs (injectors, pump, main relay on 2003-05) for the reconfiguration time (documented, README:132). Duration unknown (UNVERIFIED). On 2003-05 the main relay coil releases during that time. Do not burn with the engine running.
F-6 Clutch switch polarity (low, VERIFIED code, INFERRED effect). clutchDownPinMode defaults PI_PULLUP (engine_configuration.cpp:223) and getClutchDownState() returns the raw level (engine.cpp:235, io_pins.cpp:158), so "clutch down" = pin HIGH; stock 1V is 0 V with clutch in or neutral (R16). Inverted for launch control / shift torque reduction, which are off by default.
F-7 NA presets keep tpsMin 100 / tpsMax 650 (0.5 V / 3.25 V sensor volts: TUNER-scaled, TPS_TS_CONVERSION 5 mV per count, tps.h:17); NB presets keep rusEFI defaults 0-5 V. Real TPS span not checked; do a TPS calibration (low).
F-8 Doc: code comment in miata_board.cpp:41 names the transceiver SN65HVD230; the board uses TCAN1042VDRQ1 (low).
F-9 NB presets set only fan1AcMode = Relay (setMiataNbCommon); fan2AcMode stays Disabled: A/C does not command the condenser fan (also reported by PIN-9900; not re-reported as new).

## Checked, correct (tried to break, held)
- Pin map, yaml ids, ADC channel numbers (EFI_ADC_n = ADC1_INn, PA3 left to ADC3 for knock), LED pins, USART3 pins and 8E1 for the F103 ROM loader.
- Trigger assignment: NA triggerInputPins[0]=cam SGC (HALL2), [1]=crank SGT (HALL1) matches rusEFI's Hellen NA6/NA96 presets (primary = CAM, secondary = CRANK); NB crank = HALL1 as trigger, cam = HALL2 as camInputs matches Hellen NB1; trigger type TT_MAZDA_MIATA_NA / TT_MIATA_VVT as the rusEFI presets; hall inputs are non-inverting (no inverter on HALL1/2), same as Hellen.
- Injection/ignition: NA6 batch, 1989-93 stock wiring 2U/2V; NA94/NA96/NB sequential; wasted spark uses ignitionPins[0] and [2] as in Hellen. Main relay only on 2003-05; 2001-02 variant has no ignition sense.
- Drivers' enable sequencing and parking of unused control pins (input with pull-down; PB4/PB3 JTAG reset states are gated).
- LSE off (mcuconf.h) so PC14 can be the pump output; PC13/PC14 drive only a CMOS shifter input.
- Idle valve: low side, non-inverted, frequency rusEFI default (DEFAULT_SOLENOID_FREQUENCY, 300 in the generated headers read); NB tune does not set it. Stock valve frequency not found (UNVERIFIED either way).

## Sources actually read
repo/firmware/README.md (first 80 lines), board/miata_board.cpp, miata_pins.h, miata_board.h, board_configuration.cpp, board.mk, mcuconf.h, knock_config.h, prepend.txt, board_commands.ini, board_popular_vehicles.ini, connectors/daughterboard.yaml; diff of ordered-boards/2026-11/firmware/board against it; rusEFI at the pinned commit: mazda_miata_1_6.cpp, mazda_miata_na8.cpp, mazda_miata_vvt.cpp, trigger_mazda.cpp, hellenMiata* board_configuration.cpp, engine_type_impl.cpp, engine_configuration.cpp, hardware.cpp, debounce.cpp, io_pins.cpp, engine.cpp, init_vbatt.cpp, init_thermistors.cpp, init_flex.cpp, digital_input_exti.cpp, nitrous_controller.cpp, fan_control.cpp, stm32_can.cpp, can_hw.cpp, can_rx.cpp; evidence/cur_db and ord_db pcb_nets.txt, pcb_footprints.csv; kb/interconnect.md harness tables; kb/pinouts PIN-*; kb/research/R16; https://raw.githubusercontent.com/rusefi/ChibiOS/master/os/hal/ports/STM32/LLD/CANv1/hal_can_lld.c.

## Not checked
SN74LVC4245A OE reference rail and VIH with a 5 V pull-up on a 3.3 V port (datasheet not opened); ChibiOS at the pinned commit (submodule empty); USB VBUS sensing mode; wideband CAN frame format accepted by the ECU listener (0x190 base seen in the WBO source); stock idle-valve and tach waveforms; polarity of A/C and clutch inputs on 1994-2005; firmware simulation in repo/firmware/sim not run; no build run.
