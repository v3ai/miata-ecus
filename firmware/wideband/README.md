# On-board wideband firmware (STM32F103C8)

The daughterboard's wideband controller (U102, rev 0.6 on) runs rusEFI's wideband controller firmware
(github.com/rusefi/wideband, MIT licence; the copy pinned as a submodule of `firmware/ext/rusefi`) built with this
board's port.

| Path | What |
|---|---|
| `miata_f1/` | The board port: rusEFI's F1 port (`boards/f1_rev3`, `boards/f1_common/f1_port.cpp`) with this board's pins, an 8 MHz crystal, the FOME module's analog constants, battery sense, the three ESR drives, TIM2-remapped heater PWM, settings in the last 8 KB of 64 KB, no bootloader and no TunerStudio port. ChibiOS configuration files keep their Apache 2.0 headers |
| `build.sh` | Builds it: copies `miata_f1/` into rusEFI's wideband tree, runs its Makefile, checks the result |
| `check_wbo_image.py` | Fits the F103C8 (56 KB app area, 20 KB RAM), sane vector table |
| `miata_wbo_f103.bin`, `.txt` | The built image (raw, for 0x08000000) and the compiler / source commit / SHA-256 it was built from. The main firmware carries it (`board/board.mk`, `WBO_IMAGE`) and writes it with "Flash on-board wideband" |

Rebuild after changing the port or the rusEFI pin: `bash build.sh` (needs `arm-none-eabi-gcc` and rusEFI's
submodules), then copy `out/miata_wbo_f103.bin` and `.txt` here. CI builds it on every push: with the same compiler the bytes must match this copy; with another compiler it only reports the difference.
