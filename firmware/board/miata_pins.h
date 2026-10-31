/**
 * @file miata_pins.h
 * @brief Pin map of the miata-ecus daughterboard (rev 0.5). Must match scripts/design.py ("mcu" dict);
 * firmware/tools/check_pins.py cross-checks the two.
 */

#pragma once

// ---------------------------------------------------------------------------------------------------------------
// Pin map (daughterboard rev 0.5)
// ---------------------------------------------------------------------------------------------------------------
// Ignition: TC4427 5 V push-pull drivers, active high. The stock harness only has IGN1 (coil pack 1&4) and IGN2 (2&3).
#define MIATA_IGN1 Gpio::E1
#define MIATA_IGN2 Gpio::E0
#define MIATA_IGN3 Gpio::B9
#define MIATA_IGN4 Gpio::B8
// NCV8406A protected low sides (rev 0.5b; AUIPS2041L before), active high. Rev 0.5: driven at 5 V through an SN74LVC4245A whose output enable is
// MIATA_DRV_EN (open drain, active low, pulled up to 5 V): all eight stay off until the firmware enables them.
#define MIATA_INJ1 Gpio::B7
#define MIATA_INJ2 Gpio::B6
#define MIATA_INJ3 Gpio::B5
#define MIATA_INJ4 Gpio::B4
#define MIATA_IACV Gpio::B3
#define MIATA_VVT Gpio::D7    // NB2 OCV; 1996-97 and NB1 front O2 heater; 1989-93 purge
#define MIATA_BOOST Gpio::D6  // AUX header only
#define MIATA_ALT Gpio::D5    // NB alternator field; 1994-95 pressure regulator solenoid
// ULN2003 relay / lamp drivers, active high.
#define MIATA_FP Gpio::C14      // backup-domain pin: fine for a ULN2003 input (0.72 mA; ST's switch limit 3 mA)
#define MIATA_MAINRLY Gpio::C13 // 2003-05 main relay; NB1 VICS solenoid
#define MIATA_AC Gpio::E6
#define MIATA_FAN Gpio::E5
#define MIATA_CEL Gpio::E4
#define MIATA_TACH Gpio::E3
#define MIATA_LS7 Gpio::E2      // second fan / condenser fan relay
// Low-side driver enable (PA8): drive low to enable the eight low-side driver inputs.
#define MIATA_DRV_EN Gpio::A8
// Digital inputs.
#define MIATA_HALL1 Gpio::E7    // crank (NA: CAS SGT, NB: CKP), 1k pull-up to 5 V, clamped to 3.3 V on the board
#define MIATA_HALL2 Gpio::E8    // cam (NA: CAS SGC, NB: CMP)
#define MIATA_SW1 Gpio::E9      // 12 V input through 33k/10k: vehicle speed on every motherboard
#define MIATA_SW2 Gpio::E10     // A/C switch
#define MIATA_SW3 Gpio::E11     // clutch switch
// Analog inputs (0-5 V through 5.6k/10k, so x1.56 at the ADC).
#define MIATA_IN_VBATT EFI_ADC_1   // PA1, 33k/6.8k
#define MIATA_IN_VIGN EFI_ADC_2    // PA2, 33k/6.8k
#define MIATA_IN_TPS EFI_ADC_4     // PA4
#define MIATA_IN_MAP EFI_ADC_5     // PA5, on-board MPX5700AP
#define MIATA_IN_CLT EFI_ADC_6     // PA6, 2.7k pull-up to sensor 5 V
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
