"""nudge_part.py in out REF:AWAY_REF:DIST ... : move REF straight away from AWAY_REF's nearest pad by DIST mm, dragging the
ends of its tracks with it (track ends on its pads move with the part). Zones refilled."""
import sys, pcbnew
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union, nearest_points
b = pcbnew.LoadBoard(sys.argv[1]); mm, IU = pcbnew.ToMM, pcbnew.FromMM
def padsh(fp):
    out = []
    for p in fp.Pads():
        if not p.IsOnLayer(pcbnew.F_Cu): continue
        ol = p.GetEffectivePolygon().Outline(0)
        out.append((p, Polygon([(mm(ol.CPoint(i).x), mm(ol.CPoint(i).y)) for i in range(ol.PointCount())])))
    return out
tracks = list(b.GetTracks())
for spec in sys.argv[3:]:
    ref, away, dist = spec.split(':'); dist = float(dist)
    fp, fa = b.FindFootprintByReference(ref), b.FindFootprintByReference(away)
    pa, pb = padsh(fp), padsh(fa)
    ga, gb = unary_union([g for _, g in pa]), unary_union([g for _, g in pb])
    p1, p2 = nearest_points(ga, gb)
    dx, dy = p1.x - p2.x, p1.y - p2.y; L = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / L, dy / L
    # snap to the dominant axis so the part stays square to its neighbours
    if abs(ux) > abs(uy): ux, uy = (1 if ux > 0 else -1), 0
    else: ux, uy = 0, (1 if uy > 0 else -1)
    mvx, mvy = ux * dist, uy * dist
    hits = []
    for t in tracks:
        for end in ('Start', 'End') if t.Type() != pcbnew.PCB_VIA_T else ():
            q = getattr(t, 'Get' + end)()
            pt = Point(mm(q.x), mm(q.y))
            for p, g in pa:
                if g.buffer(0.01).contains(pt) and p.GetNetname() == t.GetNetname():
                    hits.append((t, end)); break
    # vias sitting in one of its pads (same net) move with it, and so do the track ends on those vias
    vias = [v for v in tracks if v.Type() == pcbnew.PCB_VIA_T and any(
        g.contains(Point(mm(v.GetPosition().x), mm(v.GetPosition().y))) and p.GetNetname() == v.GetNetname() for p, g in pa)]
    for v in vias:
        vp = v.GetPosition()
        for t in tracks:
            if t.Type() == pcbnew.PCB_VIA_T or t.GetNetname() != v.GetNetname():
                continue
            for end in ('Start', 'End'):
                q = getattr(t, 'Get' + end)()
                if abs(q.x - vp.x) < IU(0.01) and abs(q.y - vp.y) < IU(0.01) and (t, end) not in hits:
                    hits.append((t, end))
        v.SetPosition(pcbnew.VECTOR2I(vp.x + IU(mvx), vp.y + IU(mvy)))
    fp.Move(pcbnew.VECTOR2I(IU(mvx), IU(mvy)))
    for t, end in hits:
        q = getattr(t, 'Get' + end)()
        getattr(t, 'Set' + end)(pcbnew.VECTOR2I(q.x + IU(mvx), q.y + IU(mvy)))
    print(ref, 'moved', round(mvx, 3), round(mvy, 3), 'dragged', len(hits), 'track ends and', len(vias), 'vias')
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[2])
