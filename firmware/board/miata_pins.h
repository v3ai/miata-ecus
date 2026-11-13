/**
 * @file miata_pins.h
 * @brief Pin map of the miata-ecus daughterboard (rev 0.10; rev 0.9 boards run the same firmware: the pins added in
 * rev 0.10 are not connected there). Must match scripts/design.py ("mcu" dict);
 * firmware/tools/check_pins.py cross-checks the two.
 */

#pragma once

// ---------------------------------------------------------------------------------------------------------------
// Pin map (daughterboard rev 0.8; the MCU pins are unchanged since rev 0.5)
// ---------------------------------------------------------------------------------------------------------------
// Ignition: TC4427 5 V push-pull drivers, active high. The stock harness only has IGN1 (coil pack 1&4) and IGN2 (2&3).
// Rev 0.8: each output sources through 100 R + a Schottky and has a protected low-side pull-down (ZXMS6004, gate from
// an inverter), so a coil wire shorted to battery no longer back-drives the TC4427.
#define MIATA_IGN1 Gpio::E1
#define MIATA_IGN2 Gpio::E0
#define MIATA_IGN3 Gpio::B9
#define MIATA_IGN4 Gpio::B8
// Protected low sides, active high: ST VND7NV04 (rev 0.8; NCV8406A in rev 0.5b-0.7, AUIPS2041L before), driven at 5 V
// through an SN74LVC4245A whose output enable is MIATA_DRV_EN (open drain, active low, pulled up to 5 V): all eight
// stay off until the firmware enables them.
#define MIATA_INJ1 Gpio::B7
#define MIATA_INJ2 Gpio::B6
#define MIATA_INJ3 Gpio::B5
#define MIATA_INJ4 Gpio::B4
#define MIATA_IACV Gpio::B3
#define MIATA_VVT Gpio::D7    // NB2 OCV; 1996-97 and NB1 front O2 heater; 1989-93 purge
#define MIATA_BOOST Gpio::D6  // AUX header only
#define MIATA_ALT Gpio::D5    // NB alternator field; 1994-95 pressure regulator solenoid
// Relay / lamp / tach outputs, active high: ZXMS6004 protected low sides (rev 0.8; a ULN2003 before), driven at 5 V
// through a second SN74LVC4245A (U12) on the same MIATA_DRV_EN enable, so they too stay off until the firmware
// enables the drivers.
#define MIATA_FP Gpio::C14      // backup-domain pin: drives a CMOS shifter input (no load; ST's switch limit 3 mA). Also OSC32_IN: the LSE is kept off (board/mcuconf.h)
#define MIATA_MAINRLY Gpio::C13 // 2003-05 main relay; NB1 VICS solenoid
#define MIATA_AC Gpio::E6
#define MIATA_FAN Gpio::E5
#define MIATA_CEL Gpio::E4
#define MIATA_TACH Gpio::E3
#define MIATA_LS7 Gpio::E2      // second fan / condenser fan relay
// Low-side driver enable (PA8): drive low to enable the eight low-side driver inputs.
#define MIATA_DRV_EN Gpio::A8
// Digital inputs.
#define MIATA_HALL1 Gpio::E7    // crank (NA: CAS SGT, NB: CKP), 1k pull-up to the harness 5 V through a Schottky, clamped to 3.3 V
#define MIATA_HALL2 Gpio::E8    // cam (NA: CAS SGC, NB: CMP)
#define MIATA_SW1 Gpio::E9      // 12 V input through 22k/10k (rev 0.8; 33k/10k before): vehicle speed on every motherboard
#define MIATA_SW2 Gpio::E10     // A/C switch
#define MIATA_SW3 Gpio::E11     // clutch switch
// rev 0.10: two more 0-12 V inputs on J2 pins 24/25 (10k in series, clamped to 3.3 V; a spare UART up to rev 0.9).
#define MIATA_FLEX Gpio::C6     // flex-fuel sensor (50-150 Hz). The motherboard pulls the line up to the sensor 5 V (4.7k); 10 us filter
#define MIATA_N2O_ARM Gpio::C7  // nitrous arming switch to 12 V. The motherboard pulls the line down (10k); 100 us filter
// rev 0.10: microSD socket on SPI2 (microRusEFI's arrangement, with the clock on PB10 because PB13 is the CAN transmit pin).
#define MIATA_SD_SCK Gpio::B10
#define MIATA_SD_MISO Gpio::B14
#define MIATA_SD_MOSI Gpio::B15
#define MIATA_SD_CS Gpio::D13
// Analog inputs (0-5 V through 5.6k/10k, so x1.56 at the ADC).
#define MIATA_IN_VBATT EFI_ADC_1   // PA1, 33k/6.8k; rev 0.10: from the battery input itself (up to rev 0.9 after D7 and the fuse, 0.3-0.6 V low)
#define MIATA_IN_VIGN EFI_ADC_2    // PA2, 33k/6.8k
#define MIATA_IN_TPS EFI_ADC_4     // PA4
#define MIATA_IN_MAP EFI_ADC_5     // PA5, on-board MPX5700AP
#define MIATA_IN_CLT EFI_ADC_6     // PA6, 2.7k pull-up to the harness 5 V (V5_EXT, rev 0.8: a second TLS115 tracking +5V)
#define MIATA_IN_IAT EFI_ADC_7     // PA7, 2.7k pull-up; JP1 on the motherboard picks stock or M12 sensor
#define MIATA_IN_AFR EFI_ADC_14    // PC4, external 0-5 V wideband (the on-board one talks CAN)
#define MIATA_IN_AUX1 EFI_ADC_15   // PC5, rear O2 / idle switch / load signal, depending on year
#define MIATA_IN_AUX2 EFI_ADC_8    // PB0, front narrowband O2
#define MIATA_IN_AUX3 EFI_ADC_9    // PB1, AFM flap or MAF signal

// Board voltages and dividers.
static constexpr float MIATA_VBATT_DIVIDER = (33.0f + 6.8f) / 6.8f;
static constexpr float MIATA_ANALOG_DIVIDER = (5.6f + 10.0f) / 10.0f;
// CLT and IAT: 2.7k pull-up to 5 V, and the 5.6k + 10k ADC divider loads the same node. The Thevenin equivalent of
// the two is a 4.26 V supply behind 2.30k, which is exactly the pull-up model rusEFI's thermistor code uses.
static constexpr float MIATA_TEMP_PULLUP = 2700.0f;
static constexpr float MIATA_TEMP_LOAD = 5600.0f + 10000.0f;
static constexpr float MIATA_TEMP_BIAS = MIATA_TEMP_PULLUP * MIATA_TEMP_LOAD / (MIATA_TEMP_PULLUP + MIATA_TEMP_LOAD);
static constexpr float MIATA_TEMP_SUPPLY = 5.0f * MIATA_TEMP_LOAD / (MIATA_TEMP_PULLUP + MIATA_TEMP_LOAD);
