/**
 * @file board_configuration.cpp
 * @brief rusEFI board definition for the miata-ecus daughterboard (STM32F407VGT6) on any of its motherboards.
 *
 * All five motherboards route the same daughterboard signals (OUT_INJ1, IN_HALL1, ...) to the right pins of their
 * year's harness connector, so one firmware serves every year. The year is picked in TunerStudio
 * (Popular Vehicles, see board_popular_vehicles.ini); that only changes engine facts and the few outputs whose job
 * differs between years (see applyYearPreset()).
 *
 * The pin map below must match scripts/design.py ("mcu" dict); firmware/tools/check_pins.py cross-checks the two.
 */

#include "pch.h"
#include "board_overrides.h"
#include "wideband_uart_flash.h"

#ifndef EFI_BOOTLOADER
#include "mazda_miata_1_6.h"
#include "mazda_miata_na8.h"
#endif

// ---------------------------------------------------------------------------------------------------------------
// Pin map (daughterboard rev 0.4)
// ---------------------------------------------------------------------------------------------------------------
// Ignition: TC4427 5 V push-pull drivers, active high. The stock harness only has IGN1 (coil pack 1&4) and IGN2 (2&3).
#define MIATA_IGN1 Gpio::E1
#define MIATA_IGN2 Gpio::E0
#define MIATA_IGN3 Gpio::B9
#define MIATA_IGN4 Gpio::B8
// AUIPS2041L protected low sides, active high (10k pull-downs keep them off in reset).
#define MIATA_INJ1 Gpio::B7
#define MIATA_INJ2 Gpio::B6
#define MIATA_INJ3 Gpio::B5
#define MIATA_INJ4 Gpio::B4
#define MIATA_IACV Gpio::B3
#define MIATA_VVT Gpio::D7    // NB2 OCV; 1996-97 and NB1 front O2 heater; 1989-93 purge
#define MIATA_BOOST Gpio::D6  // AUX header only
#define MIATA_ALT Gpio::D5    // NB alternator field; 1994-95 pressure regulator solenoid
// ULN2003 relay / lamp drivers, active high.
#define MIATA_FP Gpio::C14
#define MIATA_MAINRLY Gpio::C13 // NB2 (2003-05) main relay; NB1 VICS solenoid
#define MIATA_AC Gpio::E6
#define MIATA_FAN Gpio::E5
#define MIATA_CEL Gpio::E4
#define MIATA_TACH Gpio::E3
#define MIATA_LS7 Gpio::E2      // second fan / condenser fan relay
// Digital inputs.
#define MIATA_HALL1 Gpio::E7    // crank (NA: CAS SGT, NB: CKP), 1k pull-up to 5 V on the board
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

static float miataGetThermistorSupplyVoltage(adc_channel_e channel) {
	if (channel == MIATA_IN_CLT || channel == MIATA_IN_IAT) {
		return MIATA_TEMP_SUPPLY;
	}
	return 5.0f;
}

/**
 * Facts of the PCB. Re-applied after every tune load and TunerStudio write, so they can't drift.
 */
static void miataBoardConfigOverrides() {
	engineConfiguration->adcVcc = 3.3f;
	engineConfiguration->analogInputDividerCoefficient = MIATA_ANALOG_DIVIDER;
	engineConfiguration->vbattAdcChannel = MIATA_IN_VBATT;
	engineConfiguration->vbattDividerCoeff = MIATA_VBATT_DIVIDER;

	engineConfiguration->clt.adcChannel = MIATA_IN_CLT;
	engineConfiguration->iat.adcChannel = MIATA_IN_IAT;
	engineConfiguration->clt.config.bias_resistor = MIATA_TEMP_BIAS;
	engineConfiguration->iat.config.bias_resistor = MIATA_TEMP_BIAS;

	// The only CAN bus: CAN2 on PB12/PB13 (SN65HVD230). The on-board wideband sits on the same bus.
	engineConfiguration->canTxPin = Gpio::Unassigned;
	engineConfiguration->canRxPin = Gpio::Unassigned;
	engineConfiguration->can2TxPin = Gpio::B13;
	engineConfiguration->can2RxPin = Gpio::B12;
	engineConfiguration->widebandOnSecondBus = true;
}

/**
 * MPX5700AP on the motherboard: Vout = 5 V x (0.0012858 x P[kPa] + 0.04), so 0.2 V at 0 kPa and 4.70 V at 700 kPa.
 */
static void setMpx5700() {
	engineConfiguration->map.sensor.type = MT_CUSTOM;
	engineConfiguration->map.sensor.hwChannel = MIATA_IN_MAP;
	engineConfiguration->mapLowValueVoltage = 0.2f;
	engineConfiguration->map.sensor.lowValue = 0;
	engineConfiguration->mapHighValueVoltage = 4.70f;
	engineConfiguration->map.sensor.highValue = 700;
}

static void setOutputs() {
	// Wasted spark uses ignitionPins[0] (cylinders 1&4) and [2] (2&3); [1] and [3] are for a coil-on-plug conversion.
	engineConfiguration->ignitionPins[0] = MIATA_IGN1;
	engineConfiguration->ignitionPins[1] = MIATA_IGN3;
	engineConfiguration->ignitionPins[2] = MIATA_IGN2;
	engineConfiguration->ignitionPins[3] = MIATA_IGN4;

	// In batch mode rusEFI fires each injector with its 360-degree twin, so on the 1989-95 harness (INJ1 and INJ2
	// wired, two injectors each) both groups fire once per revolution. INJ3/INJ4 are for a sequential conversion.
	engineConfiguration->injectionPins[0] = MIATA_INJ1;
	engineConfiguration->injectionPins[1] = MIATA_INJ2;
	engineConfiguration->injectionPins[2] = MIATA_INJ3;
	engineConfiguration->injectionPins[3] = MIATA_INJ4;

	engineConfiguration->idle.solenoidPin = MIATA_IACV;
	engineConfiguration->fuelPumpPin = MIATA_FP;
	engineConfiguration->acRelayPin = MIATA_AC;
	engineConfiguration->fanPin = MIATA_FAN;
	engineConfiguration->fan2Pin = MIATA_LS7;
	engineConfiguration->malfunctionIndicatorPin = MIATA_CEL;
	engineConfiguration->tachOutputPin = MIATA_TACH;
	engineConfiguration->boostControlPin = MIATA_BOOST;

	// Year-specific, set by applyYearPreset().
	engineConfiguration->mainRelayPin = Gpio::Unassigned;
	engineConfiguration->alternatorControlPin = Gpio::Unassigned;
	engineConfiguration->vvtPins[0] = Gpio::Unassigned;
	engineConfiguration->o2heaterPin = Gpio::Unassigned;
}

static void setInputs() {
	// NA (TT_MAZDA_MIATA_NA): the primary channel is the 2-pulse cam signal SGC, the secondary the 4-pulse SGT.
	engineConfiguration->triggerInputPins[0] = MIATA_HALL2;
	engineConfiguration->triggerInputPins[1] = MIATA_HALL1;
	engineConfiguration->camInputs[0] = Gpio::Unassigned;

	engineConfiguration->vehicleSpeedSensorInputPin = MIATA_SW1;
	engineConfiguration->acSwitch = MIATA_SW2;
	engineConfiguration->clutchDownPin = MIATA_SW3;

	engineConfiguration->tps1_1AdcChannel = MIATA_IN_TPS;
	engineConfiguration->tps1_2AdcChannel = EFI_ADC_NONE;
	engineConfiguration->mafAdcChannel = MIATA_IN_AUX3;
	// Used only if the CAN wideband below is switched off.
	engineConfiguration->afr.hwChannel = MIATA_IN_AFR;

	engineConfiguration->ignKeyAdcChannel = MIATA_IN_VIGN;
	engineConfiguration->ignKeyAdcDivider = MIATA_VBATT_DIVIDER;
}

/**
 * Defaults for a fresh tune, before the year preset.
 */
static void miataBoardDefaultConfiguration() {
	setOutputs();
	setInputs();

	// On-board FOME/rusEFI wideband, CAN index 0.
	engineConfiguration->canReadEnabled = true;
	engineConfiguration->canWriteEnabled = true;
	engineConfiguration->enableAemXSeries = true;

	engineConfiguration->cylindersCount = 4;
	engineConfiguration->firingOrder = FO_1_3_4_2;
}

// --- NB (1999-2005). rusEFI's own NB presets are built for Hellen boards only, so the engine facts are repeated
// here (values from rusEFI's config/engines/mazda/mazda_miata_vvt.cpp). The VE/ignition tables stay at rusEFI's
// defaults: start from a base map for your car.
static void setMiataNbCommon() {
	engineConfiguration->displacement = 1.839;
	engineConfiguration->cylindersCount = 4;
	engineConfiguration->firingOrder = FO_1_3_4_2;
	engineConfiguration->cylinderBore = 83;
	engineConfiguration->rpmHardLimit = 7200;
	strcpy(engineConfiguration->engineMake, ENGINE_MAKE_MAZDA);

	engineConfiguration->injectionMode = IM_SEQUENTIAL;
	engineConfiguration->ignitionMode = IM_WASTED_SPARK;

	// Crank on HALL1, cam on HALL2.
	engineConfiguration->trigger.type = trigger_type_e::TT_MIATA_VVT;
	engineConfiguration->triggerInputPins[0] = MIATA_HALL1;
	engineConfiguration->triggerInputPins[1] = Gpio::Unassigned;
	engineConfiguration->camInputs[0] = MIATA_HALL2;
	engineConfiguration->vvtMode[0] = VVT_MIATA_NB;
	engineConfiguration->vvtOffsets[0] = 98;

	engineConfiguration->cranking.rpm = 400;
	engineConfiguration->ignitionDwellForCrankingMs = 4;

	engineConfiguration->idleMode = idle_mode_e::IM_AUTO;
	engineConfiguration->useIdleTimingPidControl = true;
	engineConfiguration->idlePidRpmUpperLimit = 350;
	engineConfiguration->idlePidRpmDeadZone = 100;
	engineConfiguration->iacByTpsTaper = 6;
	engineConfiguration->acIdleExtraOffset = 15;
	engineConfiguration->idleRpmPid.pFactor = 0.0065;
	engineConfiguration->idleRpmPid.iFactor = 0.3;
	engineConfiguration->idleRpmPid.dFactor = 0.002;
	engineConfiguration->idleRpmPid.minValue = -8;
	engineConfiguration->idleRpmPid.maxValue = 10;
	engineConfiguration->idlerpmpid_iTermMin = -15;
	engineConfiguration->idlerpmpid_iTermMax = 30;

	engineConfiguration->fan1AcMode = fan_ac_mode_e::Relay;
	engineConfiguration->tachPulsePerRev = 2;

	// The NB charging system is regulated by the engine computer through the alternator field (ALT output).
	engineConfiguration->alternatorControlPin = MIATA_ALT;
	engineConfiguration->isAlternatorControlEnabled = true;
	setTable(config->alternatorVoltageTargetTable, 14.0f);
	engineConfiguration->alternatorControl.offset = 20;
	engineConfiguration->alternatorControl.pFactor = 16;
	engineConfiguration->alternatorControl.iFactor = 8;
	engineConfiguration->alternatorControl.dFactor = 0.1;
	engineConfiguration->alternatorControl.periodMs = 10;

	setCommonNTCSensorParameters(&engineConfiguration->clt);
	setCommonNTCSensorParameters(&engineConfiguration->iat);

	// Knock sensor on IN_KNOCK (PA3, ADC3).
	engineConfiguration->enableSoftwareKnock = true;

	// Speedo gear matched to the diff: 1.12 sensor turns per wheel turn, 4 pulses per turn.
	engineConfiguration->vssGearRatio = 3.909 * 6 / 21;
	engineConfiguration->vssToothCount = 4;
}

static void setMiataNb1() {
	setMiataNbCommon();
	strcpy(engineConfiguration->engineCode, "NB1");
	engineConfiguration->injector.flow = 256;
	// No VVT on the NB1: the VVT driver runs the front O2 sensor heater (harness pin 1U).
	engineConfiguration->o2heaterPin = MIATA_VVT;
	// MAINRLY drives the VICS solenoid (3Q); rusEFI has no VICS strategy, so set it up as a GPPWM output if wanted.
}

static void setMiataNb2() {
	setMiataNbCommon();
	strcpy(engineConfiguration->engineCode, "NB2");
	engineConfiguration->injector.flow = 265;
	engineConfiguration->fuelReferencePressure = 400; // returnless system, 58 psi
	engineConfiguration->injectorCompensationMode = ICM_FixedRailPressure;

	// Main relay control (pin 3H, 2003-05; not connected on 2001-02).
	engineConfiguration->mainRelayPin = MIATA_MAINRLY;

	// VVT oil control valve (pin 4R). The target table starts at rusEFI's default: fill in vvtTable1.
	engineConfiguration->vvtPins[0] = MIATA_VVT;
	engineConfiguration->auxPid[0].pFactor = 2;
	engineConfiguration->auxPid[0].iFactor = 0.005;
	engineConfiguration->auxPid[0].dFactor = 0.002;
	engineConfiguration->auxPid[0].offset = 33;
	engineConfiguration->auxPid[0].minValue = 20;
	engineConfiguration->auxPid[0].maxValue = 90;
}

/**
 * Year presets for the engine types this board's Popular Vehicles dialog offers. rusEFI handles those types only on
 * Hellen boards, so they reach us here as "unknown".
 */
static void applyYearPreset(engine_type_e engineType) {
	switch (engineType) {
	case engine_type_e::MAZDA_MIATA_NA6:
		// 1989-93: batch fire on INJ1/INJ2, VAF, wasted spark.
		setMazdaMiataNA6();
		break;
	case engine_type_e::MAZDA_MIATA_NA94:
		// 1994-95: rusEFI's preset assumes sequential injectors, but this harness has two batch groups.
		setMazdaMiataNA94();
		engineConfiguration->injectionMode = IM_BATCH;
		break;
	case engine_type_e::MAZDA_MIATA_NA96:
		// 1996-97: sequential; the VVT driver runs the front O2 heater (harness pin 3M).
		setMazdaMiata96();
		engineConfiguration->o2heaterPin = MIATA_VVT;
		break;
	case engine_type_e::MAZDA_MIATA_NB1:
		setMiataNb1();
		break;
	case engine_type_e::MAZDA_MIATA_NB2:
		setMiataNb2();
		break;
	default:
		firmwareError(ObdCode::CUSTOM_UNEXPECTED_ENGINE_TYPE, "Engine type %d is not set up for the miata-ecu board", (int)engineType);
		break;
	}
}

/**
 * Runs after every engine preset: put back the facts a preset may have overwritten.
 */
static void miataAfterTuneDefaults(engine_type_e) {
	miataBoardConfigOverrides();
	setMpx5700();
}

static void miataBoardInitHardware() {
	initWidebandUartFlash();
}

static void miataBoardTsCommand(uint16_t /*subsystem*/, uint16_t index) {
	if (index == MIATA_TS_WBO_UART_FLASH) {
		startWidebandUartFlash();
	}
}

void setup_custom_board_overrides() {
	custom_board_DefaultConfiguration = miataBoardDefaultConfiguration;
	custom_board_ConfigOverrides = miataBoardConfigOverrides;
	custom_board_applyUnknownType = applyYearPreset;
	custom_board_AfterTuneDefaults = miataAfterTuneDefaults;
	custom_board_getThermistorSupplyVoltage = miataGetThermistorSupplyVoltage;
	custom_board_InitHardware = miataBoardInitHardware;
	custom_board_ts_command = miataBoardTsCommand;
}

#endif // EFI_BOOTLOADER
