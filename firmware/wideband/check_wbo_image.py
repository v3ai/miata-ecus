"""Checks the wideband image for the STM32F103C8: fits the 56 KB app area, RAM fits 20 KB, vector table sane.
usage: check_wbo_image.py wideband.elf wideband.bin"""
import struct, subprocess, sys
elf, binf = sys.argv[1], sys.argv[2]
FLASH, APP, RAM_END = 0x08000000, 56 * 1024, 0x20000000 + 20 * 1024
img = open(binf, 'rb').read()
sp, reset = struct.unpack('<II', img[:8])
syms = {}
for line in subprocess.run(['arm-none-eabi-nm', elf], capture_output=True, text=True).stdout.splitlines():
    p = line.split()
    if len(p) == 3:
        syms[p[2]] = int(p[0], 16)
errs = []
if len(img) > APP:
    errs.append(f'image {len(img)} bytes > {APP} (app area; the last 8 KB hold settings)')
if not (0x20000000 < sp <= RAM_END):
    errs.append(f'initial SP 0x{sp:08x} outside 20 KB RAM')
if not (FLASH <= reset < FLASH + len(img)) or not reset & 1:
    errs.append(f'reset vector 0x{reset:08x} not a Thumb address inside the image')
heap_base = syms.get('__heap_base__', 0)
heap_end = syms.get('__heap_end__', RAM_END)
if heap_base and heap_base > RAM_END:
    errs.append(f'static RAM ends at 0x{heap_base:08x}, past 20 KB')
print(f'wideband image: {len(img)} bytes of {APP} ({100 * len(img) / APP:.0f} %), '
      f'static RAM to 0x{heap_base:08x} ({(heap_base - 0x20000000) if heap_base else 0} of {20 * 1024} bytes), '
      f'SP 0x{sp:08x}, reset 0x{reset:08x}')
for e in errs:
    print('ERROR', e)
sys.exit(1 if errs else 0)
