/**
 * @file board/mcuconf.h
 * @brief miata-ecu: rusEFI's STM32F4 mcuconf.h with the 32 kHz (LSE) oscillator turned off.
 *
 * The board has no 32 kHz crystal, and PC14 (OSC32_IN) is the fuel pump control (MIATA_FP). rusEFI's F4 default
 * enables the LSE: ChibiOS sets RCC_BDCR.LSEON at every boot, waits for it to start (it can't; the wait times out
 * after about a second) and never clears the bit. While LSEON is set, the oscillator owns PC14/PC15 whatever their
 * GPIO mode (ST RM0090, "LSE has priority over the GPIO function"), so the pump output would not be driven.
 * rusEFI's Prometheus and Subaru EG33 boards turn the LSE off the same way. The RTC runs from the LSI instead
 * (rusEFI's own fallback when the LSE doesn't start). miataBoardInitHardware() also clears LSEON, in case an older
 * bootloader or firmware left it set (the backup domain survives a reset).
 *
 * This directory is ahead of rusEFI's CONFDIR on the include path (BOARDINC), for the firmware and the OpenBLT
 * bootloader alike; #include_next then reads rusEFI's own file.
 */
#ifndef MIATA_ECU_MCUCONF_H
#define MIATA_ECU_MCUCONF_H

#include_next "mcuconf.h"

#undef STM32_LSE_ENABLED
#define STM32_LSE_ENABLED                   FALSE

#undef STM32_RTCSEL
#define STM32_RTCSEL                        STM32_RTCSEL_LSI

#endif /* MIATA_ECU_MCUCONF_H */
