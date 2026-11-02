"""Finds where ChibiOS's ARMv7-M __port_irq_epilogue tests SCB->ICSR.RETTOBASE in an ELF and prints the Renode
monitor commands that supply that bit.

Why: Renode 1.15's NVIC model never sets ICSR.RETTOBASE (bit 11, "no other exception active"). ChibiOS reschedules
on interrupt exit only when that bit is set, so without it a thread woken from an interrupt never runs. The commands
record, at the entry of every exception handler, whether that exception will return to Thread mode (EXC_RETURN bit
3), and at each `ands rX, rY, #0x800` that tests the bit (in __port_irq_epilogue and in every copy the compiler
inlined into a handler) set it in the register exactly when that is so, which is what the hardware reports. The
firmware is unchanged.

usage: chibios_rettobase.py <elf> [cpu name, default cpu]
"""
import re, subprocess, sys

elf = sys.argv[1]
cpu = sys.argv[2] if len(sys.argv) > 2 else 'cpu'
syms = subprocess.run(['arm-none-eabi-nm', elf], capture_output=True, text=True).stdout
# Every place that tests RETTOBASE: __port_irq_epilogue itself and the copies the compiler inlined into interrupt
# handlers (LTO does this on the wideband build). The test is `ands rX, rY, #2048` right after `ldr rY, [rZ, #4]`
# (rZ = SCB base 0xE000ED00, offset 4 = ICSR).
dis = subprocess.run(['arm-none-eabi-objdump', '-d', '--no-show-raw-insn', elf], capture_output=True, text=True).stdout
lines = dis.splitlines()
tests = []
for i, line in enumerate(lines):
    hit = re.match(r'^\s*([0-9a-f]+):\s+ands(?:\.w)?\s+(r\d+), (r\d+), #2048', line)
    if not hit:
        continue
    prev = ' '.join(lines[max(0, i - 3):i])
    if re.search(r'ldr(?:\.w)?\s+' + hit.group(3) + r', \[r\d+, #4\]', prev):
        tests.append((int(hit.group(1), 16), int(hit.group(2)[1:])))
if not tests:
    sys.exit(f'{elf}: no RETTOBASE test found')
# On entry to every exception handler (a PC hook on each handler in the vector table: by then the hardware has set
# ICSR.VECTACTIVE and EXC_RETURN in LR), record per vector whether it will return to Thread mode (EXC_RETURN bit 3).
# At the RETTOBASE test, look up the active vector: RETTOBASE is set exactly when the active exception returns to
# Thread mode, i.e. no other exception is active. (Counting entries and exits does not work: Renode fires no exit
# hook when ChibiOS's SVC handler returns, and its interrupt-begin hook runs before the entry.)
import struct, tempfile, os
ICSR = 0xE000ED04
vec = int(re.search(r'^([0-9a-f]+) [A-Za-z] _vectors$', syms, re.M).group(1), 16)
sec = None
for line in subprocess.run(['arm-none-eabi-objdump', '-h', elf], capture_output=True, text=True).stdout.splitlines():
    f = line.split()
    if len(f) >= 7 and f[0].isdigit() and int(f[3], 16) <= vec < int(f[3], 16) + int(f[2], 16):
        sec = f[1]
tmp = tempfile.mktemp()
subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary', '-j', sec, elf, tmp], check=True)
raw = open(tmp, 'rb').read(); os.remove(tmp)
words = struct.unpack('<%dI' % (len(raw) // 4), raw[:len(raw) // 4 * 4])
handlers = sorted({w & ~1 for w in words[1:98] if w & 1 and 0x08000000 <= w < 0x08200000})
record = (f'import sys; d = sys.__dict__.setdefault(\'base_{cpu}\', {{}}); '
          f'd[self.GetMachine().SystemBus.ReadDoubleWord({ICSR:#x}) & 0x1FF] = (self.GetRegisterUnsafe(14).RawValue & 8) != 0')
for h in handlers:
    print(f'{cpu} AddHook {h:#x} "{record}"')
for addr, reg in tests:
    print(f'{cpu} AddHook {addr:#x} "import sys; from Antmicro.Renode.Peripherals.CPU import RegisterValue; '
          f'd = sys.__dict__.get(\'base_{cpu}\', {{}}); '
          f'self.SetRegisterUnsafe({reg}, RegisterValue.Create(self.GetRegisterUnsafe({reg}).RawValue | 0x800, 32)) '
          f'if d.get(self.GetMachine().SystemBus.ReadDoubleWord({ICSR:#x}) & 0x1FF, False) else None"')
