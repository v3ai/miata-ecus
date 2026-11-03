#pragma once

// miata-ecus daughterboard wideband: the rusEFI/FOME module's analog front end (as the f0_module port) on an
// STM32F103C8 with battery sensing (R120/R121) and the three ESR drive resistors.

#define TS_SIGNATURE "rusEFI 2023.05.10.wideband_f1"

#define VCC_VOLTS (3.3f)            // VDDA = REF3033 (U103)
#define HALF_VCC (VCC_VOLTS / 2)
#define ADC_MAX_COUNT (4095)
#define ADC_OVERSAMPLE 24

#define NERNST_INPUT_GAIN (2.7f)    // U101B: R107 / R103 = 27k / 10k

#define BATTERY_INPUT_DIVIDER (10.0 / (10.0 + 100.0))   // R121 / (R120 + R121)
#define BOARD_HAS_VOLTAGE_SENSE

#define AFR_CHANNELS 1

#define VM_RESISTOR_VALUE (11.6f)   // R109 (10 ohm) + F2 (rev 0.8, PTC in the VM wire, 1.6 ohm typical)
