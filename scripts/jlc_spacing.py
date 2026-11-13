"""jlc_spacing.py board.kicad_pcb: pad-to-pad gaps between different top-side SMD parts against JLCPCB's recommended minimum
spacing per package pair (https://jlcpcb.com/help/article/minimum-spacing-for-smd-components)."""
import sys, re, pcbnew, collections
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
def kind(fp):
    n = str(fp.GetFPID().GetLibItemName())
    for pat, k in (('QFP', 'QFP'), ('QFN|DFN', 'QFN'), ('SOIC|SO-|TSSOP|SSOP|MSOP|DSO|HTSSOP', 'SOP'), ('SOT|TO-252|DPAK|SC-70|SOD-323|SOD-123', 'SOT'),
                   ('0201', '0201'), ('0402|1005Metric', '0402'), ('0603|1608Metric', '0603'), ('0805|2012Metric', '0805'),
                   ('1206|3216Metric|1210|2512|1812|2920|SMA|SMB|SMC|D_SMC|D_SMA|SOD-123F', '1206'), ('Crystal|SMD-4Pin|3225', 'SOT'),
                   ('LED', '0603'), ('CP_Elec|L_', '1206'), ('Fuse', '1206'), ('SW_', 'SOP'),
                   ('microSD', 'SOP')):      # card socket: judged like a leaded IC (its pads sit under and beside the shell)
        if re.search(pat, n): return k
    return 'OTHER:' + n
T = {}
def rule(a, c, v):
    T[(a, c)] = T[(c, a)] = v
for x in ('0201', '0402'):
    for y, v in (('0201', .15), ('0402', .15), ('0603', .18), ('0805', .18), ('1206', .25), ('QFN', 1.0), ('QFP', .5), ('SOP', .4), ('SOT', .2)): rule(x, y, v)
for x in ('0603', '0805'):
    for y, v in (('0603', .18), ('0805', .18), ('1206', .25), ('QFN', 1.0), ('QFP', .5), ('SOP', .4), ('SOT', .2)): rule(x, y, v)
for y, v in (('1206', .35), ('QFN', 1.0), ('QFP', .5), ('SOP', .4), ('SOT', .2)): rule('1206', y, v)
for y, v in (('QFN', 1.0), ('QFP', 1.0), ('SOP', 1.0), ('SOT', 1.0)): rule('QFN', y, v)
for y, v in (('QFP', 1.25), ('SOP', 1.25), ('SOT', 1.0)): rule('QFP', y, v)
rule('SOP', 'SOP', .5); rule('SOP', 'SOT', .4); rule('SOT', 'SOT', .4)
G, R = [], []
kinds = {}
for fp in b.GetFootprints():
    if fp.IsFlipped(): continue
    polys = []
    for p in fp.Pads():
        if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or not p.IsOnLayer(pcbnew.F_Cu): continue
        ol = p.GetEffectivePolygon().Outline(0)
        polys.append(Polygon([(mm(ol.CPoint(i).x), mm(ol.CPoint(i).y)) for i in range(ol.PointCount())]))
    if polys:
        G.append(unary_union(polys)); R.append(fp.GetReference()); kinds[fp.GetReference()] = kind(fp)
t = STRtree(G); bad = []; others = set()
for i, g in enumerate(G):
    for j in t.query(g.buffer(1.6)):
        if j <= i: continue
        a, c = kinds[R[i]], kinds[R[j]]
        if a.startswith('OTHER') or c.startswith('OTHER'):
            others.update(k for k in (a, c) if k.startswith('OTHER')); continue
        need = T[(a, c)]; d = g.distance(G[j])
        if d < need - 1e-3: bad.append((round(need - d, 3), round(d, 3), need, R[i], a, R[j], c))
bad.sort(reverse=True)
print(len(bad), 'pairs under JLC recommended spacing; unknown footprints:', sorted(others))
cnt = collections.Counter((x[4], x[6]) if x[4] <= x[6] else (x[6], x[4]) for x in bad); print(cnt.most_common())
for x in bad[:60]: print(f'  short by {x[0]:.2f}: {x[3]} ({x[4]}) - {x[5]} ({x[6]}) gap {x[1]:.2f} want {x[2]}')
