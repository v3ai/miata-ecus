"""
Small rip-up-and-reroute grid router for the daughterboard (2 layers).

- 0.25 mm grid aligned to the board origin (the MCU pins sit on it)
- copper rasterised with exact shapely distances: a cell is usable by net N if it is
  inside N's copper, or further than clearance + half track width from other copper
- pads are static obstacles; tracks/vias are dynamic so they can be ripped up
- A* over (layer, x, y, direction) with bend, via and bottom-layer penalties,
  multi-source from everything the net already has, nearest-pad order
- when a connection is blocked it is routed again "softly" through other nets'
  tracks (with a penalty), those nets are ripped up and queued again
- wide nets: obstacle map dilated by the extra half width, falling back to thinner
- GND is not routed: each GND SMD pad gets a short stub to a stitching via and both
  layers get a GND pour
"""
import sys, math, heapq, json, time
from collections import deque
import numpy as np
import shapely
from shapely.geometry import Polygon, Point, LineString, box
from scipy import ndimage
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

OX, OY = 100.0, 50.0
G = 0.25                       # grid pitch (mm)
CLR = 0.15                     # copper clearance
SIG_W = 0.2                    # default track width
VIA_D, VIA_DRILL = 0.6, 0.3
EDGE_CLR = 0.35
HALO = CLR + SIG_W / 2
import pcbnew as _p
ROUTE_LAYERS = [_p.F_Cu, _p.B_Cu]      # In1.Cu = GND plane, In2.Cu = +3V3 plane
NL = len(ROUTE_LAYERS)
LAYER_COST = [1.0, 1.25]
ALL = tuple(range(NL))
DIRPREF = None     # e.g. 1.8: F.Cu prefers horizontal, B.Cu vertical (cost factor for the other directions)

WIDTH = {
    'VBAT_IN': 1.0, '+12V': 0.8, '+12V_F': 0.8, 'BUCK_SW': 0.8, '+5V': 0.5, 'DAMP': 0.4,
    'V5_SENS': 0.4, 'VIGN_IN': 0.4, 'USB_VBUS': 0.4,
    'OUT_INJ1': 0.8, 'OUT_INJ2': 0.8, 'OUT_INJ3': 0.8, 'OUT_INJ4': 0.8,
    'OUT_IACV': 0.8, 'OUT_VVT': 0.8, 'OUT_BOOST': 0.8, 'OUT_ALT': 0.6,
    'OUT_FP': 0.5, 'OUT_MAINRLY': 0.5, 'OUT_AC': 0.5, 'OUT_FAN': 0.5, 'OUT_CEL': 0.4,
    'OUT_TACH': 0.4, 'OUT_LS7': 0.4,
    'OUT_IGN1': 0.4, 'OUT_IGN2': 0.4, 'OUT_IGN3': 0.4, 'OUT_IGN4': 0.4,
    'IGN1_DRV': 0.4, 'IGN2_DRV': 0.4, 'IGN3_DRV': 0.4, 'IGN4_DRV': 0.4,
}
SKIP = {'GND', '+3V3'}           # plane nets: every pad gets a via instead
ST4 = ndimage.generate_binary_structure(2, 1)


def mm(v):
    return ToMM(v)


WCLASSES = (0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0)     # 0.6 doubles as the via class
VIA_EXCL = 0.85            # min via centre spacing (any net) -> hole gap >= 0.55


def wclass(w):
    return next(c for c in WCLASSES if c >= w - 1e-9)


class Grid:
    """core = copper owner; halo[w] = owner of cells closer than CLR + w/2 to copper.
    Exact per width class, so there is no dilation approximation."""

    def __init__(self, W=125.0, H=60.0):
        self.nx, self.ny = int(round(W / G)) + 1, int(round(H / G)) + 1
        sh = (NL, self.ny, self.nx)
        self.pcore = np.zeros(sh, np.int32); self.tcore = np.zeros(sh, np.int32)
        self.phalo = {w: np.zeros(sh, np.int32) for w in WCLASSES}
        self.thalo = {w: np.zeros(sh, np.int32) for w in WCLASSES}
        self.vexcl = np.zeros((self.ny, self.nx), bool)
        self.reserved = np.zeros((self.ny, self.nx), bool)
        self.reserved_ok = set()
        self.X, self.Y = np.meshgrid(np.arange(self.nx) * G, np.arange(self.ny) * G)
        self.netid, self.netname = {}, {}
        self.nextneg = -10
        for w in WCLASSES:
            inner = box(0, 0, W, H).buffer(-EDGE_CLR - w / 2, join_style=2)
            outside = ~shapely.contains_xy(inner, self.X.ravel(), self.Y.ravel())
            for L in ALL:
                self.phalo[w][L].ravel()[outside] = -1

    def nid(self, name):
        if name not in self.netid:
            i = len(self.netid) + 1
            self.netid[name] = i
            self.netname[i] = name
        return self.netid[name]

    def stamp(self, geom, layers, net, static, extra_clear=0.0):
        core_a = self.pcore if static else self.tcore
        halos = self.phalo if static else self.thalo
        x0, y0, x1, y1 = geom.bounds
        r = CLR + extra_clear + max(WCLASSES) / 2 + G
        i0 = max(0, int(math.floor((x0 - r) / G))); i1 = min(self.nx - 1, int(math.ceil((x1 + r) / G)))
        j0 = max(0, int(math.floor((y0 - r) / G))); j1 = min(self.ny - 1, int(math.ceil((y1 + r) / G)))
        X = self.X[j0:j1 + 1, i0:i1 + 1]; Y = self.Y[j0:j1 + 1, i0:i1 + 1]
        d = shapely.distance(geom, shapely.points(X.ravel(), Y.ravel())).reshape(X.shape)
        inside = d <= 1e-6
        for L in layers:
            c = core_a[L, j0:j1 + 1, i0:i1 + 1]
            c[inside & (c == 0)] = net
            c[inside & (c != net) & (c != 0)] = -1
            for w in WCLASSES:
                near = (d < CLR + extra_clear + w / 2 - 1e-4) & ~inside
                h = halos[w][L, j0:j1 + 1, i0:i1 + 1]
                h[near & (h == 0)] = net
                h[near & (h != net) & (h != 0)] = -1

    def ok(self, net, L, width=SIG_W, soft=False):
        w = wclass(width)
        pc, tc = self.pcore[L], self.tcore[L]
        ph, th = self.phalo[w][L], self.thalo[w][L]
        own = (pc == net) | (tc == net)
        pfree = ((pc == 0) | (pc == net)) & ((ph == 0) | (ph == net))
        tfree = ((tc == 0) | (tc == net)) & ((th == 0) | (th == net))
        good = pfree if soft else (pfree & tfree)
        if net not in self.reserved_ok:
            good = good & ~self.reserved
        if w > SIG_W:
            return good, tfree
        return own | good, tfree | own

    def via_ok(self, net, soft=False):
        m = ~self.vexcl
        for L in ALL:
            m = m & self.ok(net, L, 0.6, soft)[0]
        return m

    def mark_via(self, x, y):
        i0 = max(0, int((x - 1) / G)); i1 = min(self.nx, int((x + 1) / G) + 2)
        j0 = max(0, int((y - 1) / G)); j1 = min(self.ny, int((y + 1) / G) + 2)
        d2 = (self.X[j0:j1, i0:i1] - x) ** 2 + (self.Y[j0:j1, i0:i1] - y) ** 2
        self.vexcl[j0:j1, i0:i1] |= d2 < VIA_EXCL ** 2


class Router:
    def __init__(self, path):
        self.board = pcbnew.LoadBoard(path)
        self.grid = Grid()
        self.pads = []
        self.tracks = []          # dict(net, L, p0, p1, w)
        self.vias = []            # dict(net, x, y)
        self.netcells = {}
        self.failed = []
        self.protected = set()
        self.prerouted = set()
        g = self.grid
        for fp in self.board.GetFootprints():
            for p in fp.Pads():
                o = p.GetEffectivePolygon().Outline(0)
                poly = Polygon([(mm(o.CPoint(i).x) - OX, mm(o.CPoint(i).y) - OY) for i in range(o.PointCount())])
                layers = [L for L, lid in enumerate(ROUTE_LAYERS) if p.IsOnLayer(lid)]
                pos = (mm(p.GetPosition().x) - OX, mm(p.GetPosition().y) - OY)
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    g.stamp(Point(pos).buffer(mm(p.GetDrillSize().x) / 2), ALL, -1, True, 0.15)
                    g.mark_via(*pos)
                    continue
                name = p.GetNetname()
                if name:
                    net = g.nid(name)
                else:
                    net = g.nextneg; g.nextneg -= 1
                # tiny safety margin for rounded-pad polygon approximation, except on the
                # 0.5 mm-pitch MCU where the escape lanes are exactly on the limit
                g.stamp(poly if fp.GetReference() == 'U1' else poly.buffer(0.03), layers, net, True)
                self.pads.append(dict(fp=fp.GetReference(), num=p.GetNumber(), net=name, poly=poly,
                                      layers=layers, c=pos))
        self.load_block()
        for p in self.pads:
            p['cells'] = self.pad_cells(p)
        self.add_escape_stubs()
        # keep signals out from under the MCU body (reserved for GND stitching)
        sl = (slice(int(round(25.0 / G)), int(round(39.0 / G)) + 1), slice(int(round(54.0 / G)), int(round(68.0 / G)) + 1))
        g.reserved[sl] = True
        g.reserved_ok = {g.nid('GND'), g.nid('+3V3')}
        # footprint keepout areas (Tag-Connect legs): no copper of any net, no vias
        for fp in self.board.GetFootprints():
            for z in fp.Zones():
                o = z.Outline().Outline(0)
                poly = Polygon([(mm(o.CPoint(i).x) - OX, mm(o.CPoint(i).y) - OY) for i in range(o.PointCount())])
                # Tag-Connect keepout forbids vias (and pours) only: tracks may enter
                x0, y0, x1, y1 = poly.bounds
                g.vexcl[int((y0 - 0.5) / G):int((y1 + 0.5) / G) + 2, int((x0 - 0.5) / G):int((x1 + 0.5) / G) + 2] = True
        self.static_vexcl = g.vexcl.copy()

    def load_block(self):
        """Copper already on the board (the transplanted wideband block: tracks, vias, zones)
        is fixed. Its parts' pads stay as obstacles but leave the to-connect list; the block
        joins the rest of the board only through its port vias (pseudo pads). Nets that the
        block already finishes (internal nets, the sensor-side drops onto J2) are prerouted."""
        try:
            import wideband as WB, wb_clean
        except ImportError:
            return
        block = set(WB.placement())
        if wb_clean.ENABLED:
            if any(fp.GetReference() in block for fp in self.board.GetFootprints()):
                self.load_clean_block(wb_clean)
            return
        if not any(fp.GetReference() in block for fp in self.board.GetFootprints()):
            return                      # not the daughterboard (e.g. the motherboard router)
        g = self.grid
        lay = {_p.F_Cu: 0, _p.B_Cu: 1}
        n_t = n_v = 0
        for t in self.board.GetTracks():
            if t.GetClass() == 'PCB_VIA':
                x, y = mm(t.GetPosition().x) - OX, mm(t.GetPosition().y) - OY
                g.stamp(Point(x, y).buffer(mm(t.GetWidth()) / 2), ALL, g.nid(t.GetNetname()), True)
                g.mark_via(x, y); n_v += 1
            elif t.GetLayer() in lay:
                a = (mm(t.GetStart().x) - OX, mm(t.GetStart().y) - OY); b = (mm(t.GetEnd().x) - OX, mm(t.GetEnd().y) - OY)
                g.stamp(LineString([a, b]).buffer(mm(t.GetWidth()) / 2), (lay[t.GetLayer()],), g.nid(t.GetNetname()), True)
                n_t += 1
        for z in self.board.Zones():
            if z.GetLayer() not in lay:
                continue
            o = z.Outline().Outline(0)
            poly = Polygon([(mm(o.CPoint(i).x) - OX, mm(o.CPoint(i).y) - OY) for i in range(o.PointCount())])
            g.stamp(poly, (lay[z.GetLayer()],), g.nid(z.GetNetname()), True)
        self.pads = [p for p in self.pads if p['fp'] not in block]
        for pt in WB.ports():
            if pt['side'] != 'P' or pt['net'] not in ('+5V', 'WB_CAN_RX', 'WB_CAN_TX', 'VBAT_IN'):
                continue
            x, y = pt['at']
            pad = dict(fp='WBPORT', num=str(pt['num']), net=pt['net'], poly=Point(x, y).buffer(0.3),
                       layers=list(ALL), c=(x, y))
            if pt['net'] == 'VBAT_IN':
                pad['w'] = 0.25           # sense tap: thin, routed last
            self.pads.append(pad)
        self.prerouted |= {'LSU_UN', 'LSU_RT', 'LSU_VM', 'LSU_IP', 'LSU_HTR_N', 'HTR_GND'}
        print(f'block: {n_t} tracks, {n_v} vias fixed; {len(block)} parts', flush=True)

    def load_clean_block(self, wbc):
        """rev 0.3 wideband block (wb_clean.py): placed parts are routed like the rest of the board;
        only the heater path is fixed, hand-planned copper. Thin taps on wide nets are marked."""
        for net, side, w, pts in wbc.HEATER:
            self.add_locked(net, pts, w, L=0 if side == 'F' else 1)
        for p in self.pads:
            if (p['fp'], p['num']) in wbc.TAPS:
                p['w'] = wbc.TAPS[(p['fp'], p['num'])]
        print('wideband block: clean layout, heater copper fixed', flush=True)

    def add_escape_stubs(self, ref='U1', length=1.0):
        """fixed straight stubs out of every used fine-pitch MCU pin, so no other
        track can sneak along the pad row and fence a pin in"""
        skip = {'GND', '+3V3', '+3V3A', 'VCAP1', 'VCAP2', '',
                'AN_TPS', 'AN_MAP', 'AN_CLT', 'AN_IAT', 'AN_AFR', 'AN_AUX1', 'AN_AUX2', 'AN_AUX3'}
        mx, my = 61.0, 32.0
        for p in self.pads:
            if p['fp'] != ref or p['net'] in skip:
                continue
            x, y = p['c']
            x0, y0, x1, y1 = p['poly'].bounds
            dx, dy = x - mx, y - my
            if abs(dx) > abs(dy):
                ex = (x1 if dx > 0 else x0) + (length if dx > 0 else -length)
                end = (round(ex / G) * G, y)
            else:
                ey = (y1 if dy > 0 else y0) + (length if dy > 0 else -length)
                end = (x, round(ey / G) * G)
            start = (round(x / G) * G, round(y / G) * G)
            end = (round(end[0] / G) * G, round(end[1] / G) * G)
            net = self.grid.nid(p['net'])
            self.grid.stamp(LineString([start, end]).buffer(SIG_W / 2), (0,), net, True)
            self.tracks.append(dict(net=p['net'], L=0, p0=start, p1=end, w=SIG_W, fixed=True))
            # reserve the next 1.25 mm straight out as this pin's private lane, so no other
            # track can run along the stub tips and fence the pin row in
            ext = (end[0] + (end[0] - start[0]) / max(1e-9, math.dist(start, end)) * 1.25,
                   end[1] + (end[1] - start[1]) / max(1e-9, math.dist(start, end)) * 1.25)
            ext = (round(ext[0] / G) * G, round(ext[1] / G) * G)
            self.grid.stamp(LineString([end, ext]).buffer(SIG_W / 2), (0,), net, True)

    def add_locked(self, net, pts, w=SIG_W, L=0):
        """hand-planned fixed route (list of points), stamped as static copper"""
        nid = self.grid.nid(net)
        for a, b in zip(pts, pts[1:]):
            self.grid.stamp(LineString([a, b]).buffer(w / 2), (L,), nid, True)
            self.tracks.append(dict(net=net, L=L, p0=a, p1=b, w=w, locked=True))
        self.prerouted.add(net)

    def preroute_analog_fan(self):
        """The 8 sensor inputs leave the MCU bottom edge, drop to their own lane,
        45 degrees down-left, run left in nested lanes 0.5 mm apart and drop straight
        into their conditioning column between the R/C pair."""
        mpin = {p['num']: p for p in self.pads if p['fp'] == 'U1'}
        nets = [('29', 'AN_TPS', 4), ('30', 'AN_MAP', 5), ('31', 'AN_CLT', 6), ('32', 'AN_IAT', 7),
                ('33', 'AN_AFR', 8), ('34', 'AN_AUX1', 9), ('35', 'AN_AUX2', 10), ('36', 'AN_AUX3', 11)]
        for k, (pin, net, jpin) in enumerate(nets):
            assert mpin[pin]['net'] == net, (pin, net)
            xp = mpin[pin]['c'][0]
            xc = round((13.0 + (jpin - 1) * 2.54) * 4) / 4
            lane = 42.5 + 0.5 * k
            y0 = 41.75
            series = [p for p in self.pads if p['net'] == net and p['fp'] != 'U1'
                      and abs(p['c'][0] - xc) < 0.05]
            ytop = min(p['c'][1] for p in series)          # series R top pad (node)
            pair = [p for p in self.pads if p['net'] == net and abs(p['c'][0] - xc) > 0.3
                    and abs(p['c'][0] - xc) < 0.9]
            pts = [(xp, mpin[pin]['c'][1]), (xp, y0), (xp - (lane - y0), lane), (xc, lane), (xc, ytop)]
            self.add_locked(net, pts)
            yp = pair[0]['c'][1]
            self.add_locked(net, [(xc - 0.6, yp), (xc + 0.6, yp)])

    def pad_cells(self, pad):
        cells = []
        x0, y0, x1, y1 = pad['poly'].bounds
        pp = pad['poly'].buffer(1e-6)
        for j in range(int(math.floor(y0 / G)), int(math.ceil(y1 / G)) + 1):
            for i in range(int(math.floor(x0 / G)), int(math.ceil(x1 / G)) + 1):
                if 0 <= i < self.grid.nx and 0 <= j < self.grid.ny and pp.contains(Point(i * G, j * G)):
                    cells += [(L, j, i) for L in pad['layers']]
        if not cells:
            i, j = int(round(pad['c'][0] / G)), int(round(pad['c'][1] / G))
            cells = [(L, j, i) for L in pad['layers']]
        return cells

    # ------------------------------------------------------------------ search
    def astar(self, net, sources, targets, width, soft=False, via_ok=True, mask=None,
              bottom_cost=None, via_cost=10.0, penalty=25.0, limit=1500000):
        g = self.grid
        P, T = [], []
        for L in ALL:
            okm, tf = g.ok(net, L, width, soft)
            if mask is not None:
                okm = okm & mask
            P.append(okm); T.append(tf)
        if via_ok:
            V = g.via_ok(net, soft) & P[0] & P[1]
        nx, ny = g.nx, g.ny
        tset = set(targets)
        tj = np.array([t[1] for t in targets]); ti = np.array([t[2] for t in targets])
        cy, cx = tj.mean(), ti.mean()

        def h(j, i):
            dx, dy = abs(i - cx), abs(j - cy)
            return (max(dx, dy) + 0.414 * min(dx, dy)) * 0.9

        q, best, parent = [], {}, {}
        for (L, j, i) in sources:
            if P[L][j, i]:
                k = (L, j, i, 8)
                best[k] = 0.0
                heapq.heappush(q, (h(j, i), 0.0, k))
        n = 0
        while q:
            f, gc, key = heapq.heappop(q)
            if best.get(key, 1e18) < gc - 1e-9:
                continue
            L, j, i, d = key
            if (L, j, i) in tset:
                path = [(L, j, i)]
                k = key
                while k in parent:
                    k = parent[k]
                    path.append(k[:3])
                path = path[::-1]
                return path if soft else self.smooth(path, P)
            n += 1
            if n > limit:
                return None
            lc = LAYER_COST[L]
            PL, TL = P[L], T[L]
            for nd, (di, dj) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))):
                ii, jj = i + di, j + dj
                if ii < 0 or jj < 0 or ii >= nx or jj >= ny or not PL[jj, ii]:
                    continue
                if di and dj and not (PL[j, ii] and PL[jj, i]):
                    continue
                cost = (1.4142 if (di and dj) else 1.0) * lc
                if DIRPREF and ((L == 0 and dj) or (L == 1 and di)):
                    cost *= DIRPREF
                if d != 8 and d != nd:
                    cost += 0.6
                if soft and not TL[jj, ii]:
                    cost += penalty
                nk = (L, jj, ii, nd); ng = gc + cost
                if ng < best.get(nk, 1e18) - 1e-9:
                    best[nk] = ng; parent[nk] = key
                    heapq.heappush(q, (ng + h(jj, ii), ng, nk))
            if via_ok and V[j, i]:
                for L2 in ALL:
                    if L2 == L or not P[L2][j, i]:
                        continue
                    nk = (L2, j, i, 8); ng = gc + via_cost
                    if soft and not all(T[k][j, i] for k in ALL):
                        ng += penalty
                    if ng < best.get(nk, 1e18) - 1e-9:
                        best[nk] = ng; parent[nk] = key
                        heapq.heappush(q, (ng + h(j, i), ng, nk))
        return None

    @staticmethod
    def octi(a, b, diag_first):
        """cells of an octilinear 2-segment path a->b (same layer)"""
        (j0, i0), (j1, i1) = a, b
        dj, di = j1 - j0, i1 - i0
        n_d = min(abs(dj), abs(di))
        sj, si = (dj > 0) - (dj < 0), (di > 0) - (di < 0)
        steps = []
        straight = (sj, 0) if abs(dj) > abs(di) else (0, si)
        n_s = max(abs(dj), abs(di)) - n_d
        seq = [(sj, si)] * n_d + [straight] * n_s if diag_first else [straight] * n_s + [(sj, si)] * n_d
        j, i = j0, i0
        cells = [(j, i)]
        for (a1, b1) in seq:
            j += a1; i += b1
            cells.append((j, i))
        return cells

    def smooth(self, path, P):
        """string-pulling to octilinear segments: fewer bends, no zig-zags"""
        out = [path[0]]
        k = 0
        n = len(path)
        while k < n - 1:
            L = path[k][0]
            best = k + 1
            # farthest point on the same layer reachable with one bend
            m = k + 1
            while m < n and path[m][0] == L:
                m += 1
            for t in range(m - 1, k + 1, -1):
                ok = False
                for df in (True, False):
                    cells = self.octi(path[k][1:], path[t][1:], df)
                    good = True
                    for (a, b), (c, d) in zip(cells, cells[1:]):
                        if not P[L][c, d]:
                            good = False; break
                        if a != c and b != d and not (P[L][a, d] and P[L][c, b]):
                            good = False; break
                    if good:
                        out.extend((L, c, d) for (c, d) in cells[1:])
                        ok = True
                        break
                if ok:
                    best = t
                    break
            if best == k + 1:
                out.append(path[k + 1])
            k = best
        return out

    # ------------------------------------------------------------------ copper
    @staticmethod
    def runs(path):
        runs, vias = [], []
        start = prev = path[0]; pdir = None
        for c in path[1:]:
            if c[0] != prev[0]:
                if prev != start:
                    runs.append((start, prev))
                vias.append((prev[2] * G, prev[1] * G))
                start, pdir = c, None
            else:
                dirn = (c[1] - prev[1], c[2] - prev[2])
                if pdir is not None and dirn != pdir:
                    runs.append((start, prev)); start = prev
                pdir = dirn
            prev = c
        if prev != start:
            runs.append((start, prev))
        return [(a[0], (a[2] * G, a[1] * G), (b[2] * G, b[1] * G)) for a, b in runs], vias

    def add_path(self, name, path, width):
        net = self.grid.nid(name)
        segs, vias = self.runs(path)
        for L, p0, p1 in segs:
            t = dict(net=name, L=L, p0=p0, p1=p1, w=width)
            self.tracks.append(t)
            self.grid.stamp(LineString([p0, p1]).buffer(width / 2), (L,), net, False)
        for x, y in vias:
            self.vias.append(dict(net=name, x=x, y=y))
            self.grid.stamp(Point(x, y).buffer(VIA_D / 2), ALL, net, False)
            self.grid.mark_via(x, y)
        self.netcells.setdefault(name, set()).update(path)

    def rebuild_dynamic(self):
        g = self.grid
        g.tcore[:] = 0
        for w in WCLASSES:
            g.thalo[w][:] = 0
        g.vexcl[:] = self.static_vexcl
        for t in self.tracks:
            if t.get('fixed') or t.get('locked'):
                continue
            g.stamp(LineString([t['p0'], t['p1']]).buffer(t['w'] / 2), (t['L'],), g.nid(t['net']), False)
        for v in self.vias:
            g.stamp(Point(v['x'], v['y']).buffer(VIA_D / 2), ALL, g.nid(v['net']), False)
            g.mark_via(v['x'], v['y'])

    def rip(self, names):
        names = set(names)
        self.tracks = [t for t in self.tracks if t['net'] not in names or t.get('fixed') or t.get('locked')]
        self.vias = [v for v in self.vias if v['net'] not in names]
        for n in names:
            self.netcells.pop(n, None)
        self.rebuild_dynamic()

    def victims(self, name, path, width):
        segs, vias = self.runs(path) if len(path) > 1 else ([], [])
        geoms = {L: [] for L in ALL}
        for L, p0, p1 in segs:
            geoms[L].append(LineString([p0, p1]).buffer(width / 2 + CLR - 0.01))
        for x, y in vias:
            for L in ALL:
                geoms[L].append(Point(x, y).buffer(VIA_D / 2 + CLR - 0.01))
        out = set()
        for t in self.tracks:
            if t['net'] == name or t['net'] in SKIP or t['net'] in self.protected or t.get('locked'):
                continue
            tg = LineString([t['p0'], t['p1']]).buffer(t['w'] / 2)
            if any(gm.intersects(tg) for gm in geoms[t['L']]):
                out.add(t['net'])
        for v in self.vias:
            if v['net'] == name or v['net'] in SKIP or v['net'] in self.protected:
                continue
            vg = Point(v['x'], v['y']).buffer(VIA_D / 2)
            if any(gm.intersects(vg) for L in ALL for gm in geoms[L]):
                out.add(v['net'])
        return out

    # ------------------------------------------------------------------ nets
    def route_net(self, name, width, ripcount, allow_rip=True):
        """returns set of nets ripped (to be re-queued); records failures"""
        if name in self.prerouted:
            return set()
        mypads = sorted((p for p in self.pads if p['net'] == name), key=lambda p: 'w' in p)   # thin taps last
        ripped = set()
        if len(mypads) < 2:
            return ripped
        connected = [mypads[0]]
        remaining = mypads[1:]
        src = set(mypads[0]['cells'])
        while remaining:
            pool = [p for p in remaining if 'w' not in p] or remaining
            best = min(pool, key=lambda p: min(math.dist(p['c'], q['c']) for q in connected))
            remaining.remove(best)
            tgt = set(best['cells'])
            if src & tgt:
                connected.append(best); src |= tgt; continue
            path, used_w = None, None
            widths = [w for w in (width, 0.5, 0.3, SIG_W) if w <= width]
            if 'w' in best:
                widths = [best['w'], SIG_W]
            for w in dict.fromkeys(widths):
                path = self.astar(self.grid.nid(name), src | self.netcells.get(name, set()), tgt, w)
                if path:
                    used_w = w; break
            if not path and allow_rip:
                for w in dict.fromkeys(widths[-2:]):
                    sp = self.astar(self.grid.nid(name), src | self.netcells.get(name, set()), tgt, w, soft=True)
                    if not sp:
                        continue
                    vic = {v for v in self.victims(name, sp, w) if ripcount.get(v, 0) < 8} - {name}
                    if not vic:
                        continue
                    for v in vic:
                        ripcount[v] = ripcount.get(v, 0) + 1
                    self.rip(vic)
                    ripped |= vic
                    path = self.astar(self.grid.nid(name), src | self.netcells.get(name, set()), tgt, w)
                    if path:
                        used_w = w
                        break
            if not path:
                # keep going: the unreachable pad becomes a new island so the rest of
                # the net can still attach to it (one missing link, not a dead net)
                self.failed.append((name, best['fp'], best['num']))
                connected.append(best); src |= tgt
                continue
            self.add_path(name, path, used_w)
            connected.append(best)
            src |= tgt | set(path)
        return ripped

    def route_all(self, order, max_rips=500):
        self.failed = []
        q = deque(order)
        ripcount = {}
        total = 0
        while q:
            n = q.popleft()
            before = len(self.failed)
            ripped = self.route_net(n, WIDTH.get(n, SIG_W), ripcount, allow_rip=total < max_rips)
            total += len(ripped)
            for r in ripped:
                # drop stale failure records of ripped nets, they get routed again
                self.failed = [f for f in self.failed if f[0] != r]
                if r not in q:
                    q.append(r)
        return self.failed

    def gnd_stitch(self, name='GND', radius=4.0, only=None):
        g = self.grid
        net = g.nid(name)
        V = g.via_ok(net)
        self.stitched = getattr(self, 'stitched', set())
        pads = [p for p in self.pads if p['net'] == name and len(p['layers']) == 1     # SMD, either side
                and (p['fp'], p['num'], p['c']) not in self.stitched
                and (only is None or only(p))]
        # fine-pitch pins first: they have the fewest options
        pads.sort(key=lambda p: p['poly'].area)
        for p in pads:
            cx, cy = p['c']
            PL = p['layers'][0]                 # stitch on the pad's own layer
            tg = set()
            for j in range(int((cy - radius) / G), int((cy + radius) / G) + 1):
                for i in range(int((cx - radius) / G), int((cx + radius) / G) + 1):
                    if 0 <= i < g.nx and 0 <= j < g.ny and V[j, i]:
                        # MCU supply pins always drop inward, never into the fan-out
                        if p['fp'] == 'U1':
                            if not g.reserved[j, i]:
                                continue
                            if name != '+3V3':
                                tg.add((PL, j, i)); continue
                            # straight in along the pin axis, so neighbours keep their lane
                            bx0, by0, bx1, by1 = p['poly'].bounds
                            # ...and deep enough that the neighbouring VSS pin can turn past it
                            if (by1 - by0) > (bx1 - bx0):
                                if abs(i * G - cx) > 0.13 or abs(j * G - cy) < 2.4:
                                    continue
                            elif abs(j * G - cy) > 0.13 or abs(i * G - cx) < 2.4:
                                continue
                        tg.add((PL, j, i))
            # ...or join copper that is already tied to the plane: a via of this net
            # or a through-hole pad of this net
            joinable = set()
            for v in self.vias:
                if v['net'] == name and abs(v['x'] - cx) < radius and abs(v['y'] - cy) < radius:
                    joinable.add((PL, int(round(v['y'] / G)), int(round(v['x'] / G))))
            for q in self.pads:
                if q['net'] == name and len(q['layers']) > 1 and math.dist(q['c'], p['c']) < radius:
                    joinable.update(c for c in q['cells'] if c[0] == PL)
            tg |= joinable
            path = None
            if tg:
                for w in (0.3, SIG_W):
                    m = None
                    if p['fp'] == 'U1':        # MCU supply pins: stay inside the pad ring
                        m = g.reserved.copy()
                        bx0, by0, bx1, by1 = p['poly'].bounds
                        m[int(by0 / G) - 2:int(by1 / G) + 3, int(bx0 / G) - 2:int(bx1 / G) + 3] = True
                    path = self.astar(net, set(p['cells']), tg, w, via_ok=False,
                                      limit=20000 if radius < 5 else 200000, mask=m)
                    if path:
                        break
            if not path:
                self.failed.append((name + '-stitch', p['fp'], p['num'])); continue
            if len(path) > 1:
                self.add_path(name, path, w)
            L, j, i = path[-1]
            self.stitched.add((p['fp'], p['num'], p['c']))
            if (PL, j, i) in joinable:
                continue          # ended on a plane via / THT pad: no new via needed
            self.vias.append(dict(net=name, x=i * G, y=j * G))
            g.stamp(Point(i * G, j * G).buffer(VIA_D / 2), ALL, net, False)
            g.mark_via(i * G, j * G)
            V = g.via_ok(net)

    def thermal_and_stitch(self, pitch=3.0):
        g = self.grid
        net = g.nid('GND')
        n_ep = n_st = 0
        for p in self.pads:
            if p['net'] != 'GND' or p['poly'].area < 4.0:
                continue
            cx, cy = p['poly'].centroid.x, p['poly'].centroid.y
            x0, y0, x1, y1 = p['poly'].bounds
            horiz = (x1 - x0) > (y1 - y0)
            for o in (-0.9, 0.0, 0.9):
                x, y = (cx + o, cy) if horiz else (cx, cy + o)
                i, j = int(round(x / G)), int(round(y / G))
                if g.via_ok(net)[j, i]:
                    self.vias.append(dict(net='GND', x=i * G, y=j * G))
                    g.stamp(Point(i * G, j * G).buffer(VIA_D / 2), ALL, net, False)
                    g.mark_via(i * G, j * G); n_ep += 1
        V = g.via_ok(net)
        step = int(round(pitch / G))
        for j in range(step // 2, g.ny, step):
            for i in range(step // 2, g.nx, step):
                if V[j, i]:
                    self.vias.append(dict(net='GND', x=i * G, y=j * G))
                    g.mark_via(i * G, j * G); n_st += 1
        print(f'thermal vias {n_ep}, stitching vias {n_st}')

    def trim_stubs(self):
        out = []
        for t in self.tracks:
            if not t.get('fixed'):
                out.append(t); continue
            a = np.array(t['p0']); b = np.array(t['p1'])
            L = np.linalg.norm(b - a)
            best = -1.0
            pts = [o['p0'] for o in self.tracks if o['net'] == t['net'] and not o.get('fixed')] + \
                  [o['p1'] for o in self.tracks if o['net'] == t['net'] and not o.get('fixed')] + \
                  [(v['x'], v['y']) for v in self.vias if v['net'] == t['net']]
            for p in pts:
                p = np.array(p)
                u = np.dot(p - a, b - a) / (L * L)
                if -1e-6 <= u <= 1 + 1e-6 and np.linalg.norm(a + u * (b - a) - p) < 0.01:
                    best = max(best, u)
            if best > 1e-6:
                t = dict(t, p1=tuple(float(v) for v in (a + best * (b - a))))
                out.append(t)
        self.tracks = out

    def commit(self):
        seen, uniq = set(), []
        for t in self.tracks:
            k = (t['net'], t['L'], tuple(round(v, 4) for v in t['p0']), tuple(round(v, 4) for v in t['p1']), t['w'])
            if k not in seen:
                seen.add(k); uniq.append(t)
        self.tracks = uniq
        self.trim_stubs()
        b = self.board
        nets = b.GetNetsByName()
        for t in self.tracks:
            tr = pcbnew.PCB_TRACK(b)
            tr.SetStart(VECTOR2I(FromMM(t['p0'][0] + OX), FromMM(t['p0'][1] + OY)))
            tr.SetEnd(VECTOR2I(FromMM(t['p1'][0] + OX), FromMM(t['p1'][1] + OY)))
            tr.SetWidth(FromMM(t['w']))
            tr.SetLayer(ROUTE_LAYERS[t['L']])
            tr.SetNet(nets[t['net']])
            b.Add(tr)
        seen = set()
        for v in self.vias:
            k = (round(v['x'], 3), round(v['y'], 3))
            if k in seen:
                continue
            seen.add(k)
            vi = pcbnew.PCB_VIA(b)
            vi.SetPosition(VECTOR2I(FromMM(v['x'] + OX), FromMM(v['y'] + OY)))
            vi.SetWidth(FromMM(VIA_D)); vi.SetDrill(FromMM(VIA_DRILL))
            vi.SetNet(nets[v['net']])
            b.Add(vi)


def add_gnd_zones(board, W=125.0, H=60.0):
    nets = board.GetNetsByName()
    for layer, nn in ((pcbnew.F_Cu, 'GND'), (pcbnew.In1_Cu, 'GND'), (pcbnew.In2_Cu, '+3V3'), (pcbnew.B_Cu, 'GND')):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(nets[nn])
        ol = z.Outline()
        ol.NewOutline()
        for x, y in [(0, 0), (W, 0), (W, H), (0, H)]:
            ol.Append(FromMM(x + OX), FromMM(y + OY))
        z.SetLocalClearance(FromMM(0.25))
        z.SetMinThickness(FromMM(0.2))
        z.SetThermalReliefGap(FromMM(0.25))
        z.SetThermalReliefSpokeWidth(FromMM(0.35))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def main(inp, out):
    t0 = time.time()
    r = Router(inp)
    pads = r.pads
    netnames = sorted({p['net'] for p in pads if p['net'] and p['net'] not in SKIP})

    def netlen(n):
        ps = [p['c'] for p in pads if p['net'] == n]
        xs = [c[0] for c in ps]; ys = [c[1] for c in ps]
        return (max(xs) - min(xs)) + (max(ys) - min(ys))
    wide = [n for n in netnames if WIDTH.get(n, SIG_W) > SIG_W]
    narrow = [n for n in netnames if n not in wide]
    mcu = {p['net'] for p in pads if p['fp'] == 'U1'}
    first = sorted([n for n in narrow if n in mcu and n not in ('+3V3', '+3V3A')], key=netlen)
    rest = sorted([n for n in narrow if n not in first], key=netlen)
    # escape-critical fans under the MCU, routed so each new line lies outside the last
    # MCU pin order (counter-clockwise): each line turns off next to the package and
    # the next pin's line passes underneath it, so the fan nests without crossings
    fan = ['AN_VBATT', 'AN_VIGN', 'AN_KNOCK', 'AN_TPS', 'AN_MAP', 'AN_CLT', 'AN_IAT', 'AN_AFR',
           'AN_AUX1', 'AN_AUX2', 'AN_AUX3', 'HALL1', 'HALL2', 'SW1', 'SW2', 'SW3']
    # top-edge outputs: rightmost pin first, each next line runs above the previous one
    tops = ['ALT_CTL', 'BOOST_CTL', 'VVT_CTL', 'IACV_CTL', 'INJ4_CTL', 'INJ3_CTL', 'INJ2_CTL', 'INJ1_CTL',
            'IGN4_CTL', 'IGN3_CTL', 'IGN2_CTL', 'IGN1_CTL']
    fan = fan + tops
    first = fan + [n for n in first if n not in fan]
    r.protected = set()
    r.preroute_analog_fan()
    order = first + ['+5V'] + rest + [n for n in sorted(wide, key=netlen) if n != '+5V']
    import os, pickle
    state = out + '.state.pkl'
    if os.environ.get('RESUME') and os.path.exists(state):
        r.tracks, r.vias, r.failed = pickle.load(open(state, 'rb'))
        r.rebuild_dynamic()
        if os.environ.get('FINISH'):
            import random, copy
            random.seed(int(os.environ.get('FSEED', '1')))
            repaired = None
            # plane stitches hemmed in by signal tracks: rip the signals right around the pad, place the
            # stitch first, then route those signals again (kept only if nothing new fails)
            sb = [f for f in r.failed if 'stitch' in f[0]]
            if sb:
                pos = [p['c'] for f in sb for p in r.pads if p['fp'] == f[1] and p['num'] == f[2]]
                neigh = sorted({t['net'] for t in r.tracks if not (t.get('fixed') or t.get('locked'))
                                and t['net'] not in SKIP
                                and any(LineString([t['p0'], t['p1']]).distance(Point(c)) < 1.6 for c in pos)})
                keep = (list(r.tracks), list(r.vias), list(r.failed), set(getattr(r, 'stitched', set())))
                print('stitch repair: ripping', neigh, flush=True)
                r.rip(neigh)
                r.failed = [f for f in r.failed if 'stitch' not in f[0]]
                for nm, fp, num in sb:
                    r.gnd_stitch(nm.replace('-stitch', ''), 4.0, lambda p, fp=fp, num=num: p['fp'] == fp and p['num'] == num)
                r.route_all(neigh, max_rips=100)
                bad_sig = [f for f in r.failed if 'stitch' not in f[0]]
                n_st = len([f for f in r.failed if 'stitch' in f[0]])
                print('  -> signals failed', len(bad_sig), 'stitches failed', n_st, 'of', len(sb), flush=True)
                if n_st >= len(sb):
                    r.tracks, r.vias, r.failed, r.stitched = keep
                    r.rebuild_dynamic()
                else:
                    repaired = keep            # signals it displaced are fixed by the loop below
            best_state = (list(r.tracks), list(r.vias), list(r.failed))
            best_n = len([f for f in r.failed if 'stitch' not in f[0]])
            for it in range(10):
                bad = list(dict.fromkeys(f[0] for f in r.failed if 'stitch' not in f[0]))
                stitch_bad = [f for f in r.failed if 'stitch' in f[0]]
                if not bad:
                    break
                # rip the failing nets plus their neighbours around the failing pads
                padpos = [p['c'] for p in r.pads if p['net'] in bad]
                radius = 2.0 + 0.5 * it
                neigh = set()
                for t in r.tracks:
                    if t.get('fixed') or t.get('locked') or t['net'] in SKIP:
                        continue
                    seg = LineString([t['p0'], t['p1']])
                    if any(seg.distance(Point(c)) < radius for c in padpos):
                        neigh.add(t['net'])
                group = list(dict.fromkeys(bad + sorted(neigh - set(bad))))
                rest_order = group[len(bad):]
                random.shuffle(rest_order)
                print('finish pass', it, 'bad', bad, 'ripping', len(group), flush=True)
                r.rip(group)
                r.failed = []
                r.route_all(bad + rest_order, max_rips=300)
                n = len([f for f in r.failed if 'stitch' not in f[0]])
                r.failed += stitch_bad
                if n < best_n:
                    best_n = n
                    best_state = (list(r.tracks), list(r.vias), list(r.failed))
                print('  ->', n, 'failed', flush=True)
            r.tracks, r.vias, r.failed = best_state
            r.rebuild_dynamic()
            if repaired and len([f for f in r.failed if 'stitch' not in f[0]]) > len([f for f in repaired[2] if 'stitch' not in f[0]]):
                print('stitch repair cost a signal: reverted', flush=True)
                r.tracks, r.vias, r.failed, r.stitched = repaired
                r.rebuild_dynamic()
            # retry plane stitches that failed, with a wider search
            sb = [f for f in r.failed if 'stitch' in f[0]]
            r.failed = [f for f in r.failed if 'stitch' not in f[0]]
            r.stitched = set()
            for nm, fp, num in sb:
                r.gnd_stitch(nm.replace('-stitch', ''), 6.0, lambda p, fp=fp, num=num: p['fp'] == fp and p['num'] == num)
            pickle.dump((r.tracks, r.vias, r.failed), open(state, 'wb'))
        fails = [f for f in r.failed if 'stitch' not in f[0]]
    else:
        # fine-pitch IC pins and the boxed-in sense divider get their plane vias first
        ic = lambda p: p['fp'].startswith('U') or p['fp'] in ('R12', 'R14', 'C28', 'C29')
        r.gnd_stitch('+3V3', 3.0, ic)
        r.gnd_stitch('GND', 3.0, ic)
        stitch_fail = list(r.failed)
        fails = r.route_all(order)
        r.failed = stitch_fail + r.failed
        r.gnd_stitch('+3V3', 4.0)                       # passives after the signals
        r.gnd_stitch('GND', 4.0)
        pickle.dump((r.tracks, r.vias, r.failed), open(state, 'wb'))
    print(f'signals/power routed in {time.time()-t0:.0f}s, failed {len(fails)}: {fails}', flush=True)
    r.thermal_and_stitch()
    r.commit()
    r.board.Save(out.replace('.kicad_pcb', '_nz.kicad_pcb'))
    add_gnd_zones(r.board)
    r.board.Save(out)
    print(f'done in {time.time()-t0:.0f}s, tracks {len(r.tracks)}, vias {len(r.vias)}')
    print('FAILED:', len(r.failed))
    for f in r.failed:
        print('  ', f)
    json.dump(r.failed, open(out + '.failed.json', 'w'))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
