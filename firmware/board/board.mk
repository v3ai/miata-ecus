# rusEFI board definition for the miata-ecus daughterboard (STM32F407VGT6).
BOARDCPPSRC += $(BOARD_DIR)/board_configuration.cpp \
	$(BOARD_DIR)/miata_board.cpp \
	$(BOARD_DIR)/wideband_uart_flash.cpp

DDEFS += -DSTM32F407xx
DDEFS += -DFIRMWARE_ID=\"miata-ecu\"

# First boot with a blank tune: 1989-93 settings. Pick the year in TunerStudio > Popular Vehicles.
ifeq ($(MIATA_DEFAULT_ENGINE),)
  MIATA_DEFAULT_ENGINE = MAZDA_MIATA_NA6
endif
DDEFS += -DDEFAULT_ENGINE_TYPE=engine_type_e::$(MIATA_DEFAULT_ENGINE)

# Red LED (PD15). Run, comms and warning LEDs are PD12-PD14, set in board_configuration.cpp.
DDEFS += -DLED_CRITICAL_ERROR_BRAIN_PIN=Gpio::D15

# Knock sensor input on PA3 (ADC3_IN3), see knock_config.h.
DDEFS += -DEFI_SOFTWARE_KNOCK=TRUE -DSTM32_ADC_USE_ADC3=TRUE

# USART3 (PD8/PD9) is the link to the wideband MCU's ROM bootloader. A 128-byte queue holds a whole
# 64-byte read-back reply even if the flashing thread is slow to run.
DDEFS += -DSTM32_SERIAL_USE_USART3=TRUE -DSERIAL_BUFFERS_SIZE=128

# Wideband image (CAN bootloader + firmware) from the wideband submodule of the rusEFI tree being built.
WBO_IMAGE ?= $(PROJECT_DIR)/controllers/can/wideband_firmware/release/rc/wideband_image_with_bl.bin
DDEFS += -DWBO_IMAGE_PATH=\"$(abspath $(WBO_IMAGE))\"
