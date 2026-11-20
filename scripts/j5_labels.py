"""j5_labels.py <motherboard.kicad_pcb (KiCad 7)> <out.kicad_pcb> <8995 | 9697 | 9900 | 0105>

Names the add-on header J5's pins on the silkscreen, where they stay readable with the ribbon cable's plug fitted:
below the header's shroud, one vertical name per pin column. The band nearer the shroud names the even pins (the row
nearer the board edge), the band below it the odd pins (the row nearer the daughterboard); a key at the left end says
which band is which, and pin 1 keeps the footprint's triangle. Text 1.0 mm high, 0.15 mm lines (JLCPCB's minimum).

The ground stitching vias in the even band's row (y 188) that would sit under a name move sideways onto the gap
between two columns. The pin names are checked against the nets on J5's pads, so they cannot outlive a pinout change.
Afterwards the zones need a refill (KiCad 9: load, ZONE_FILLER, save, then backport_copper.py into this file).
U4's reference moves to U4's right, out of the way. Also sets the board title's revision (REV)."""
import re
import sys
import uuid

REV = {'8995': '0.17', '9697': '0.13', '9900': '0.13', '0105': '0.13'}
# pin -> (silkscreen name, net); the names are scripts/annotate.py's AUX_NAMES in ASCII
PINS = {1: ('IGN3', 'OUT_IGN3'), 2: ('IGN4', 'OUT_IGN4'), 3: ('BOOST', 'OUT_BOOST'), 4: ('ALT', 'OUT_ALT'),
        5: ('RELAY', 'OUT_MAINRLY'), 6: ('KNOCK', 'IN_KNOCK'), 7: ('VR1+', 'VR1_P'), 8: ('VR1-', 'VR1_N'),
        9: ('VR2+', 'VR2_P'), 10: ('VR2-', 'VR2_N'), 11: ('AFR', 'IN_AFR'), 12: ('FLEX', 'IN_FLEX'),
        13: ('N2O', 'IN_N2O'), 14: ('+5V', 'V5_EXT'), 15: ('+12V', 'AUX_VBAT'), 16: ('GND', 'GND'),
        17: ('GND', 'GND'), 18: ('GND', 'GND'), 19: ('CANH', 'CAN_H'), 20: ('CANL', 'CAN_L')}
PITCH = 2.54
EVEN_Y = 185.2          # the even names start here (just below the shroud's courtyard, y 184.51) and run down
ODD_Y = 192.0           # the odd names: below the even band and clear of the V5_SENS vias at y 191.3-191.5
VIA_ROW = 188.0         # the stitching vias in the even band
H, T = 1.0, 0.15


def fmt(v):
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def text(t, x, y):
    # rotated 90 degrees: reads upwards; justify right puts the text's end at (x, y), so it runs down the board from y
    return (f'  (gr_text "{t}" (at {fmt(x)} {fmt(y)} 90) (layer "F.SilkS") (tstamp {uuid.uuid4()})\n'
            f'    (effects (font (size {fmt(H)} {fmt(H)}) (thickness {fmt(T)})) (justify right))\n  )\n')


def main(src, dst, short):
    t = open(src).read()
    # J5's pads: position and net, from the footprint (KiCad 7 stores pad positions relative to the footprint)
    i = t.index('(fp_text reference "J5"')
    a = t.rfind('\n  (footprint', 0, i)
    b = t.find('\n  (footprint', i)
    fp = t[a:b]
    fx, fy, fa = (lambda m: (float(m[1]), float(m[2]), float(m[3] or 0)))(re.search(r'\n    \(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', fp))
    assert fa in (-90, 270), fa
    pads = {}
    for m in re.finditer(r'\(pad "(\d+)" thru_hole \w+ \(at ([-\d.]+) ([-\d.]+)[^)]*\)(?:(?!\(pad ).)*?\(net \d+ "([^"]*)"\)', fp, re.S):
        lx, ly = float(m[2]), float(m[3])
        pads[int(m[1])] = (fx - ly, fy + lx, m[4])           # footprint turned -90 degrees: (x, y) -> (-y, x)
    assert len(pads) == 20, len(pads)
    for n, (name, net) in PINS.items():
        assert pads[n][2].split('/')[-1] == net, (n, pads[n][2], net)    # local nets carry their sheet path
    cols = sorted({round(pads[n][0], 3) for n in pads})
    assert len(cols) == 10 and all(abs(cols[k + 1] - cols[k] - PITCH) < 1e-3 for k in range(9)), cols
    assert abs(pads[1][1] - pads[2][1] + PITCH) < 1e-3          # odd row above the even row

    # stitching vias under a name move onto the nearest gap between columns
    gaps = [cols[0] - PITCH / 2 - PITCH] + [c + PITCH / 2 for c in cols]   # incl. the gap left of the key column
    key_x = cols[0] - PITCH
    moved = []

    def mv(m):
        x = float(m[1])
        near = min([key_x] + cols, key=lambda c: abs(c - x))
        if abs(near - x) >= 1.0:                                # text half-width 0.6 + via ring 0.3 + 0.1
            return m[0]
        nx = min(gaps, key=lambda g: abs(g - x))
        moved.append((x, round(nx, 2)))
        return f'(via (at {fmt(nx)} {fmt(VIA_ROW)}) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net {m[2]})'
    gnd = re.search(r'\(net (\d+) "GND"\)', t)[1]
    t = re.sub(r'\(via \(at ([-\d.]+) ' + fmt(VIA_ROW) + r'\) \(size 0\.6\) \(drill 0\.3\) \(layers "F\.Cu" "B\.Cu"\) \(net (' + gnd + r')\)',
               lambda m: mv(m) if cols[0] - 3 < float(m[1]) < cols[-1] + 1.5 else m[0], t)

    # U4's reference sat above U4, where the VR1+ name now ends: it moves to U4's right, before R3
    t, n = re.subn(r'\(fp_text reference "U4" \(at 0 -2\.4\)', '(fp_text reference "U4" (at 3.9 0)', t)
    assert n == 1, n
    labels = ''.join(text(PINS[n][0], pads[n][0], EVEN_Y if n % 2 == 0 else ODD_Y) for n in PINS)
    labels += text('EVEN', key_x, EVEN_Y) + text('ODD', key_x, ODD_Y)
    k = t.rindex('\n)')
    t = t[:k + 1] + labels + t[k + 1:]
    t, n = re.subn(r'(\(gr_text "Miata ECU motherboard [^"]*  rev )[\d.]+"', lambda q: q[1] + REV[short] + '"', t)
    assert n == 1, n
    open(dst, 'w').write(t)
    print(f'{short}: J5 pin names on the silkscreen (22 texts), stitching vias moved {moved}, rev {REV[short]}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
