"""castellate_daughter.py <daughterboard.kicad_pcb (KiCad 7)> <out.kicad_pcb> [J2:6=1.7,J1:16=2.2,...]

Turns the finished daughterboard into a castellated module that reflows flat onto the motherboard, without moving
any part or track: the two long edges are cut through the centres of the J1 / J2 pin rows (y 52.75 and 123.25),
so the 80 plated header holes become plated half-holes on the board edge, and the board shrinks from 125 x 76 mm
to 125 x 70.5 mm.

  - Edge.Cuts: the top edge moves down 2.75 mm and the bottom edge up 2.75 mm (corner radii kept).
  - J1 / J2: every pad becomes a castellated pad (KiCad's castellated property, which exempts it from the edge
    clearance rule), a rounded rectangle PAD_W along the edge and PAD_L across it (the pads sit at 270 degrees, so
    the size is written PAD_L PAD_W), centred on the hole, so after the
    cut it reaches PAD_L / 2 in from the edge on the top and bottom copper. Their bottom silkscreen (the header
    outline, which would now cross the edge) is removed.
  - H1-H4 (M3 standoff holes, which sat in the cut strips) are removed.
  - Vias within VIA_KEEP of the new edges (the GND stitching row along each old edge) are removed.
  - "J1" and "J2" on the top silkscreen in the left corners, so the module goes on the right way round.

Zone outlines are left as they are; the fill is clipped to the new edge when the zones are refilled. Afterwards
refill the zones under KiCad 9 and carry the fill back with backport_copper.py (see castellate_daughter.sh)."""
import re
import sys

TOP_OLD, BOT_OLD = 50.0, 126.0
TOP_NEW, BOT_NEW = 52.75, 123.25
MID = (TOP_OLD + BOT_OLD) / 2
PAD_W, PAD_L = 1.6, 2.6        # mm; 0.94 mm copper gap at 2.54 mm pitch, 1.3 mm of pad inside the edge
# Pads that sit close to a part or track inside the edge are shorter (DRC finds them; castellate_daughter.sh):
# the third argument, e.g. J2:6=1.7. 1.7 is the original round pad's reach (0.85 mm inside the edge).
VIA_KEEP = 0.8                 # mm from via centre to the new edge
# Silkscreen labels the new edge would cut: footprint -> (old, new) reference position.
LABEL_MOVES = {'D29': ('(fp_text reference "D29" (at 0 -1.85 180)', '(fp_text reference "D29" (at 0 1.85 180)')}


def blocks(text, head):
    """(start, end) of every top-level s-expression starting with `head` (two-space indented)."""
    out = []
    for m in re.finditer(r'^  \(' + re.escape(head) + r'\b', text, re.M):
        i, depth = m.start() + 2, 0
        while True:
            c = text[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            elif c == '"':
                i += 1
                while text[i] != '"':
                    i += 2 if text[i] == '\\' else 1
            i += 1
        j = i + 1
        if text[j] == '\n':
            j += 1
        out.append((m.start(), j))
    return out


def cut(text, spans):
    for a, b in sorted(spans, reverse=True):
        text = text[:a] + text[b:]
    return text


def shift_y(y):
    y = float(y)
    return y + (TOP_NEW - TOP_OLD) if y < MID else y - (BOT_OLD - BOT_NEW)


def fmt(v):
    s = f'{v:.6f}'.rstrip('0').rstrip('.')
    return s


SHORT = 'J1:16=1.7,J2:6=1.7,J2:7=1.7,J2:8=1.7,J2:14=1.7,J2:15=1.7,J2:25=1.7'   # found by DRC, 2026-11-20


def main(src, dst, short=SHORT):
    lengths = {tuple(k.split(':')): float(v) for k, v in (x.split('=') for x in short.split(',') if x)}
    text = open(src).read()

    # 1. outline
    n_edge = 0
    spans = [s for h in ('gr_line', 'gr_arc') for s in blocks(text, h)]
    for a, b in sorted(spans, reverse=True):
        blk = text[a:b]
        if '"Edge.Cuts"' not in blk:
            continue
        new = re.sub(r'\((start|mid|end) ([-\d.]+) ([-\d.]+)\)',
                     lambda m: f'({m.group(1)} {m.group(2)} {fmt(shift_y(m.group(3)))})', blk)
        text = text[:a] + new + text[b:]
        n_edge += 1

    # 2. mounting holes
    holes = [s for s in blocks(text, 'footprint') if text[s[0]:s[1]].startswith('  (footprint "MountingHole:')]
    refs = [re.search(r'reference "([^"]+)"', text[a:b]).group(1) for a, b in holes]
    assert sorted(refs) == ['H1', 'H2', 'H3', 'H4'], refs
    text = cut(text, holes)

    # 3. stitching vias at the old edges
    vias = []
    for a, b in blocks(text, 'via'):
        y = float(re.match(r'  \(via \(at [-\d.]+ ([-\d.]+)\)', text[a:b]).group(1))
        if y < TOP_NEW + VIA_KEEP or y > BOT_NEW - VIA_KEEP:
            net = re.search(r'\(net (\d+)\)', text[a:b]).group(1)
            vias.append((a, b, net))
    gnd = re.search(r'^  \(net (\d+) "GND"\)$', text, re.M).group(1)
    assert all(n == gnd for _, _, n in vias), 'a non-GND via sits at the new edge'
    text = cut(text, [(a, b) for a, b, _ in vias])

    # 4. J1 / J2 pads and silkscreen
    n_pad = 0
    for a, b in sorted(blocks(text, 'footprint'), reverse=True):
        blk = text[a:b]
        m = re.search(r'\(fp_text reference "(J1|J2)"', blk)
        if not m or 'PinHeader_1x40' not in blk:
            continue
        blk, k = re.subn(
            r'\(pad "(\d+)" thru_hole (?:rect|oval) \(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\) \(size 1\.7 1\.7\) '
            r'\(drill 1\) \(layers "\*\.Cu" "\*\.Mask"\)',
            lambda q: (f'(pad "{q.group(1)}" thru_hole roundrect (at {q.group(2)} {q.group(3)} {q.group(4)}) '
                       f'(size {fmt(lengths.get((m.group(1), q.group(1)), PAD_L))} {fmt(PAD_W)}) (drill 1) (property pad_prop_castellated) '
                       f'(layers "*.Cu" "*.Mask") (roundrect_rratio 0.25)'), blk)
        assert k == 40, (m.group(1), k)
        n_pad += k
        blk = re.sub(r'    \(fp_line [^\n]*\n[^\n]*\(layer "B\.SilkS"\)[^\n]*\n', '', blk)
        # now part of the board, not a part to buy: design.py's CAST40, no LCSC number
        blk = blk.replace('(footprint "Connector_PinHeader_2.54mm:PinHeader_1x40_P2.54mm_Vertical"',
                          '(footprint "miata_ecu:Castellated_1x40_P2.54mm"')
        blk = re.sub(r'\(descr "[^"]*"\)', '(descr "Castellated edge, 40 plated half-holes, 2.54 mm pitch")', blk)
        blk = re.sub(r'\(tags "[^"]*"\)', '(tags "castellated")', blk)
        blk = re.sub(r'\n    \(property "LCSC" "C2977586"\)', '', blk)
        blk = blk.replace('(attr through_hole)', '(attr through_hole exclude_from_pos_files exclude_from_bom)')
        # the reference sits on the bottom, under the module once it is soldered down
        blk = re.sub(r'(\(fp_text reference "J[12]" \(at [^)]*\) \(layer "B\.SilkS"\))', r'\1 hide', blk)
        text = text[:a] + blk + text[b:]

    # Orientation: both edges carry 40 pins at the same places, so the module also fits turned round, which would put
    # the battery on the sensor inputs. Name each edge on top, in the corners the standoff holes left free; the
    # motherboard's silkscreen names its land rows the same way (castellate_mb.py).
    import uuid
    marks = ''.join(f'  (gr_text "{t}" (at {x} {y}) (layer "F.SilkS") (tstamp {uuid.uuid4()})\n'
                    f'    (effects (font (size 1.5 1.5) (thickness 0.2)) (justify left))\n  )\n'
                    for t, x, y in (('J1', 101.5, 55.5), ('J2', 101.5, 120.5)))
    i = text.rindex('\n)')
    text = text[:i + 1] + marks + text[i + 1:]
    for ref, (old, new) in LABEL_MOVES.items():
        assert text.count(old) == 1, ref
        text = text.replace(old, new)

    open(dst, 'w').write(text)
    print(f'outline segments moved {n_edge}, holes removed {refs}, edge vias removed {len(vias)}, '
          f'castellated pads {n_pad}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
