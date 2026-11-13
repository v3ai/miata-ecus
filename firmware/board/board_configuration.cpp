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

// Rev 0.8: comms and warning moved from PD13/PD14 to PC8/PC9 (routing).
Gpio getCommsLedPin() {
	return Gpio::C8;
}

Gpio getWarningLedPin() {
	return Gpio::C9;
}

#ifndef EFI_BOOTLOADER

// The fifteen low-side drivers (injectors, idle, VVT, boost, alternator, and since rev 0.8 the relay, lamp and tach
// outputs) sit behind two level shifters whose shared output enable is pulled up on the board: they stay off through reset, boot, the bootloader and DFU. The firmware releases them
// only once the engine controller has configured every output (a few slow ticks after start), takes them off again
// while rusEFI re-applies its pins during a configuration change (every Burn), and never enables them during a fatal
// error.
//
// MIATA_DRV_EN is open drain with inverted logic: logical 0 (OutputPin's initial state) leaves the pin released, so
// the shifter stays disabled from the moment the pin is set up; logical 1 pulls it low and enables the drivers.
// Writes are forced, so they also apply in rusEFI's hardware QC mode.
static OutputPin driverEnable;
static int slowTicks = 0;
static volatile bool reconfiguring = false;

// The fifteen control lines into the shifters have no pull-downs on the MCU side (only on the driver side, which
// matters while the shifter is disabled). rusEFI's default board.h starts every pin as input with pull-down, but a
// pin rusEFI releases goes to input-with-pull-UP, which would switch that driver on. So every control pin no rusEFI
// function owns is parked as an input with pull-down: at start-up (before the drivers are enabled), after every
// configuration change (before they are enabled again), and on every slow tick as a backstop.
static const Gpio lowSideControlPins[] = {
	MIATA_INJ1, MIATA_INJ2, MIATA_INJ3, MIATA_INJ4, MIATA_IACV, MIATA_VVT, MIATA_BOOST, MIATA_ALT,
	// rev 0.8: the relay / lamp / tach outputs moved from a ULN2003 to ZXMS6004 drivers behind U12
	MIATA_FP, MIATA_MAINRLY, MIATA_AC, MIATA_FAN, MIATA_CEL, MIATA_TACH, MIATA_LS7,
};

// Only pins not already parked are touched, so the slow-tick backstop writes nothing in normal running. The mode
// registers are shared read-modify-write with the port's other pins (the ignition outputs sit on port E with five of
// these lines), so a change is made with interrupts locked.
static void parkUnusedLowSideInputs() {
	for (Gpio pin : lowSideControlPins) {
		if (getPinFunction(pin) != nullptr) {
			continue;
		}
		if (pin == MIATA_CEL && hasFirmwareError()) {
			continue;                              // held on by lightCelOnFatalError()
		}
		ioportid_t port = getHwPort("low side", pin);
		int bit = getHwPin("low side", pin);
		uint32_t mode = (port->MODER >> (bit * 2)) & 3U;
		uint32_t pull = (port->PUPDR >> (bit * 2)) & 3U;
		if (mode == 0U && pull == 2U) {          // input, pull-down: already parked
			continue;
		}
		chSysLock();
		palSetPadMode(port, bit, PAL_MODE_INPUT_PULLDOWN);
		chSysUnlock();
	}
}

// rev 0.10: the check-engine lamp driver takes its gate straight from the processor pin, outside the shared driver
// enable, so the lamp can be lit when the drivers are held off after a fatal error. rusEFI switches every output off
// in that state, so the pin is driven here directly. On a rev 0.9 board the lamp is behind the enable and stays dark.
static void lightCelOnFatalError() {
	ioportid_t port = getHwPort("CEL", MIATA_CEL);
	int bit = getHwPin("CEL", MIATA_CEL);
	chSysLock();
	palSetPadMode(port, bit, PAL_MODE_OUTPUT_PUSHPULL);
	palSetPad(port, bit);
	chSysUnlock();
}

static void setDriversEnabled(bool enabled) {
	driverEnable.setValue(enabled ? 1 : 0, /*isForce*/ true);
}

// PC14 (MIATA_FP) is also the LSE oscillator's input pin, and the oscillator owns it whenever RCC_BDCR.LSEON is set,
// whatever the GPIO mode. board/mcuconf.h keeps ChibiOS from setting the bit, but the backup domain survives a
// reset, so a bootloader or firmware built without it may have left it set: clear it before any output is used.
static void releaseLsePins() {
	PWR->CR |= PWR_CR_DBP;           // backup-domain write access (ChibiOS leaves it open anyway)
	RCC->BDCR &= ~RCC_BDCR_LSEON;    // no 32 kHz crystal on this board
}

static void miataBoardInitHardware() {
	releaseLsePins();
	parkUnusedLowSideInputs();
	driverEnable.initPin("Low-side enable", MIATA_DRV_EN, OM_OPENDRAIN_INVERTED);   // starts released: disabled
	setDriversEnabled(false);
	initWidebandUartFlash();
}

// Stop phase of a configuration change (every Burn): rusEFI is about to release the pins whose setting changed and
// re-start them. Disable the drivers first, so a released control pin (pulled up for a moment) can't switch one on.
static void miataBoardStopHardware() {
	reconfiguring = true;
	setDriversEnabled(false);
}

// Straight after rusEFI has re-started its pins (same call): park whatever is now unused and enable the drivers again
// at once, so a Burn with the engine running drops the outputs only for the re-configuration itself (it used
// to wait for the next slow tick, up to 50 ms without injectors, pump or the 2003-05 main relay). Not before the
// start-up delay has run, and never during a fatal error.
static void miataBoardOnConfigurationChange(const engine_configuration_s* /*previousConfiguration*/) {
	parkUnusedLowSideInputs();
	reconfiguring = false;
	if (slowTicks >= 4) {
		setDriversEnabled(!hasFirmwareError());
	}
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
	if (hasFirmwareError()) {
		lightCelOnFatalError();
	}
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

