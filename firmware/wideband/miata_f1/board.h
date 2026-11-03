/*
    ChibiOS - Copyright (C) 2006..2018 Giovanni Di Sirio

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
*/

#ifndef _BOARD_H_
#define _BOARD_H_

/*
 * Board identifier.
 */
#define BOARD_NAME                  "miata-ecus daughterboard wideband (STM32F103C8)"

/*
 * Board oscillators-related settings.
 * NOTE: LSE not fitted.
 * HSE: 8 MHz crystal Y101.
 */
#if !defined(STM32_LSECLK)
#define STM32_LSECLK                0U
#endif

#if !defined(STM32_HSECLK)
#define STM32_HSECLK                8000000U
#endif

/*
 * MCU type: STM32F103C8T6 / CBT6 (medium density, 64/128 KB flash, 20 KB RAM, LQFP48).
 */
#define STM32F103xB

/*
 * I/O ports initial setup, this configuration is established soon after reset
 * in the initialization code.
 *
 * The digits have the following meaning:
 *   0 - Analog input.
 *   1 - Push Pull output 10MHz.
 *   2 - Push Pull output 2MHz.
 *   3 - Push Pull output 50MHz.
 *   4 - Digital input.
 *   5 - Open Drain output 10MHz.
 *   6 - Open Drain output 2MHz.
 *   7 - Open Drain output 50MHz.
 *   8 - Digital input with PullUp or PullDown resistor depending on ODR.
 *   9 - Alternate Push Pull output 10MHz.
 *   A - Alternate Push Pull output 2MHz.
 *   B - Alternate Push Pull output 50MHz.
 *   C - Reserved.
 *   D - Alternate Open Drain output 10MHz.
 *   E - Alternate Open Drain output 2MHz.
 *   F - Alternate Open Drain output 50MHz.
 * Please refer to the STM32 Reference Manual for details.
 */

/*
 * Port A setup (the analog front end is the rusEFI/FOME wideband module, rev C).
 * PA0  - Un_sense (Nernst, x2.7)   (analog in, ADC12_IN0).
 * PA1  - not connected (rev 0.7; the module wired it to LSU_Vm, never sampled).
 * PA2  - Ip_sense                  (analog in, ADC12_IN2).
 * PA3  - Vm_sense (virtual ground) (analog in, ADC12_IN3).
 * PA4, PA5 - unused                (input, pull-up).
 * PA6  - Ip_dac PWM, TIM3_CH1      (alternate pushpull, 50 MHz).
 * PA7, PA8 - unused                (input, pull-up).
 * PA9  - USART1_TX                 (input, pull-up: only the ROM bootloader uses it, for flashing from the ECU).
 * PA10 - USART1_RX                 (input, pull-up).
 * PA11 - CAN_RX                    (input, pull-up).
 * PA12 - CAN_TX                    (alternate pushpull, 50 MHz).
 * PA13 - SWDIO, PA14 - SWCLK, PA15 - unused (JTDI).
 */
#define VAL_GPIOACRL            0x8B880000      /*  PA7...PA0 */
#define VAL_GPIOACRH            0x888B8888      /* PA15...PA8 */
#define VAL_GPIOAODR            0x0000FFFF

/*
 * Port B setup.
 * PB0  - Vbatt_sense, 100k/10k     (analog in, ADC12_IN8).
 * PB1  - unused                    (input, pull-up).
 * PB2  - BOOT1, 10k to GND (R135)  (input, floating).
 * PB3, PB4 - unused (JTDO, NJTRST) (input, pull-up).
 * PB5  - Nernst 4.2 ESR drive, 6.8k (input, floating: high-Z until selected).
 * PB6  - Nernst ADV ESR drive, 47k (input, floating: high-Z until selected).
 * PB7  - Nernst 4.9 ESR drive, 22k (output pushpull, 50 MHz: the default sensor).
 * PB8  - LED_BLUE                  (output pushpull, 2 MHz, starts off).
 * PB9  - LED_GREEN                 (output pushpull, 2 MHz, starts off).
 * PB10 - heater PWM, TIM2_CH3      (alternate pushpull, 50 MHz; TIM2 partial remap 2, set in boardInit).
 * PB11..PB15 - unused              (input, pull-up).
 */
#define VAL_GPIOBCRL            0x34488480      /*  PB7...PB0 */
#define VAL_GPIOBCRH            0x88888B22      /* PB15...PB8 */
#define VAL_GPIOBODR            0x0000FCFF

/*
 * Port C setup.
 * PC13 - ID_SEL1, PC14 - ID_SEL2   (digital input, not connected: "floating" strap = default CAN index).
 * PC15 - unused                    (input, pull-up). PC0..PC12 are not bonded on LQFP48.
 */
#define VAL_GPIOCCRL            0x88888888      /*  PC7...PC0 */
#define VAL_GPIOCCRH            0x84488888      /* PC15...PC8 */
#define VAL_GPIOCODR            0x0000FFFF

/*
 * Port D setup.
 * PD0, PD1 - OSC_IN / OSC_OUT (crystal).
 */
#define VAL_GPIODCRL            0x88888844      /*  PD7...PD0 */
#define VAL_GPIODCRH            0x88888888      /* PD15...PD8 */
#define VAL_GPIODODR            0x0000FFFF

/*
 * Port E setup (not bonded on LQFP48).
 */
#define VAL_GPIOECRL            0x88888888      /*  PE7...PE0 */
#define VAL_GPIOECRH            0x88888888      /* PE15...PE8 */
#define VAL_GPIOEODR            0x0000FFFF

/*
 * USB bus activation macro, required by the USB driver.
 */
#define usb_lld_connect_bus(usbp)

/*
 * USB bus de-activation macro, required by the USB driver.
 */
#define usb_lld_disconnect_bus(usbp)

#if !defined(_FROM_ASM_)
#ifdef __cplusplus
extern "C" {
#endif
  void boardInit(void);
#ifdef __cplusplus
}
#endif
#endif /* _FROM_ASM_ */

#endif /* _BOARD_H_ */
