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
rm -rf "$TMP/board/connectors"                  # their generated pin-name file comes from the Java step
sed -i 's/^SHORT_BOARD_NAME=.*/SHORT_BOARD_NAME=f407-discovery/' "$TMP/board/meta-info.env"
GEN=$FW/controllers/generated
if [ ! -f "$GEN/signature_f407-discovery.h" ]; then      # normally written by gen_signature.sh
  printf '#define SIGNATURE_HASH 1\n#define TS_SIGNATURE "rusEFI offline.f407-discovery.1"\n' > "$GEN/signature_f407-discovery.h"
fi
J=../java_tools
cd "$FW"
bash bin/compile.sh "$(realpath --relative-to=. "$TMP/board/meta-info.env")" \
  -o .config-sentinel -o .docsenums-sentinel -o .tooljars-sentinel -o .ramdisk-sentinel \
  -o $J/configuration_definition/build/libs/config_definition-all.jar "$@"
