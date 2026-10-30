/**
 * @file miata_board.h
 * @brief Board configuration hooks for the miata-ecus board. Kept apart from board_configuration.cpp so that the
 * unit tests (firmware/board/tests) can run exactly this code inside rusEFI's engine simulator.
 */

#pragma once

#include "rusefi_types.h"
#include "engine_configuration.h"

float miataGetThermistorSupplyVoltage(adc_channel_e channel);
// Facts of the PCB, re-applied after every tune load and TunerStudio write.
void miataBoardConfigOverrides();
// Defaults for a fresh tune, before the year preset.
void miataBoardDefaultConfiguration();
// The five model-year presets (engine types MAZDA_MIATA_NA6/NA94/NA96/NB1/NB2).
void miataApplyYearPreset(engine_type_e engineType);
// Runs after every engine preset.
void miataAfterTuneDefaults(engine_type_e engineType);
// Board slow callback: expires old warnings on schedule. rusEFI otherwise only does that while TunerStudio (or Lua /
// SD logging) polls, so with no laptop connected a one-off start-up warning (e.g. NB "not firing until cam sync") would
// keep the check engine light blinking.
void miataPeriodicSlowCallback();
// Makes the next MAZDA_MIATA_NB2 preset the 2001-02 variant (no ignition sense, no main-relay control).
void miataSelectNb2Early(bool early);
