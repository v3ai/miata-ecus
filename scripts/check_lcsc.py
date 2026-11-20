#!/usr/bin/env python3
"""Every LCSC number on every board against what it really is (scripts/mpn.json, read from LCSC / JLCPCB).

R110 was fitted for two revisions with a 0.62 ohm part where the schematic said 62 ohm: the number was a real part,
just not that value. This catches that class of mistake at build time. For each part with an LCSC number, on the
daughterboard and on each motherboard year module:
  - the number must be in mpn.json, marked as matching, and not superseded;
  - for resistors, capacitors and inductors, the value written in the schematic must be the value in
    the part's description, and the footprint's size code (0402, 0603, 0805, 1206, 1210) its package;
  - for everything else but connectors, jumpers and switches (whose value is their job, 'INJ3'), the schematic value
    must name the part (its maker's part number, or a value it contains).
Exits non-zero on any mismatch.

usage: python3 scripts/check_lcsc.py
"""
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)
MPN = json.load(open('mpn.json'))
YEARS = ['mb_na6', 'mb_na96', 'mb_nb1', 'mb_nb2']

MULT = {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6, 'm': 1e-3, 'k': 1e3, 'K': 1e3, 'M': 1e6, 'R': 1.0, '': 1.0}


def num(text):
    """'4.7k' / '4k7' / '62' / '0R' / '100n' / '10u' / '2.2uH' -> float (ohms, farads, henries)."""
    t = text.split('/')[0].strip().replace('Ω', '').replace('ohm', '').replace(' ', '')   # '10u/50V' -> '10u'
    t = re.sub(r'(F|H)$', '', t)
    m = re.fullmatch(r'(\d+)([pnuµmkKMR])(\d+)', t)           # 4k7, 2R2
    if m:
        return float(f'{m.group(1)}.{m.group(3)}') * MULT[m.group(2)]
    m = re.fullmatch(r'(\d+(?:\.\d+)?)([pnuµmkKMR]?)', t)
    return float(m.group(1)) * MULT[m.group(2)] if m else None


def desc_value(desc):
    """The value in an mpn.json description, in base units, or None."""
    d = desc.replace('mohm', 'mΩ').replace('milliohm', 'mΩ')
    if re.search(r'[Ii]nductor', d):
        m = re.search(r'(\d+(?:\.\d+)?)\s*([nuµm])H', d)
        return float(m.group(1)) * MULT[m.group(2)] if m else None
    if re.search(r'MLCC|[Cc]apacitor', d):
        m = re.search(r'(\d+(?:\.\d+)?)\s*([pnuµ])F', d)
        return float(m.group(1)) * MULT[m.group(2)] if m else None
    if re.search(r'\b0 ohm\b', d):
        return 0.0
    m = re.search(r'(\d+(?:\.\d+)?)\s*(m)Ω', d)
    if m:
        return float(m.group(1)) * 1e-3
    m = re.search(r'(\d+(?:\.\d+)?)\s*([kKM]?)\s*(?:ohm|R\b|Ω)', d) or re.search(r'\b(\d+(?:\.\d+)?)([kKM])\b', d)
    if m and re.search(r'[Rr]esistor', d):
        return float(m.group(1)) * MULT[m.group(2)]
    m = re.search(r'(\d+(?:\.\d+)?)\s*([pnuµ])F', d)
    if m:
        return float(m.group(1)) * MULT[m.group(2)]
    m = re.search(r'(\d+(?:\.\d+)?)\s*([nuµm])H', d)
    if m:
        return float(m.group(1)) * MULT[m.group(2)]
    m = re.search(r'(\d+)\s*ohm\s*@', d)                     # ferrite bead: impedance at 100 MHz
    if m:
        return float(m.group(1))
    return None


SIZE = re.compile(r'\b(0201|0402|0603|0805|1206|1210|1812|2010|2512)\b')
SIZE_FP = re.compile(r'_(0201|0402|0603|0805|1206|1210|1812|2010|2512)_')


def check(board, parts, errors):
    n = 0
    for p in parts:
        code = (p.get('lcsc') or '').strip()
        if not code:
            continue
        n += 1
        where = f'{board} {p["ref"]} ({p["value"]}, {code})'
        m = MPN.get(code)
        if not m:
            errors.append(f'{where}: not in mpn.json; look it up and add it'); continue
        if not m.get('match', True) or m.get('superseded'):
            errors.append(f'{where}: mpn.json marks it wrong or superseded: {m.get("note", "")}'); continue
        desc, ref, fp = m.get('desc', ''), p['ref'], p.get('fp', '')
        if re.match(r'(J|JP|JD|SW|H|TP|BT)\d', ref):
            continue          # connectors, jumpers, switches: the value is their job ('INJ3', 'USB-C'), not a part name
        passive = re.match(r'(R|C|L)\d', ref) \
            and re.search(r'[Rr]esistor|MLCC|[Cc]apacitor|[Ff]errite|[Ii]nductor', desc) \
            and not re.search(r'array', desc)
        if passive:
            want, got = num(p['value']), desc_value(desc)
            if want is None or got is None:
                errors.append(f'{where}: cannot read a value from {p["value"]!r} / {desc!r}')
            elif abs(want - got) > 1e-9 + 0.001 * max(abs(want), abs(got)):
                errors.append(f'{where}: schematic value {p["value"]} but the part is {desc!r}')
            s1, s2 = SIZE.search(desc), SIZE_FP.search(fp + '_')
            if s1 and s2 and s1.group(1) != s2.group(1):
                errors.append(f'{where}: footprint {fp} but the part is {s1.group(1)} ({desc!r})')
        else:
            v = re.sub(r'[^A-Z0-9]', '', p['value'].upper())
            mpn = re.sub(r'[^A-Z0-9]', '', (m.get('mpn') or '').upper())
            hay = re.sub(r'[^A-Z0-9]', '', (desc + ' ' + (m.get('mpn') or '')).upper())
            if v and not (v in hay or (mpn and (mpn.startswith(v) or v.startswith(mpn[:max(6, len(v) - 3)])))):
                errors.append(f'{where}: schematic value {p["value"]!r} does not name {m.get("mpn")!r} ({desc!r})')
    return n


def main():
    errors = []
    import design
    n = check('daughterboard', design.parts, errors)
    total = n
    for y in YEARS:
        mod = importlib.import_module(y)
        total += check(y, mod.build_parts(), errors)
    for e in errors:
        print('FAIL', e)
    print(f'{total} parts with an LCSC number checked against mpn.json: {len(errors)} mismatches')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
