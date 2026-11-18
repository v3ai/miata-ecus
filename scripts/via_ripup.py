"""via_ripup.py in.kicad_pcb out.kicad_pcb: second pass after via_out_of_pad.py, for the vias it could not move.

For each via still in (or within GAP of) an SMD pad: find the nearest spot within RMAX where the via and its stubs
would be legal if some OTHER nets' track segments were not there (pads, holes, vias and the board edge are never
moved), preferring spots that rip up the fewest and shortest segments and never ripping the high-current outer-layer
nets. Those segments are deleted, the via moves and gets its stubs, and the ripped nets are listed. Then run
finish_route.py on the result to join the ripped nets again; it keeps its own vias out of every pad.
usage: via_ripup.py in.kicad_pcb out.kicad_pcb [--rmax 2.5] [--keep NET,NET] [--thin]   (--keep: nets never to rip; --rip-planes: GND / +3V3
       tracks may go too, the finisher ties their pads to the planes again; prints the ripped nets at the end)"""
import sys, os, json, math, argparse
import pcbnew
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

mm, MM = pcbnew.ToMM, pcbnew.FromMM
GAP, PAD_HOLE_GAP, STEP, MARGIN = 0.10, 0.45, 0.05, 0.01
WIDE = True            # stubs as wide as the track they continue; --thin caps them at 0.3 mm
NO_RIP = {'OUT_INJ1', 'OUT_INJ2', 'OUT_INJ3', 'OUT_INJ4', 'OUT_IACV', 'OUT_VVT', 'OUT_BOOST', 'OUT_ALT', '+12V_IN',
          '+12V', '+12V_F', 'BUCK_SW', 'USB_VBUS', 'VBAT_IN', 'GND', '+3V3'}


def poly_of(ps):
    out = []
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        g = Polygon([(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())])
        out.append(g if g.is_valid else g.buffer(0))
    return unary_union(out) if out else Polygon()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out'); ap.add_argument('--rmax', type=float, default=2.5); ap.add_argument('--keep', default=''); ap.add_argument('--rip-planes', action='store_true'); ap.add_argument('--thin', action='store_true')
    a = ap.parse_args()
    global WIDE
    WIDE = not a.thin
    no_rip = (NO_RIP - ({'GND', '+3V3'} if a.rip_planes else set())) | {n for n in a.keep.split(',') if n}
    d = json.load(open(os.path.splitext(a.inp)[0] + '.kicad_pro'))
    rules = d['board']['design_settings']['rules']
    CL = [c for c in d['net_settings']['classes'] if c['name'] == 'Default'][0]['clearance'] + MARGIN
    EDGE = rules.get('min_copper_edge_clearance', 0.3)
    H2H = max(0.25, rules.get('min_hole_to_hole', 0.25))
    b = pcbnew.LoadBoard(a.inp)
    cu = list(b.GetEnabledLayers().CuStack())
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    fixed, smd, holes, tracks, vias = [], [], [], [], []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            att = p.GetAttribute()
            if att in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                ds = p.GetDrillSize()
                holes.append((Point(mm(p.GetPosition().x), mm(p.GetPosition().y)), mm(min(ds.x, ds.y)) / 2))
            for l in cu:
                if not p.IsOnLayer(l) or (att == pcbnew.PAD_ATTRIB_PTH and not p.FlashLayer(l)):
                    continue
                ps = pcbnew.SHAPE_POLY_SET()
                p.TransformShapeToPolygon(ps, l, 0, MM(0.005), pcbnew.ERROR_INSIDE)
                g = poly_of(ps)
                if g.is_empty:
                    continue
                fixed.append((g, p.GetNetname(), l))
                if att == pcbnew.PAD_ATTRIB_SMD and l in (F, B):
                    smd.append((g, f'{fp.GetReference()}.{p.GetNumber()}', p.GetNetname(), l))
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            vias.append(t)
        else:
            s, e = t.GetStart(), t.GetEnd()
            tracks.append([LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2), t])
    vpos = lambda v: Point(mm(v.GetPosition().x), mm(v.GetPosition().y))
    ol = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ol)
    border = poly_of(ol).exterior
    smd_tree = STRtree([s[0] for s in smd])
    fixed_tree = STRtree([f[0] for f in fixed])
    removed = set()
    ripped_nets = set()

    def trk_tree():
        live = [(g, t) for g, t in tracks if id(t) not in removed]
        return STRtree([g for g, t in live]), live

    offs = sorted((math.hypot(i * STEP, j * STEP), i * STEP, j * STEP)
                  for i in range(-int(a.rmax / STEP), int(a.rmax / STEP) + 1)
                  for j in range(-int(a.rmax / STEP), int(a.rmax / STEP) + 1)
                  if 0 < math.hypot(i * STEP, j * STEP) <= a.rmax)
    todo = []
    for v in vias:
        ring = vpos(v).buffer(mm(v.GetWidth(F)) / 2)
        hits = [smd[j] for j in smd_tree.query(ring.buffer(GAP - 1e-4), predicate='intersects')]
        if hits:
            todo.append((v, hits))
    print(f'{len(todo)} vias still in or against an SMD pad')
    report = []
    for v, hits in todo:
        net, old = v.GetNetname(), vpos(v)
        r, h = mm(v.GetWidth(F)) / 2, mm(v.GetDrillValue()) / 2
        ttree, live = trk_tree()
        # stub starts: track ends inside the via, per layer; the pad layer from the old centre
        lays = {}
        for j in ttree.query(old.buffer(r), predicate='intersects'):
            g, t = live[j]
            if t.GetNetname() != net:
                continue
            for q in (t.GetStart(), t.GetEnd()):
                qp = (mm(q.x), mm(q.y))
                if Point(qp).distance(old) <= r + 1e-3:
                    e = lays.setdefault(t.GetLayer(), [0.2, set()])
                    e[0] = max(e[0], mm(t.GetWidth()) if WIDE else min(mm(t.GetWidth()), 0.3)); e[1].add(qp)
        for hh in hits:
            if hh[2] == net:
                lays.setdefault(hh[3], [0.2, set()])[1].add((old.x, old.y))
        others_v = [o for o in vias if o is not v]
        best = None
        for rr, dx, dy in offs:
            c = Point(old.x + dx, old.y + dy)
            ring = c.buffer(r)
            if len(smd_tree.query(ring.buffer(GAP), predicate='intersects')) or border.distance(c) < EDGE + r:
                continue
            if any(hp.distance(c) < hr + h + PAD_HOLE_GAP for hp, hr in holes):
                continue
            bad = False
            for o in others_v:
                q = vpos(o)
                if q.distance(c) < 2.5 and (q.distance(c) < h + mm(o.GetDrillValue()) / 2 + H2H or
                                            (o.GetNetname() != net and q.distance(c) < r + mm(o.GetWidth(F)) / 2 + CL)):
                    bad = True; break
            if bad:
                continue
            if any(fixed[j][1] != net and fixed[j][0].distance(ring) < CL
                   for j in fixed_tree.query(ring, predicate='dwithin', distance=CL)):
                continue
            # stubs must clear fixed copper of other nets on their layer
            segs = []
            for l, (w, starts) in lays.items():
                for st in starts:
                    if Point(st).distance(c) > 1e-6:
                        segs.append((l, w, LineString([st, (c.x, c.y)]).buffer(w / 2)))
            if any(fixed[j][1] != net and fixed[j][2] == l and fixed[j][0].distance(g) < CL
                   for l, w, g in segs for j in fixed_tree.query(g, predicate='dwithin', distance=CL)):
                continue
            # ... and other nets' vias (on every layer)
            if any(o.GetNetname() != net and vpos(o).distance(g) < mm(o.GetWidth(F)) / 2 + CL
                   for l, w, g in segs for o in others_v if vpos(o).distance(c) < 4.0):
                continue
            # what would have to go: other nets' segments near the via (every layer) or a stub (its layer)
            rip = set()
            for j in ttree.query(ring, predicate='dwithin', distance=CL):
                g, t = live[j]
                if t.GetNetname() != net and g.distance(ring) < CL:
                    rip.add(j)
            for l, w, sg in segs:
                for j in ttree.query(sg, predicate='dwithin', distance=CL):
                    g, t = live[j]
                    if t.GetNetname() != net and t.GetLayer() == l and g.distance(sg) < CL:
                        rip.add(j)
            if any(live[j][1].GetNetname() in no_rip for j in rip):
                continue
            cost = rr + sum(1.0 + live[j][0].length / 4 for j in rip) * 2.0
            if best is None or cost < best[0]:
                best = (cost, c, rip, segs)
            if not rip:
                break
        if best is None:
            report.append(f'  NO SPOT even with rip-up: {hits[0][1]} {net} at {old.x:.2f},{old.y:.2f}')
            continue
        cost, c, rip, segs = best
        names = set()
        for j in rip:
            g, t = live[j]
            names.add(t.GetNetname()); removed.add(id(t)); b.Remove(t)
        ripped_nets |= names
        v.SetPosition(pcbnew.VECTOR2I(MM(c.x), MM(c.y)))
        for l, (w, starts) in lays.items():
            for st in starts:
                if Point(st).distance(c) < 1e-6:
                    continue
                t = pcbnew.PCB_TRACK(b)
                t.SetStart(pcbnew.VECTOR2I(MM(st[0]), MM(st[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(c.x), MM(c.y)))
                t.SetWidth(MM(w)); t.SetLayer(l); t.SetNet(v.GetNet())
                b.Add(t)
                tracks.append([LineString([st, (c.x, c.y)]).buffer(w / 2), t])
        report.append(f'  moved {hits[0][1]} {net} {old.distance(c):.2f} mm, ripped {len(rip)} segments of {sorted(names) or "nothing"}')
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(a.out)
    print('\n'.join(report))
    print('RIPPED\n' + '\n'.join(sorted(ripped_nets)))


if __name__ == '__main__':
    main()
