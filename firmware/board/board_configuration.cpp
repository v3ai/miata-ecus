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
#include "miata_pins.h"
#include "settings.h"
#include "tunerstudio.h"
#include "pin_repository.h"
#include "io_pins.h"

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

// The eight low-side drivers (injectors, idle, VVT, boost, alternator) sit behind a level shifter whose output enable
// is pulled up on the board: they stay off through reset, boot, the bootloader and DFU. The firmware releases them
// only once the engine controller has configured every output (a few slow ticks after start), takes them off again
// for the whole of any configuration change, and never enables them during a fatal error.
//
// MIATA_DRV_EN is open drain with inverted logic: logical 0 (OutputPin's initial state) leaves the pin released, so
// the shifter stays disabled from the moment the pin is set up; logical 1 pulls it low and enables the drivers.
// Writes are forced, so they also apply in rusEFI's hardware QC mode.
static OutputPin driverEnable;
static int slowTicks = 0;
static volatile bool reconfiguring = false;

// The eight control lines into the shifter have no pull-downs on the MCU side (only on the driver side, which
// matters while the shifter is disabled). rusEFI's default board.h starts every pin as input with pull-down, but a
// pin rusEFI releases goes to input-with-pull-UP, which would switch that driver on. So every control pin no rusEFI
// function owns is parked as an input with pull-down: at start-up (before the drivers are enabled), after every
// configuration change (before they are enabled again), and on every slow tick as a backstop.
static const Gpio lowSideControlPins[] = {
	MIATA_INJ1, MIATA_INJ2, MIATA_INJ3, MIATA_INJ4, MIATA_IACV, MIATA_VVT, MIATA_BOOST, MIATA_ALT,
};

static void parkUnusedLowSideInputs() {
	for (Gpio pin : lowSideControlPins) {
		if (getPinFunction(pin) == nullptr) {
			palSetPadMode(getHwPort("low side", pin), getHwPin("low side", pin), PAL_MODE_INPUT_PULLDOWN);
		}
	}
}

static void setDriversEnabled(bool enabled) {
	driverEnable.setValue(enabled ? 1 : 0, /*isForce*/ true);
}

static void miataBoardInitHardware() {
	parkUnusedLowSideInputs();
	driverEnable.initPin("Low-side enable", MIATA_DRV_EN, OM_OPENDRAIN_INVERTED);   // starts released: disabled
	setDriversEnabled(false);
	initWidebandUartFlash();
}

// Stop phase of a configuration change: rusEFI is about to release and re-start its pins. Disable the drivers
// first, so a released control pin (pulled up for a moment) can't switch one on.
static void miataBoardStopHardware() {
	reconfiguring = true;
	setDriversEnabled(false);
}

// Straight after rusEFI has re-started its pins: park whatever is now unused; the next slow tick enables again.
static void miataBoardOnConfigurationChange(const engine_configuration_s* /*previousConfiguration*/) {
	parkUnusedLowSideInputs();
	reconfiguring = false;
}

static void miataBoardSlowCallback() {
	miataPeriodicSlowCallback();
	if (reconfiguring) {
		return;
	}
	parkUnusedLowSideInputs();
	if (slowTicks < 4) {
		slowTicks++;
		return;
	}
	setDriversEnabled(!hasFirmwareError());
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
	custom_board_periodicSlowCallback = miataBoardSlowCallback;
	custom_board_OnConfigurationChange = miataBoardOnConfigurationChange;
	custom_board_StopHardware = miataBoardStopHardware;
}

#endif // EFI_BOOTLOADER

