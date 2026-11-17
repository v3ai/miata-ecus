# F03 wideband firmware port + UART flasher

## Summary
- No hard error found in port pins/peripherals: every U102 (LQFP48) pin matches PCB nets (VERIFIED, pcb_nets.txt vs board.h/io_pins.h/port.cpp): PA0 Un, PA2 Ip, PA3 Vm, PB0 Vbat (ADC ch 0/2/3/8), PA6 TIM3_CH1 pump DAC, PB10 TIM2_CH3 (partial remap 2) heater, PB5/6/7 ESR 6.8k/47k/22k, PB8/9 LEDs, PA11/PA12 CAN, PA9/PA10 flasher link, BOOT0 pin44, NRST pin7, BOOT1 (PB2) 10k pulldown.
- Clock 8 MHz x6 = 48 MHz, APB1 24 MHz, CAN BRP3 TS1=13 TS2=2 -> 24M/(3*16)=500 kbit/s, SP 87.5% (VERIFIED by computation, mcuconf.h:49-53, f1_port/port_shared.cpp). ADC clk 12 MHz.
- Constants: gain 2.7 = R107/R103 27k/10k with R105 27k to GND (VERIFIED topology); Ip amp gain 10 (R117/R111 100k/10k); sense R110 62 ohm vs firmware 61.9 (0.2%); Vbat divider 100k/10k (R120/R121) matches; VDDA REF3033 3.3 V.
- Heater params (pinned wideband 27e115b): preheat 2.0 V (Bosch graph 1.5 V), ramp starts 7 V (Bosch jumps to 8.5 V) at 0.4 V/s (Bosch max 0.4 V/s) to 12 V (Bosch max 13 V), target ESR 300 ohm / 780 C (Bosch nominal 300 ohm), PWM 390 Hz (Bosch >=100 Hz), start >9.5 V, stop <8.5 V, off >=23 V. Conservative vs Bosch.
- Vbat source for heater duty = R120 from VBAT_IN (before F1 3A fuse), same battery; ok.
- Flasher AN3155 sequence read against code: Get N semantics, GetID 0x410, 0x43 mass erase (FF 00), write 256 B, read-verify 64 B, even parity 115200: all consistent with AN3155 as I know it (UNVERIFIED: st.com unreachable from sandbox, AN3155/AN2606 not fetched).
- Committed binary: sha256 matches .txt (VERIFIED); source = pinned rusEFI wideband 27e115b (matches gitlink); build reproducible only with same gcc (CI compares).

## Findings (details)
1. No watchdog (IWDG disabled mcuconf.h:225, HAL_USE_WDG FALSE) -> a firmware hang with TIM2 CH3 high leaves VND14NV04 on = full battery on LSU heater (Bosch 13 V max). Upstream shares this. Low probability; fix: enable IWDG.
2. Main MCU reset mid-flash: PD10 goes hi-Z, R129 pulls BOOT0 low but F103 not reset -> stays in ROM bootloader with partial/erased flash until power cycle; then dead wideband (blank vector) until user re-runs flash. Recovery is always possible (ROM bootloader immutable). Heater safe (R126 pulldown). Doc item.
3. Engine check only at start (wideband_uart_flash.cpp:372); not rechecked during ~10-15 s flash. Also wideband heater/CAN off during flash. Low.
4. Blank F103 from JLC has no firmware: wideband dead until first flash via TS (or SWD J102). Seller must flash before shipping; UX/doc.
5. ESR calc: measured node VMS is after PTC F2 but before R109, so R109 not in measured loop while VM_RESISTOR_VALUE=11.6 subtracts R109+F2 (upstream module has same 10 ohm convention). INFERRED: ~10 ohm low bias = ~4.5 C (table 250->350 ohm = 806->761 C). Negligible.
6. ID straps PC13/PC14 unconnected: hwId = 3*1+1 = 4 (strap_pin.cpp); CAN index comes from config default RusEfiIdx=0 -> ID 0x190 base, matches rusEFI index 0 (reId). Checked, ok. rusEFI sends ECU_STATUS (heater enable, vbatt) every 50 ms; baud default B500KBPS.
7. Mass erase wipes wideband settings incl. sensor type, CAN index (documented).

## Sources read
repo/firmware/wideband/*, miata_f1/*, board/wideband_uart_flash.*, evidence/cur_db/pcb_nets.txt, sch_netlist.xml, pinned wideband sources fetched from GitHub at 27e115b into work/F03.../pin, datasheets/extra/LSU49_bosch.pdf p2 (heater strategy graph), rusefi_wideband.cpp.

## Not checked
AN3155/AN2606 (st.com unreachable); no build/reproduction run (no arm gcc); VND14NV04 input drive; which CAN hardware (CAN1/CAN2) bus 0 maps to on main MCU (PB12/PB13) - F01 scope; tx/rx wiring of TCAN1042 (out of scope).
