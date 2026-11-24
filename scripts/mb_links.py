"""mb_links.py <1989-95 motherboard .kicad_pcb (KiCad 7)> <out.kicad_pcb>

1989-95 motherboard rev 0.19: the year-specific jumpers become soldered 0R links, fitted by JLCPCB in one of two
assembly versions (1989-93 / 1994-95); the jumpers an owner may change stay headers (JP5 tach after a coil-on-plug
conversion, JP6 airflow meter / boost). mb_na6.LINKS is the netlist side.

  JP1 (INJ3: PAIR / SEQ)      -> R38  OUT_INJ3 - HARN_2Y   fitted on 1994-95
  JP2 (INJ4: PAIR / SEQ)      -> R39  OUT_INJ4 - HARN_2Z   fitted on 1994-95
  JP3 (FAN2: 90-93 / 94-95)   -> R40  OUT_LS7 - HARN_1R    fitted on 1989-93
                                 R41  OUT_LS7 - HARN_2S    fitted on 1994-95
  JP4 (94-95 2R)              -> R42  OUT_ALT - HARN_2R    fitted on 1994-95

PAIR (injectors 3 / 4 in parallel with 1 / 2) is gone: it was only for a rev 0.9 daughterboard, which does not fit a
castellated motherboard. Each link is an 0805 0R at its header's place, named on the silkscreen just above it. This
step edits the KiCad 7 text only; the copper to the new pads is joined by mb_links.sh.
"""
import re
import sys
import uuid

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from mb_rev19 import drop_block   # noqa: E402

# ref, x, y (board, mm), net 1, net 2, silkscreen name (one line, just above the link)
LINKS = [('R38', 247.5, 110.8, 'OUT_INJ3', 'HARN_2Y', 'INJ3 94-95'),
         ('R39', 247.5, 121.8, 'OUT_INJ4', 'HARN_2Z', 'INJ4 94-95'),
         ('R40', 106.5, 100.0, 'OUT_LS7', 'HARN_1R', 'FAN2 90-93'),
         ('R41', 106.5, 105.5, 'OUT_LS7', 'HARN_2S', 'FAN2 94-95'),
         ('R42', 106.5, 125.27, 'OUT_ALT', 'HARN_2R', '2R 94-95')]
LABEL_DY = -1.8          # label centre above the link's centre: 0.57 mm clear of its pads
# the old header pins whose net no link uses: the copper that led only there goes (INJ1 / INJ2 reached JP1 / JP2 for
# PAIR)
DEAD_PINS = [('OUT_INJ2', 247.5, 107.0), ('OUT_INJ1', 247.5, 118.0)]
OLD_TEXTS = [('INJ3', '246 104.6'), ('PAIR', '243.3 107'), ('SEQ', '243.3 112.08'), ('INJ4', '246 115.6'),
             ('PAIR', '243.3 118'), ('SEQ', '243.3 123.08'), ('FAN2', '108 97.6'), ('90-93', '110.8 100'),
             ('94-95', '110.8 105.08'), ('94-95 2R', '108 121.6')]


def u():
    return str(uuid.uuid4())


def r0805(ref, x, y, n1, net1, n2, net2):
    line = lambda x0, y0, x1, y1, w, layer: (f'    (fp_line (start {x0} {y0}) (end {x1} {y1})\n'
                                             f'      (stroke (width {w}) (type solid)) (layer "{layer}") (tstamp {u()}))\n')
    return (f'  (footprint "Resistor_SMD:R_0805_2012Metric" (layer "F.Cu")\n    (tstamp {u()})\n    (at {x} {y})\n'
            '    (descr "Resistor SMD 0805 (2012 Metric), square (rectangular) end terminal, IPC_7351 nominal, generated with kicad-footprint-generator")\n'
            '    (tags "resistor")\n    (property "LCSC" "C17477")\n    (attr smd)\n'
            f'    (fp_text reference "{ref}" (at 0 -1.65) (layer "F.SilkS")\n        (effects (font (size 1 1) (thickness 0.15)))\n      (tstamp {u()})\n    )\n'
            f'    (fp_text value "0R" (at 0 1.65) (layer "F.Fab")\n        (effects (font (size 1 1) (thickness 0.15)))\n      (tstamp {u()})\n    )\n'
            + line(-0.227064, -0.735, 0.227064, -0.735, 0.15, 'F.SilkS') + line(-0.227064, 0.735, 0.227064, 0.735, 0.15, 'F.SilkS')
            + line(-1.68, -0.95, 1.68, -0.95, 0.05, 'F.CrtYd') + line(-1.68, 0.95, -1.68, -0.95, 0.05, 'F.CrtYd')
            + line(1.68, -0.95, 1.68, 0.95, 0.05, 'F.CrtYd') + line(1.68, 0.95, -1.68, 0.95, 0.05, 'F.CrtYd')
            + line(-1, -0.625, 1, -0.625, 0.1, 'F.Fab') + line(-1, 0.625, -1, -0.625, 0.1, 'F.Fab')
            + line(1, -0.625, 1, 0.625, 0.1, 'F.Fab') + line(1, 0.625, -1, 0.625, 0.1, 'F.Fab')
            + f'    (pad "1" smd roundrect (at -0.9125 0) (size 1.025 1.4) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.243902)\n'
              f'      (net {n1} "{net1}") (tstamp {u()}))\n'
              f'    (pad "2" smd roundrect (at 0.9125 0) (size 1.025 1.4) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.243902)\n'
              f'      (net {n2} "{net2}") (tstamp {u()}))\n'
              '    (model "${KICAD6_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0805_2012Metric.wrl"\n'
              '      (offset (xyz 0 0 0))\n      (scale (xyz 1 1 1))\n      (rotate (xyz 0 0 0))\n    )\n  )\n')


def prune(t, net_no, x0, y0):
    """Remove the tracks and vias of one net that lead only to (x0, y0), an old pin: from the segments that end within
    1 mm of it, follow the chain while it is one track through a bend or one via with nothing else on it; stop where
    it meets anything else (a junction, a pad, another track's middle)."""
    seg_re = re.compile(r'\n  \(segment \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\) [^\n]*\(net %s\) [^\n]*' % net_no)
    via_re = re.compile(r'\n  \(via \(at ([-\d.]+) ([-\d.]+)\) [^\n]*\(net %s\) [^\n]*' % net_no)
    segs = [(m[0], (float(m[1]), float(m[2])), (float(m[3]), float(m[4]))) for m in seg_re.finditer(t)]
    vias = [(m[0], (float(m[1]), float(m[2]))) for m in via_re.finditer(t)]
    near = lambda a, b, r=0.05: abs(a[0] - b[0]) < r and abs(a[1] - b[1]) < r
    gone, front = set(), [(x0, y0, 1.0)]
    while front:
        x, y, r = front.pop()
        here = [s for s in segs if s[0] not in gone and (near(s[1], (x, y), r) or near(s[2], (x, y), r))]
        vh = [v for v in vias if v[0] not in gone and near(v[1], (x, y), max(r, 0.05))]
        if r < 1.0:                                     # a point on the chain: go on only through a plain bend or via
            if len(vh) > 1 or (not vh and len(here) != 1) or (vh and len(here) > 1):
                continue
            for v in vh:
                gone.add(v[0])
        for s in here:
            gone.add(s[0])
            far = s[2] if near(s[1], (x, y), r) else s[1]
            front.append((far[0], far[1], 0.05))
    for g in gone:
        t = t.replace(g, '', 1)
    return t, len(gone)


def main(src, dst):
    t = open(src).read()
    nets = {m[2]: m[1] for m in re.finditer(r'\n  \(net (\d+) "([^"]*)"\)', t)}
    for net, x, y in DEAD_PINS:
        t, n = prune(t, nets[net], x, y)
        print(f'{net}: {n} tracks / vias that led only to the old pin at {x} {y} removed')
    for ref in ('JP1', 'JP2', 'JP3', 'JP4'):
        i = t.index(f'(fp_text reference "{ref}"')
        a = t.rfind('\n  (footprint', 0, i) + 3
        t = drop_block(t, t[a:t.index('\n', t.index('(tstamp', a))])     # its header up to its unique tstamp
    for txt, at in OLD_TEXTS:
        t = drop_block(t, f'(gr_text "{txt}" (at {at})')
    fps, labels = [], []
    for ref, x, y, a, b, name in LINKS:
        assert f'(fp_text reference "{ref}"' not in t, ref
        fps.append(r0805(ref, x, y, nets[a], a, nets[b], b))
        labels.append(f'  (gr_text "{name}" (at {x} {y + LABEL_DY:.2f}) (layer "F.SilkS") (tstamp {u()})\n'
                      f'    (effects (font (size 1 1) (thickness 0.15)))\n  )\n')
    k = t.index('\n  (gr_') + 1
    t = t[:k] + ''.join(fps) + ''.join(labels) + t[k:]
    open(dst, 'w').write(t)
    print('JP1-JP4 -> ' + ', '.join(f'{r} ({n})' for r, *_, n in LINKS))


def novia():
    """The links' names as no-via rectangles for finish_route.py (x0 y0 x1 y1, mm): about 0.93 mm a character, 1 mm
    tall, plus 0.4 mm round."""
    for ref, x, y, a, b, name in LINKS:
        w, cy = len(name) * 0.93 / 2 + 0.4, y + LABEL_DY
        print(f'{x - w:.2f} {cy - 0.9:.2f} {x + w:.2f} {cy + 0.9:.2f}')


if __name__ == '__main__':
    if sys.argv[1] == '--novia':
        novia()
    else:
        main(*sys.argv[1:3])
