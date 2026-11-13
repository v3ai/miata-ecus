#!/usr/bin/env python3
"""Join what the autorouter left open, on the real copper, on every signal layer.

The autorouter (route.py) works on a 0.25 mm grid and gives up on a pad it cannot reach there. This finisher works on
the board file itself: exact copper outlines of every other net as obstacles (tracks, vias, pads, pours that are not
planes), a 0.05 mm grid, 0.15 mm clearance plus a margin, through vias 0.6 / 0.3 mm. It handles any number of signal
layers (two-layer boards; four-layer boards with two planes; the six-layer daughterboard: F.Cu, In2.Cu, In3.Cu, B.Cu).

For each net that is in more than one piece it takes the piece holding the named pad (or the smallest piece), starts
from all of that piece's copper, and searches to any copper of another piece of the same net. A pad of a plane net
(GND, +3V3) that nothing ties to its plane (a pour island around it does not count) is led to the nearest spot where
a via fits, and gets the via. Tracks that the grid router left nearer than the clearance to another net are removed
first and joined again.

usage: finish_route.py --unclose in.kicad_pcb out.kicad_pcb                (first: remove the too-close tracks)
       finish_route.py --free in.kicad_pcb out.kicad_pcb REF.PAD ...       (make room for a via in a boxed-in pad)
       finish_route.py in.kicad_pcb out.kicad_pcb [NET[:REF:PAD] ...]      (no nets given: every net in pieces)
env:   TW track width (0.2), CL clearance with margin (0.17); PLANE_FIRST=1 places the plane vias before the signals
Prints one line per connection; exits 1 if any is left open.
"""
import collections
import heapq
import math
import os
import sys
import pcbnew
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely import prepared
from shapely.strtree import STRtree

mm, IU = pcbnew.ToMM, pcbnew.FromMM
TW = float(os.environ.get('TW', '0.2'))
CL = float(os.environ.get('CL', '0.17'))
VD, VDRILL, G = 0.6, 0.3, 0.05
PLANES = ('GND', '+3V3')
# nets whose current needs the thicker outer copper on a six-layer board (as route.py's OUTER_ONLY)
OUTER = {'OUT_INJ1', 'OUT_INJ2', 'OUT_INJ3', 'OUT_INJ4', 'OUT_IACV', 'OUT_VVT', 'OUT_BOOST', '+12V_IN', '+12V', '+12V_F',
         'BUCK_SW', 'USB_VBUS'}
MARGINS = (3.0, 6.0, 10.0, 16.0)
LIMIT = 900000


def sig_layers(b):
    n = b.GetCopperLayerCount()
    names = ['F.Cu', 'In2.Cu', 'In3.Cu', 'B.Cu'] if n == 6 else ['F.Cu', 'B.Cu']
    return names


def pad_poly(pd):
    try:
        ol = pd.GetEffectivePolygon().Outline(0)
        return Polygon([(mm(ol.CPoint(i).x), mm(ol.CPoint(i).y)) for i in range(ol.PointCount())])
    except Exception:
        bb = pd.GetBoundingBox()
        return box(mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))


class Board:
    def __init__(self, path):
        self.b = pcbnew.LoadBoard(path)
        self.sig = sig_layers(self.b)
        self.lid = {n: self.b.GetLayerID(n) for n in self.sig}
        bb = self.b.GetBoardEdgesBoundingBox()
        self.edge = box(mm(bb.GetLeft()) + 0.4, mm(bb.GetTop()) + 0.4, mm(bb.GetRight()) - 0.4, mm(bb.GetBottom()) - 0.4)
        self.load()

    def load(self):
        """items per net: ('t', layer, geom) track, ('v', None, geom) via, ('p', layers, geom, ref, num) pad"""
        b = self.b
        self.items = collections.defaultdict(list)
        self.holes = []
        for t in b.GetTracks():
            n = t.GetNetname()
            if t.Type() == pcbnew.PCB_VIA_T:
                p = t.GetPosition()
                self.items[n].append(('v', None, Point(mm(p.x), mm(p.y)).buffer(mm(t.GetWidth()) / 2)))
                self.holes.append(Point(mm(p.x), mm(p.y)).buffer(mm(t.GetDrillValue()) / 2))
            elif t.GetLayerName() in self.lid:
                s, e = t.GetStart(), t.GetEnd()
                g = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, cap_style=1)
                self.items[n].append(('t', t.GetLayerName(), g))
        for fp in b.GetFootprints():
            for pd in fp.Pads():
                layers = [l for l in self.sig if pd.IsOnLayer(self.lid[l])]
                poly = pad_poly(pd)
                if pd.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    poly = poly.buffer(0.05)                       # 0.2 mm to a bare hole, not 0.15
                    layers = list(self.sig)
                if layers:
                    self.items[pd.GetNetname()].append(('p', layers, poly, fp.GetReference(), pd.GetNumber()))
                if pd.GetDrillSize().x > 0:
                    self.holes.append(Point(mm(pd.GetPosition().x), mm(pd.GetPosition().y)).buffer(mm(pd.GetDrillSize().x) / 2))
        # pours that are not planes block the way like any copper (their outline: they may not be filled yet)
        self.zones = collections.defaultdict(list)
        for z in b.Zones():
            if z.GetNetname() in PLANES or z.GetIsRuleArea():
                continue
            o = z.Outline().Outline(0)
            poly = Polygon([(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())])
            for L in z.GetLayerSet().Seq():
                nm = b.GetLayerName(L)
                if nm in self.lid:
                    self.zones[z.GetNetname()].append((nm, poly))

    def pieces(self, net):
        """connected pieces of a net's copper: lists of item indexes"""
        it = self.items[net]
        par = list(range(len(it)))

        def find(a):
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a
        lay = [set(self.sig if a[0] == 'v' else ([a[1]] if a[0] == 't' else a[1])) for a in it]
        if it:
            tree = STRtree([a[2] for a in it])
            for i, a in enumerate(it):
                for j in tree.query(a[2], predicate='intersects'):
                    if j > i and lay[i] & lay[j]:
                        par[find(i)] = find(int(j))
        # a pour of the net joins what it covers (plane nets are handled by the caller)
        for nm, poly in self.zones.get(net, []):
            first = None
            for i, a in enumerate(it):
                la = self.sig if a[0] == 'v' else ([a[1]] if a[0] == 't' else a[1])
                if nm in la and a[2].intersects(poly):
                    if first is None:
                        first = i
                    else:
                        par[find(i)] = find(first)
        groups = collections.defaultdict(list)
        for i in range(len(it)):
            groups[find(i)].append(i)
        return list(groups.values())

    def route(self, net, src_idx, dst_idx, plane=False, tw=TW):
        """A* from the copper of items src_idx to the copper of items dst_idx (or, plane=True, to a via site)"""
        from shapely.ops import nearest_points
        it = self.items[net]
        sg = unary_union([it[i][2] for i in src_idx])
        if plane:
            x0, y0, x1, y1 = unary_union([it[i][2] for i in src_idx if it[i][0] == 'p']).bounds
        else:
            # window around the closest approach of the two pieces, not around the whole net
            pa, pb = nearest_points(sg, unary_union([it[i][2] for i in dst_idx]))
            x0, y0, x1, y1 = min(pa.x, pb.x), min(pa.y, pb.y), max(pa.x, pb.x), max(pa.y, pb.y)
        for margin in MARGINS:
            win = box(x0 - margin, y0 - margin, x1 + margin, y1 + margin).intersection(self.edge)
            r = self._search(net, src_idx, dst_idx, plane, tw, win)
            if r:
                return r
        return None

    def _search(self, net, src_idx, dst_idx, plane, tw, win):
        it = self.items[net]
        X0, Y0, X1, Y1 = win.bounds
        nx, ny = int((X1 - X0) / G) + 1, int((Y1 - Y0) / G) + 1
        big = win.buffer(1.5)
        obs = {l: [] for l in self.sig}
        for n2, lst in self.items.items():
            if n2 == net:
                continue
            for a in lst:
                if not a[2].intersects(big):
                    continue
                for l in (self.sig if a[0] == 'v' else ([a[1]] if a[0] == 't' else a[1])):
                    obs[l].append(a[2])
        for n2, lst in self.zones.items():
            if n2 != net:
                for nm, poly in lst:
                    if poly.intersects(big):
                        obs[nm].append(poly)
        ob = {l: prepared.prep(unary_union(obs[l]).buffer(CL + tw / 2)) for l in self.sig}
        ov = prepared.prep(unary_union([g for l in self.sig for g in obs[l]]).buffer(CL + VD / 2))
        hv = prepared.prep(unary_union([h for h in self.holes if h.intersects(big)] or [Point(-1e3, -1e3)]).buffer(0.32 + VD / 2))
        own_pads = [a[2] for a in it if a[0] == 'p']
        nopad = prepared.prep(unary_union(own_pads or [Point(-1e3, -1e3)]).buffer(VD / 2 + 0.25))
        winp = prepared.prep(win)

        def xy(i, j):
            return (X0 + i * G, Y0 + j * G)
        free, vfree = {}, {}

        def ok(l, i, j):
            k = (l, i, j)
            if k not in free:
                free[k] = not ob[l].contains(Point(*xy(i, j)))
            return free[k]

        def vok(i, j):
            if (i, j) not in vfree:
                p = Point(*xy(i, j))
                vfree[(i, j)] = not ov.contains(p) and not hv.contains(p) and not nopad.contains(p)
            return vfree[(i, j)]

        def cells(idx, shrink=0.03):
            out = set()
            for k in idx:
                a = it[k]
                g = a[2].buffer(-shrink).intersection(win)
                if g.is_empty:
                    g = a[2].intersection(win)
                    if g.is_empty:
                        continue
                gp = prepared.prep(g.buffer(1e-6))
                bx0, by0, bx1, by1 = g.bounds
                ls = self.sig if a[0] == 'v' else ([a[1]] if a[0] == 't' else a[1])
                for i in range(max(0, int((bx0 - X0) / G)), min(nx, int((bx1 - X0) / G) + 2)):
                    for j in range(max(0, int((by0 - Y0) / G)), min(ny, int((by1 - Y0) / G) + 2)):
                        if gp.contains(Point(*xy(i, j))):
                            for l in ls:
                                out.add((l, i, j))
            return out
        starts = cells(src_idx)
        own = set(starts)
        goals = set() if plane else cells(dst_idx)
        if not starts or (not plane and not goals):
            return None
        if plane:
            c = unary_union([it[i][2] for i in src_idx]).centroid
            gx = [(c.x, c.y)]
        else:
            gx = [xy(i, j) for (_, i, j) in goals]
            gx = gx[::max(1, len(gx) // 300)]

        def h(i, j):
            if plane:
                return 0.0
            x, y = xy(i, j)
            return min(math.hypot(x - a, y - c) for a, c in gx)
        DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        LC = {l: (1.0 if l in ('F.Cu', 'B.Cu') else 0.9) for l in self.sig}
        openq = [(h(s[1], s[2]), 0.0, s, None) for s in starts]
        heapq.heapify(openq)
        cost = {s: 0.0 for s in starts}
        came = {}
        found, via_at, n = None, None, 0
        while openq:
            f, g, s, d = heapq.heappop(openq)
            if cost.get(s, 1e9) < g - 1e-9:
                continue
            l, i, j = s
            if s in goals:
                found = s
                break
            if plane and s not in own and vok(i, j):
                found, via_at = s, xy(i, j)
                break
            n += 1
            if n > LIMIT:
                break
            for di, dj in DIRS:
                ni, nj = i + di, j + dj
                if not (0 <= ni < nx and 0 <= nj < ny):
                    continue
                ns = (l, ni, nj)
                if ns in own or ns in goals or ok(l, ni, nj):
                    ng = g + G * math.hypot(di, dj) * LC[l] + (0.02 if d and d != (di, dj) else 0)
                    if ng < cost.get(ns, 1e9):
                        cost[ns] = ng; came[ns] = (s, (di, dj))
                        heapq.heappush(openq, (ng + h(ni, nj), ng, ns, (di, dj)))
            if not plane and vok(i, j):
                for ol in (('F.Cu', 'B.Cu') if net in OUTER else self.sig):
                    if ol != l and (ok(ol, i, j) or (ol, i, j) in own or (ol, i, j) in goals):
                        ns = (ol, i, j)
                        ng = g + 1.5
                        if ng < cost.get(ns, 1e9):
                            cost[ns] = ng; came[ns] = (s, None)
                            heapq.heappush(openq, (ng + h(i, j), ng, ns, None))
        if not found:
            return None
        path = [found]
        while path[-1] in came:
            path.append(came[path[-1]][0])
        path.reverse()
        # drop the part of the path that runs inside the start piece's own copper, keeping one point of it
        k = 0
        while k + 1 < len(path) and path[k + 1] in own and path[k + 1][0] == path[k][0]:
            k += 1
        path = path[k:]
        segs, vias, run = [], [], [path[0]]
        for a, c2 in zip(path, path[1:]):
            if a[0] != c2[0]:
                segs.append(run); vias.append(xy(a[1], a[2])); run = [c2]
            else:
                run.append(c2)
        segs.append(run)
        if via_at:
            vias.append(via_at)
        return [[(r[0][0], [xy(p[1], p[2]) for p in simplify(r)]) for r in segs if len(r) > 1], vias, cost[found], tw]

    def commit(self, net, res):
        segs, vias, length, tw = res
        nt = self.b.FindNet(net)
        for layer, pts in segs:
            for a, c in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(self.b)
                t.SetStart(pcbnew.VECTOR2I(IU(a[0]), IU(a[1]))); t.SetEnd(pcbnew.VECTOR2I(IU(c[0]), IU(c[1])))
                t.SetWidth(IU(tw)); t.SetLayer(self.lid[layer]); t.SetNet(nt)
                self.b.Add(t)
        for x, y in vias:
            v = pcbnew.PCB_VIA(self.b)
            v.SetPosition(pcbnew.VECTOR2I(IU(x), IU(y))); v.SetWidth(IU(VD)); v.SetDrill(IU(VDRILL)); v.SetNet(nt)
            self.b.Add(v)
        self.load()


def simplify(run):
    pts = [run[0]]
    for k in range(1, len(run) - 1):
        d1 = (run[k][1] - pts[-1][1], run[k][2] - pts[-1][2])
        d2 = (run[k + 1][1] - run[k][1], run[k + 1][2] - run[k][2])
        if math.atan2(d1[1], d1[0]) != math.atan2(d2[1], d2[0]):
            pts.append(run[k])
    pts.append(run[-1])
    return pts


def fill_polys(B, net):
    """[(layer name, polygon)] for every filled piece of the net's pours on the signal layers"""
    out = []
    for z in B.b.Zones():
        if z.GetNetname() != net:
            continue
        for L in z.GetLayerSet().Seq():
            nm = B.b.GetLayerName(L)
            if nm not in B.lid:
                continue
            ps = z.GetFilledPolysList(L)
            for k in range(ps.OutlineCount()):
                o = ps.Outline(k)
                pts = [(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())]
                if len(pts) >= 3:
                    g = Polygon(pts)
                    out.append((nm, g if g.is_valid else g.buffer(0)))
    return out


def loose_plane_pieces(B, net):
    """Pieces of a plane net (pads, tracks, pour islands) that hold a pad but no via and no plated hole: nothing ties
    them to the plane. Returns [(item indexes of B.items[net], pad names)]."""
    it = B.items[net]
    geoms = [a[2] for a in it]
    lay = [set(B.sig if a[0] == 'v' else ([a[1]] if a[0] == 't' else a[1])) for a in it]
    n0 = len(it)
    for nm, g in fill_polys(B, net):
        geoms.append(g); lay.append({nm})
    par = list(range(len(geoms)))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    tree = STRtree(geoms)
    for i, g in enumerate(geoms):
        for j in tree.query(g, predicate='intersects'):
            if j > i and lay[i] & lay[j]:
                par[find(i)] = find(int(j))
    groups = collections.defaultdict(list)
    for i in range(n0):
        groups[find(i)].append(i)
    out = []
    for idx in groups.values():
        its = [it[i] for i in idx]
        pads = [a for a in its if a[0] == 'p']
        if pads and not any(a[0] == 'v' for a in its) and not any(len(a[1]) == len(B.sig) for a in pads):
            out.append((idx, tuple(sorted((a[3], a[4]) for a in pads))))
    return out


def via_in_pad(B, net, idx):
    """A boxed-in pad on a six-layer board: the via goes into the pad itself (JLCPCB fills and caps every via on a
    six-layer board, so a via in a pad solders like the pad). Returns a route result or None."""
    if len(B.sig) != 4:
        return None
    others = [a[2] for n2, lst in B.items.items() if n2 != net for a in lst]
    tree = STRtree(others)
    holes = unary_union(B.holes).buffer(0.32 + VD / 2)
    for i in idx:
        a = B.items[net][i]
        if a[0] != 'p':
            continue
        c0 = a[2].centroid
        x0, y0, x1, y1 = a[2].bounds
        cand = [Point(x0 + i * G, y0 + j * G) for i in range(int((x1 - x0) / G) + 1) for j in range(int((y1 - y0) / G) + 1)]
        for c in sorted((q for q in cand if a[2].contains(q)), key=lambda q: q.distance(c0)):    # nearest the middle first
            v = c.buffer(VD / 2)
            if holes.contains(c) or not B.edge.contains(c):
                continue
            if any(others[int(j)].distance(v) < CL for j in tree.query(v, predicate='dwithin', distance=CL)):
                continue
            return [[], [(round(c.x, 3), round(c.y, 3))], 0.0, TW]
    return None


def stitch_planes(B):
    """pads of the plane nets that nothing ties to their plane: lead each loose piece to a via site"""
    left = 0
    for net in PLANES:
        skip = set()
        for _ in range(80):
            pcbnew.ZONE_FILLER(B.b).Fill(B.b.Zones())
            todo = [t for t in loose_plane_pieces(B, net) if t[1] not in skip]
            if not todo:
                break
            idx, key = todo[0]
            names = ', '.join(f'{r}.{n}' for r, n in key[:4])
            res = B.route(net, idx, [], plane=True) or B.route(net, idx, [], plane=True, tw=0.15) or via_in_pad(B, net, idx)
            if not res:
                print(f'{net}: NO VIA SITE for {names}  (BLOCKED {key[0][0]}.{key[0][1]})', flush=True)
                left += 1
                skip.add(key)
                continue
            print(f'{net}: via for {names}, ' + (f'{res[2]:.1f} mm of track' if res[0] else 'in the pad'), flush=True)
            B.commit(net, res)
    return left


def too_close(B, limit=0.149):
    """Tracks nearer than the clearance to another net's pad, track or via on the same layer (the grid router's
    rounding leaves a few). They are removed; the net is then in pieces and gets joined again with the full
    clearance. Returns the nets touched."""
    flat = []                                     # (net, kind, layers, geom)
    for n, lst in B.items.items():
        for a in lst:
            flat.append((n, a[0], set(B.sig if a[0] == 'v' else ([a[1]] if a[0] == 't' else a[1])), a[2]))
    tree = STRtree([f[3] for f in flat])
    bad = []
    for i, (n, kind, ls, g) in enumerate(flat):
        if kind != 't':
            continue
        for j in tree.query(g, predicate='dwithin', distance=limit):
            m, k2, l2, g2 = flat[int(j)]
            if m != n and ls & l2 and (k2 != 't' or n > m) and g.distance(g2) < limit:
                bad.append((n, g))
                break
    nets = set()
    tracks = [t for t in B.b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
    for n, g in bad:
        c = g.centroid
        for t in tracks:
            if t.GetNetname() != n:
                continue
            s, e = t.GetStart(), t.GetEnd()
            if abs((mm(s.x) + mm(e.x)) / 2 - c.x) < 1e-3 and abs((mm(s.y) + mm(e.y)) / 2 - c.y) < 1e-3:
                B.b.Remove(t)
                nets.add(n)
                break
    return nets


def main(src, out, specs):
    B = Board(src)
    want = {}
    for s in specs:
        p = s.split(':')
        want.setdefault(p[0], []).append(tuple(p[1:3]) if len(p) == 3 else None)
    nets = list(want) if want else sorted(n for n in B.items if n and n not in PLANES)
    left = 0
    first = os.environ.get('PLANE_FIRST')
    if first and not want:
        left += stitch_planes(B)
    for net in nets:
        for _ in range(12):
            pcs = B.pieces(net)
            with_pads = [p for p in pcs if any(B.items[net][i][0] == 'p' for i in p)]
            if len(with_pads) < 2:
                break
            # start from the piece holding a named pad, else the smallest piece with a pad
            named = [p for p in with_pads if any(B.items[net][i][0] == 'p' and tuple(B.items[net][i][3:5]) in (want.get(net) or [])
                                                 for i in p)]
            src_p = min(named or with_pads, key=len)
            dst = [i for p in pcs if p is not src_p for i in p]
            res = None
            for tw in dict.fromkeys((TW, 0.15)):
                res = B.route(net, src_p, dst, tw=tw)
                if res:
                    break
            pads = [f'{B.items[net][i][3]}.{B.items[net][i][4]}' for i in src_p if B.items[net][i][0] == 'p']
            if not res:
                print(f'{net}: NO PATH from the piece with {", ".join(pads[:4])}', flush=True)
                left += 1
                break
            print(f'{net}: joined {", ".join(pads[:4])}: {sum(len(p) - 1 for _, p in res[0])} segments on '
                  f'{"/".join(dict.fromkeys(l for l, _ in res[0]))}, {len(res[1])} vias, {res[2]:.1f} mm, {res[3]} mm wide',
                  flush=True)
            B.commit(net, res)
    if not first and not want:
        left += stitch_planes(B)
    pcbnew.ZONE_FILLER(B.b).Fill(B.b.Zones())
    B.b.Save(out)
    print('left open:', left)
    return 1 if left else 0


def free_pads(src, out, pads):
    """Make room for a via in each named pad (REF.PAD): remove the other nets' track segments that a via in the pad's
    middle would foul, on any layer. Those nets are then in pieces; the next finishing run places the via first and
    joins them again around it."""
    B = Board(src)
    want = {tuple(p.split('.')) for p in pads}
    kill = []
    for net, lst in B.items.items():
        for a in lst:
            if a[0] == 'p' and (a[3], a[4]) in want:
                v = a[2].centroid.buffer(VD / 2 + CL)
                for n2, l2 in B.items.items():
                    if n2 != net:
                        kill += [(n2, c[1], c[2].centroid) for c in l2 if c[0] == 't' and c[2].intersects(v)]
    nets = set()
    for t in [t for t in B.b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]:
        s_, e_ = t.GetStart(), t.GetEnd()
        cx, cy = (mm(s_.x) + mm(e_.x)) / 2, (mm(s_.y) + mm(e_.y)) / 2
        if any(t.GetNetname() == n2 and t.GetLayerName() == l and abs(c.x - cx) < 1e-3 and abs(c.y - cy) < 1e-3 for n2, l, c in kill):
            nets.add(t.GetNetname())
            B.b.Remove(t)
    print('made room at', ', '.join(pads), 'by removing track of:', ', '.join(sorted(nets)) or 'nothing', flush=True)
    B.b.Save(out)


if __name__ == '__main__':
    if sys.argv[1] == '--free':
        free_pads(sys.argv[2], sys.argv[3], sys.argv[4:])
        os._exit(0)
    if sys.argv[1] == '--unclose':
        # its own run: pcbnew's objects go bad after a Remove, even across a reload in the same process
        B_ = Board(sys.argv[2])
        nets_ = too_close(B_)
        print('removed tracks nearer than the clearance to another net (to be joined again):',
              ', '.join(sorted(nets_)) or 'none', flush=True)
        B_.b.Save(sys.argv[3])
        os._exit(0)
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3:]))
