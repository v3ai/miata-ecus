"""j5_clear.py <in.kicad_pcb> <out.kicad_pcb> <novia.txt> [--check] (KiCad 9): keep vias out from under J5's pin names.

Finds the silkscreen texts that scripts/j5_labels.py put round J5 (the pin names and pin numbers) and writes their
outlines, grown by a via's radius and a margin, to novia.txt: the NOVIA file finish_route.py and stitch_islands.py
read, so nothing they add lands under a name. Then, for each via that sits under one now:
  - a ground stitching via with no track on it moves sideways (then up or down) to the nearest spot clear of the
    names and of other nets' copper and holes;
  - any other via goes, with the track segments that end in it; the net is then in pieces for finish_route.py.
--check changes nothing and exits 1 if any via is under a name (the last step of scripts/j5_mb.sh)."""
import gc
import sys

import pcbnew
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

gc.disable()
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from j5_labels import NUMBERS, PINS   # noqa: E402

MM, mm = pcbnew.FromMM, pcbnew.ToMM
VR, MARGIN, CLEAR = 0.3, 0.1, 0.2        # via radius; room between a via and a name; via to other nets' copper


def labels(b):
    """the texts j5_labels.py placed: J5's pin names and numbers, within a few mm of J5"""
    j5 = b.FindFootprintByReference('J5')
    cb = j5.GetBoundingBox(False)
    x0, y0, x1, y1 = mm(cb.GetLeft()) - 6, mm(cb.GetTop()) - 8, mm(cb.GetRight()) + 6, mm(cb.GetBottom()) + 8
    names = {n for n, _ in PINS.values()} | set(NUMBERS)
    out = []
    for d in b.GetDrawings():
        if d.GetClass() == 'PCB_TEXT' and d.GetLayer() == pcbnew.F_SilkS and d.GetText() in names:
            r = d.GetBoundingBox()
            g = box(mm(r.GetLeft()), mm(r.GetTop()), mm(r.GetRight()), mm(r.GetBottom()))
            if g.within(box(x0, y0, x1, y1)):
                out.append(g)
    assert len(out) == len(PINS) + len(NUMBERS), len(out)
    return out


def main(src, dst, novia_path, check=False):
    b = pcbnew.LoadBoard(src)
    rects = [g.buffer(VR + MARGIN, join_style=2) for g in labels(b)]
    under = unary_union(rects)
    if not check:
        with open(novia_path, 'w') as f:
            for g in rects:
                f.write(' '.join(f'{v:.3f}' for v in g.bounds) + '\n')
    tracks = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
    vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    bad = [v for v in vias if under.contains(Point(mm(v.GetPosition().x), mm(v.GetPosition().y)))]
    if check:
        for v in bad:
            print(f'  via under a name: {v.GetNetname()} at ({mm(v.GetPosition().x):.2f}, {mm(v.GetPosition().y):.2f})')
        print(f'{len(bad)} vias under J5\'s names')
        sys.exit(1 if bad else 0)

    def other_copper(net):
        g = []
        for t in tracks:
            if t.GetNetname() != net:
                g.append(LineString([(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))])
                         .buffer(mm(t.GetWidth()) / 2))
        for v in vias:
            if v.GetNetname() != net:
                g.append(Point(mm(v.GetPosition().x), mm(v.GetPosition().y)).buffer(mm(v.GetWidth()) / 2))
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if p.GetNetname() != net or p.GetDrillSize().x > 0:
                    r = p.GetBoundingBox()
                    g.append(box(mm(r.GetLeft()), mm(r.GetTop()), mm(r.GetRight()), mm(r.GetBottom())))
        return unary_union(g)

    gone, moved = [], []
    for v in bad:
        x, y, net = mm(v.GetPosition().x), mm(v.GetPosition().y), v.GetNetname()
        ends = [t for t in tracks if t.GetNetname() == net and
                any(Point(mm(p.x), mm(p.y)).distance(Point(x, y)) < mm(v.GetWidth()) / 2 for p in (t.GetStart(), t.GetEnd()))]
        if net == 'GND' and not ends:
            block = other_copper(net).buffer(CLEAR + VR).union(under)
            others = unary_union([Point(mm(u.GetPosition().x), mm(u.GetPosition().y)).buffer(0.3 + 0.3 + 0.2)
                                  for u in vias if u is not v])
            spot = None
            for k in range(1, 41):
                for dx, dy in ((k * 0.1, 0), (-k * 0.1, 0), (0, k * 0.1), (0, -k * 0.1)):
                    p = Point(x + dx, y + dy)
                    if not block.contains(p) and not others.contains(p):
                        spot = p
                        break
                if spot:
                    break
            if spot:
                v.SetPosition(pcbnew.VECTOR2I(MM(round(spot.x, 2)), MM(round(spot.y, 2))))
                moved.append(f'GND ({x:.2f}, {y:.2f}) -> ({spot.x:.2f}, {spot.y:.2f})')
                continue
        for t in ends:
            b.Remove(t)
        b.Remove(v)
        gone.append(f'{net} ({x:.2f}, {y:.2f}) with {len(ends)} tracks')
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)
    print(f'{len(rects)} names; vias moved: {moved}; vias removed: {gone}')


if __name__ == '__main__':
    main(*sys.argv[1:4], check='--check' in sys.argv)
