/**
 * @file test_miata_ecu.cpp
 * @brief Engine simulation of the miata-ecus board for every model year, inside rusEFI's own unit-test engine.
 *
 * The tests build the tune exactly as the real board does (rusEFI defaults -> miataBoardDefaultConfiguration ->
 * miataBoardConfigOverrides -> year preset through the "unknown engine type" hook -> miataAfterTuneDefaults), feed
 * crank/cam signals, and record every edge on every output pin, keyed by the STM32 pin it is wired to.
 *
 * Signals:
 *  - real logic-analyser captures that ship with rusEFI (NA CAS cranking, NB2 crank+cam cranking);
 *  - steady running at several speeds: NA from rusEFI's TT_MAZDA_MIATA_NA wheel, NB from one 720-degree cycle of
 *    crank and cam edges extracted from the NB2 capture (11 cycles averaged, see NB_CYCLE).
 *
 * Each run prints "MIATA|..." lines that firmware/tools/sim_report.py turns into the end-to-end harness check.
 */

#include "pch.h"

#include "miata_board.h"
#include "miata_pins.h"
#include "board_overrides.h"
#include "logicdata_csv_reader.h"
#include "trigger_emulator_algo.h"
#include "trigger_central.h"
#include "engine_math.h"
#include "malfunction_central.h"

#include <cmath>
#include <map>
#include <string>
#include <vector>

using ::testing::_;
using ::testing::Return;

namespace {

engine_type_e g_year;
bool g_knockRequested;

// rusEFI's unit-test build has no software knock (the board build enables it in board.mk), and rusEFI refuses a tune
// asking for it there. Record what the preset asked for, then switch it off for the simulation only.
void afterTuneHook(engine_type_e t) {
	miataAfterTuneDefaults(t);
	g_knockRequested = engineConfiguration->enableSoftwareKnock;
	engineConfiguration->enableSoftwareKnock = false;
}

// Gpio::A0 = 2, then 16 pins per port
std::string pinName(Gpio pin) {
	int v = static_cast<int>(pin);
	if (v < 2) {
		return "-";
	}
	return std::string("P") + char('A' + (v - 2) / 16) + std::to_string((v - 2) % 16);
}

void applyYearHook(engine_type_e) {
	miataApplyYearPreset(g_year);
}

// On the real board resetConfigurationExt() calls DefaultConfiguration then ConfigOverrides (EFI_PROD_CODE only);
// the unit-test build runs this callback at that same point instead.
void boardCallback(engine_configuration_s*) {
	miataBoardDefaultConfiguration();
	miataBoardConfigOverrides();
}

engine_type_e installMiataHooks(engine_type_e year) {
	g_year = year;
	custom_board_applyUnknownType = applyYearHook;
	custom_board_AfterTuneDefaults = afterTuneHook;
	custom_board_getThermistorSupplyVoltage = miataGetThermistorSupplyVoltage;
	custom_board_ConfigOverrides = miataBoardConfigOverrides;
	custom_board_periodicSlowCallback = miataPeriodicSlowCallback;
	// Out of range, so applyEngineType() takes its default: branch into custom_board_applyUnknownType - exactly the
	// path MAZDA_MIATA_* take on this board in production (rusEFI handles them only on Hellen boards; the unit-test
	// build defines HW_HELLEN, so passing them directly would run the Hellen presets instead of ours).
	return static_cast<engine_type_e>(200);
}

struct HookReset {
	~HookReset() {
		custom_board_applyUnknownType.reset();
		custom_board_AfterTuneDefaults.reset();
		custom_board_getThermistorSupplyVoltage.reset();
		custom_board_ConfigOverrides.reset();
		custom_board_periodicSlowCallback.reset();
	}
};

const char* yearName(engine_type_e t) {
	switch (t) {
	case engine_type_e::MAZDA_MIATA_NA6: return "1989-93";
	case engine_type_e::MAZDA_MIATA_NA94: return "1994-95";
	case engine_type_e::MAZDA_MIATA_NA96: return "1996-97";
	case engine_type_e::MAZDA_MIATA_NB1: return "1999-2000";
	case engine_type_e::MAZDA_MIATA_NB2: return "2001-05";
	default: return "?";
	}
}

bool isNb(engine_type_e t) {
	return t == engine_type_e::MAZDA_MIATA_NB1 || t == engine_type_e::MAZDA_MIATA_NB2;
}

class MiataEcu {
public:
	HookReset hookReset; // declared first: destroyed after eth
	EngineTestHelper eth;

	explicit MiataEcu(engine_type_e year) : eth(installMiataHooks(year), boardCallback) {
		engineConfiguration->engineType = year;
		// Load: unit tests replace the airmass model with a mock. 0.2 g/cyl ~ light cruise on a 1.8.
		EXPECT_CALL(*eth.mockAirmass, getAirmass(_, _)).WillRepeatedly(Return(AirmassResult{0.2f, 50.0f}));
		Sensor::setMockValue(SensorType::BatteryVoltage, 13.8);
		Sensor::setMockValue(SensorType::Clt, 85);
		Sensor::setMockValue(SensorType::Iat, 25);
		Sensor::setMockValue(SensorType::Tps1, 10);
		Sensor::setMockValue(SensorType::Map, 50);
	}
};

// ---- output recorder ---------------------------------------------------------------------------------------------

struct Edge {
	double tUs;
	bool on;
	float angle; // engine angle after TDC #1, NaN if not known yet
};

struct Probe {
	std::string name;
	OutputPin* pin;
	int last = 0;
	std::vector<Edge> edges;
};

float engineAngleNow() {
	auto phase = engine->triggerCentral.getCurrentEnginePhase(getTimeNowNt());
	if (!phase) {
		return NAN;
	}
	float a = phase.Value - tdcPosition();
	a = std::fmod(a, 720.0f);
	if (a < 0) {
		a += 720;
	}
	return a;
}

class Recorder {
public:
	std::vector<Probe> probes;

	Recorder() {
		for (int i = 0; i < 4; i++) {
			add("coil" + std::to_string(i + 1), &enginePins.coils[i]);
			add("inj" + std::to_string(i + 1), &enginePins.injectors[i]);
		}
		add("fuelPump", &enginePins.fuelPumpRelay);
		add("tach", &enginePins.tachOut);
		add("cel", &enginePins.checkEnginePin);
		add("fan", &enginePins.fanRelay);
		add("fan2", &enginePins.fanRelay2);
		add("acRelay", &enginePins.acRelay);
		add("mainRelay", &enginePins.mainRelay);
		add("o2heater", &enginePins.o2heater);
		add("alternator", &enginePins.alternatorPin);
		add("idleValve", &enginePins.idleSolenoidPin);
	}

	void add(const std::string& name, OutputPin* pin) {
		probes.push_back(Probe{name, pin, pin->getLogicValue(), {}});
	}

	void sample() {
		double t = getTimeNowUs();
		float angle = NAN;
		bool angleDone = false;
		for (auto& p : probes) {
			int v = p.pin->getLogicValue();
			if (v != p.last) {
				if (!angleDone) {
					angle = engineAngleNow();
					angleDone = true;
				}
				p.edges.push_back(Edge{t, v != 0, angle});
				p.last = v;
			}
		}
	}

	void clear() {
		for (auto& p : probes) {
			p.edges.clear();
		}
	}

	Probe& get(const std::string& name) {
		for (auto& p : probes) {
			if (p.name == name) {
				return p;
			}
		}
		throw std::runtime_error(name);
	}
};

// Moves simulated time forward in small steps, running the periodic callbacks like the real main loop and
// sampling every output after each step.
class Clock {
public:
	EngineTestHelper& eth;
	Recorder& rec;
	double nextFastUs;
	double nextSlowUs;

	Clock(EngineTestHelper& e, Recorder& r) : eth(e), rec(r) {
		nextFastUs = getTimeNowUs();
		nextSlowUs = getTimeNowUs();
	}

	void advanceTo(double tUs, int stepUs) {
		while (getTimeNowUs() < tUs) {
			int step = (int)std::min<double>(stepUs, tUs - getTimeNowUs());
			if (step < 1) {
				step = 1;
			}
			eth.moveTimeForwardAndInvokeEventsUs(step);
			double now = getTimeNowUs();
			if (now >= nextFastUs) {
				engine->periodicFastCallback();
				nextFastUs = now + 5000;
			}
			if (now >= nextSlowUs) {
				engine->periodicSlowCallback();
				nextSlowUs = now + 50000;
			}
			rec.sample();
		}
	}
};

// ---- signal sources ----------------------------------------------------------------------------------------------

// One engine cycle of NB crank (ch 1) and cam (ch 2) edges, degrees from a crank tooth, extracted from rusEFI's
// tests/trigger/resources/nb2-cranking-good.csv (real NB2 capture, 11 steady cycles averaged; crank spread 0.1 deg,
// cam spread ~4.5 deg from cranking speed ripple).
struct NbEdge {
	float angle;
	int channel;
	int level;
};
const NbEdge NB_CYCLE[] = {
	{0.0f, 1, 1}, {66.4f, 1, 0}, {70.0f, 1, 1}, {122.2f, 2, 0}, {157.6f, 2, 1}, {176.5f, 1, 0}, {180.0f, 1, 1},
	{246.4f, 1, 0}, {250.0f, 1, 1}, {356.5f, 1, 0}, {360.0f, 1, 1}, {426.4f, 1, 0}, {430.0f, 1, 1},
	{439.0f, 2, 0}, {476.2f, 2, 1}, {498.1f, 2, 0}, {516.7f, 2, 1}, {536.5f, 1, 0}, {540.0f, 1, 1},
	{606.4f, 1, 0}, {610.0f, 1, 1}, {716.5f, 1, 0},
};

int stepFor(float rpm) {
	// about a fifth of a degree per step
	float degUs = 1e6f / (rpm * 6);
	return std::max(1, (int)(degUs / 5));
}

// Plays rusEFI's NA CAS wheel (both channels) with the speed changing linearly from rpmFrom to rpmTo.
void runNa(Clock& clock, float rpmFrom, float rpmTo, int cycles) {
	TriggerWaveform& shape = engine->triggerCentral.triggerShape;
	TriggerEmulatorHelper emulator;
	double t = getTimeNowUs();
	double prevAngle = 0;
	double total = cycles * 720.0;
	for (int c = 0; c < cycles; c++) {
		for (size_t i = 0; i < shape.getSize(); i++) {
			double angle = (c + shape.wave.getSwitchTime(i)) * 720.0;
			double rpm = rpmFrom + (rpmTo - rpmFrom) * (prevAngle + angle) / 2 / total;
			t += (angle - prevAngle) * 1e6 / (6 * rpm);
			prevAngle = angle;
			clock.advanceTo(t, stepFor(rpm));
			emulator.handleEmulatorCallback(0, shape.wave, i);
		}
	}
}

void runNa(Clock& clock, float rpm, int cycles) {
	runNa(clock, rpm, rpm, cycles);
}

// Plays the captured NB crank+cam cycle with the speed changing linearly from rpmFrom to rpmTo.
void runNb(Clock& clock, float rpmFrom, float rpmTo, int cycles, bool invert = false) {
	double t = getTimeNowUs();
	double prevAngle = 0;
	double total = cycles * 720.0;
	float rpm = rpmFrom;
	for (int c = 0; c < cycles; c++) {
		for (const auto& e : NB_CYCLE) {
			double angle = c * 720.0 + e.angle;
			rpm = rpmFrom + (rpmTo - rpmFrom) * (prevAngle + angle) / 2 / total;
			t += (angle - prevAngle) * 1e6 / (6 * rpm);
			prevAngle = angle;
			clock.advanceTo(t, stepFor(rpm));
			bool level = (e.level != 0) ^ invert;
			if (e.channel == 1) {
				hwHandleShaftSignal(0, level, getTimeNowNt());
			} else {
				hwHandleVvtCamSignal(level, getTimeNowNt(), 0);
			}
		}
	}
	// finish the last cycle
	t += (total - prevAngle) * 1e6 / (6 * rpmTo);
	clock.advanceTo(t, stepFor(rpmTo));
}

void runNb(Clock& clock, float rpm, int cycles, bool invert = false) {
	runNb(clock, rpm, rpm, cycles, invert);
}

// ---- analysis ----------------------------------------------------------------------------------------------------

float wrap720(float a) {
	a = std::fmod(a, 720.0f);
	return a < 0 ? a + 720 : a;
}

float angleDiff(float a, float b) {
	float d = wrap720(a - b);
	return d > 360 ? d - 720 : d;
}

std::vector<float> anglesOf(const Probe& p, bool on) {
	std::vector<float> out;
	for (const auto& e : p.edges) {
		if (e.on == on && !std::isnan(e.angle)) {
			out.push_back(e.angle);
		}
	}
	return out;
}

int countEdges(const Probe& p, bool on) {
	int n = 0;
	for (const auto& e : p.edges) {
		n += e.on == on;
	}
	return n;
}

// mean on-time of a pin in ms
float meanPulseMs(const Probe& p) {
	double sum = 0;
	int n = 0;
	double start = -1;
	for (const auto& e : p.edges) {
		if (e.on) {
			start = e.tUs;
		} else if (start >= 0) {
			sum += e.tUs - start;
			n++;
			start = -1;
		}
	}
	return n ? (float)(sum / n / 1000) : 0;
}

std::string probePin(const std::string& n) {
	auto idx = [&](size_t prefix) { return n[prefix] - '1'; };
	if (n.rfind("coil", 0) == 0) return pinName(engineConfiguration->ignitionPins[idx(4)]);
	if (n.rfind("inj", 0) == 0) return pinName(engineConfiguration->injectionPins[idx(3)]);
	if (n == "fuelPump") return pinName(engineConfiguration->fuelPumpPin);
	if (n == "tach") return pinName(engineConfiguration->tachOutputPin);
	if (n == "cel") return pinName(engineConfiguration->malfunctionIndicatorPin);
	if (n == "fan") return pinName(engineConfiguration->fanPin);
	if (n == "fan2") return pinName(engineConfiguration->fan2Pin);
	if (n == "acRelay") return pinName(engineConfiguration->acRelayPin);
	if (n == "mainRelay") return pinName(engineConfiguration->mainRelayPin);
	if (n == "o2heater") return pinName(engineConfiguration->o2heaterPin);
	if (n == "alternator") return pinName(engineConfiguration->alternatorControlPin);
	if (n == "idleValve") return pinName(engineConfiguration->idle.solenoidPin);
	return "?";
}

void report(const char* what, float rpm, Recorder& rec) {
	for (auto& p : rec.probes) {
		printf("MIATA|%s|%s|%.0f|%s|%s|state=%d|on=%d|off=%d|pulse_ms=%.3f|angles_on=", yearName(g_year), what, rpm,
			p.name.c_str(), probePin(p.name).c_str(), p.last, countEdges(p, true), countEdges(p, false), meanPulseMs(p));
		for (float a : anglesOf(p, true)) {
			printf("%.1f,", a);
		}
		printf("|angles_off=");
		for (float a : anglesOf(p, false)) {
			printf("%.1f,", a);
		}
		printf("\n");
	}
}

// Expected wasted-spark firing: the coil-pack outputs fire at TDC of their two cylinders minus the advance.
// Cylinder TDC angles for firing order 1-3-4-2: cyl1 0, cyl3 180, cyl4 360, cyl2 540.
void checkSparks(Recorder& rec, int cycles, float rpm) {
	float adv1 = engine->engineState.timingAdvance[0];
	auto& ign1 = rec.get("coil1"); // ignitionPins[0] = IGN1 (PE1): coil pack 1&4
	auto& ign2 = rec.get("coil3"); // ignitionPins[2] = IGN2 (PE0): coil pack 2&3
	EXPECT_EQ(MIATA_IGN1, engineConfiguration->ignitionPins[0]);
	EXPECT_EQ(MIATA_IGN2, engineConfiguration->ignitionPins[2]);
	EXPECT_EQ(2 * cycles, countEdges(ign1, false)) << "IGN1 sparks @" << rpm;
	EXPECT_EQ(2 * cycles, countEdges(ign2, false)) << "IGN2 sparks @" << rpm;
	EXPECT_EQ(0, countEdges(rec.get("coil2"), false)) << "IGN3 must stay idle in wasted spark";
	EXPECT_EQ(0, countEdges(rec.get("coil4"), false)) << "IGN4 must stay idle in wasted spark";
	for (float a : anglesOf(ign1, false)) {
		float d = std::min(std::fabs(angleDiff(a, -adv1)), std::fabs(angleDiff(a, 360 - adv1)));
		EXPECT_LT(d, 1.5f) << "IGN1 spark at " << a << " (advance " << adv1 << ") @" << rpm;
	}
	for (float a : anglesOf(ign2, false)) {
		float d = std::min(std::fabs(angleDiff(a, 180 - adv1)), std::fabs(angleDiff(a, 540 - adv1)));
		EXPECT_LT(d, 1.5f) << "IGN2 spark at " << a << " (advance " << adv1 << ") @" << rpm;
	}
}

void checkInjectors(Recorder& rec, int cycles, float rpm) {
	bool batch = engineConfiguration->injectionMode == IM_BATCH;
	auto& i1 = rec.get("inj1");
	auto& i2 = rec.get("inj2");
	auto& i3 = rec.get("inj3");
	auto& i4 = rec.get("inj4");
	float duration = engine->engineState.injectionDuration;
	if (batch) {
		// 1989-93: two groups, each opening once per crank revolution
		EXPECT_EQ(2 * cycles, countEdges(i1, true)) << "INJ1 @" << rpm;
		EXPECT_EQ(2 * cycles, countEdges(i2, true)) << "INJ2 @" << rpm;
		// rusEFI still runs the logic of injector channels 3/4, but with no pin assigned nothing reaches PB5/PB4
		// (3Y, and 3Z = A/T unit on automatics)
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->injectionPins[2]);
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->injectionPins[3]);
		// injectionDuration is per pulse; in batch mode rusEFI has already halved the fuel for the second pulse
		EXPECT_NEAR(meanPulseMs(i1), duration, 0.05);
		EXPECT_NEAR(meanPulseMs(i2), duration, 0.05);
		auto a1 = anglesOf(i1, true);
		auto a2 = anglesOf(i2, true);
		ASSERT_GE(a1.size(), 2u);
		ASSERT_GE(a2.size(), 2u);
		EXPECT_NEAR(std::fabs(angleDiff(a1[1], a1[0])), 360, 2) << "INJ1 opens every revolution";
		EXPECT_NEAR(std::fabs(angleDiff(a2[0], a1[0])), 180, 2) << "INJ2 is half a revolution from INJ1";
	} else {
		for (auto* p : {&i1, &i2, &i3, &i4}) {
			EXPECT_EQ(cycles, countEdges(*p, true)) << p->name << " once per cycle @" << rpm;
			EXPECT_NEAR(meanPulseMs(*p), duration, 0.05) << p->name;
		}
		// firing order 1-3-4-2: each injector 180 degrees after the previous one
		auto a1 = anglesOf(i1, true), a3 = anglesOf(i3, true), a4 = anglesOf(i4, true), a2 = anglesOf(i2, true);
		ASSERT_FALSE(a1.empty() || a2.empty() || a3.empty() || a4.empty());
		EXPECT_NEAR(wrap720(a3[0] - a1[0]), 180, 2);
		EXPECT_NEAR(wrap720(a4[0] - a1[0]), 360, 2);
		EXPECT_NEAR(wrap720(a2[0] - a1[0]), 540, 2);
	}
}

void runYear(engine_type_e year) {
	MiataEcu ecu(year);
	Recorder rec;
	Clock clock(ecu.eth, rec);
	// a moment with the key on before cranking (fuel pump prime, CEL bulb check)
	clock.advanceTo(getTimeNowUs() + 500000, 1000);
	report("key_on", 0, rec);
	EXPECT_EQ(1, rec.get("fuelPump").last) << "fuel pump primes at key-on";

	float prev = 250;
	for (float rpm : {250.0f, 900.0f, 3000.0f, 6500.0f}) {
		int cycles = 6;
		// accelerate at 700 rpm/s (pulling in a middle gear), then settle for 4 cycles. Harder acceleration makes
		// rusEFI log a trigger timing warning, see MiataLimits.TriggerTimingWarningVsAcceleration.
		int ramp = std::max(6, (int)((rpm - prev) / 700 * ((rpm + prev) / 2) / 120));
		if (isNb(year)) {
			runNb(clock, prev, rpm, ramp);
			runNb(clock, rpm, 4);
		} else {
			runNa(clock, prev, rpm, ramp);
			runNa(clock, rpm, 4);
		}
		prev = rpm;
		rec.clear();
		if (isNb(year)) {
			runNb(clock, rpm, cycles);
		} else {
			runNa(clock, rpm, cycles);
		}
		EXPECT_NEAR(Sensor::getOrZero(SensorType::Rpm), rpm, rpm * 0.02) << yearName(year);
		EXPECT_TRUE(engine->triggerCentral.triggerState.getShaftSynchronized());
		EXPECT_TRUE(engine->triggerCentral.triggerState.hasSynchronizedPhase()) << "full 720-degree phase @" << rpm;
		report("run", rpm, rec);
		{
			error_codes_set_s codes;
			getErrorCodes(&codes, nullptr);
			printf("MIATA|%s|codes|%.0f|count=%d|", yearName(year), rpm, (int)codes.count);
			for (size_t i = 0; i < codes.count; i++) {
				printf("%d,", (int)codes.error_codes[i]);
			}
			printf("\n");
		}
		if (rpm >= 500) { // above cranking, where spark/fuel follow the run tables
			checkSparks(rec, cycles, rpm);
			checkInjectors(rec, cycles, rpm);
			EXPECT_EQ(4 * cycles, countEdges(rec.get("tach"), true)) << "tach: 2 pulses per revolution";
			EXPECT_EQ(1, rec.get("fuelPump").last) << "fuel pump on while running";
			EXPECT_EQ(0, rec.get("cel").last) << "no check engine light on a clean run @" << rpm;
			if (engineConfiguration->o2heaterPin != Gpio::Unassigned) {
				EXPECT_EQ(1, rec.get("o2heater").last) << "O2 heater on while running";
			}
			if (engineConfiguration->alternatorControlPin != Gpio::Unassigned) {
				EXPECT_GT(countEdges(rec.get("alternator"), true), cycles) << "alternator field PWM running";
			}
		}
	}

	printf("MIATA|%s|summary|0|warnings|count=%d|", yearName(year), (int)ecu.eth.recentWarnings()->getCount());
	for (size_t i = 0; i < ecu.eth.recentWarnings()->getCount(); i++) {
		printf("%d,", (int)ecu.eth.recentWarnings()->get(i).Code);
	}
	printf("|firmwareError=%d\n", hasFirmwareError());
	EXPECT_FALSE(hasFirmwareError()) << getCriticalErrorMessage();

	if (year == engine_type_e::MAZDA_MIATA_NB2) {
		EXPECT_TRUE(rec.get("mainRelay").last) << "NB2 main relay held on";
	}
}

} // namespace

// ---- configuration: what each year's tune looks like -----------------------------------------------------------

void checkConfiguration(engine_type_e year) {
	MiataEcu ecu(year);
	bool nb = isNb(year);

	EXPECT_EQ(std::string("PB7"), pinName(Gpio::B7));
	// pins that are the same on every motherboard
	EXPECT_EQ(MIATA_IGN1, engineConfiguration->ignitionPins[0]);
	EXPECT_EQ(MIATA_IGN3, engineConfiguration->ignitionPins[1]);
	EXPECT_EQ(MIATA_IGN2, engineConfiguration->ignitionPins[2]);
	EXPECT_EQ(MIATA_IGN4, engineConfiguration->ignitionPins[3]);
	EXPECT_EQ(IM_WASTED_SPARK, engineConfiguration->ignitionMode);
	EXPECT_EQ(MIATA_INJ1, engineConfiguration->injectionPins[0]);
	EXPECT_EQ(MIATA_INJ2, engineConfiguration->injectionPins[1]);
	EXPECT_EQ(MIATA_FP, engineConfiguration->fuelPumpPin);
	EXPECT_EQ(MIATA_FAN, engineConfiguration->fanPin);
	EXPECT_EQ(MIATA_LS7, engineConfiguration->fan2Pin);
	EXPECT_EQ(MIATA_AC, engineConfiguration->acRelayPin);
	EXPECT_EQ(MIATA_CEL, engineConfiguration->malfunctionIndicatorPin);
	EXPECT_EQ(MIATA_TACH, engineConfiguration->tachOutputPin);
	EXPECT_EQ(MIATA_IACV, engineConfiguration->idle.solenoidPin);
	EXPECT_EQ(MIATA_SW1, engineConfiguration->vehicleSpeedSensorInputPin);
	EXPECT_EQ(MIATA_SW2, engineConfiguration->acSwitch);
	EXPECT_EQ(MIATA_SW3, engineConfiguration->clutchDownPin);
	EXPECT_EQ(4, engineConfiguration->cylindersCount);
	EXPECT_EQ(FO_1_3_4_2, engineConfiguration->firingOrder);

	// board facts
	EXPECT_NEAR(1.56f, engineConfiguration->analogInputDividerCoefficient, 1e-4);
	EXPECT_NEAR(5.853f, engineConfiguration->vbattDividerCoeff, 1e-3);
	EXPECT_EQ(MIATA_IN_VBATT, engineConfiguration->vbattAdcChannel);
	EXPECT_EQ(MIATA_IN_CLT, engineConfiguration->clt.adcChannel);
	EXPECT_EQ(MIATA_IN_IAT, engineConfiguration->iat.adcChannel);
	EXPECT_NEAR(2301.6f, engineConfiguration->clt.config.bias_resistor, 0.5) << "preset's 2.7k must be replaced";
	EXPECT_NEAR(2301.6f, engineConfiguration->iat.config.bias_resistor, 0.5);
	EXPECT_NEAR(4.262f, miataGetThermistorSupplyVoltage(MIATA_IN_CLT), 1e-3);
	EXPECT_NEAR(5.0f, miataGetThermistorSupplyVoltage(MIATA_IN_TPS), 1e-6);
	EXPECT_EQ(MT_CUSTOM, engineConfiguration->map.sensor.type) << "on-board MPX5700AP, not the preset's sensor";
	EXPECT_EQ(MIATA_IN_MAP, engineConfiguration->map.sensor.hwChannel);
	EXPECT_EQ(MIATA_IN_TPS, engineConfiguration->tps1_1AdcChannel);
	EXPECT_EQ(Gpio::B13, engineConfiguration->can2TxPin);
	EXPECT_EQ(Gpio::B12, engineConfiguration->can2RxPin);
	EXPECT_EQ(Gpio::Unassigned, engineConfiguration->canTxPin);
	EXPECT_TRUE(engineConfiguration->widebandOnSecondBus);
	EXPECT_TRUE(engineConfiguration->enableAemXSeries);
	EXPECT_TRUE(engineConfiguration->canReadEnabled && engineConfiguration->canWriteEnabled);

	// triggers
	if (nb) {
		EXPECT_EQ(trigger_type_e::TT_MIATA_VVT, engineConfiguration->trigger.type);
		EXPECT_EQ(MIATA_HALL1, engineConfiguration->triggerInputPins[0]);
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->triggerInputPins[1]);
		EXPECT_EQ(MIATA_HALL2, engineConfiguration->camInputs[0]);
		EXPECT_EQ(VVT_MIATA_NB, engineConfiguration->vvtMode[0]);
		EXPECT_TRUE(g_knockRequested) << "NB has a knock sensor (2F / 4M)";
	} else {
		EXPECT_EQ(trigger_type_e::TT_MAZDA_MIATA_NA, engineConfiguration->trigger.type);
		EXPECT_EQ(MIATA_HALL2, engineConfiguration->triggerInputPins[0]) << "NA primary = SGC (cam, 3G/4G)";
		EXPECT_EQ(MIATA_HALL1, engineConfiguration->triggerInputPins[1]) << "NA secondary = SGT (3E/4F)";
	}

	// year-specific outputs
	switch (year) {
	case engine_type_e::MAZDA_MIATA_NA6:
		EXPECT_EQ(IM_BATCH, engineConfiguration->injectionMode);
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->injectionPins[2]);
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->injectionPins[3]);
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->o2heaterPin);
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->alternatorControlPin);
		EXPECT_NEAR(1.6f, engineConfiguration->displacement, 0.01);
		break;
	case engine_type_e::MAZDA_MIATA_NA94:
		EXPECT_EQ(IM_SEQUENTIAL, engineConfiguration->injectionMode);
		EXPECT_EQ(MIATA_INJ3, engineConfiguration->injectionPins[2]);
		EXPECT_EQ(MIATA_INJ4, engineConfiguration->injectionPins[3]);
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->alternatorControlPin) << "94-95 ALT pin is the PRC solenoid";
		EXPECT_NEAR(1.8f, engineConfiguration->displacement, 0.05);
		break;
	case engine_type_e::MAZDA_MIATA_NA96:
		EXPECT_EQ(IM_SEQUENTIAL, engineConfiguration->injectionMode);
		EXPECT_EQ(MIATA_VVT, engineConfiguration->o2heaterPin) << "front O2 heater on 3M";
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->alternatorControlPin);
		break;
	case engine_type_e::MAZDA_MIATA_NB1:
		EXPECT_EQ(IM_SEQUENTIAL, engineConfiguration->injectionMode);
		EXPECT_EQ(MIATA_VVT, engineConfiguration->o2heaterPin) << "front O2 heater on 1U";
		EXPECT_EQ(MIATA_ALT, engineConfiguration->alternatorControlPin);
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->vvtPins[0]);
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->mainRelayPin) << "MAINRLY drives VICS on NB1, not a relay";
		EXPECT_NEAR(256, engineConfiguration->injector.flow, 0.1);
		break;
	case engine_type_e::MAZDA_MIATA_NB2:
		EXPECT_EQ(IM_SEQUENTIAL, engineConfiguration->injectionMode);
		EXPECT_EQ(MIATA_VVT, engineConfiguration->vvtPins[0]) << "OCV on 4R";
		EXPECT_EQ(Gpio::Unassigned, engineConfiguration->o2heaterPin);
		EXPECT_EQ(MIATA_ALT, engineConfiguration->alternatorControlPin);
		EXPECT_EQ(MIATA_MAINRLY, engineConfiguration->mainRelayPin);
		EXPECT_NEAR(265, engineConfiguration->injector.flow, 0.1);
		break;
	default:
		FAIL();
	}

	// the dump that tools/sim_report.py checks against the harness maps
	printf("MIATA|%s|config|0|pins|", yearName(year));
	printf("ign=%s,%s,%s,%s|", pinName(engineConfiguration->ignitionPins[0]).c_str(), pinName(engineConfiguration->ignitionPins[1]).c_str(),
		pinName(engineConfiguration->ignitionPins[2]).c_str(), pinName(engineConfiguration->ignitionPins[3]).c_str());
	printf("inj=%s,%s,%s,%s|", pinName(engineConfiguration->injectionPins[0]).c_str(), pinName(engineConfiguration->injectionPins[1]).c_str(),
		pinName(engineConfiguration->injectionPins[2]).c_str(), pinName(engineConfiguration->injectionPins[3]).c_str());
	printf("trigger=%s,%s|cam=%s|", pinName(engineConfiguration->triggerInputPins[0]).c_str(),
		pinName(engineConfiguration->triggerInputPins[1]).c_str(), pinName(engineConfiguration->camInputs[0]).c_str());
	printf("fuelPump=%s|fan=%s|fan2=%s|acRelay=%s|cel=%s|tach=%s|idle=%s|mainRelay=%s|alternator=%s|o2heater=%s|vvt=%s|boost=%s|",
		pinName(engineConfiguration->fuelPumpPin).c_str(), pinName(engineConfiguration->fanPin).c_str(),
		pinName(engineConfiguration->fan2Pin).c_str(), pinName(engineConfiguration->acRelayPin).c_str(),
		pinName(engineConfiguration->malfunctionIndicatorPin).c_str(), pinName(engineConfiguration->tachOutputPin).c_str(),
		pinName(engineConfiguration->idle.solenoidPin).c_str(), pinName(engineConfiguration->mainRelayPin).c_str(),
		pinName(engineConfiguration->alternatorControlPin).c_str(), pinName(engineConfiguration->o2heaterPin).c_str(),
		pinName(engineConfiguration->vvtPins[0]).c_str(), pinName(engineConfiguration->boostControlPin).c_str());
	printf("vss=%s|acSwitch=%s|clutch=%s|mode=%s\n", pinName(engineConfiguration->vehicleSpeedSensorInputPin).c_str(),
		pinName(engineConfiguration->acSwitch).c_str(), pinName(engineConfiguration->clutchDownPin).c_str(),
		engineConfiguration->injectionMode == IM_BATCH ? "batch" : "sequential");
}


#define MIATA_YEAR_TESTS(name, type) \
	TEST(MiataYear, Configuration_##name) { checkConfiguration(engine_type_e::type); } \
	TEST(MiataYear, Running_##name) { runYear(engine_type_e::type); }

MIATA_YEAR_TESTS(NA6_1989_93, MAZDA_MIATA_NA6)
MIATA_YEAR_TESTS(NA8_1994_95, MAZDA_MIATA_NA94)
MIATA_YEAR_TESTS(NA8_1996_97, MAZDA_MIATA_NA96)
MIATA_YEAR_TESTS(NB1_1999_2000, MAZDA_MIATA_NB1)
MIATA_YEAR_TESTS(NB2_2001_05, MAZDA_MIATA_NB2)

// ---- real captures ------------------------------------------------------------------------------------------------

TEST(MiataRealCapture, NaCasCrankingAllNaYears) {
	for (auto year : {engine_type_e::MAZDA_MIATA_NA6, engine_type_e::MAZDA_MIATA_NA94, engine_type_e::MAZDA_MIATA_NA96}) {
		MiataEcu ecu(year);
		engineConfiguration->alwaysInstantRpm = true;
		CsvReader reader(2, /* vvtCount */ 0);
		// this capture has the first trigger channel in the second column (see rusEFI's own NA cranking test)
		reader.open("tests/trigger/resources/cranking_na_3.csv", REVERSE_ORDER);
		while (reader.haveMore()) {
			reader.processLine(&ecu.eth);
		}
		EXPECT_TRUE(engine->triggerCentral.triggerState.getShaftSynchronized()) << yearName(year);
		// rusEFI's own NA6 test ends this capture at 191 rpm
		EXPECT_NEAR(191, Sensor::getOrZero(SensorType::Rpm), 2) << yearName(year);
		printf("MIATA|%s|capture_na|%d|warnings|count=%d\n", yearName(year), (int)Sensor::getOrZero(SensorType::Rpm),
			(int)ecu.eth.recentWarnings()->getCount());
	}
}

TEST(MiataRealCapture, Nb2CrankAndCamBothNbYears) {
	for (auto year : {engine_type_e::MAZDA_MIATA_NB1, engine_type_e::MAZDA_MIATA_NB2}) {
		MiataEcu ecu(year);
		engineConfiguration->alwaysInstantRpm = true;
		CsvReader reader(1, /* vvtCount */ 1);
		reader.open("tests/trigger/resources/nb2-cranking-good.csv");
		while (reader.haveMore()) {
			reader.processLine(&ecu.eth);
		}
		EXPECT_TRUE(engine->triggerCentral.triggerState.hasSynchronizedPhase()) << yearName(year);
		// rusEFI's Hellen NB2 preset reads 4.26 deg VVT and 876 rpm from this capture; ours must agree
		EXPECT_NEAR(876, Sensor::getOrZero(SensorType::Rpm), 2) << yearName(year);
		EXPECT_NEAR(4.26f, engine->triggerCentral.getVVTPosition(0, 0), 0.1) << yearName(year);
		printf("MIATA|%s|capture_nb2|%d|vvt=%.2f\n", yearName(year), (int)Sensor::getOrZero(SensorType::Rpm),
			engine->triggerCentral.getVVTPosition(0, 0));
	}
}

// Our hall inputs are non-inverting; check what happens if the car's sensor polarity is the other way round.
TEST(MiataRealCapture, NbInvertedPolarityNeedsTheInvertSetting) {
	MiataEcu ecu(engine_type_e::MAZDA_MIATA_NB2);
	Recorder rec;
	Clock clock(ecu.eth, rec);
	runNb(clock, 900, 16, /* invert */ true);
	bool syncedInverted = engine->triggerCentral.triggerState.hasSynchronizedPhase();
	printf("MIATA|2001-05|inverted_signal|900|phase_sync=%d|rpm=%.0f\n", syncedInverted, Sensor::getOrZero(SensorType::Rpm));
}

// Rev limiter: the presets set 7200 rpm; fuel must be cut above it.
TEST(MiataLimits, RevLimiter) {
	MiataEcu ecu(engine_type_e::MAZDA_MIATA_NB2);
	Recorder rec;
	Clock clock(ecu.eth, rec);
	runNb(clock, 7600, 12);
	rec.clear();
	runNb(clock, 7600, 6);
	int pulses = countEdges(rec.get("inj1"), true) + countEdges(rec.get("inj2"), true) + countEdges(rec.get("inj3"), true)
		+ countEdges(rec.get("inj4"), true);
	printf("MIATA|2001-05|revlimit|7600|injector_pulses=%d\n", pulses);
	EXPECT_EQ(0, pulses) << "fuel must be cut at 7600 rpm with a 7200 rpm limit";
}

// rusEFI warns (code 9007/9008) when a trigger tooth lands >10 degrees from where the previous tooth's speed predicted
// it. That depends on how hard the engine accelerates, not on the board: measure it for both trigger types.
TEST(MiataLimits, TriggerTimingWarningVsAcceleration) {
	for (auto year : {engine_type_e::MAZDA_MIATA_NA6, engine_type_e::MAZDA_MIATA_NB2}) {
		for (int rampCycles : {10, 20, 40, 80, 160}) {
			MiataEcu ecu(year);
			Recorder rec;
			Clock clock(ecu.eth, rec);
			auto run = [&](float a, float b, int n) {
				if (isNb(year)) {
					runNb(clock, a, b, n);
				} else {
					runNa(clock, a, b, n);
				}
			};
			run(250, 250, 6);
			run(250, 900, 20);
			run(900, 900, 10);
			double t0 = getTimeNowUs();
			run(900, 3000, rampCycles);
			double seconds = (getTimeNowUs() - t0) / 1e6;
			run(3000, 3000, 6);
			bool early = false;
			auto* w = ecu.eth.recentWarnings();
			for (size_t i = 0; i < w->getCount(); i++) {
				early |= w->get(i).Code == ObdCode::CUSTOM_PRIMARY_BAD_TOOTH_TIMING_EARLY;
			}
			printf("MIATA|%s|accel|%.0f|rpm_per_s=%.0f|bad_tooth_warning=%d\n", yearName(year), 3000.0,
				2100 / seconds, early);
		}
	}
}

// Without the board's warning expiry (miataPeriodicSlowCallback) and with no TunerStudio polling, does the NB start-up
// warning keep the check engine light on? Documents why the board installs that callback.
TEST(MiataLimits, CelAfterNbStartWithAndWithoutWarningExpiry) {
	for (bool expiry : {false, true}) {
		MiataEcu ecu(engine_type_e::MAZDA_MIATA_NB2);
		if (!expiry) {
			custom_board_periodicSlowCallback.reset();
		}
		Recorder rec;
		Clock clock(ecu.eth, rec);
		runNb(clock, 250, 6);
		runNb(clock, 250.0f, 900.0f, 20);
		runNb(clock, 900.0f, 120); // ~16 s of idle
		printf("MIATA|2001-05|cel_after_start|900|warning_expiry=%d|cel=%d\n", expiry, rec.get("cel").last);
		if (expiry) {
			EXPECT_EQ(0, rec.get("cel").last) << "CEL must go out once the start-up warning has expired";
		}
	}
}
