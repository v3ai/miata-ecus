#!/usr/bin/env python3
"""Resolves C/C++ expressions in a firmware ELF to memory probes (address, size, how to decode) using gdb and the
ELF's DWARF debug info, so the simulation can read rusEFI's live state (RPM, sensors, timing, config) straight from
emulated RAM. Nothing in the firmware changes.

usage: elf_probes.py <elf> <name=expression> ...  -> JSON on stdout
       name=expression may also be name=@symbol (address of a symbol from nm, read as a raw u32; a compiler suffix
       such as .lto_priv.0 is matched)
Each probe: {"addr": int, "size": int, "kind": "f32"|"f64"|"u8"|"u16"|"u32"|"i8"|"i16"|"i32"|"bytes", "scale": float}
scaled_channel<T, mult, div> fields are decoded with scale = div/mult.
"""
import json
import re
import subprocess
import sys

elf = sys.argv[1]
probes = dict(a.split('=', 1) for a in sys.argv[2:])
symbols = {probes.pop(k)[1:]: k for k in [k for k, v in probes.items() if v.startswith('@')]}
nm = {}
if symbols:
    for line in subprocess.run(['arm-none-eabi-nm', elf], capture_output=True, text=True).stdout.splitlines():
        f = line.split()
        if len(f) == 3:
            # exact name, or the name with a compiler suffix (LTO: name.lto_priv.0)
            base = f[2] if f[2] in symbols else f[2].split('.')[0]
            if base in symbols and symbols[base] not in nm:
                nm[symbols[base]] = {'addr': int(f[0], 16), 'size': 4, 'kind': 'u32', 'scale': 1.0, 'type': 'symbol ' + f[2]}
    missing = set(symbols.values()) - set(nm)
    if missing:
        sys.exit('symbols not found: ' + ', '.join(missing))
script = r'''
import gdb, json, re
out = {}
for name, expr in %s.items():
    try:
        v = gdb.parse_and_eval(expr)
        t = v.type.strip_typedefs()
        addr = int(v.address)
        size = t.sizeof
        scale = 1.0
        tname = str(v.type)
        m = re.match(r'scaled_channel<(.+?), (\d+), (\d+)>', tname)
        if m:
            inner = gdb.lookup_type(m.group(1)).strip_typedefs()
            scale = int(m.group(3)) / int(m.group(2))
            t = inner
        if t.code == gdb.TYPE_CODE_FLT:
            kind = 'f32' if size == 4 else 'f64'
        elif t.code in (gdb.TYPE_CODE_INT, gdb.TYPE_CODE_ENUM, gdb.TYPE_CODE_BOOL, gdb.TYPE_CODE_CHAR):
            signed = t.code in (gdb.TYPE_CODE_INT, gdb.TYPE_CODE_CHAR) and t.is_signed
            kind = ('i' if signed else 'u') + str(8 * size)
        elif t.code == gdb.TYPE_CODE_PTR:
            kind = 'u32'
        else:
            kind = 'bytes'
        out[name] = {'addr': addr, 'size': size, 'kind': kind, 'scale': scale, 'type': tname}
    except gdb.error as e:
        out[name] = {'error': str(e)}
print('PROBES' + json.dumps(out))
''' % repr(probes)
res = subprocess.run(['gdb', '-batch', '-nx', '-ex', 'python\n' + script + '\nend', elf], capture_output=True, text=True)
m = re.search(r'^PROBES(.*)$', res.stdout, re.M)
if not m:
    sys.exit('gdb failed:\n' + res.stdout + res.stderr)
data = json.loads(m.group(1))
data.update(nm)
bad = {k: v for k, v in data.items() if 'error' in v}
if bad:
    sys.exit('unresolved probes: ' + json.dumps(bad, indent=1))
json.dump(data, sys.stdout, indent=1)
