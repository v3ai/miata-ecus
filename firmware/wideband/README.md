# On-board wideband firmware (STM32F103C8)

The daughterboard's wideband controller (U102, rev 0.6 on) runs rusEFI's wideband controller firmware
(github.com/rusefi/wideband, MIT licence; the copy pinned as a submodule of `firmware/ext/rusefi`) built with this
board's port.

| Path | What |
|---|---|
| `miata_f1/` | The board port: rusEFI's F1 port (`boards/f1_rev3`, `boards/f1_common/f1_port.cpp`) with this board's pins, an 8 MHz crystal, the FOME module's analog constants, battery sense, the three ESR drives, TIM2-remapped heater PWM, settings in the last 8 KB of 64 KB, no bootloader and no TunerStudio port. ChibiOS configuration files keep their Apache 2.0 headers |
| `patches/` | This board's changes to the controller sources themselves, applied for the build and taken out after. `0001-heater-loop-watchdog.patch`: the heater loop calls the port's `PortHeaterLoopAlive()` |
| `build.sh` | Builds it: copies `miata_f1/` into rusEFI's wideband tree, applies `patches/`, runs its Makefile, checks the result |
| `check_wbo_image.py` | Fits the F103C8 (56 KB app area, 20 KB RAM), sane vector table |
| `miata_wbo_f103.bin`, `.txt` | The built image (raw, for 0x08000000) and the compiler / source commit / SHA-256 it was built from. The main firmware carries it (`board/board.mk`, `WBO_IMAGE`) and writes it with "Flash on-board wideband" |

Rebuild after changing the port or the rusEFI pin: `bash build.sh` (needs `arm-none-eabi-gcc` and rusEFI's
submodules), then copy `out/miata_wbo_f103.bin` and `.txt` here. CI builds it on every push: with the same compiler the bytes must match this copy; with another compiler it only reports the difference.

## Watchdog (2026-11-19)
The independent watchdog runs from the moment sampling starts: 4 s nominal (2.7-5.3 s over the LSI clock's range).
The heater loop kicks it 20 times a second, but only when the sampling loop has taken a new sample since the last
kick, so a stop in either loop resets the controller, and the reset turns the heater output off. Upstream leaves the
watchdog off. Flashing is not affected: the ECU resets the controller through NRST first, which stops the watchdog.

## Upstream fixes checked (2026-11-19)
The pinned controller source is rusEFI's production branch `prod-2026-01` (27e115b), not upstream main. The two main
fixes the review asked for are already there in another form: bootloader entry needs a one-byte request (91aa7c6 on
main), and the heater state machine checks the measured supply voltage even when the ECU allows heating (6d27ef2 and
7670779 on that branch; 9295698 on main). Main's later changes (a reformat, an analog output, a fixed 6 kHz sample
rate, the system tick moved to TIM14) touch the port and haven't been taken.
