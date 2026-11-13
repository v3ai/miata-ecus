/**
 * @file knock_config.h
 * Knock sensor: AC-coupled, biased to 1.65 V and amplified on the daughterboard, then PA3 (ADC3_IN3).
 */

#pragma once

#define KNOCK_ADC ADCD3

#define KNOCK_ADC_CH1 ADC_CHANNEL_IN3
#define KNOCK_PIN_CH1 Gpio::A3

#define KNOCK_SAMPLE_TIME ADC_SAMPLE_84
#define KNOCK_SAMPLE_RATE (STM32_PCLK2 / (4 * (84 + 12)))
