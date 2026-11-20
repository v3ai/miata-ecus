"""rip_conflicts.py <in.kicad_pcb> <out.kicad_pcb> [new.txt] (KiCad 9): clear the copper conflicts that KiCad's DRC
finds after a change order grew or moved pads (the castellated module's lands, the parts moved out from under it).

For each conflict (clearance, hole clearance, hole to hole, short, solder-mask bridge, crossing tracks, copper to edge)
it takes out as little as it can, never a pad:
  - copper that the change order itself added (new.txt from via_lands.py: a via and its links per line) goes first,
    as a whole group;
  - otherwise a track loses only the stretch near the conflict (the other item's size plus GAP each way, about the
    point of closest approach), so the net is left in two pieces a few millimetres apart; a via goes whole.
Then the zones are refilled. Run it until it removes nothing (one round per process: pcbnew's objects go bad after a
Remove), then join the pieces with finish_route.py."""
import gc
import json
import os
import subprocess
import sys
import tempfile
import pcbnew
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points

gc.disable()      # pcbnew's SWIG temporaries crash the cyclic collector under KiCad 9

TYPES = {'clearance', 'hole_clearance', 'hole_to_hole', 'shorting_items', 'solder_mask_bridge', 'tracks_crossing',
         'copper_edge_clearance'}
GAP = 0.5                       # mm cut beyond the other item's reach, each way
mm, MM = pcbnew.ToMM, pcbnew.FromMM


def geom(o):
    """shapely geometry (mm) and reach (half width) of a track, via or pad"""
    if isinstance(o, pcbnew.PAD):
        p, s = o.GetPosition(), o.GetSize()
        return Point(mm(p.x), mm(p.y)), max(mm(s.x), mm(s.y)) / 2
    if o.Type() == pcbnew.PCB_VIA_T:
        p = o.GetPosition()
        return Point(mm(p.x), mm(p.y)), mm(o.GetWidth(pcbnew.F_Cu)) / 2
    s, e = o.GetStart(), o.GetEnd()
    return LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]), mm(o.GetWidth()) / 2


def main(src, dst, new=None):
    with tempfile.TemporaryDirectory() as td:
        rep = os.path.join(td, 'drc.json')
        subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '-o', rep, src], capture_output=True)
        d = json.load(open(rep))
    b = pcbnew.LoadBoard(src)
    tracks = {t.m_Uuid.AsString(): t for t in b.GetTracks()}
    pads = {p.m_Uuid.AsString(): p for f in b.GetFootprints() for p in f.Pads()}
    group_of = {}
    if new and os.path.exists(new):
        for line in open(new):
            ids = line.split()
            for i in ids:
                group_of[i] = ids

    whole, cuts = {}, []          # uuid -> track/via removed whole; (track, point, reach) cut
    for v in d['violations']:
        if v['severity'] != 'error' or v['type'] not in TYPES:
            continue
        ids = [i.get('uuid') for i in v['items']]
        mine = [i for i in ids if i in group_of and all(g in tracks for g in group_of[i])]
        if mine:
            for g in group_of[mine[0]]:
                whole[g] = tracks[g]
            continue
        objs = [tracks[i] for i in ids if i in tracks]
        others = [tracks.get(i) or pads.get(i) for i in ids]
        if not objs:
            print('nothing to remove:', v['type'], [i['description'][:60] for i in v['items']])
            continue
        vias = [o for o in objs if o.Type() == pcbnew.PCB_VIA_T]
        if vias:
            whole[vias[0].m_Uuid.AsString()] = vias[0]
            continue
        # a track: cut it near the other item (or, two tracks, cut the one a cut shortens least)
        t = objs[0] if len(objs) == 1 else min(objs, key=lambda o: o.GetLength())
        other = next((o for o in others if o is not None and o is not t), None)
        tg, _ = geom(t)
        if other is None:
            whole[t.m_Uuid.AsString()] = t
            continue
        og, reach = geom(other)
        q = nearest_points(tg, og)[0]
        cuts.append((t, q, reach + mm(t.GetWidth()) / 2 + GAP))

    # every conflict on one track is cut in the same round: merge its stretches
    per = {}
    for t, q, r in cuts:
        k = t.m_Uuid.AsString()
        if k in whole:
            continue
        g, _ = geom(t)
        a = g.project(q)
        per.setdefault(k, (t, g, []))[2].append((a - r, a + r))
    n_cut = 0
    for k, (t, g, iv) in per.items():
        L = g.length
        iv.sort()
        merged = [list(iv[0])]
        for x0, x1 in iv[1:]:
            if x0 <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], x1)
            else:
                merged.append([x0, x1])
        keep, pos = [], 0.0
        for x0, x1 in merged:
            if x0 - pos > 0.05:
                keep.append((pos, x0))
            pos = max(pos, x1)
        if L - pos > 0.05:
            keep.append((pos, L))
        if not keep:
            whole[k] = t
            continue
        pts = [(g.interpolate(x0), g.interpolate(x1)) for x0, x1 in keep]
        (p0, p1), rest = pts[0], pts[1:]
        t.SetStart(pcbnew.VECTOR2I(MM(p0.x), MM(p0.y)))
        t.SetEnd(pcbnew.VECTOR2I(MM(p1.x), MM(p1.y)))
        for p0, p1 in rest:
            n = pcbnew.PCB_TRACK(b)
            n.SetStart(pcbnew.VECTOR2I(MM(p0.x), MM(p0.y)))
            n.SetEnd(pcbnew.VECTOR2I(MM(p1.x), MM(p1.y)))
            n.SetWidth(t.GetWidth())
            n.SetLayer(t.GetLayer())
            n.SetNet(t.GetNet())
            b.Add(n)
        n_cut += 1
        print('cut', b.GetLayerName(t.GetLayer()), t.GetNetname(), len(merged), 'stretch(es),',
              f'{sum(x1 - x0 for x0, x1 in merged):.1f} mm, near', tuple(round(c, 1) for c in g.interpolate(merged[0][0]).coords[0]))
    for t in whole.values():
        p = t.GetPosition() if t.Type() == pcbnew.PCB_VIA_T else t.GetStart()
        print('removed', 'via' if t.Type() == pcbnew.PCB_VIA_T else b.GetLayerName(t.GetLayer()), t.GetNetname(),
              (round(mm(p.x), 2), round(mm(p.y), 2)))
        b.Remove(t)
    if whole or n_cut:
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)
    print(f'RIP {len(whole)} {n_cut}')


def rounds(src, dst, new=None):
    import shutil
    shutil.copy(src, dst)
    tot = 0
    for i in range(25):
        r = subprocess.run([sys.executable] + sys.argv[:1] + ['--round', dst, dst] + ([new] if new else []),
                           capture_output=True, text=True)
        import re
        m = re.search(r'RIP (\d+) (\d+)', r.stdout)
        sys.stdout.write(''.join(l + '\n' for l in r.stdout.splitlines() if l.startswith(('cut', 'removed', 'nothing'))))
        if not m:
            sys.exit(f'round {i + 1} failed:\n{r.stdout[-2000:]}{r.stderr[-2000:]}')
        n = int(m.group(1)) + int(m.group(2))
        tot += n
        if not n:
            break
    print(f'{tot} cuts and removals in {i + 1} rounds')


if __name__ == '__main__':
    if sys.argv[1] == '--round':
        main(*sys.argv[2:5])
    else:
        rounds(*sys.argv[1:4])
