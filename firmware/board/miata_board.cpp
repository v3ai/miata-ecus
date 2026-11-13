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

	// The only CAN bus: the STM32's CAN2 peripheral on PB12/PB13 (SN65HVD230), set up as rusEFI's FIRST bus.
	// rusEFI picks the CAN peripheral from the pins, so PB12/PB13 on bus 1 runs on CAN2. Everything rusEFI sends on
	// its first bus by default (the extended CAN broadcast it enables in every fresh tune, dashboard broadcasts, the
	// wideband) then goes out on the one bus that is wired. With the pins on rusEFI's second bus instead, the first
	// broadcast hit an unconfigured bus 1 and raised a critical error ("Send: CAN1 device not configured"), which
	// stops fuel and spark: found by the firmware-in-the-loop run (firmware/sim).
	engineConfiguration->canTxPin = Gpio::B13;
	engineConfiguration->canRxPin = Gpio::B12;
	engineConfiguration->can2TxPin = Gpio::Unassigned;
	engineConfiguration->can2RxPin = Gpio::Unassigned;
	engineConfiguration->widebandOnSecondBus = false;

	// microSD socket (rev 0.10) on SPI2. On a rev 0.9 board these four pins are not connected: rusEFI finds no card
	// and carries on.
	engineConfiguration->is_enabled_spi_2 = true;
	engineConfiguration->spi2sckPin = MIATA_SD_SCK;
	engineConfiguration->spi2misoPin = MIATA_SD_MISO;
	engineConfiguration->spi2mosiPin = MIATA_SD_MOSI;
	engineConfiguration->sdCardSpiDevice = SPI_DEVICE_2;
	engineConfiguration->sdCardCsPin = MIATA_SD_CS;
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
	// No analog AFR input by default: the on-board wideband reports over CAN (enableAemXSeries below), and rusEFI
	// refuses to run with both ("Please pick either analog AFR or CAN AFR input not both" is a critical error,
	// found by the firmware-in-the-loop run). For an external 0-5 V wideband on the AUX header, set the AFR input
	// to MIATA_IN_AFR (PC4) in TunerStudio and turn the CAN wideband off.
	engineConfiguration->afr.hwChannel = EFI_ADC_NONE;

	// Ignition-switch sense: only years whose harness has the wire set it (see setIgnitionSense()). With a channel
	// assigned rusEFI trusts it, and a missing wire would read "key off" and cut fuel and spark. Without one it uses
	// the battery voltage, which comes from the key-switched main relay on 1989-2002.
	engineConfiguration->ignKeyAdcChannel = EFI_ADC_NONE;
	engineConfiguration->ignKeyAdcDivider = MIATA_VBATT_DIVIDER;
}

// 2003-05 only: 4S (IG1). The ECU needs it there to know when to drop the main relay it holds.
// Not 1989-95: their 1C is the starter (START) signal, live only while cranking (Link's MX5 pinout: "Start Signal").
// As ignition sense it would read "key off" as soon as the key springs back from START, and rusEFI would cut fuel and
// spark. The key-switched main relay on 1B already tells the ECU the key is on.
static void setIgnitionSense() {
	engineConfiguration->ignKeyAdcChannel = MIATA_IN_VIGN;
}

// 1989-95: harness cavity 2I is the igniter's signal INTO the ECU; the igniter drives the tachometer itself (the 1990-93
// coil-on-plug conversion notes and rusEFI's 1994 pinout both show 2I as an input). An ECU tach output on that wire
// would fight the igniter, so the output is left unassigned. After a coil-on-plug conversion with the igniter removed,
// fit JP5 on the rev 0.12 motherboard and set the tach output to "Tach (J1-11)" in TunerStudio.
static void miataNoTachOutput() {
	engineConfiguration->tachOutputPin = Gpio::Unassigned;
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

	// Closed-loop fuel from the on-board wideband, on by default: every board has the sensor input, and the base
	// tables were tuned on other cars, so let the ECU trim towards the target lambda once the engine is warm
	// (rusEFI's defaults: after 60 s, coolant above 60 C, AFR 12-17). Idle and cruise may move 10 % either way.
	// Under load it may add 10 % but remove only 5 %: a sensor that wrongly reads rich must not lean a loaded
	// engine out. With no sensor fitted there is no reading and no correction. A fresh tune only: turn "Short term
	// fuel trim" off in TunerStudio and it stays off.
	engineConfiguration->fuelClosedLoopCorrectionEnabled = true;
	for (int region : { ftRegionIdle, ftRegionCruise, ftRegionPower }) {
		engineConfiguration->stft.cellCfgs[region].maxAdd = 10;
		engineConfiguration->stft.cellCfgs[region].maxRemove = region == ftRegionPower ? 5 : 10;
	}

	engineConfiguration->cylindersCount = 4;
	engineConfiguration->firingOrder = FO_1_3_4_2;

	// Log to the microSD card when one is fitted (rev 0.10). A fresh tune only.
	engineConfiguration->isSdCardEnabled = true;
	// Flex fuel and nitrous ship off, with no pins assigned: an assigned flex input with no sensor on it reads as a
	// failed sensor. To use them, pick "Flex input (J2-24)" as the flex sensor pin, or "Nitrous arm (J2-25)" as the
	// nitrous trigger and a spare output (boost, second fan) as the nitrous relay, in TunerStudio.
	engineConfiguration->flexSensorPin = Gpio::Unassigned;
	engineConfiguration->nitrousControlEnabled = false;
}

// --- NB (1999-2005). rusEFI's own NB presets are built for Hellen boards only, so the engine facts are repeated
// here (values from rusEFI's config/engines/mazda/mazda_miata_vvt.cpp), and its NB base tables (VE, ignition,
// injector lag, cranking, idle, VVT target) are loaded by miataSetNbBaseTune() in miata_nb_tune.cpp.
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

	// The NB charging voltage is set by the engine computer: harness pin 1O (NB1) / 3M (NB2) is a logic-level PWM
	// input to the regulator inside the alternator, not the field coil itself (a scope on a stock 1999 ECU showed
	// 250 Hz; working MS3 / ECUMaster set-ups drive it from a low side with a 1k pull-up to 5 V, about 5 mA).
	// Alternator control ships OFF until a car has been checked (VERIFICATION.md M5): with the ECU unplugged and the
	// key on, the wire either already sits high (the alternator pulls it up: just turn on "Alternator control") or
	// near 0 V (then fit 1k + 1N4148 from AUX J5-14, 5 V, to J5-4, OUT_ALT first). The pin and PID are set up.
	engineConfiguration->alternatorControlPin = MIATA_ALT;
	engineConfiguration->alternatorPwmFrequency = 250;   // as the stock ECU
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
	miataSetNbBaseTune(false);
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
	miataSetNbBaseTune(true);

	if (!nb2Early) {
		// 2003-05: the ECU holds the main relay (3H) and senses the key on 4S.
		engineConfiguration->mainRelayPin = MIATA_MAINRLY;
		setIgnitionSense();
	}
	// 2001-02: the key switches the main relay and 4S/3H are not wired, so neither is used.

	// VVT oil control valve (pin 4R). The target table is rusEFI's NB2 table (miataSetNbBaseTune).
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
		miataNoTachOutput();
		engineConfiguration->injectionMode = IM_BATCH;
		engineConfiguration->injectionPins[0] = MIATA_INJ1;   // slot 1 -> 2U
		engineConfiguration->injectionPins[1] = MIATA_INJ2;   // slot 2 -> 2V
		engineConfiguration->injectionPins[2] = MIATA_INJ3;   // slot 3 -> 2V, paired with slot 2
		engineConfiguration->injectionPins[3] = MIATA_INJ4;   // slot 4 -> 2U, paired with slot 1
		break;
	case engine_type_e::MAZDA_MIATA_NA94:
		// 1994-95: four injector wires (2U/2V/2Y/2Z), sequential like rusEFI's own 1994 preset.
		setMazdaMiataNA94();
		miataNoTachOutput();
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
