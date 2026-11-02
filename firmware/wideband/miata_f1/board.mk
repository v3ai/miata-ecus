# miata-ecus daughterboard wideband (STM32F103C8). No bootloader (the ECU flashes it over the ROM bootloader) and no
# TunerStudio port (it talks to rusEFI over CAN only), which keeps it inside the C8's 64 KB flash and 20 KB RAM.
USE_BOOTLOADER = no

MCU = cortex-m3

ALLCPPSRC += $(BOARDDIR)/f1_port.cpp

include $(CHIBIOS)/os/common/startup/ARMCMx/compilers/GCC/mk/startup_stm32f1xx.mk
include $(CHIBIOS)/os/hal/ports/STM32/STM32F1xx/platform.mk
include $(CHIBIOS)/os/common/ports/ARMv7-M/compilers/GCC/mk/port.mk
