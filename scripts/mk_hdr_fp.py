"""Write the Mazda ECU harness-header footprints with OEM terminal names (1A, 1B, ... 3Z).

TE 178780-1 (76 pins: plug 1 = 22, plug 4 = 12 (not used by the OEM harness), plug 2 = 16, plug 3 = 26)
  geometry from the Hellen NA8-96 board (hellen-one-common:178780-1);
TE 176122-6 (64 pins: 22 + 16 + 26) geometry from rusefi_lib 176122-6_2nd.
Within every plug the lower row (nearest the board centre) carries A, C, E ... and the upper row
B, D, F ... (checked against the Hellen board's net names). Footprint origin = terminal 1A.
"""
import re, sys
import pcbnew

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mb', 'ecu_mb.pretty') + '/'
# reference designs the header geometry is read from (rusEFI hellen-one boards, rusefi KiCad library)
REF = os.environ.get('MIATA_REF', '/home/claude/ref')
LIBS = os.environ.get('RUSEFI_LIBS', '/home/claude/tools/KiCAD-libraries')
L = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def names(plug, n):
    lo = [f'{plug}{c}' for c in L[0::2][:(n + 1) // 2]]
    hi = [f'{plug}{c}' for c in L[1::2][:n // 2]]
    return lo, hi


def write(name, desc, pins, pegs, lines, model=''):
    x0, y0 = pins[0][1], pins[0][2]          # 1A
    out = [f'(footprint "{name}" (version 20221018) (generator pcbnew) (layer "F.Cu")',
           f'  (descr "{desc}")', '  (attr through_hole)',
           '  (fp_text reference "J1" (at 0 3 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
           f'  (fp_text value "{name}" (at 0 5 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))']
    for (a, b, c, d) in lines:
        out.append(f'  (fp_line (start {a - x0:.4f} {b - y0:.4f}) (end {c - x0:.4f} {d - y0:.4f}) (stroke (width 0.381) (type solid)) (layer "F.SilkS"))')
    xs = [p[1] - x0 for p in pins] + [p[0] - x0 for p in pegs]
    for (a, b, c, d) in lines:
        xs += [a - x0, c - x0]
    ys = [p[2] - y0 for p in pins] + [y - y0 for x, y in pegs]
    for (a, b, c, d) in lines:
        ys += [b - y0, d - y0]
    out.append(f'  (fp_rect (start {min(xs) - 0.5:.3f} {min(ys) - 0.5:.3f}) (end {max(xs) + 0.5:.3f} {max(ys) + 1.6:.3f}) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))')
    for nm, x, y in pins:
        out.append(f'  (pad "{nm}" thru_hole circle (at {x - x0:.4f} {y - y0:.4f}) (size 1.8 1.8) (drill 1.1) (layers "*.Cu" "*.Mask"))')
    for x, y in pegs:
        out.append(f'  (pad "" np_thru_hole circle (at {x - x0:.4f} {y - y0:.4f}) (size 3.5 3.5) (drill 3.5) (layers "*.Cu" "*.Mask"))')
    for nm, x, y in pins:
        if nm.endswith('A') or nm[-1] in 'BZ' or nm in ('1V', '2P', '4L'):
            out.append(f'  (fp_text user "{nm}" (at {x - x0:.4f} {y - y0 + (1.8 if y == y0 else -1.8):.4f}) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))')
    out.append(')')
    open(OUT + name + '.kicad_mod', 'w').write('\n'.join(out) + '\n')
    print('wrote', name, len(pins), 'pins', len(pegs), 'pegs')


# ---- 178780-1 from the Hellen NA8-96 board
b = pcbnew.LoadBoard(REF + '/miata/hellen-NA8-96/hellen64_NA8_96.kicad_pcb')
fp = b.FindFootprintByReference('P2'); o = fp.GetPosition()
pad = {p.GetNumber(): (pcbnew.ToMM(p.GetPosition().x - o.x), pcbnew.ToMM(p.GetPosition().y - o.y)) for p in fp.Pads() if p.GetNumber()}
pegs = [(pcbnew.ToMM(p.GetPosition().x - o.x), pcbnew.ToMM(p.GetPosition().y - o.y)) for p in fp.Pads() if not p.GetNumber()]
lines = []
for g in fp.GraphicalItems():
    g = g.Cast()
    if hasattr(g, 'GetShapeStr') and g.GetShapeStr() == 'Line':
        lines.append((pcbnew.ToMM(g.GetStart().x - o.x), pcbnew.ToMM(g.GetStart().y - o.y),
                      pcbnew.ToMM(g.GetEnd().x - o.x), pcbnew.ToMM(g.GetEnd().y - o.y)))
pins = []
# OEM naming for 1996-97: 1 (22) | 2 (12, no harness plug) | 3 (16) | 4 (26); Hellen calls them 1 | 4 | 2 | 3
for plug, n, lo_nums, hi_nums in (('1', 22, range(1, 12), range(12, 23)), ('2', 12, range(65, 71), range(71, 77)),
                                   ('3', 16, range(23, 31), range(31, 39)), ('4', 26, range(39, 52), range(52, 65))):
    lo, hi = names(plug, n)
    pins += [(nm, *pad[str(k)]) for nm, k in zip(lo, lo_nums)]
    pins += [(nm, *pad[str(k)]) for nm, k in zip(hi, hi_nums)]
pins.sort(key=lambda p: (p[0][0] != '1', p[0]))     # 1A first (origin)
write('TE_178780-1_76P', 'TE 178780-1 Mazda 76-pin ECU header (OEM plugs 1=22, 2=12 unused, 3=16, 4=26), 1996-97 Miata',
      pins, pegs, lines)

# ---- 176122-6 from rusefi_lib
s = open(LIBS + '/rusefi_lib.pretty/176122-6_2nd.kicad_mod').read()
pp = re.findall(r'\(pad "?([^" ]*)"? (\w+) (\w+) \(at ([-\d.]+) ([-\d.]+)', s)
pad = {p[0]: (float(p[3]), float(p[4])) for p in pp if p[0]}
pegs = [(float(p[3]), float(p[4])) for p in pp if not p[0]]
lines = [tuple(float(v) for v in m) for m in re.findall(r'fp_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\)', s)]
pins = []
for plug, n, lo_nums, hi_nums in (('1', 22, range(1, 12), range(12, 23)), ('2', 16, range(23, 31), range(31, 39)),
                                   ('3', 26, range(39, 52), range(52, 65))):
    lo, hi = names(plug, n)
    pins += [(nm, *pad[str(k)]) for nm, k in zip(lo, lo_nums)]
    pins += [(nm, *pad[str(k)]) for nm, k in zip(hi, hi_nums)]
pins.sort(key=lambda p: (p[0][0] != '1', p[0]))
write('TE_176122-6_64P', 'TE 176122-6 Mazda 64-pin ECU header (22+16+26), 1999-2000 Miata; pads named by OEM terminal',
      pins, pegs, lines)


# ---- 72-pin NB2 header (TE 353830-5 / 1123038-2): OEM plugs 2 (17), 3 (24), 4 (31) in three rows.
# Geometry = sections 2-4 of the Hellen NB2 122-pos footprint (identical to rusefi_lib 1123038-2: same
# 23/27/22 pins per row and the same two pegs). Terminal names from the Hellen board's net names and the
# 2005 Mazda workshop manual terminal table. Rows: y 0 (outer), 3.6, 8.0 (inner).
NB2 = {
    (0.0, '2'): 'C F I O R', (3.6, '2'): 'B E H K N Q', (8.0, '2'): 'A D G J M P',
    (0.0, '3'): 'C F I L O T W Z', (3.6, '3'): 'B E H K N Q S V Y', (8.0, '3'): 'A D J M P U X',
    (0.0, '4'): 'C F I K N T W AB AE AH', (3.6, '4'): 'B E H J M P S V X AA AD AG', (8.0, '4'): 'A D L O R U Z AC AF',
}
b2 = pcbnew.LoadBoard(REF + '/miata/hellen-NB2/hellen72_NB2.kicad_pcb')
fp = b2.FindFootprintByReference('P2'); o = fp.GetPosition()
pp = [(pcbnew.ToMM(p.GetPosition().x - o.x), pcbnew.ToMM(p.GetPosition().y - o.y), p.GetNumber()) for p in fp.Pads()]
X0 = 52.1                                            # first column of OEM plug 2
sect = lambda x: '2' if x < 67 else ('3' if x < 93 else '4')
pins = []
for row in (0.0, 3.6, 8.0):
    for sc in '234':
        xs = sorted(x for x, y, n in pp if n and abs(y - row) < 0.05 and x > X0 - 0.5 and sect(x) == sc)
        letters = NB2[(row, sc)].split()
        assert len(xs) == len(letters), (row, sc, len(xs), len(letters))
        pins += [(sc + L, x, row) for x, L in zip(xs, letters)]
assert len(pins) == 72 and len({p[0] for p in pins}) == 72
pegs = [(x, y) for x, y, n in pp if not n and x > X0]
pins.sort(key=lambda p: (p[0] != '2A', p[0]))          # 2A (inner row, first column) is the origin
lines = [(X0, -16.0, X0 + 72.1, -16.0), (X0, 12.75, X0 + 72.1, 12.75), (X0, -16.0, X0, 12.75), (X0 + 72.1, -16.0, X0 + 72.1, 12.75)]
write('TE_353830-5_72P', 'TE 353830-5 (alt. 1123038-2) Mazda 72-pin ECU header, 2001-05 Miata: OEM plugs 2 (17), 3 (24), 4 (31)',
      pins, pegs, lines)
