#pragma once

// miata-ecus daughterboard: rusEFI/FOME wideband module circuit (rev C) on an STM32F103C8 (LQFP48).
// Pins chosen so each group faces its parts: ESR drives and LEDs left, heater/battery/pump right, CAN up, analog down.

#define LED_BLUE_PORT GPIOB
#define LED_BLUE_PIN 8

#define LED_GREEN_PORT GPIOB
#define LED_GREEN_PIN 9

// LSU 4.2 - 6.8K (R116)
#define NERNST_42_ESR_DRIVER_PORT   GPIOB
#define NERNST_42_ESR_DRIVER_PIN    5

// LSU 4.9 - 22K (R106)
#define NERNST_49_ESR_DRIVER_PORT   GPIOB
#define NERNST_49_ESR_DRIVER_PIN    7

// LSU ADV - 47K (R119)
#define NERNST_ADV_ESR_DRIVER_PORT  GPIOB
#define NERNST_ADV_ESR_DRIVER_PIN   6

// PB10 TIM2_CH3 (partial remap 2, see board.c)
#define HEATER_PWM_DEVICE PWMD2
#define HEATER_PWM_CHANNEL_0 2

// PA6 TIM3_CH1
#define PUMP_DAC_PWM_DEVICE PWMD3
#define PUMP_DAC_PWM_CHANNEL_0 0

// CAN index straps: not fitted (both read "floating", so the default index is used)
#define ID_SEL1_PORT                GPIOC
#define ID_SEL1_PIN                 13

#define ID_SEL2_PORT                GPIOC
#define ID_SEL2_PIN                 14
