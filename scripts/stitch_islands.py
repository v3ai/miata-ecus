"""stitch_islands.py <in.kicad_pcb> <out.kicad_pcb> [NET=GND] (KiCad 9): tie stray islands of a plane net's pours back
to the rest with a via.

On a two-layer motherboard the GND pours on the top and bottom copper are one net only through vias and plated holes.
Where a change order took vias out (castellate_mb.sh: rip_conflicts.py, strip_stubs.py) or a pad lost its bottom
copper (the JD1 / JD2 lands are top only), an island of one pour can be left with no via to the other, and KiCad lists
it as unconnected. This finds the pieces of the net (pour islands, tracks, vias, pads, joined where they touch on a
layer; vias and plated holes join the layers), takes the largest as the body, and for every other piece puts a via
where one of its islands overlaps a body island on the other layer: the via's copper inside both fills by MARGIN, and
clear of any pad (TRIES) and hole, and outside the env NOVIA file's rectangles (as finish_route.py). Zones are refilled and the check repeated until nothing is left or no spot is found."""
import gc
import sys
import pcbnew
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import os
from shapely.geometry import box
NOVIA = (unary_union([box(*map(float, ln.split())) for ln in open(os.environ['NOVIA']) if ln.strip()])
         if os.environ.get('NOVIA') else None)

gc.disable()      # pcbnew's SWIG temporaries crash the cyclic collector under KiCad 9
mm, MM = pcbnew.ToMM, pcbnew.FromMM
# (via, drill, margin inside both fills, clear of any pad's copper): the second, for a pocket round a pad, is the
# smallest via JLCPCB makes on two layers (0.3 mm hole, 0.1 mm ring), 0.15 mm from the pad (JLCPCB's no-via-in-pad check wants 0.1); the
# fill's own edge already keeps other nets' copper at the zone clearance
TRIES = [(0.6, 0.3, 0.15, 0.6), (0.5, 0.3, 0.05, 0.15)]
HOLE_CLEAR = 0.6                 # hole edge to hole edge
STEP = 0.1


def pieces(b, net):
    F, Bc = pcbnew.F_Cu, pcbnew.B_Cu
    nodes = []                   # (kind, layers, geom)
    for z in b.Zones():
        if z.GetNetname() != net:
            continue
        for L in (F, Bc):
            if not z.IsOnLayer(L):
                continue
            ps = z.GetFilledPolysList(L)
            for k in range(ps.OutlineCount()):
                o = ps.Outline(k)
                pts = [(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())]
                if len(pts) >= 3:
                    g = Polygon(pts)
                    nodes.append(('z', {L}, g if g.is_valid else g.buffer(0)))
    for t in b.GetTracks():
        if t.GetNetname() != net:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            nodes.append(('v', {F, Bc}, Point(mm(p.x), mm(p.y)).buffer(mm(t.GetWidth(F)) / 2)))
        elif t.GetLayer() in (F, Bc):
            s, e = t.GetStart(), t.GetEnd()
            from shapely.geometry import LineString
            nodes.append(('t', {t.GetLayer()}, LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2)))
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != net:
                continue
            ls = {L for L in (F, Bc) if p.IsOnLayer(L)}
            if ls:
                bb = p.GetBoundingBox()
                g = Polygon([(mm(bb.GetLeft()), mm(bb.GetTop())), (mm(bb.GetRight()), mm(bb.GetTop())),
                             (mm(bb.GetRight()), mm(bb.GetBottom())), (mm(bb.GetLeft()), mm(bb.GetBottom()))])
                nodes.append(('p', ls, g))
    par = list(range(len(nodes)))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if nodes[i][1] & nodes[j][1] and nodes[i][2].intersects(nodes[j][2]):
                par[find(i)] = find(j)
    groups = {}
    for i in range(len(nodes)):
        groups.setdefault(find(i), []).append(nodes[i])
    return sorted(groups.values(), key=lambda g: -sum(n[2].area for n in g))


def main(src, dst, net='GND'):
    b = pcbnew.LoadBoard(src)
    nc = b.FindNet(net)
    keep_out, holes = [], []
    for f in b.GetFootprints():
        for p in f.Pads():
            bb = p.GetBoundingBox()
            keep_out.append(Polygon([(mm(bb.GetLeft()), mm(bb.GetTop())), (mm(bb.GetRight()), mm(bb.GetTop())),
                                     (mm(bb.GetRight()), mm(bb.GetBottom())), (mm(bb.GetLeft()), mm(bb.GetBottom()))]))
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            holes.append(Point(mm(p.x), mm(p.y)).buffer(mm(t.GetDrillValue()) / 2))
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetDrillSize().x > 0:
                holes.append(Point(mm(p.GetPosition().x), mm(p.GetPosition().y)).buffer(mm(p.GetDrillSize().x) / 2))
    added = 0
    for _ in range(20):
        groups = pieces(b, net)
        if len(groups) < 2:
            break
        body = groups[0]
        done = False
        for (VIA, DRILL, MARGIN, CLEAR), g in ((t, g) for t in TRIES for g in groups[1:]):
            if done:
                break
            ko = unary_union(keep_out).buffer(CLEAR + VIA / 2).union(unary_union(holes).buffer(HOLE_CLEAR + DRILL / 2))
            if NOVIA is not None:
                ko = ko.union(NOVIA)                    # silkscreen text (finish_route.py's NOVIA file)
            for kind, ls, geom in g:
                if kind != 'z':
                    continue
                L = next(iter(ls))
                other = unary_union([n[2] for n in body if n[0] == 'z' and n[1] != ls])
                ok = geom.buffer(-(VIA / 2 + MARGIN)).intersection(other.buffer(-(VIA / 2 + MARGIN))).difference(ko)
                if ok.is_empty:
                    continue
                p = ok.representative_point()
                v = pcbnew.PCB_VIA(b)
                v.SetPosition(pcbnew.VECTOR2I(MM(p.x), MM(p.y)))
                v.SetWidth(MM(VIA))
                v.SetDrill(MM(DRILL))
                v.SetNet(nc)
                b.Add(v)
                holes.append(Point(p.x, p.y).buffer(DRILL / 2))
                print(f'{net}: {VIA} mm via at ({p.x:.2f}, {p.y:.2f}) ties an island on {b.GetLayerName(L)} '
                      f'({geom.area:.0f} mm2) to the rest')
                added += 1
                done = True
                break
            if done:
                break
        if not done:
            print(f'{net}: {len(groups) - 1} piece(s) left with no spot for a via')
            for g in groups[1:]:
                print('   ', [(k, b.GetLayerName(next(iter(ls))), tuple(round(c, 1) for c in geom.bounds), round(geom.area, 1)) for k, ls, geom in g][:6])
            break
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)
    print(f'{added} vias added')


if __name__ == '__main__':
    main(*sys.argv[1:4])
