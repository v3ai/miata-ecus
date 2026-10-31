/**
 * @file miata_board.cpp
 * @brief Board defaults, pinned board facts and the five model-year presets of the miata-ecus board.
 *
 * All five motherboards route the same daughterboard signals (OUT_INJ1, IN_HALL1, ...) to the right pins of their
 * year's harness connector, so one firmware serves every year. The year is picked in TunerStudio
 * (Popular Vehicles, see board_popular_vehicles.ini); that only changes engine facts and the few outputs whose job
 * differs between years (see miataApplyYearPreset()).
 */

#include "pch.h"

#ifndef EFI_BOOTLOADER

#include "miata_board.h"
#include "miata_pins.h"
#include "mazda_miata_1_6.h"
#include "mazda_miata_na8.h"

float miataGetThermistorSupplyVoltage(adc_channel_e channel) {
	if (channel == MIATA_IN_CLT || channel == MIATA_IN_IAT) {
		return MIATA_TEMP_SUPPLY;
	}
	return 5.0f;
}

/**
 * Facts of the PCB. Re-applied after every tune load and TunerStudio write, so they can't drift.
 */
void miataBoardConfigOverrides() {
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

	// Ignition-switch sense: only years whose harness has the wire set it (see setIgnitionSense()). With a channel
	// assigned rusEFI trusts it, and a missing wire would read "key off" and cut fuel and spark. Without one it uses
	// the battery voltage, which comes from the key-switched main relay on 1996-2002.
	engineConfiguration->ignKeyAdcChannel = EFI_ADC_NONE;
	engineConfiguration->ignKeyAdcDivider = MIATA_VBATT_DIVIDER;
}

// 1989-95: 1C (VIO); 2003-05: 4S (IG1). The ECU needs it on 2003-05 to know when to drop the main relay it holds.
static void setIgnitionSense() {
	engineConfiguration->ignKeyAdcChannel = MIATA_IN_VIGN;
}

static bool nb2Early = false;

void miataSelectNb2Early(bool early) {
	nb2Early = early;
}

/**
 * Defaults for a fresh tune, before the year preset.
 */
void miataBoardDefaultConfiguration() {
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
	// Alternator control ships OFF: the field current and its supply haven't been measured (VERIFICATION.md M5), and
	// the low-side driver is a SOT-223 part. The pin and PID are set up, so turning it on is one switch in TunerStudio
	// (Alternator control) once the field has been measured. Until then the car may not charge: watch the battery.
	engineConfiguration->alternatorControlPin = MIATA_ALT;
	engineConfiguration->isAlternatorControlEnabled = false;
	// VBATT is measured on the board's +12V rail, after the reverse diode D7 and the PTC F1, so it reads about
	// 0.3-0.4 V below the battery. A 14.0 V target therefore holds the battery near 14.3-14.4 V, inside the stock NB
	// regulator's range; lower the table if a voltmeter at the battery says otherwise.
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

	if (!nb2Early) {
		// 2003-05: the ECU holds the main relay (3H) and senses the key on 4S.
		engineConfiguration->mainRelayPin = MIATA_MAINRLY;
		setIgnitionSense();
	}
	// 2001-02: the key switches the main relay and 4S/3H are not wired, so neither is used.

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
void miataApplyYearPreset(engine_type_e engineType) {
	switch (engineType) {
	case engine_type_e::MAZDA_MIATA_NA6:
		// 1989-93: batch fire, VAF, wasted spark. The stock harness has two injectors on each of 2U and 2V. The 1989-93
		// motherboard (rev 0.6) wires two drivers to each wire: INJ1 + INJ4 to 2U, INJ2 + INJ3 to 2V. rusEFI's batch
		// mode fires each cylinder's output together with the cylinder 360 degrees away (1 with 4, 3 with 2 in the
		// 1-3-4-2 order), so each pair switches together and each driver carries one injector. 2Y/2Z (2Z is the A/T
		// unit on automatics) are not connected unless the motherboard links are moved for a sequential conversion.
		// The "cylinder" numbers below are rusEFI's output slots, not the injectors on each wire: in the car 2U feeds
		// injectors 1 and 3 and 2V feeds 2 and 4. In batch mode that doesn't matter; it only pairs the drivers.
		// This needs the rev 0.6 1989-93 motherboard: on an older one INJ3/INJ4 would drive the unused 2Y/2Z pins
		// and each 2U/2V driver would carry two injectors on its own.
		setMazdaMiataNA6();
		setIgnitionSense();
		engineConfiguration->injectionMode = IM_BATCH;
		engineConfiguration->injectionPins[0] = MIATA_INJ1;   // slot 1 -> 2U
		engineConfiguration->injectionPins[1] = MIATA_INJ2;   // slot 2 -> 2V
		engineConfiguration->injectionPins[2] = MIATA_INJ3;   // slot 3 -> 2V, paired with slot 2
		engineConfiguration->injectionPins[3] = MIATA_INJ4;   // slot 4 -> 2U, paired with slot 1
		break;
	case engine_type_e::MAZDA_MIATA_NA94:
		// 1994-95: four injector wires (2U/2V/2Y/2Z), sequential like rusEFI's own 1994 preset.
		setMazdaMiataNA94();
		setIgnitionSense();
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
void miataAfterTuneDefaults(engine_type_e) {
	miataBoardConfigOverrides();
	setMpx5700();
}

void miataPeriodicSlowCallback() {
	engine->engineState.warnings.refreshTs();
}

#endif // EFI_BOOTLOADER
