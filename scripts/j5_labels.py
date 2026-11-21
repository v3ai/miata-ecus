"""j5_labels.py <motherboard.kicad_pcb (KiCad 7), rev 0.16 / 0.12> <out.kicad_pcb> <8995 | 9697 | 9900 | 0105>

Names the add-on header J5's pins on the silkscreen on both sides of the header, outside its shroud, where they stay
readable with the ribbon cable's plug fitted: one vertical name per pin, in line with its pin column. The odd pins'
names stand above the header (their row is the one nearer the daughterboard) and read up from it; the even pins'
names hang below it (the row nearer the board edge). Pin numbers outside the shroud's ends: 1 / 2 at the right, 19 / 20
at the left; they replace the footprint's pin-1 triangle, which sat where pin 1's name goes. Text 1.0 mm high, 0.15 mm
lines (JLCPCB's minimum). The names are checked against the nets on J5's pads, so they cannot outlive a pinout change.

To make room, R35 / R36 (the flex-fuel input's pull-up and the nitrous input's pull-down), which sat where the odd
names go, move to the free board left of J5, level with its two rows (MOVES); the ground stitching vias in the even
names' row (y 188) that would sit under a name move sideways onto the gap between two columns, and J5's reference
moves below the pin numbers at the right end. Also sets the board
title's revision (REV). The copper is joined again by scripts/j5_mb.sh (this is its first step)."""
import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from castellate_mb import blocks, move, ref_of   # noqa: E402

REV = {'8995': '0.18', '9697': '0.14', '9900': '0.14', '0105': '0.14'}
# same place on every board: horizontal, in the free strips between the tracks that pass J5's left end between its rows
MOVES = {'R35': (156.0, 178.25, 0), 'R36': (156.0, 180.79, 180)}     # R36 turned: its signal pad faces J5
# pin -> (silkscreen name, net); the names are scripts/annotate.py's AUX_NAMES in ASCII
PINS = {1: ('IGN3', 'OUT_IGN3'), 2: ('IGN4', 'OUT_IGN4'), 3: ('BOOST', 'OUT_BOOST'), 4: ('ALT', 'OUT_ALT'),
        5: ('RELAY', 'OUT_MAINRLY'), 6: ('KNOCK', 'IN_KNOCK'), 7: ('VR1+', 'VR1_P'), 8: ('VR1-', 'VR1_N'),
        9: ('VR2+', 'VR2_P'), 10: ('VR2-', 'VR2_N'), 11: ('AFR', 'IN_AFR'), 12: ('FLEX', 'IN_FLEX'),
        13: ('N2O', 'IN_N2O'), 14: ('+5V', 'V5_EXT'), 15: ('+12V', 'AUX_VBAT'), 16: ('GND', 'GND'),
        17: ('GND', 'GND'), 18: ('GND', 'GND'), 19: ('CANH', 'CAN_H'), 20: ('CANL', 'CAN_L')}
NUMBERS = ('1', '2', '19', '20')
PITCH = 2.54
ODD_Y = 174.5           # the odd names start here (above the shroud's outline, y 174.82 at its top edge) and run up
EVEN_Y = 185.2          # the even names start here (below the shroud's courtyard, y 184.51) and run down
VIA_ROW = 188.0         # the stitching vias under the even names
H, T = 1.0, 0.15


def fmt(v):
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def text(t, x, y, angle=90, justify='left'):
    # at 90 degrees the text reads upwards: justify left starts it at (x, y) and runs it up the board, justify right
    # ends it at (x, y), so it runs down the board from there
    return (f'  (gr_text "{t}" (at {fmt(x)} {fmt(y)}{" " + str(angle) if angle else ""}) (layer "F.SilkS") '
            f'(tstamp {uuid.uuid4()})\n'
            f'    (effects (font (size {fmt(H)} {fmt(H)}) (thickness {fmt(T)})) (justify {justify}))\n  )\n')


def main(src, dst, short):
    t = open(src).read()
    assert 'gr_text "IGN3"' not in t, 'already labelled: start from the rev 0.16 / 0.12 board'
    i = t.index('(fp_text reference "J5"')
    a = t.rfind('\n  (footprint', 0, i) + 1
    b = t.find('\n  (footprint', i) + 1
    fp = t[a:b]
    m = re.search(r'\n    \(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', fp)
    fx, fy, fa = float(m[1]), float(m[2]), float(m[3] or 0)
    assert fa in (-90, 270), fa
    pads = {}
    for m in re.finditer(r'\(pad "(\d+)" thru_hole \w+ \(at ([-\d.]+) ([-\d.]+)[^)]*\)(?:(?!\(pad ).)*?\(net \d+ "([^"]*)"\)',
                         fp, re.S):
        lx, ly = float(m[2]), float(m[3])
        pads[int(m[1])] = (fx - ly, fy + lx, m[4])           # footprint turned -90 degrees: (x, y) -> (-y, x)
    assert len(pads) == 20, len(pads)
    for n, (name, net) in PINS.items():
        assert pads[n][2].split('/')[-1] == net, (n, pads[n][2], net)    # local nets carry their sheet path
    cols = sorted({round(pads[n][0], 3) for n in pads})
    assert len(cols) == 10 and all(abs(cols[k + 1] - cols[k] - PITCH) < 1e-3 for k in range(9)), cols
    y_odd, y_even = pads[1][1], pads[2][1]
    assert abs(y_even - y_odd - PITCH) < 1e-3                  # odd row above the even row

    # the pin-1 triangle: the footprint's three silkscreen lines beyond pin 1's end of the shroud (local x < -3.5)
    lines = list(re.finditer(r'    \(fp_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\)(?:(?!\n    \().)*?'
                             r'\(layer "F\.SilkS"\)(?:(?!\n    \().)*\n', fp, re.S))
    tri = [q for q in lines if max(float(q[1]), float(q[3])) < -3.5 and all(abs(float(v)) < 1 for v in (q[2], q[4]))]
    assert len(tri) == 3, [q[0] for q in tri]
    for q in sorted(tri, key=lambda q: -q.start()):
        fp = fp[:q.start()] + fp[q.end():]
    t = t[:a] + fp + t[b:]

    # R35 / R36 move left of J5
    done = []
    for a2, b2 in sorted(blocks(t, 'footprint'), reverse=True):
        r = ref_of(t[a2:b2])
        if r in MOVES:
            t = t[:a2] + move(t[a2:b2], *MOVES[r]) + t[b2:]
            done.append(r)
    assert sorted(done) == sorted(MOVES), done

    # stitching vias under an even name move onto the nearest gap between columns
    gaps = [c + PITCH / 2 for c in cols] + [cols[0] - PITCH / 2]
    moved = []

    def mv(q):
        x = float(q[1])
        if not cols[0] - 2 < x < cols[-1] + 2 or min(abs(c - x) for c in cols) >= 1.2:   # half a name + via ring
            return q[0]
        nx = min(gaps, key=lambda g: abs(g - x))
        moved.append((x, round(nx, 2)))
        return f'(via (at {fmt(nx)} {fmt(VIA_ROW)}) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net {q[2]})'
    gnd = re.search(r'\(net (\d+) "GND"\)', t)[1]
    t = re.sub(r'\(via \(at ([-\d.]+) ' + fmt(VIA_ROW) + r'\) \(size 0\.6\) \(drill 0\.3\) \(layers "F\.Cu" "B\.Cu"\) \(net (' + gnd + r')\)',
               mv, t)

    # J5's reference stood upright at the shroud's right end, where the pin numbers go: it moves below them, level
    t, n = re.subn(r'\(fp_text reference "J5" \(at 1\.27 -6\.1 -90\)', '(fp_text reference "J5" (at 4.5 -6.97)', t)
    assert n == 1, n

    labels = ''.join(text(PINS[n][0], pads[n][0], ODD_Y, justify='left') if n % 2 else
                     text(PINS[n][0], pads[n][0], EVEN_Y, justify='right') for n in PINS)
    right, left = 194.4, 159.6                                  # just outside the shroud's ends (courtyard 159.93-194.07)
    labels += (text('1', right, y_odd, 0, 'left') + text('2', right, y_even, 0, 'left') +
               text('19', left, y_odd, 0, 'right') + text('20', left, y_even, 0, 'right'))
    k = t.rindex('\n)')
    t = t[:k + 1] + labels + t[k + 1:]
    t, n = re.subn(r'(\(gr_text "Miata ECU motherboard [^"]*  rev )[\d.]+"', lambda q: q[1] + REV[short] + '"', t)
    assert n == 1, n
    open(dst, 'w').write(t)
    print(f'{short}: J5 pin names on both sides (20 names, 4 pin numbers), R35 / R36 moved left of J5, pin-1 triangle '
          f'removed, stitching vias moved {moved}, rev {REV[short]}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
