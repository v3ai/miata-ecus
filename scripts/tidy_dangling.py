"""tidy_dangling.py <in.kicad_pcb> <out.kicad_pcb> (KiCad 9): trim the tracks and remove the vias that KiCad's DRC
calls dangling (track_dangling, via_dangling), as long as nothing becomes unconnected.

A change order that cuts and rejoins copper (castellate_mb.sh) leaves stubs: a track end past the point where a
join met it (finish_route.py joins onto the middle of a segment), a via left with one track. KiCad's own report says
what dangles. A dangling segment is cut back to the farthest point where other copper of its net still meets it
(another track's end, a via, a pad); with no such point beyond its connected end, or lying wholly inside other
copper of its net, it goes. A via goes; tracks ending inside its ring off its centre are moved to the centre first
(a via that joins tracks on one layer only).
A batch that would leave a connection open is undone and split in two, down to single items, which are then left
as they are. One batch per process (pcbnew's objects go bad after a Remove)."""
import gc
import json
import os
import shutil
import subprocess
import sys
import tempfile

gc.disable()      # pcbnew's SWIG temporaries crash the cyclic collector under KiCad 9
TOL = 1e-3        # mm


def drc(path):
    with tempfile.TemporaryDirectory() as td:
        rep = os.path.join(td, 'drc.json')
        subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', rep, path],
                       capture_output=True)
        return json.load(open(rep))


def one_round(path, ids):
    import pcbnew
    from shapely.geometry import LineString, Point, Polygon
    from shapely.ops import unary_union
    mm, MM = pcbnew.ToMM, pcbnew.FromMM
    b = pcbnew.LoadBoard(path)

    def copper(net, layer, skip):
        """this net's other copper on the layer, and the points where it can meet a track (anchors)"""
        geo, anchors = [], []
        for t in b.GetTracks():
            if t.GetNetname() != net or t.m_Uuid.AsString() == skip:
                continue
            if t.Type() == pcbnew.PCB_VIA_T:
                p = t.GetPosition()
                c = Point(mm(p.x), mm(p.y))
                geo.append(c.buffer(mm(t.GetWidth(layer)) / 2))
                anchors.append(c)
            elif t.GetLayer() == layer:
                s, e = t.GetStart(), t.GetEnd()
                ln = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]) if s != e else Point(mm(s.x), mm(s.y))
                geo.append(ln.buffer(mm(t.GetWidth()) / 2))
                anchors += [Point(mm(s.x), mm(s.y)), Point(mm(e.x), mm(e.y))]
        for f in b.GetFootprints():
            for p in f.Pads():
                if p.GetNetname() != net or not p.IsOnLayer(layer):
                    continue
                ps = pcbnew.SHAPE_POLY_SET()
                p.TransformShapeToPolygon(ps, layer, 0, MM(0.005), pcbnew.ERROR_INSIDE)
                for i in range(ps.OutlineCount()):
                    o = ps.Outline(i)
                    q = Polygon([(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())])
                    geo.append(q if q.is_valid else q.buffer(0))
                anchors.append(Point(mm(p.GetPosition().x), mm(p.GetPosition().y)))
        for z in b.Zones():
            if z.GetNetname() == net and z.IsOnLayer(layer):
                ps = z.GetFilledPolysList(layer)
                for i in range(ps.OutlineCount()):
                    o = ps.Outline(i)
                    if o.PointCount() >= 3:
                        q = Polygon([(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())])
                        geo.append(q if q.is_valid else q.buffer(0))
        return unary_union(geo) if geo else Polygon(), anchors

    drop, trim = [], []                        # decide everything first: pcbnew's objects go bad after a Remove
    for t in list(b.GetTracks()):
        uid = t.m_Uuid.AsString()
        if uid not in ids:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            # a via that only joins tracks on one layer: their ends inside its ring move to its centre first
            c = t.GetPosition()
            r = t.GetWidth(pcbnew.F_Cu) / 2
            for u in b.GetTracks():
                if u.Type() == pcbnew.PCB_VIA_T or u.GetNetname() != t.GetNetname():
                    continue
                for get, put in ((u.GetStart, u.SetStart), (u.GetEnd, u.SetEnd)):
                    q = get()
                    if q != c and (q - c).EuclideanNorm() < r:
                        trim.append((u, put, c))
            drop.append(t)
            continue
        s, e = t.GetStart(), t.GetEnd()
        S, E = Point(mm(s.x), mm(s.y)), Point(mm(e.x), mm(e.y))
        seg = LineString([S, E]) if S.distance(E) > TOL else None
        geo, anchors = copper(t.GetNetname(), t.GetLayer(), uid)
        if seg is None:
            drop.append(t)
            continue
        half = mm(t.GetWidth()) / 2
        if geo.buffer(TOL).contains(seg.buffer(half)):
            drop.append(t)                     # wholly inside other copper of its net: adds nothing
            continue
        # positions along the segment (0 at start, 1 at end) where other copper meets it
        ts = [seg.project(a, normalized=True) for a in anchors if a.distance(seg) <= half + TOL]
        s_ok, e_ok = geo.distance(S) <= TOL, geo.distance(E) <= TOL
        lo = 0.0 if s_ok else min(ts, default=None)
        hi = 1.0 if e_ok else max(ts, default=None)
        if lo is not None and hi is not None and lo * seg.length < TOL and (1 - hi) * seg.length < TOL:
            lo = None                          # nothing to cut back: both ends look joined here, KiCad says not
        if lo is None or hi is None or hi - lo < TOL / seg.length:
            drop.append(t)                     # (both ends may look joined here: KiCad's verdict wins, and the
                                               # check that nothing comes open still guards it)
            continue
        a, c = seg.interpolate(lo, normalized=True), seg.interpolate(hi, normalized=True)
        trim += [(t, t.SetStart, pcbnew.VECTOR2I(MM(a.x), MM(a.y))), (t, t.SetEnd, pcbnew.VECTOR2I(MM(c.x), MM(c.y)))]
    for _, put, q in trim:
        put(q)
    for t in drop:
        b.Remove(t)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(path, b)
    print('DONE', len(drop), len(trim))


def dangling(d):
    return sorted({i['uuid'] for v in d['violations'] if v['type'] in ('track_dangling', 'via_dangling')
                   for i in v['items'] if i.get('uuid')})


def main(src, dst):
    shutil.copy(src, dst)
    pro = src[:-len('.kicad_pcb')] + '.kicad_pro'
    if os.path.exists(pro):
        shutil.copy(pro, dst[:-len('.kicad_pcb')] + '.kicad_pro')
    d = drc(dst)
    open0 = len(d['unconnected_items'])
    tried_alone, done = set(), 0

    def attempt(ids):
        keep = dst + '.bak'
        shutil.copy(dst, keep)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), '--round', dst] + ids,
                           capture_output=True, text=True)
        if 'DONE' not in r.stdout:
            shutil.move(keep, dst)
            sys.exit(f'round failed:\n{r.stdout[-1500:]}{r.stderr[-1500:]}')
        dd = drc(dst)
        if len(dd['unconnected_items']) > open0:
            shutil.move(keep, dst)
            return None
        os.remove(keep)
        return dd

    for _ in range(12):
        ids = [i for i in dangling(d) if i not in tried_alone]
        if not ids:
            break
        stack, progress = [ids], False
        while stack:
            batch = stack.pop()
            dd = attempt(batch)
            if dd is not None:
                d, done, progress = dd, done + len(batch), True
            elif len(batch) > 1:
                stack += [batch[:len(batch) // 2], batch[len(batch) // 2:]]
            else:
                tried_alone.add(batch[0])
        if not progress:
            break
    left = dangling(d)
    print(f'{done} dangling tracks and vias trimmed or removed; {len(left)} left'
          + (f' ({len(tried_alone)} would open a connection)' if tried_alone else ''))


if __name__ == '__main__':
    if sys.argv[1] == '--round':
        one_round(sys.argv[2], set(sys.argv[3:]))
    else:
        main(*sys.argv[1:3])
