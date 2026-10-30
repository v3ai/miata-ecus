#!/bin/bash
# Exercises firmware/board/wideband_uart_flash.cpp (compiled for the PC) against the AN3155 bootloader model.
# usage: run_flash_sim.sh <rusefi checkout> <work dir>
set -u
RUSEFI=$(realpath "$1"); W=$(realpath -m "$2"); mkdir -p "$W"
HERE=$(dirname "$(realpath "$0")")
IMG=$RUSEFI/firmware/controllers/can/wideband_firmware/release/rc/wideband_image_with_bl.bin
g++ -std=c++20 -O1 -Wall -I"$HERE/shim" -I"$HERE/../../board" -DWBO_IMAGE_PATH="\"$IMG\"" \
  "$HERE/../../board/wideband_uart_flash.cpp" "$HERE/host_main.cpp" -o "$W/host_flasher" || exit 1
# a chip that already holds a different program, for the re-flash case
head -c 32768 /dev/urandom > "$W/old_firmware.bin"
fail=0
run() { # name expect(ok|fail|refused) model-args... [-- flasher-args]
  local name=$1 expect=$2; shift 2
  local margs=() fargs=()
  while [ $# -gt 0 ] && [ "$1" != "--" ]; do margs+=("$1"); shift; done
  [ "${1:-}" == "--" ] && { shift; fargs=("$@"); }
  rm -f "$W/link" "$W/ctrl"; mkfifo "$W/ctrl"
  python3 "$HERE/an3155_model.py" "$W/link" "$W/$name.bin" --ctrl "$W/ctrl" "${margs[@]}" &
  local mp=$!
  while [ ! -s "$W/link" ]; do sleep 0.1; done
  "$W/host_flasher" "$(cat "$W/link")" "$W/ctrl" "${fargs[@]}" > "$W/$name.out" 2>&1
  wait $mp
  local status; status=$(grep "WBO UART:" "$W/$name.out" | tail -1)
  local res; res=$(grep RESULT "$W/$name.out")
  local same=no
  cmp -s <(head -c "$(stat -c%s "$IMG")" "$W/$name.bin") "$IMG" && same=yes
  local final; final=$(grep "^final" "$W/$name.bin.log")
  local boots; boots=$(grep -o "'boot_into': \[[^]]*\]" "$W/$name.bin.log")
  local verdict=PASS
  case $expect in
    ok) [[ $same == yes && $status == *"done"* && $res == *"boot0=0 nrst=1"* && $boots == *"'app']" ]] || verdict=FAIL ;;
    fail) [[ $status == *"FAILED"* && $res == *"boot0=0 nrst=1"* ]] || verdict=FAIL ;;
    refused) [[ $status == *"refused"* && $(grep -c "pin" "$W/$name.bin.log") -le 2 ]] || verdict=FAIL ;;
  esac
  [ $verdict == FAIL ] && fail=1
  printf '%-4s %-22s image_written=%-3s | %s\n      %s\n      model: %s %s\n' "$verdict" "$name" "$same" "$status" "$res" "$final" "$boots"
}
run blank_chip_ext_erase ok --erase 44
run blank_chip_std_erase ok --erase 43
run reflash_over_old_fw  ok --erase 44 --preload "$W/old_firmware.bin"
run no_bootloader_answer fail --fault silent
run read_protected       fail --fault rdp
run readback_mismatch    fail --fault corrupt_read
run wrong_chip           fail --fault wrong_pid
run write_nacked         fail --fault nack_write
run engine_running       refused -- running
exit $fail
