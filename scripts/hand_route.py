"""Route one missing connection on a finished board with a two-layer grid A* over the real copper.
usage: hand_route.py in.kicad_pcb out.kicad_pcb NET  x0 y0 x1 y1 (search window, mm)  srcpad(ref:num) dst pads(ref:num,...)
A destination of COPPER means any existing track or via of NET inside the window (join the net's routed copper).
Tracks 0.2 mm (TW in the environment for another width), vias 0.6/0.3, clearance 0.15 mm (+0.02 margin; CL in the
environment). GND/+3V3 zones are ignored as obstacles and refilled. Two-layer boards only: it does not look at inner layers."""
import sys, heapq, math
import pcbnew
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely import prepared

src, out, NET = sys.argv[1], sys.argv[2], sys.argv[3]
X0, Y0, X1, Y1 = map(float, sys.argv[4:8])
SRC = sys.argv[8].split(':')
DSTS = [d.split(':') for d in sys.argv[9].split(',')]
mm, IU = pcbnew.ToMM, pcbnew.FromMM
TW, VD = float(__import__('os').environ.get('TW', '0.2')), 0.6      # TW: track width (0.2; wider for a ground tie)
CL = float(__import__('os').environ.get('CL', '0.17'))   # clearance + margin: 0.17 for the daughterboard's 0.15 rule, 0.22 for the motherboards' 0.2
b = pcbnew.LoadBoard(src)
win = box(X0 - 2, Y0 - 2, X1 + 2, Y1 + 2)
obs = {'F.Cu': [], 'B.Cu': []}
holes = []
COPPER = ['COPPER'] in DSTS
copper = []                         # (layers, polygon) of NET's own tracks and vias, as goals when COPPER is asked
for t in b.GetTracks():
    if t.GetNetname() == NET:
        if COPPER:
            if t.Type() == pcbnew.PCB_VIA_T:
                p = t.GetPosition(); g = Point(mm(p.x), mm(p.y)).buffer(mm(t.GetWidth()) / 2)
                copper.append((['F.Cu', 'B.Cu'], g))
            elif t.GetLayerName() in ('F.Cu', 'B.Cu'):
                s, e = t.GetStart(), t.GetEnd()
                copper.append(([t.GetLayerName()], LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, cap_style=1)))
        continue
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition(); g = Point(mm(p.x), mm(p.y)).buffer(mm(t.GetWidth()) / 2)
        if g.intersects(win):
            obs['F.Cu'].append(g); obs['B.Cu'].append(g); holes.append(Point(mm(p.x), mm(p.y)).buffer(mm(t.GetDrillValue()) / 2))
        continue
    s, e = t.GetStart(), t.GetEnd()
    g = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, cap_style=1)
    if g.intersects(win) and t.GetLayerName() in obs:
        obs[t.GetLayerName()].append(g)
# GOALS in the environment: a file of "layer|WKT polygon" lines (copper of NET already tied to the rest of the net, for
# example the main ground pour); the route may end anywhere inside one, a track's half width plus 0.15 mm from its edge
_gp = __import__('os').environ.get('GOALS')
if _gp:
    from shapely import wkt as _wkt
    for _line in open(_gp):
        _l, _w = _line.rstrip('\n').split('|', 1)
        _g = _wkt.loads(_w).buffer(-(TW / 2 + 0.15)).intersection(box(X0, Y0, X1, Y1))
        if not _g.is_empty:
            copper.append(([_l], _g))
targets = []
for fp in b.GetFootprints():
    for pd in fp.Pads():
        sh = pd.GetEffectivePolygon()
        poly = None
        try:
            ol = sh.Outline(0); poly = Polygon([(mm(ol.CPoint(i).x), mm(ol.CPoint(i).y)) for i in range(ol.PointCount())])
        except Exception:
            bb = pd.GetBoundingBox(); poly = box(mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
        if not poly.intersects(win):
            continue
        layers = [l for l in ('F.Cu', 'B.Cu') if pd.IsOnLayer(b.GetLayerID(l))]
        key = [fp.GetReference(), pd.GetNumber()]
        if pd.GetNetname() == NET:
            if key in DSTS or key == SRC:
                targets.append((key, layers, poly))
            continue
        npth = pd.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
        for l in layers:
            obs[l].append(poly.buffer(0.05) if npth else poly)   # NPTH: 0.2 mm hole clearance, not 0.15
        if pd.GetDrillSize().x > 0:
            holes.append(Point(mm(pd.GetPosition().x), mm(pd.GetPosition().y)).buffer(mm(pd.GetDrillSize().x) / 2))
ob = {l: prepared.prep(unary_union(obs[l]).buffer(CL + TW / 2)) for l in obs}
ov = {l: prepared.prep(unary_union(obs[l]).buffer(CL + VD / 2)) for l in obs}
hv = prepared.prep(unary_union(holes).buffer(0.32 + VD / 2)) if holes else None   # via hole >= 0.47 mm from any hole (JLC: 0.45)
G = 0.05
nx, ny = int((X1 - X0) / G) + 1, int((Y1 - Y0) / G) + 1
def xy(i, j): return (X0 + i * G, Y0 + j * G)
free = {}
def ok(l, i, j):
    k = (l, i, j)
    if k not in free:
        free[k] = not ob[l].contains(Point(*xy(i, j)))
    return free[k]
vfree = {}
nopad = prepared.prep(unary_union([t[2] for t in targets]).buffer(VD / 2 + 0.25))   # no via in or near a pad
def vok(i, j):
    if (i, j) not in vfree:
        p = Point(*xy(i, j))
        vfree[(i, j)] = (not ov['F.Cu'].contains(p) and not ov['B.Cu'].contains(p) and not (hv and hv.contains(p))
                         and not nopad.contains(p))
    return vfree[(i, j)]
def near_pad(key, l, i, j):
    for k, layers, poly in targets:
        if k == key and l in layers and poly.buffer(-0.02).contains(Point(*xy(i, j))):
            return True
    return False
def cell(x, y): return (round((x - X0) / G), round((y - Y0) / G))
srcpad = next(t for t in targets if t[0] == SRC)
c = srcpad[2].centroid; si, sj = cell(c.x, c.y)
starts = [(l, si, sj) for l in srcpad[1]]          # a through-hole source pad starts on either layer, no via
start = starts[0]
goal_cells = set()
for k, layers, poly in targets:
    if k == SRC:
        continue
    c = poly.centroid
    gi, gj = cell(c.x, c.y)
    for l in layers:
        goal_cells.add((l, gi, gj))
for layers, g in copper:            # every grid cell inside the net's own copper is a goal
    g = g.buffer(-0.03)
    if g.is_empty or not g.intersects(box(X0, Y0, X1, Y1)):
        continue
    x0_, y0_, x1_, y1_ = g.bounds
    gprep = prepared.prep(g)
    for i in range(max(0, int((x0_ - X0) / G)), min(nx, int((x1_ - X0) / G) + 2)):
        for j in range(max(0, int((y0_ - Y0) / G)), min(ny, int((y1_ - Y0) / G) + 2)):
            if gprep.contains(Point(*xy(i, j))):
                for l in layers:
                    goal_cells.add((l, i, j))
gx = [(xy(i, j)) for (_, i, j) in goal_cells]
gx = gx[::max(1, len(gx) // 400)]   # heuristic only: a sample of the goal cells keeps it fast
def h(i, j):
    x, y = xy(i, j); return min(math.hypot(x - a, y - b_) for a, b_ in gx)
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
LC = {'F.Cu': 1.6, 'B.Cu': 1.0}   # prefer the bottom layer here
openq = [(h(si, sj), 0.0, st, None) for st in starts]
came, cost = {}, {st: 0.0 for st in starts}
found = None
while openq:
    f, g, s, d = heapq.heappop(openq)
    if s in came and cost.get(s, 1e9) < g - 1e-9:
        continue
    l, i, j = s
    if s in goal_cells:
        found = s; break
    nb = []
    for di, dj in DIRS:
        ni, nj = i + di, j + dj
        if not (0 <= ni < nx and 0 <= nj < ny):
            continue
        if ok(l, ni, nj) or (l, ni, nj) in goal_cells or any(near_pad(k, l, ni, nj) for k, *_ in targets):
            step = G * math.hypot(di, dj) * LC[l] + (0.02 if d and d != (di, dj) else 0)
            nb.append(((l, ni, nj), step, (di, dj)))
    if vok(i, j):
        ol = 'B.Cu' if l == 'F.Cu' else 'F.Cu'
        nb.append(((ol, i, j), 1.5, None))
    for ns, st, nd in nb:
        ng = g + st
        if ng < cost.get(ns, 1e9):
            cost[ns] = ng; came[ns] = (s, nd)
            heapq.heappush(openq, (ng + h(ns[1], ns[2]), ng, ns, nd))
if not found:
    print('no path'); sys.exit(1)
path = [found]
while path[-1] not in starts:
    path.append(came[path[-1]][0])
path.reverse()
# compress into segments and vias
net = b.FindNet(NET)
segs, vias = [], []
run = [path[0]]
for a, c2 in zip(path, path[1:]):
    if a[0] != c2[0]:
        segs.append(run); vias.append(xy(a[1], a[2])); run = [c2]
    else:
        run.append(c2)
segs.append(run)
def simplify(run):
    pts = [run[0]]
    for k in range(1, len(run) - 1):
        d1 = (run[k][1] - pts[-1][1], run[k][2] - pts[-1][2]); d2 = (run[k + 1][1] - run[k][1], run[k + 1][2] - run[k][2])
        if math.atan2(d1[1], d1[0]) != math.atan2(d2[1], d2[0]):
            pts.append(run[k])
    pts.append(run[-1]); return pts
n = 0
for run in segs:
    pts = simplify(run)
    for a, c2 in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(IU(xy(a[1], a[2])[0]), IU(xy(a[1], a[2])[1])))
        t.SetEnd(pcbnew.VECTOR2I(IU(xy(c2[1], c2[2])[0]), IU(xy(c2[1], c2[2])[1]))); t.SetWidth(IU(TW))
        t.SetLayer(b.GetLayerID(a[0])); t.SetNet(net); b.Add(t); n += 1
for (x, y) in vias:
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(IU(x), IU(y))); v.SetWidth(IU(VD)); v.SetDrill(IU(0.3)); v.SetNet(net); b.Add(v)
print('segments', n, 'vias', len(vias), 'length', round(cost[found], 2))
for run in segs:
    print(run[0][0], [tuple(round(v, 2) for v in xy(p[1], p[2])) for p in simplify(run)])
filler = pcbnew.ZONE_FILLER(b); filler.Fill(b.Zones())
b.Save(out)
