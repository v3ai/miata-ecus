#!/bin/bash
# Builds the on-board wideband's firmware: rusEFI's wideband controller sources (the wideband_firmware submodule of the
# rusEFI tree) with this board's port (miata_f1/, STM32F103C8).
# usage: build.sh [rusEFI dir, default firmware/ext/rusefi] [output dir, default firmware/wideband/out]
# Output: miata_wbo_f103.bin (raw image for 0x08000000, written by the ECU's flasher), .elf, .map.
set -eo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
RUSEFI=$(realpath "${1:-$HERE/../ext/rusefi}")
OUT=$(realpath -m "${2:-$HERE/out}")
WB=$RUSEFI/firmware/controllers/can/wideband_firmware/firmware
[ -f "$WB/Makefile" ] || { echo "no wideband sources at $WB (init rusEFI's submodules)"; exit 1; }
[ -f "$WB/ChibiOS/os/license/license.mk" ] || (cd "$WB/.." && git submodule update --init firmware/ChibiOS firmware/libfirmware)
mkdir -p "$OUT"
BOARD=miata_f1
rm -rf "$WB/boards/$BOARD"
cp -r "$HERE/$BOARD" "$WB/boards/$BOARD"
trap 'rm -rf "$WB/boards/$BOARD"' EXIT
make -C "$WB" -j"$(nproc)" BOARD=$BOARD BUILDDIR="$OUT/build" > "$OUT/build.log" 2>&1 || { tail -40 "$OUT/build.log"; exit 1; }
cp "$OUT/build/wideband.bin" "$OUT/miata_wbo_f103.bin"
cp "$OUT/build/wideband.elf" "$OUT/miata_wbo_f103.elf"
cp "$OUT/build/wideband.map" "$OUT/miata_wbo_f103.map" 2>/dev/null || true
arm-none-eabi-size "$OUT/miata_wbo_f103.elf"
python3 "$HERE/check_wbo_image.py" "$OUT/miata_wbo_f103.elf" "$OUT/miata_wbo_f103.bin"
# provenance: compiler and sources, so an identical rebuild can be checked
{ echo "compiler: $(arm-none-eabi-gcc --version | head -1)"
  echo "wideband: $(git -C "$WB/.." rev-parse HEAD)"
  echo "sha256: $(sha256sum "$OUT/miata_wbo_f103.bin" | cut -d' ' -f1)"; } > "$OUT/miata_wbo_f103.txt"
cat "$OUT/miata_wbo_f103.txt"
