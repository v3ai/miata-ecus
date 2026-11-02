/*
 * STM32F103x8 memory setup (64 KB flash, 20 KB RAM). No bootloader: the ECU writes the image through the ROM
 * serial bootloader. The last 8 KB of flash hold the settings (two 4 KB MFS banks, see f1_port.cpp).
 */
MEMORY
{
    /* empty section to keep linker happy */
    blflash (rx) : org = 0x08000000, len = 0
    appflash (rx) : org = 0x08000000, len = 64k - 8k
    configflash (rx) : org = 0x08000000 + 64k - 8k, len = 8k
    flash1 (rx) : org = 0x00000000, len = 0
    flash2 (rx) : org = 0x00000000, len = 0
    flash3 (rx) : org = 0x00000000, len = 0
    flash4 (rx) : org = 0x00000000, len = 0
    flash5 (rx) : org = 0x00000000, len = 0
    flash6 (rx) : org = 0x00000000, len = 0
    flash7 (rx) : org = 0x00000000, len = 0
    ram0   (wx) : org = 0x20000000, len = 20k
    ram1   (wx) : org = 0x00000000, len = 0
    ram2   (wx) : org = 0x00000000, len = 0
    ram3   (wx) : org = 0x00000000, len = 0
    ram4   (wx) : org = 0x00000000, len = 0
    ram5   (wx) : org = 0x00000000, len = 0
    ram6   (wx) : org = 0x00000000, len = 0
    ram7   (wx) : org = 0x00000000, len = 0
}

__configflash__start__ = ORIGIN(configflash);
