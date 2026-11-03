"""Incremental re-route (ECO) for a board revision that changes only a few parts.

Starts from an earlier revision's router state (route.py's routed.kicad_pcb.state.pkl), keeps all of its copper except
  - every net with a pad that was added, removed, moved, resized or re-netted between the two placed boards, and
  - anything that now overlaps a new or changed pad (its whole net, or the single via / stub of a plane net),
and writes a state whose failed list holds those nets (and plane stitches for the new and changed plane pads), so that
    RESUME=1 FINISH=1 route.py placed.kicad_pcb routed.kicad_pcb
routes only them, ripping neighbours as it needs to. Routing the whole board again from scratch reshuffles nets far
from the change (route.py is order-dependent); this keeps the proven layout everywhere else.

usage: route_eco.py old_placed.kicad_pcb old_state.pkl new_placed.kicad_pcb out_state.pkl
"""
import sys, pickle, math
import pcbnew
from shapely.geometry import LineString, Point, box

old_brd, old_state, new_brd, out_state = sys.argv[1:5]
OX, OY = 100.0, 50.0
PLANES = {'GND', '+3V3'}
CLEAR = 0.17
VIA_R = 0.3


def pads(path):
    b = pcbnew.LoadBoard(path)
    out = {}
    for fp in b.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            g = box(pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetTop()) - OY,
                    pcbnew.ToMM(bb.GetRight()) - OX, pcbnew.ToMM(bb.GetBottom()) - OY)
            out[(fp.GetReference(), p.GetNumber())] = dict(net=p.GetNetname(), g=g, smd=p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD,
                                                           layers=('F' if p.IsOnLayer(pcbnew.F_Cu) else '') +
                                                                  ('B' if p.IsOnLayer(pcbnew.B_Cu) else ''))
    return out


old, new = pads(old_brd), pads(new_brd)
changed = []          # keys of new pads that are new or differ
dirty = set()
for k, p in new.items():
    o = old.get(k)
    if o is None or o['net'] != p['net'] or not o['g'].equals_exact(p['g'], 1e-3):
        changed.append(k)
        dirty.add(p['net'])
        if o:
            dirty.add(o['net'])
for k, o in old.items():
    if k not in new:
        dirty.add(o['net'])
dirty.discard('')
tracks, vias, failed = pickle.load(open(old_state, 'rb'))
print(f'{len(changed)} new or changed pads; nets touched: {sorted(dirty - PLANES)}')


def tgeom(t):
    return LineString([t['p0'], t['p1']]).buffer(t['w'] / 2)


def layer_ok(t, p):
    return ('F' if t['L'] == 0 else 'B') in p['layers']


# nets with any copper on a changed pad of another net (or a plane via/stub there)
cp = [new[k] for k in changed]
plane_drop_t, plane_drop_v = set(), set()
while True:
    grow = False
    for i, t in enumerate(tracks):
        if t['net'] in dirty and t['net'] not in PLANES:
            continue
        if t.get('locked'):
            continue
        g = tgeom(t)
        for p in cp:
            if p['net'] != t['net'] and layer_ok(t, p) and g.distance(p['g']) < CLEAR:
                if t['net'] in PLANES:
                    plane_drop_t.add(i)
                else:
                    dirty.add(t['net']); grow = True
                break
    for i, v in enumerate(vias):
        if v['net'] in dirty and v['net'] not in PLANES:
            continue
        c = Point(v['x'], v['y'])
        for p in cp:
            if p['net'] != v['net'] and c.distance(p['g']) < CLEAR + VIA_R:
                if v['net'] in PLANES:
                    plane_drop_v.add(i)
                else:
                    dirty.add(v['net']); grow = True
                break
    if not grow:
        break

sig_dirty = sorted(dirty - PLANES)
keep_t = [t for i, t in enumerate(tracks) if not ((t['net'] in sig_dirty and not t.get('locked')) or i in plane_drop_t)]
keep_v = [v for i, v in enumerate(vias) if not (v['net'] in sig_dirty or i in plane_drop_v)]
# plane stitches: every new or changed plane pad, and plane pads whose via went (within 1.2 mm of a dropped via)
dropped = [vias[i] for i in plane_drop_v]
stitch = set()
for k in changed:
    if new[k]['net'] in PLANES and new[k]['smd']:
        stitch.add((new[k]['net'] + '-stitch', k[0], k[1]))
for v in dropped:
    for k, p in new.items():
        if p['net'] == v['net'] and p['smd'] and p['g'].distance(Point(v['x'], v['y'])) < 1.2:
            stitch.add((p['net'] + '-stitch', k[0], k[1]))
new_failed = [(n, '', '') for n in sig_dirty] + sorted(stitch)
pickle.dump((keep_t, keep_v, new_failed), open(out_state, 'wb'))
print(f'kept {len(keep_t)}/{len(tracks)} tracks, {len(keep_v)}/{len(vias)} vias; to route: {len(sig_dirty)} nets, '
      f'{len(stitch)} plane stitches')
print('nets:', ', '.join(sig_dirty))
