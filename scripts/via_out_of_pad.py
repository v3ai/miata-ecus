"""via_out_of_pad.py in.kicad_pcb out.kicad_pcb: change order that takes every via out of the SMD pads.

No via may sit in, or within GAP of, an SMD pad (no epoxy fill needed, no solder wicking down a hole).
For each such via, in order:
  * a via in a DPAK driver tab (pad of 20 mm2 or more on a TO-252) is deleted; the tab copper keeps its vias
    around the tab, and new ones are added in the tab's own copper pour outside the pad (`--tab-ring`);
  * any other via moves to the nearest legal spot within RMAX of where it was (a "dog-bone"): its ring and GAP
    clear of every SMD pad, CL clear of other nets' copper on every layer, hole-to-hole and hole-to-pad-hole
    spacing kept, inside the board edge clearance. A stub joins the old spot to the new one on every layer where
    a track ended at the via, plus the pad's layer;
  * failing a straight or L-shaped stub, a grid search finds a bent stub to a legal spot; a via that only joins
    its pad to the other layers may instead be deleted and its pad routed to a neighbouring via of the same net;
  * a via with no legal spot is left in place and listed (hand re-route).
jlc_fab_check.py fails the release while any via is still in or against an SMD pad.
Then the zones are refilled. Rules come from the board's .kicad_pro (Default net class clearance, edge, holes).
usage: via_out_of_pad.py in.kicad_pcb out.kicad_pcb [--rmax 2.0] [--no-tab-ring] [--report report.txt]"""
import sys, os, json, math, argparse
import pcbnew
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

mm, MM = pcbnew.ToMM, pcbnew.FromMM
GAP = 0.10              # via ring to any SMD pad edge (same as the jlc_fab_check rule)
THIN = 0.3              # stub width tried when a full-width stub fits nowhere (logged)
PAD_HOLE_GAP = 0.45     # via hole to plated/unplated pad hole, edge to edge (via_hole_gap.py)
VIA_GAP = 0.25          # via hole to via hole, edge to edge (JLC 0.20; board rule 0.25)
TAB_MM2 = 20.0          # a pad this big on a TO-252 is the driver tab
STEP = 0.05
MARGIN = 0.01         # pad outlines are polygons inside the true arcs: keep this much over the rule


def rules(path):
    pro = os.path.splitext(path)[0] + '.kicad_pro'
    d = json.load(open(pro))
    r = d['board']['design_settings']['rules']
    cl = [c for c in d['net_settings']['classes'] if c['name'] == 'Default'][0]
    return dict(cl=cl['clearance'], edge=r.get('min_copper_edge_clearance', 0.3),
                h2h=max(VIA_GAP, r.get('min_hole_to_hole', 0.25)), stub=cl.get('track_width', 0.2))


def poly_of(ps):
    out = []
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        g = Polygon([(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())])
        out.append(g if g.is_valid else g.buffer(0))
    return unary_union(out) if out else Polygon()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--rmax', type=float, default=2.0)
    ap.add_argument('--no-tab-ring', action='store_true')
    ap.add_argument('--report')
    a = ap.parse_args()
    R = rules(a.inp)
    CL = R['cl'] + MARGIN
    b = pcbnew.LoadBoard(a.inp)
    cu = list(b.GetEnabledLayers().CuStack())
    F, B = pcbnew.F_Cu, pcbnew.B_Cu

    # ---- geometry: copper items per layer, SMD pads, holes
    items = []          # [geom, net, layer (-1 = every layer), kind, ref]
    smd = []            # (geom, id, net, layer, pad, is_tab)
    holes = []          # (Point, radius)
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        is_dpak = 'TO-252' in str(fp.GetFPID().GetLibItemName())
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
                items.append([g, p.GetNetname(), l, 'pad', f'{ref}.{p.GetNumber()}'])
                if att == pcbnew.PAD_ATTRIB_SMD and l in (F, B):
                    smd.append((g, f'{ref}.{p.GetNumber()}', p.GetNetname(), l, p, is_dpak and g.area >= TAB_MM2))
    vias = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            c = Point(mm(t.GetPosition().x), mm(t.GetPosition().y))
            vias.append(t)
            items.append([c.buffer(mm(t.GetWidth(F)) / 2), t.GetNetname(), -1, 'via', t])
        else:
            s, e = t.GetStart(), t.GetEnd()
            g = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2)
            items.append([g, t.GetNetname(), t.GetLayer(), 'trk', t])
    keep = []           # rule areas that forbid vias / tracks
    for z in b.Zones():
        if z.GetIsRuleArea():
            keep.append((poly_of(z.Outline()), z.GetDoNotAllowVias(), z.GetDoNotAllowTracks(), list(z.GetLayerSet().CuStack())))
    ol = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ol)
    border = poly_of(ol).exterior
    tree = STRtree([it[0] for it in items])
    smd_tree = STRtree([s[0] for s in smd])
    via_holes = {id(v): Point(mm(v.GetPosition().x), mm(v.GetPosition().y)) for v in vias}
    dead, added = set(), []      # item indices no longer present; new items [geom, net, layer, kind, ref]

    def others(g, dist):
        for j in tree.query(g, predicate='dwithin', distance=dist):
            if j not in dead:
                yield items[j]
        for it in added:
            if it[0].distance(g) <= dist:
                yield it

    def via_ok(c, net, r, h, self_v):
        pt = Point(c)
        ring = pt.buffer(r)
        if len(smd_tree.query(ring.buffer(GAP), predicate='intersects')):
            return False
        if border.distance(pt) < R['edge'] + r:
            return False
        for g, ok_v, ok_t, lays in keep:
            if ok_v and g.intersects(ring):
                return False
        for hp, hr in holes:
            if hp.distance(pt) < hr + h + PAD_HOLE_GAP:
                return False
        for g, n, l, k, ref in others(ring, CL + 0.01):
            if k == 'via':
                if ref is self_v:
                    continue
                if g.centroid.distance(pt) < h + mm(ref.GetDrillValue()) / 2 + R['h2h']:
                    return False
                if n != net and g.distance(ring) < CL:
                    return False
                continue
            if n != net and g.distance(ring) < CL:
                return False
        return True

    def stub_ok(seg, net, lay, self_v):
        for g, ok_v, ok_t, lays in keep:
            if ok_t and lay in lays and g.intersects(seg):
                return False
        for g, n, l, k, ref in others(seg, CL + 0.01):
            if n == net or (k == 'via' and ref is self_v):
                continue
            if (l == lay or l == -1) and g.distance(seg) < CL:
                return False
        return True


    def grid_paths(old, lays, net, self_v, spots):
        """Fallback when no straight or L stub fits: 8-connected grid search (STEP) on each stub layer from each stub
        start, through free copper, to the via spots. Returns (spot, {(layer, start): path}) or None."""
        import heapq
        from shapely import prepared
        win = old.buffer(a.rmax + 0.6).envelope
        dist = {}
        for l, (w, starts) in lays.items():
            obs = [g for g, n, ll, k, ref in others(win, 0.0) if n != net and (ll == l or ll == -1) and not (k == 'via' and ref is self_v)]
            obs += [hp.buffer(hr) for hp, hr in holes if hp.distance(old) < a.rmax + 1]
            for g, ok_v, ok_t, lays_ in keep:
                if ok_t and l in lays_:
                    obs.append(g)
            bad = prepared.prep(unary_union(obs).buffer(CL + w / 2)) if obs else None
            for st in starts:
                n = int((a.rmax + 0.5) / STEP)
                free = lambda i, j: bad is None or not bad.contains(Point(old.x + i * STEP, old.y + j * STEP))
                s0 = (round((st[0] - old.x) / STEP), round((st[1] - old.y) / STEP))
                D, prev, pq = {s0: 0.0}, {}, [(0.0, s0)]
                while pq:
                    d, (i, j) = heapq.heappop(pq)
                    if d > D.get((i, j), 9e9):
                        continue
                    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        q = (i + di, j + dj)
                        if abs(q[0]) > n or abs(q[1]) > n:
                            continue
                        nd = d + STEP * (1.4142 if di and dj else 1.0)
                        if nd < D.get(q, 9e9) and free(*q):
                            D[q] = nd; prev[q] = (i, j); heapq.heappush(pq, (nd, q))
                dist[(l, st)] = (D, prev, s0, st)
        best = None
        for rr, dx, dy in spots:
            q = (round(dx / STEP), round(dy / STEP))
            if all(q in v[0] for v in dist.values()):
                tot = sum(v[0][q] for v in dist.values())
                if best is None or tot < best[0]:
                    best = (tot, q, (old.x + dx, old.y + dy))
        if best is None:
            return None
        _, q, c = best
        out = {}
        for key, (D, prev, s0, st) in dist.items():
            cells = [q]
            while cells[-1] != s0:
                cells.append(prev[cells[-1]])
            cells.reverse()
            pts = [st] + [(old.x + i * STEP, old.y + j * STEP) for i, j in cells[1:-1]] + [c]
            # drop points on a straight run
            simp = [pts[0]]
            for k in range(1, len(pts) - 1):
                (x0, y0), (x1, y1), (x2, y2) = simp[-1], pts[k], pts[k + 1]
                if abs((x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1)) > 1e-9:
                    simp.append(pts[k])
            simp.append(c)
            if not stub_ok(LineString(simp).buffer(lays[key[0]][0] / 2), net, key[0], self_v):
                return None
            out[key] = simp
        return c, out

    offs = []
    n = int(a.rmax / STEP)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            r = math.hypot(i * STEP, j * STEP)
            if 0 < r <= a.rmax:
                offs.append((r, i * STEP, j * STEP))
    offs.sort()

    # ---- which vias break the rule
    bad = []
    for v in vias:
        pt = via_holes[id(v)]
        ring = pt.buffer(mm(v.GetWidth(F)) / 2)
        hits = [smd[j] for j in smd_tree.query(ring.buffer(GAP), predicate='intersects')]
        if hits:
            bad.append((v, hits))
    vidx = {id(it[4]): k for k, it in enumerate(items) if it[3] == 'via'}

    log, moved, deleted, failed = [], 0, [], []
    tabs = {}
    for v, hits in bad:
        if any(h[5] for h in hits):
            tab = [h for h in hits if h[5]][0]
            dead.add(vidx[id(v)])
            b.Remove(v)
            deleted.append(tab[1])
            tabs.setdefault(tab[1], [tab, 0])[1] += 1
    def search(old, lays, net, r, h, v):
        """nearest legal via spot with straight or L stubs, else grid-routed stubs: ((dist, c), paths) or None"""
        for rr, dx, dy in offs:
            c = (old.x + dx, old.y + dy)
            if not via_ok(c, net, r, h, v):
                continue
            ok = True
            paths = {}
            for l, (w, starts) in lays.items():
                for st in starts:
                    if Point(st).distance(Point(c)) < 1e-6:
                        continue
                    for pth in ([st, c], [st, (c[0], st[1]), c], [st, (st[0], c[1]), c]):
                        if stub_ok(LineString(pth).buffer(w / 2), net, l, v):
                            paths[(l, st)] = pth; break
                    else:
                        ok = False; break
                if not ok:
                    break
            if ok:
                return (rr, c), paths
        spots = [(rr, dx, dy) for rr, dx, dy in offs if via_ok((old.x + dx, old.y + dy), net, r, h, v)]
        gp = grid_paths(old, lays, net, v, spots) if spots else None
        if gp:
            c, paths = gp
            return (math.hypot(c[0] - old.x, c[1] - old.y), c), paths
        return None

    for v, hits in bad:
        if any(h[5] for h in hits):
            continue
        net = v.GetNetname()
        old = via_holes[id(v)]
        r, h = mm(v.GetWidth(F)) / 2, mm(v.GetDrillValue()) / 2
        # layers on which copper meets the via: tracks ending in it (stub from that track end), and the pads it
        # sits in (stub from the old centre, which is inside the pad)
        lays = {}          # layer -> [width, set of stub start points]
        for g, n_, l, k, ref in others(old.buffer(r), 0.0):
            if n_ != net:
                continue
            if k == 'trk':
                for q in (ref.GetStart(), ref.GetEnd()):
                    qp = (round(mm(q.x), 6), round(mm(q.y), 6))
                    if Point(qp).distance(old) <= r + 1e-3:
                        e = lays.setdefault(l, [0, set()])
                        e[0] = max(e[0], mm(ref.GetWidth())); e[1].add(qp)
            elif k == 'pad' and l in (F, B):
                lays.setdefault(l, [0, set()])[1].add((old.x, old.y))
        for hh in hits:
            if hh[2] == net:
                lays.setdefault(hh[3], [0, set()])[1].add((old.x, old.y))
        for l, e in lays.items():
            if e[0] == 0:
                padw = min((min(hh[0].bounds[2] - hh[0].bounds[0], hh[0].bounds[3] - hh[0].bounds[1]) for hh in hits if hh[3] == l), default=R['stub'])
                e[0] = max(R['stub'], min(1.0, padw))
        dead.add(vidx[id(v)])
        # stubs as wide as the track they continue (a power via keeps its current capacity); only when nothing fits
        # are they narrowed to THIN, and the log says so
        tries = [lays]
        if any(w > THIN for w, _ in lays.values()):
            tries.append({l: [min(w, THIN), st] for l, (w, st) in lays.items()})
        for lays in tries:
            found = search(old, lays, net, r, h, v)
            if found:
                found, found_paths = found
                break
        if found and lays is not tries[0]:
            log.append(f'narrowed stubs to {THIN} mm: {hits[0][1]} {net}')
        if not found and len(lays) == 1 and net:
            # the via only joins its pad to the other layers: route the pad to a neighbouring via of the same net
            # instead, and delete this one
            others_v = [(Point(mm(o.GetPosition().x), mm(o.GetPosition().y)), o) for o in vias
                        if o is not v and o.GetNetname() == net and vidx[id(o)] not in dead
                        and Point(mm(o.GetPosition().x), mm(o.GetPosition().y)).distance(old) <= a.rmax]
            others_v += [(it[0].centroid, it[4]) for it in added if it[3] == 'via' and it[1] == net and it[0].centroid.distance(old) <= a.rmax]
            spots2 = sorted((q.distance(old), q.x - old.x, q.y - old.y) for q, o in others_v)
            spots2 = [sp for sp in spots2 if abs(sp[1] / STEP - round(sp[1] / STEP)) < 1e-6 and abs(sp[2] / STEP - round(sp[2] / STEP)) < 1e-6] or spots2
            gp = grid_paths(old, lays, net, v, spots2) if spots2 else None
            if gp:
                c, pths = gp
                (l, _), pth = next(iter(pths.items()))
                w = lays[l][0]
                for p0, p1 in zip(pth, pth[1:]):
                    if Point(p0).distance(Point(p1)) < 1e-6:
                        continue
                    t = pcbnew.PCB_TRACK(b)
                    t.SetStart(pcbnew.VECTOR2I(MM(p0[0]), MM(p0[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(p1[0]), MM(p1[1])))
                    t.SetWidth(MM(w)); t.SetLayer(l); t.SetNet(v.GetNet())
                    b.Add(t)
                    added.append([LineString([p0, p1]).buffer(w / 2), net, l, 'trk', t])
                b.Remove(v)
                moved += 1
                log.append(f'joined {hits[0][1]} {net} to a neighbouring via ({math.hypot(c[0] - old.x, c[1] - old.y):.2f} mm), in-pad via deleted')
                continue
        if not found:
            if os.environ.get('DIAG'):
                nv = sum(1 for rr, dx, dy in offs if via_ok((old.x + dx, old.y + dy), net, r, h, v))
                print(f'DIAG {hits[0][1]} {net}: {nv} legal via spots within {a.rmax} mm, stub layers '
                      f'{[b.GetLayerName(l) for l in lays]}', file=sys.stderr)
            dead.discard(vidx[id(v)])
            failed.append((hits[0][1], net, round(old.x, 2), round(old.y, 2)))
            continue
        rr, c = found
        paths = found_paths
        v.SetPosition(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
        added.append([Point(c).buffer(r), net, -1, 'via', v])
        for (l, st), pth in paths.items():
            w = lays[l][0]
            for p0, p1 in zip(pth, pth[1:]):
                if Point(p0).distance(Point(p1)) < 1e-6:
                    continue
                t = pcbnew.PCB_TRACK(b)
                t.SetStart(pcbnew.VECTOR2I(MM(p0[0]), MM(p0[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(p1[0]), MM(p1[1])))
                t.SetWidth(MM(w)); t.SetLayer(l); t.SetNet(v.GetNet())
                b.Add(t)
                added.append([LineString([p0, p1]).buffer(w / 2), net, l, 'trk', t])
        moved += 1
        log.append(f'moved {hits[0][1]} {net} {rr:.2f} mm')

    # ---- replace the deleted tab vias with vias in the tab's own copper, outside the pad
    ringed = 0
    if not a.no_tab_ring and tabs:
        zones = {}
        for z in b.Zones():
            if not z.GetIsRuleArea():
                for l in z.GetLayerSet().CuStack():
                    zones.setdefault((z.GetNetname(), l), []).append(poly_of(z.Outline()))
        proto = [v for v in vias if v.GetNetname()][0]
        r, h = mm(proto.GetWidth(F)) / 2, mm(proto.GetDrillValue()) / 2
        for tid, (tab, ndel) in tabs.items():
            g, _, net, lay, pad, _ = tab
            fz = unary_union(zones.get((net, F), []))
            if fz.is_empty:
                continue
            # candidates: a 0.9 mm grid in the pour within 3 mm of the tab, nearest first
            minx, miny, maxx, maxy = g.buffer(3).bounds
            cand = []
            x = minx
            while x <= maxx:
                y = miny
                while y <= maxy:
                    p = Point(x, y)
                    if fz.contains(p.buffer(r + CL)) and g.distance(p) <= 3.0:
                        cand.append((g.distance(p), x, y))
                    y += 0.45
                x += 0.45
            cand.sort()
            k = 0
            for _, x, y in cand:
                if k >= ndel:
                    break
                if via_ok((x, y), net, r, h, None):
                    nv = pcbnew.PCB_VIA(b)
                    nv.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
                    nv.SetWidth(MM(2 * r)); nv.SetDrill(MM(2 * h)); nv.SetNet(pad.GetNet())
                    nv.SetViaType(pcbnew.VIATYPE_THROUGH)
                    b.Add(nv)
                    added.append([Point(x, y).buffer(r), net, -1, 'via', nv])
                    k += 1
            ringed += k
            log.append(f'tab {tid} {net}: {ndel} vias removed from the pad, {k} added around it')

    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(a.out)
    summ = (f'{len(bad)} vias in or within {GAP} mm of an SMD pad: {len(deleted)} deleted from {len(tabs)} driver tabs '
            f'({ringed} added around the tabs), {moved} moved out, {len(failed)} left for a hand re-route')
    lines = [summ] + [f'  hand re-route: {f[0]} {f[1]} at {f[2]},{f[3]}' for f in failed] + log
    if a.report:
        open(a.report, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:1 + len(failed)]))


if __name__ == '__main__':
    main()
