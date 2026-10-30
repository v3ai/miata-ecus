#!/usr/bin/env python3
"""Checks a main-MCU firmware build the way the hardware will see it:
  - OpenBLT bootloader at 0x08000000: vector table (stack in SRAM, reset handler inside the bootloader area);
  - rusEFI application at 0x08008000: vector table, and the CRC-32 + size header that rusEFI's OpenBLT verifies
    before jumping to it (bootloader/openblt_chibios/openblt_flash.cpp FlashVerifyChecksum);
  - the merged DFU image (bootloader + app) that is written at 0x08000000;
  - everything fits below rusEFI's settings sectors in the STM32F407VG's 1 MB flash.

usage: check_image.py <openblt .bin> <app .bin with CRC (build/rusefi_crc32.bin)> [merged .bin [app .hex]]

With the app's .hex (build/rusefi.hex), the merged image is compared with the app only at the addresses the firmware
defines. rusEFI's merge tool (hex2dfu) fills gaps between hex sections with leftover buffer data, which differs
between the standalone and the merged image; each carries a CRC over its own fill, so both are valid.
"""
import struct
import sys
import zlib

FLASH = 0x08000000
APP = 0x08008000
FLASH_END = FLASH + 1024 * 1024
SETTINGS = 0x080C0000            # rusEFI F4: configuration lives in the last two 128K sectors (10, 11)
SRAM = (0x20000000, 0x20020000)  # 128K SRAM (CCM at 0x10000000 is not valid for the initial stack)
ok = True


def hex_addresses(path):
    """Set of addresses an Intel hex file defines."""
    out, base = set(), 0
    for line in open(path):
        line = line.strip()
        if not line.startswith(':'):
            continue
        n, addr, typ = int(line[1:3], 16), int(line[3:7], 16), int(line[7:9], 16)
        if typ == 0:
            out.update(range(base + addr, base + addr + n))
        elif typ == 4:
            base = int(line[9:13], 16) << 16
        elif typ == 2:
            base = int(line[9:13], 16) << 4
    return out


def check(cond, msg):
    global ok
    print(('OK   ' if cond else 'FAIL ') + msg)
    ok &= bool(cond)


def vectors(img, base, end, name):
    sp, reset = struct.unpack_from('<II', img, 0)
    check(SRAM[0] < sp <= SRAM[1], f'{name}: initial stack 0x{sp:08x} is in SRAM')
    check(base <= (reset & ~1) < end and reset & 1, f'{name}: reset handler 0x{reset:08x} is Thumb code inside 0x{base:08x}..0x{end:08x}')


def openblt_accepts(app):
    """FlashVerifyChecksum(): CRC over [0, 0x1C) then [0x20, size); stored CRC at 0x1C, size at 0x20."""
    if app[:4] == b'\xff' * 4:
        return False, 'first word blank'
    crc_stored, size = struct.unpack_from('<II', app, 0x1C)
    if size > 1024 * 1024 - (APP - FLASH):
        return False, f'size {size} impossible'
    crc = zlib.crc32(app[:0x1C])
    crc = zlib.crc32(app[0x1C + 4:size], crc)
    return crc == crc_stored, f'stored 0x{crc_stored:08x}, computed 0x{crc:08x}, size {size}'


bl = open(sys.argv[1], 'rb').read()
app = open(sys.argv[2], 'rb').read()
check(len(bl) <= APP - FLASH, f'OpenBLT is {len(bl)} bytes, fits the {APP - FLASH} byte bootloader area')
vectors(bl, FLASH, APP, 'OpenBLT')
vectors(app, APP, SETTINGS, 'rusEFI app')
accepted, why = openblt_accepts(app)
check(accepted, 'OpenBLT accepts the app (CRC-32 + size header): ' + why)
check(APP + len(app) <= SETTINGS, f'app ends at 0x{APP + len(app):08x}, below the settings sectors at 0x{SETTINGS:08x} '
      f'({(SETTINGS - APP - len(app)) // 1024} KB spare)')

# corrupting one byte must make OpenBLT refuse the app (a half-written update stays in the bootloader)
bad = bytearray(app)
bad[len(bad) // 2] ^= 0xFF
check(not openblt_accepts(bytes(bad))[0], 'a corrupted app is refused by OpenBLT (stays in the bootloader for a re-flash)')

if len(sys.argv) > 3:
    merged = bytearray(open(sys.argv[3], 'rb').read())
    # rusEFI's bin/set_bl_bin_version.sh stamps 'BL10' into a reserved vector-table word (offset 0x24)
    check(merged[0x24:0x28] == b'BL10', f"merged image carries the bootloader version stamp {bytes(merged[0x24:0x28])!r}")
    merged[0x24:0x28] = bl[0x24:0x28]
    check(merged[:len(bl)] == bl, 'merged DFU image starts with this OpenBLT at 0x08000000')
    inside = merged[APP - FLASH:APP - FLASH + len(app)]
    if len(sys.argv) > 4:
        defined = hex_addresses(sys.argv[4])
        crc_word = range(APP + 0x1C, APP + 0x20)      # written by hex2dfu, differs with the gap fill
        diff = [a for a in defined if a not in crc_word and APP <= a < APP + len(app)
                and inside[a - APP] != app[a - APP]]
        gaps = len(app) - sum(1 for a in defined if APP <= a < APP + len(app))
        check(not diff, f'merged DFU image holds this app at 0x08008000 ({len(defined)} defined bytes compared, '
              f'{gaps} gap-fill bytes ignored)' + (f'; first difference at 0x{diff[0]:08x}' if diff else ''))
    else:
        check(inside == app, 'merged DFU image holds this app at 0x08008000')
    accepted, why = openblt_accepts(bytes(merged[APP - FLASH:]))
    check(accepted, 'OpenBLT accepts the app inside the merged image: ' + why)
sys.exit(0 if ok else 1)
