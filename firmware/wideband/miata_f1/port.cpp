// miata-ecus daughterboard wideband: STM32F103C8 with the rusEFI/FOME module's analog front end.
// Sampling follows rusEFI's f0_module port (same circuit); ESR drive selection follows its f1_rev3 port.
#include "port.h"

#include "wideband_config.h"

#include "ch.hpp"

void PortPrepareAnalogSampling()
{
    adcStart(&ADCD1, nullptr);
}

#define ADC_CHANNEL_COUNT 4
#define ADC_SAMPLE ADC_SAMPLE_7P5

static adcsample_t adcBuffer[ADC_CHANNEL_COUNT * ADC_OVERSAMPLE];

static chibios_rt::BinarySemaphore adcDoneSemaphore(/* taken =*/ true);

static void adcDoneCallback(ADCDriver*)
{
    chSysLockFromISR();
    adcDoneSemaphore.signalI();
    chSysUnlockFromISR();
}

const ADCConversionGroup convGroup =
{
    .circular = false,
    .num_channels = ADC_CHANNEL_COUNT,
    .end_cb = adcDoneCallback,
    .error_cb = nullptr,
    .cr1 = 0,
    .cr2 =
        ADC_CR2_CONT |
        ADC_CR2_ADON,
    .smpr1 = 0,
    .smpr2 =
        ADC_SMPR2_SMP_AN0(ADC_SAMPLE) |
        ADC_SMPR2_SMP_AN2(ADC_SAMPLE) |
        ADC_SMPR2_SMP_AN3(ADC_SAMPLE) |
        ADC_SMPR2_SMP_AN8(ADC_SAMPLE),
    .sqr1 = ADC_SQR1_NUM_CH(ADC_CHANNEL_COUNT),
    .sqr2 = 0,
    .sqr3 =
        ADC_SQR3_SQ1_N(0) | /* PA0 - ADC12_IN0 - Un_sense (Nernst x2.7) */
        ADC_SQR3_SQ2_N(2) | /* PA2 - ADC12_IN2 - Ip_sense */
        ADC_SQR3_SQ3_N(3) | /* PA3 - ADC12_IN3 - Vm_sense (virtual ground) */
        ADC_SQR3_SQ4_N(8)   /* PB0 - ADC12_IN8 - Vbatt_sense */
};

static float AverageSamples(adcsample_t* buffer, size_t idx)
{
    uint32_t sum = 0;

    for (size_t i = 0; i < ADC_OVERSAMPLE; i++)
    {
        sum += buffer[idx];
        idx += ADC_CHANNEL_COUNT;
    }

    constexpr float scale = VCC_VOLTS / (ADC_MAX_COUNT * ADC_OVERSAMPLE);

    return (float)sum * scale;
}

void AnalogSampleStart()
{
    adcStartConversion(&ADCD1, &convGroup, adcBuffer, ADC_OVERSAMPLE);
}

AnalogResult AnalogSampleFinish()
{
    adcDoneSemaphore.wait(TIME_INFINITE);

    float vbatt = AverageSamples(adcBuffer, 3) / BATTERY_INPUT_DIVIDER;

    return
    {
        .ch = {
            {
                .NernstVoltage = AverageSamples(adcBuffer, 0) * (1.0 / NERNST_INPUT_GAIN),
                .PumpCurrentVoltage = AverageSamples(adcBuffer, 1),
                /* the heater runs from the same battery feed as the board's sense divider */
                .HeaterSupplyVoltage = vbatt,
            },
        },
        /* measured, as on the f0 module: the pump current amp is referenced to this node */
        .VirtualGroundVoltageInt = AverageSamples(adcBuffer, 2),
        .SupplyVoltage = vbatt,
        .McuTemp = 0,
    };
}

void SetupESRDriver(SensorType sensor)
{
    /* only the selected sensor's ESR resistor is driven; the other two pins stay high-Z */
    palSetPadMode(NERNST_42_ESR_DRIVER_PORT, NERNST_42_ESR_DRIVER_PIN, PAL_MODE_INPUT);
    palSetPadMode(NERNST_49_ESR_DRIVER_PORT, NERNST_49_ESR_DRIVER_PIN, PAL_MODE_INPUT);
    palSetPadMode(NERNST_ADV_ESR_DRIVER_PORT, NERNST_ADV_ESR_DRIVER_PIN, PAL_MODE_INPUT);

    switch (sensor) {
        case SensorType::LSU42:
            palSetPadMode(NERNST_42_ESR_DRIVER_PORT, NERNST_42_ESR_DRIVER_PIN, PAL_MODE_OUTPUT_PUSHPULL);
            break;
        case SensorType::LSU49:
        case SensorType::LSU49_FAE:
            palSetPadMode(NERNST_49_ESR_DRIVER_PORT, NERNST_49_ESR_DRIVER_PIN, PAL_MODE_OUTPUT_PUSHPULL);
            break;
        case SensorType::LSUADV:
            palSetPadMode(NERNST_ADV_ESR_DRIVER_PORT, NERNST_ADV_ESR_DRIVER_PIN, PAL_MODE_OUTPUT_PUSHPULL);
            break;
    }
}

int GetESRSupplyR()
{
    switch (GetSensorType()) {
        case SensorType::LSU42:
            return 6800;
        case SensorType::LSU49:
        case SensorType::LSU49_FAE:
            return 22000;
        case SensorType::LSUADV:
            return 47000;
    }

    return 0;
}
