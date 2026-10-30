/**
 * @file wideband_uart_flash.h
 * @brief Programs the on-board wideband MCU (STM32F042) through its ROM serial bootloader.
 */

#pragma once

// TunerStudio board action index (TS_BOARD_ACTION) for the "Flash wideband (UART)" button, see board_commands.ini.
#define MIATA_TS_WBO_UART_FLASH 0x10

// Sets PD10 (F042 BOOT0) low and releases PD11 (F042 NRST) so the wideband runs its own firmware, and registers the
// console commands wbo_uart_flash and wbo_uart_status.
void initWidebandUartFlash();

// Starts flashing in a background thread. Refused while the engine turns or a flash is already running.
void startWidebandUartFlash();
