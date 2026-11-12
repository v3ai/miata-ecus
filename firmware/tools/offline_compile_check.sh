#!/bin/bash
# Compile-check the board without rusEFI's Java code generation (for machines that can't reach Gradle/Maven).
#
# It borrows the configuration headers rusEFI already commits for its f407-discovery board, so it proves the board
# code compiles and links; it does NOT produce a firmware to flash or a TunerStudio .ini (the GitHub Actions build
# does both). usage: offline_compile_check.sh <rusefi checkout> [make args]
set -e
RUSEFI=$(realpath "$1"); shift
HERE=$(dirname "$(realpath "$0")")
FW=$RUSEFI/firmware
TMP=$RUSEFI/.miata-ecu-offline          # fixed path, so make can rebuild incrementally
rm -rf "$TMP/board"; mkdir -p "$TMP"
cp -r "$HERE/../board" "$TMP/board"
rm -rf "$TMP/wideband"; mkdir -p "$TMP/wideband"; cp "$HERE/../wideband/miata_wbo_f103.bin" "$TMP/wideband/"   # WBO_IMAGE
rm -rf "$TMP/board/connectors"                  # their generated pin-name file comes from the Java step
sed -i 's/^SHORT_BOARD_NAME=.*/SHORT_BOARD_NAME=f407-discovery/' "$TMP/board/meta-info.env"
GEN=$FW/controllers/generated
if [ ! -f "$GEN/signature_f407-discovery.h" ]; then      # normally written by gen_signature.sh
  printf '#define SIGNATURE_HASH 1\n#define TS_SIGNATURE "rusEFI offline.f407-discovery.1"\n' > "$GEN/signature_f407-discovery.h"
fi
J=../java_tools
cd "$FW"
rc=0
bash bin/compile.sh "$(realpath --relative-to=. "$TMP/board/meta-info.env")" \
  -o .config-sentinel -o .docsenums-sentinel -o .tooljars-sentinel -o .ramdisk-sentinel \
  -o $J/configuration_definition/build/libs/config_definition-all.jar "$@" || rc=$?

# The OpenBLT bootloader compiles every board source too, with EFI_BOOTLOADER set and without the engine include
# paths. rusEFI builds it in the bundle step, which comes after the point where the offline build stops (the map
# reader jar), so build it here: a board file that only compiles for the firmware fails CI otherwise.
BL_BOARD=$(realpath --relative-to=bootloader "$TMP/board")
BOARD_DIR=$BL_BOARD BOARD_META_PATH=$BL_BOARD/meta-info.env SHORT_BOARD_NAME=f407-discovery \
  TGT_SENTINEL=../.target-sentinel make -C bootloader -r SUBMAKE=yes "$@"
echo "bootloader: built with the board sources"
exit $rc
