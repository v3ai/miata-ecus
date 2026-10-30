"""Preview the wideband block placement: courtyards, pads coloured by net, ratsnest (MST per net),
courtyard overlaps.  usage: wb_preview.py board.kicad_pcb out.png [x0 y0 x1 y1]"""
import sys, math, hashlib
import pcbnew
from shapely.geometry import Polygon, box
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OX, OY = 100.0, 50.0
b = pcbnew.LoadBoard(sys.argv[1])
x0, y0, x1, y1 = (float(v) for v in sys.argv[3:7]) if len(sys.argv) > 6 else (84, 16, 118, 59)
mm = pcbnew.ToMM


def poly_of(sps):
    out = []
    for k in range(sps.OutlineCount()):
        o = sps.Outline(k)
        out.append(Polygon([(mm(o.CPoint(i).x) - OX, mm(o.CPoint(i).y) - OY) for i in range(o.PointCount())]))
    return out


fig, ax = plt.subplots(figsize=(14, 17))
ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.set_aspect('equal')
ax.add_patch(plt.Rectangle((0, 0), 125, 60, fill=False, ec='k'))
col = lambda n: '#' + hashlib.md5(n.encode()).hexdigest()[:6] if n else '#bbbbbb'
crts = {}
pads = []
for fp in b.GetFootprints():
    r = fp.GetReference()
    side = 'B' if fp.IsFlipped() else 'F'
    try:
        cp = poly_of(fp.GetCourtyard(pcbnew.B_CrtYd if side == 'B' else pcbnew.F_CrtYd))
    except Exception:
        cp = []
    if not cp:
        bb = fp.GetBoundingBox(False, False)
        cp = [box(mm(bb.GetX()) - OX, mm(bb.GetY()) - OY, mm(bb.GetRight()) - OX, mm(bb.GetBottom()) - OY)]
    crts[r] = (side, cp)
    for c in cp:
        xs, ys = c.exterior.xy
        ax.plot(xs, ys, color='#888' if side == 'F' else '#c6c', lw=0.6, ls='-' if side == 'F' else '--')
    cx, cy = mm(fp.GetPosition().x) - OX, mm(fp.GetPosition().y) - OY
    if x0 < cx < x1 and y0 < cy < y1:
        ax.text(cx, cy, r, fontsize=6, ha='center', va='center', color='k' if side == 'F' else '#a3a',
                fontweight='bold')
    for p in fp.Pads():
        n = p.GetNetname()
        for pg in poly_of(p.GetEffectivePolygon()):
            xs, ys = pg.exterior.xy
            ax.fill(xs, ys, color=col(n), alpha=0.75 if side == 'F' else 0.3)
        c = (mm(p.GetPosition().x) - OX, mm(p.GetPosition().y) - OY)
        pads.append((n, c, r))
# ratsnest: MST per net (planes GND/+3V3 skipped)
nets = {}
for n, c, r in pads:
    if n and n not in ('GND', '+3V3'):
        nets.setdefault(n, []).append(c)
total = 0.0
for n, pts in nets.items():
    if len(pts) < 2:
        continue
    inn, out = [pts[0]], pts[1:]
    while out:
        d, a, bb = min((math.dist(a, q), a, q) for a in inn for q in out)
        ax.plot([a[0], bb[0]], [a[1], bb[1]], color=col(n), lw=0.7)
        total += d
        inn.append(bb); out.remove(bb)
# overlaps
over = []
items = list(crts.items())
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        (ra, (sa, pa)), (rb, (sb, pb)) = items[i], items[j]
        if sa != sb:
            continue
        for a in pa:
            for c in pb:
                if a.intersection(c).area > 0.01:
                    over.append((ra, rb, round(a.intersection(c).area, 2)))
ax.set_title(f'{sys.argv[1]}  overlaps: {len(over)}')
fig.savefig(sys.argv[2], dpi=110, bbox_inches='tight')
print('overlaps:', over)
