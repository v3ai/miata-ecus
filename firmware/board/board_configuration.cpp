/**
 * @file board_configuration.cpp
 * @brief rusEFI board definition for the miata-ecus daughterboard (STM32F407VGT6) on any of its motherboards.
 *
 * The configuration itself (pin map, board facts, year presets) is in miata_board.cpp; this file wires it into
 * rusEFI's board hooks and adds the parts that only exist on the real hardware (LEDs, wideband flasher).
 */

#include "pch.h"
#include "board_overrides.h"
#include "wideband_uart_flash.h"
#include "miata_board.h"
#include "settings.h"
#include "tunerstudio.h"

// LEDs (active high through 1k). The red error LED is LED_CRITICAL_ERROR_BRAIN_PIN in board.mk.
Gpio getRunningLedPin() {
	return Gpio::D12;
}

Gpio getCommsLedPin() {
	return Gpio::D13;
}

Gpio getWarningLedPin() {
	return Gpio::D14;
}

#ifndef EFI_BOOTLOADER

static void miataBoardInitHardware() {
	initWidebandUartFlash();
}

static void miataBoardTsCommand(uint16_t /*subsystem*/, uint16_t index) {
	if (index == MIATA_TS_WBO_UART_FLASH) {
		startWidebandUartFlash();
	} else if (index == MIATA_TS_PRESET_NB2_EARLY) {
		// Popular Vehicles "2001-02": the NB2 preset without ignition sense or main-relay control
		miataSelectNb2Early(true);
		setEngineType((int)engine_type_e::MAZDA_MIATA_NB2);
		miataSelectNb2Early(false);
		onApplyPreset();
	}
}

void setup_custom_board_overrides() {
	custom_board_DefaultConfiguration = miataBoardDefaultConfiguration;
	custom_board_ConfigOverrides = miataBoardConfigOverrides;
	custom_board_applyUnknownType = miataApplyYearPreset;
	custom_board_AfterTuneDefaults = miataAfterTuneDefaults;
	custom_board_getThermistorSupplyVoltage = miataGetThermistorSupplyVoltage;
	custom_board_InitHardware = miataBoardInitHardware;
	custom_board_ts_command = miataBoardTsCommand;
	custom_board_periodicSlowCallback = miataPeriodicSlowCallback;
}

#endif // EFI_BOOTLOADER

