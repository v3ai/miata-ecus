"""Route a 2-layer motherboard with the daughterboard router (route.py), adapted:
board size and notched outline from the year module, no MCU fan-out rules,
GND poured on both layers with a via next to every SMD GND pad.
usage: mb_route.py <year module> in.kicad_pcb out.kicad_pcb"""
import sys, os, importlib, time, json
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import shapely
from shapely.geometry import Polygon
import pcbnew
from pcbnew import FromMM
import route as R
import mb_build

M = importlib.import_module(sys.argv[1])
R.EDGE_CLR = 0.5
R.WCLASSES = (0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2)
R.CLR = 0.2
R.HALO = R.CLR + R.SIG_W / 2
R.SKIP = {'GND'}
R.DIRPREF = 1.8
R.LAYER_COST = [1.0, 1.0]
# long runs across the board (LSU connector <-> daughterboard J2 33-40, MAP) need a bigger search
_d = list(R.Router.astar.__defaults__); _d[-1] = 8000000; R.Router.astar.__defaults__ = tuple(_d)
R.WIDTH = {
    'IAC_12V': 0.8, 'OCV_12V': 0.8,
    'VBAT_IN': 1.2, 'HTR_PWR': 1.0, 'LSU_HTR_N': 1.0, 'VIGN_IN': 0.4, 'V5_SENS': 0.4, '+5V': 0.5,
    'USB_VBUS': 0.4,
    'OUT_INJ1': 0.8, 'OUT_INJ2': 0.8, 'OUT_INJ3': 0.8, 'OUT_INJ4': 0.8, 'OUT_IACV': 0.8, 'OUT_VVT': 0.8,
    'OUT_BOOST': 0.8, 'OUT_ALT': 0.6, 'OUT_FP': 0.5, 'OUT_MAINRLY': 0.5, 'OUT_AC': 0.5, 'OUT_FAN': 0.5,
    'OUT_CEL': 0.4, 'OUT_TACH': 0.4, 'OUT_LS7': 0.4,
    'OUT_IGN1': 0.4, 'OUT_IGN2': 0.4, 'OUT_IGN3': 0.4, 'OUT_IGN4': 0.4,
}
POLY = Polygon(mb_build.outline_polygon(M.OUTLINE))


class MBGrid(R.Grid):
    def __init__(self, W=M.W, H=M.H):
        super().__init__(W, H)
        for w in R.WCLASSES:
            inner = POLY.buffer(-R.EDGE_CLR - w / 2, join_style=2)
            outside = ~shapely.contains_xy(inner, self.X.ravel(), self.Y.ravel())
            for L in R.ALL:
                self.phalo[w][L].ravel()[outside] = -1


R.Grid = MBGrid
R.Router.add_escape_stubs = lambda self, *a, **k: None


def add_zones(board):
    nets = board.GetNetsByName()
    pts = mb_build.outline_polygon(M.OUTLINE, 16)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer); z.SetNet(nets['GND'])
        ol = z.Outline(); ol.NewOutline()
        for x, y in pts:
            ol.Append(FromMM(x + R.OX), FromMM(y + R.OY))
        z.SetLocalClearance(FromMM(0.3)); z.SetMinThickness(FromMM(0.25))
        z.SetThermalReliefGap(FromMM(0.3)); z.SetThermalReliefSpokeWidth(FromMM(0.5))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


# ---------------------------------------------------------------- harness bus
def plan_bus(r, hdr='J1', s1='JD1', s2='JD2', pass_nets=('HARN_IAT',)):
    """Neat, deterministic harness -> daughter-socket wiring: every signal drops from its
    header pin on B.Cu, runs along its own horizontal lane on F.Cu, and drops on B.Cu into
    its socket pin (JD1) or through a JD1 gap straight down to its JD2 pin."""
    import math
    from shapely.geometry import LineString, Point
    g = r.grid
    r.lockcells = {}
    P = {(p['fp'], p['num']): p for p in r.pads}
    hp = [p for p in r.pads if p['fp'] == hdr and p['net'] and p['net'] not in R.SKIP]
    cols = sorted({round(p['c'][0], 3) for p in r.pads if p['fp'] == hdr and p['num']})
    rows = sorted({round(p['c'][1], 3) for p in r.pads if p['fp'] == hdr and p['num']})
    yb = rows[-1]                                   # lower header row
    j1 = [p for p in r.pads if p['fp'] == s1]; j2 = [p for p in r.pads if p['fp'] == s2]
    y1 = j1[0]['c'][1]; y2 = j2[0]['c'][1]
    BW = lambda n: min(R.WIDTH.get(n, R.SIG_W), 0.6)
    nets = []
    for p in hp:
        n = p['net']
        x, y = p['c']
        if abs(y - yb) < 0.01:
            esc = [(x, y)]; xe = x
        else:
            k = cols.index(round(x, 3))
            xe = (x + cols[k + 1]) / 2 if k + 1 < len(cols) else x + 1.5
            esc = [(x, y), (xe, y + abs(xe - x))]
        t1 = [q for q in j1 if q['net'] == n]
        t2 = [q for q in j2 if q['net'] == n]
        tg = []
        w = BW(n)
        if t1:
            tg = [('d', q['c'][0], q) for q in t1]
        elif t2:
            q = t2[0]; tg = [('g', q['c'][0] + 1.27, q)]; w = min(w, 0.3)
        elif n in pass_nets:
            tg = [('p', None, None)]; w = min(w, 0.3)
        else:
            continue
        nets.append(dict(net=n, pad=p, esc=esc, xe=xe, tg=tg, w=w))
    # a signal on two header pins (e.g. the 5 V reference on 1N and 2K): one lane, from the pin
    # nearest its target; the router joins the other pin to it afterwards
    best = {}
    for d in nets:
        dist = abs(d['xe'] - (d['tg'][0][1] if d['tg'][0][1] is not None else d['xe']))
        if d['net'] not in best or dist < best[d['net']][0]:
            best[d['net']] = (dist, d)
    nets = [v[1] for v in best.values()]
    # pass-through nets: pick a gap column no JD2 net uses
    used = {round(t[1], 2) for d in nets for t in d['tg'] if t[0] == 'g'}
    pitch = 2.54
    xs2 = sorted(q['c'][0] for q in j2)
    for d in nets:
        if d['tg'][0][0] == 'p':
            cands = [x + pitch / 2 for x in xs2[:-1] if round(x + pitch / 2, 2) not in used
                     and abs(x + pitch / 2 - d['xe']) > 1.0]
            xg = min(cands, key=lambda x: abs(x - d['xe']))
            used.add(round(xg, 2)); d['tg'] = [('p', xg, None)]
    # vertical constraints: escape column of A vs target column of B
    def sep(a, b):
        return 0.3 + 0.2 + max(a['w'], b['w']) / 2 + 0.05
    above = {d['net']: set() for d in nets}       # above[A] = nets whose lane must be below A's
    for a in nets:
        for b in nets:
            if a is b:
                continue
            if any(abs(a['xe'] - t[1]) < sep(a, b) for t in b['tg']):
                above[a['net']].add(b['net'])
    # Kahn: put the nets with the leftmost-going lanes first among the free ones
    indeg = {d['net']: 0 for d in nets}
    for a, bs in above.items():
        for b in bs:
            indeg[b] += 1
    byname = {d['net']: d for d in nets}
    order, free = [], [n for n, v in indeg.items() if v == 0]
    while free:
        free.sort(key=lambda n: -abs(byname[n]['xe'] - byname[n]['tg'][0][1]))
        n = free.pop(0); order.append(n)
        for b in above[n]:
            indeg[b] -= 1
            if indeg[b] == 0:
                free.append(b)
    if len(order) != len(nets):
        raise SystemExit(f'bus: constraint cycle among {set(indeg) - set(order)}')
    # first lane clears the lower header row (pad radius from the footprint: 1.51 or 1.8 mm pads)
    rad = max(p['poly'].bounds[3] - p['c'][1] for p in r.pads if p['fp'] == hdr and p['num']
              and abs(p['c'][1] - yb) < 0.01)
    y = yb + max(rad, 0.755) + 0.2 + 0.03 + byname[order[0]]['w'] / 2
    prev = None
    for n in order:
        d = byname[n]
        if prev is not None:
            sp = max((d['w'] + prev['w']) / 2 + 0.25, 0.3 + 0.25 + max(d['w'], prev['w']) / 2)
            ca = [d['xe']] + [t[1] for t in d['tg']]; cb = [prev['xe']] + [t[1] for t in prev['tg']]
            if any(abs(a - b) < 0.9 for a in ca for b in cb):
                sp = max(sp, R.VIA_D + 0.25)
            y += sp
        d['y'] = round(y, 3); prev = d
    ymax = y1 - 0.85 - 0.2 - 0.3 - 0.05
    print(f'bus: {len(order)} lanes, last lane y={y:.2f} (limit {ymax:.2f})')
    if y > ymax:
        raise SystemExit('bus does not fit')
    # emit copper
    def seg(n, L, a, b, w):
        nid = g.nid(n)
        g.stamp(LineString([a, b]).buffer(w / 2), (L,), nid, True)
        r.tracks.append(dict(net=n, L=L, p0=a, p1=b, w=w, locked=True))
        cells = r.netcells.setdefault(n, set())
        lk = r.lockcells.setdefault(n, set())
        Ls = math.dist(a, b); k = max(1, int(Ls / R.G))
        for s in range(k + 1):
            x = a[0] + (b[0] - a[0]) * s / k; yy = a[1] + (b[1] - a[1]) * s / k
            cells.add((L, int(round(yy / R.G)), int(round(x / R.G))))
            lk.add((L, int(round(yy / R.G)), int(round(x / R.G))))
    def via(n, x, yy):
        nid = g.nid(n)
        g.stamp(Point(x, yy).buffer(R.VIA_D / 2), R.ALL, nid, True)
        g.mark_via(x, yy)
        r.vias.append(dict(net=n, x=x, y=yy, locked=True))
        for L in R.ALL:
            c = (L, int(round(yy / R.G)), int(round(x / R.G)))
            r.netcells.setdefault(n, set()).add(c); r.lockcells.setdefault(n, set()).add(c)
    for d in nets:
        n, w, yl = d['net'], d['w'], d['y']
        pts = d['esc'] + [(d['xe'], yl)]
        for a, b in zip(pts, pts[1:]):
            seg(n, 1, a, b, w)
        via(n, d['xe'], yl)
        xt = [t[1] for t in d['tg']]
        lo, hi = min(xt + [d['xe']]), max(xt + [d['xe']])
        seg(n, 0, (lo, yl), (hi, yl), w)
        for kind, x, q in d['tg']:
            via(n, x, yl)
            if kind == 'd':
                seg(n, 1, (x, yl), q['c'], w)
            elif kind == 'g':
                px, py = q['c']
                seg(n, 1, (x, yl), (x, py - 1.27), w)
                seg(n, 1, (x, py - 1.27), (px, py), w)
            else:
                seg(n, 1, (x, yl), (x, y2 + 4.0), w)
        r.netcells[n].update(d['pad']['cells']); r.lockcells[n].update(d['pad']['cells'])
        for kind, x, q in d['tg']:
            if q:
                r.netcells[n].update(q['cells']); r.lockcells[n].update(q['cells'])
        allpads = {(p['fp'], p['num']) for p in r.pads if p['net'] == n}
        covered = {(d['pad']['fp'], d['pad']['num'])} | {(q['fp'], q['num']) for _, _, q in d['tg'] if q}
        if allpads <= covered:
            r.prerouted.add(n)
    r.static_vexcl = g.vexcl.copy()
    # route_net grows each net from its first pad; for bus nets that must be a bus pad, or
    # the bus cells would count as 'connected' to a tree they are not part of
    busp = {(d['pad']['fp'], d['pad']['num']) for d in nets}
    r.pads.sort(key=lambda p: 0 if (p['fp'], p['num']) in busp else 1)
    return nets


_rip = R.Router.rip
def rip_keep_locked(self, names):
    names = set(names)
    keep = [v for v in self.vias if v.get('locked') and v['net'] in names]
    _rip(self, names)
    self.vias += keep
    for n in names:
        lc = getattr(self, 'lockcells', {}).get(n)
        if lc:
            self.netcells[n] = set(lc)
    self.rebuild_dynamic()
R.Router.rip = rip_keep_locked


def main(inp, out):
    t0 = time.time()
    r = R.Router(inp)
    g = r.grid
    g.reserved[:] = False
    if getattr(M, 'BUS', True):
        plan_bus(r, pass_nets=getattr(M, 'PASS_NETS', ('HARN_IAT',)))
    else:
        r.lockcells = {}
    pads = r.pads
    names = sorted({p['net'] for p in pads if p['net'] and p['net'] not in R.SKIP})

    def netlen(n):
        ps = [p['c'] for p in pads if p['net'] == n]
        xs = [c[0] for c in ps]; ys = [c[1] for c in ps]
        return (max(xs) - min(xs)) + (max(ys) - min(ys))
    wide = sorted([n for n in names if R.WIDTH.get(n, R.SIG_W) > 0.45], key=lambda n: -R.WIDTH[n])
    rest = sorted([n for n in names if n not in wide], key=netlen)
    import pickle
    state = out + '.state.pkl'
    if os.environ.get('RESUME') and os.path.exists(state):
        r.tracks, r.vias, r.failed, r.netcells = pickle.load(open(state, 'rb'))
        r.rebuild_dynamic()
    else:
        r.gnd_stitch('GND', 3.0)
        stitch_fail = list(r.failed)
        fails = r.route_all(wide + rest)
        r.failed = stitch_fail + r.failed
        r.gnd_stitch('GND', 5.0)
    # retry what failed, ripping the failing nets plus their neighbours around the failing pads
    from shapely.geometry import LineString, Point
    for it in range(6):
        bad = list(dict.fromkeys(f[0] for f in r.failed if 'stitch' not in f[0]))
        if not bad:
            break
        padpos = [p['c'] for p in r.pads if p['net'] in bad]
        neigh = set()
        for t in r.tracks:
            if t.get('fixed') or t.get('locked') or t['net'] in R.SKIP:
                continue
            seg = LineString([t['p0'], t['p1']])
            if any(seg.distance(Point(c)) < 3.0 + 2.0 * it for c in padpos):
                neigh.add(t['net'])
        group = bad + sorted(neigh - set(bad))
        print('retry', it, bad, 'ripping', len(group), flush=True)
        r.rip(group)
        r.failed = [f for f in r.failed if 'stitch' in f[0]]
        r.route_all(group, max_rips=300)
    # last resort: drop the layer-direction preference and search harder
    if any('stitch' not in f[0] for f in r.failed):
        R.DIRPREF = None
        for it in range(4):
            bad = list(dict.fromkeys(f[0] for f in r.failed if 'stitch' not in f[0]))
            if not bad:
                break
            padpos = [p['c'] for p in r.pads if p['net'] in bad]
            neigh = {t['net'] for t in r.tracks if not t.get('locked') and t['net'] not in R.SKIP
                     and any(LineString([t['p0'], t['p1']]).distance(Point(c)) < 4.0 + 3.0 * it for c in padpos)}
            group = bad + sorted(neigh - set(bad))
            print('fallback', it, bad, 'ripping', len(group), flush=True)
            r.rip(group)
            r.failed = [f for f in r.failed if 'stitch' in f[0]]
            r.route_all(group, max_rips=300)
    pickle.dump((r.tracks, r.vias, r.failed, r.netcells), open(state, 'wb'))
    print(f'routed in {time.time() - t0:.0f}s, failed: {r.failed}', flush=True)
    r.thermal_and_stitch(pitch=4.0)       # tie the two GND pours together everywhere
    r.commit()
    add_zones(r.board)
    r.board.Save(out)
    json.dump(r.failed, open(out + '.failed.json', 'w'))
    print('tracks', len(r.tracks), 'vias', len(r.vias))


if __name__ == '__main__':
    main(sys.argv[2], sys.argv[3])
