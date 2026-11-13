"""Tie ground copper the pours cannot reach back to the board's ground (motherboards, two layers).

The motherboard router does not route GND: both layers are poured and every ground pad is expected to land in the
pour. Where the harness bus boxes a pad in on both layers (it happened to the 2001-05 board's injector-ground pins
3A/3B and to a pull-down on the 1999-2000 board), the pad ends up in a pour island of its own, or in none: DRC shows
one "unconnected" item and nothing else. This finds every such group and routes a track from it to ground copper of
the main group with hand_route.py (two-layer A* over the real copper), 0.8 mm wide for through-hole pads (harness and
socket ground pins carry load current), 0.3 mm for a small part's pad, narrower only if the wide one finds no way.

usage: mb_gnd_islands.py board.kicad_pcb        (edits the board in place; exits 1 if a group stays unconnected)
"""
import os, subprocess, sys
import pcbnew
from pcbnew import ToMM
from shapely.geometry import Polygon, Point, LineString, box
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
OX, OY = 100.0, 50.0


def groups(path):
    b = pcbnew.LoadBoard(path)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    code = [n.GetNetCode() for name, n in b.GetNetsByName().items() if str(name).split('/')[-1] == 'GND'][0]
    name = b.FindNet(code).GetNetname()
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    items = []          # (layers, geometry, kind, ref, num, (x, y), through-hole)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() != code:
                continue
            o = p.GetEffectivePolygon().Outline(0)
            pg = Polygon([(ToMM(o.CPoint(i).x), ToMM(o.CPoint(i).y)) for i in range(o.PointCount())]).buffer(-0.01)
            Ls = {L for L in (F, B) if p.IsOnLayer(L)}
            items.append((Ls, pg, 'pad', fp.GetReference(), p.GetNumber(), (ToMM(p.GetPosition().x), ToMM(p.GetPosition().y)),
                          p.GetDrillSize().x > 0))
    for t in b.GetTracks():
        if t.GetNetCode() != code:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            c = (ToMM(t.GetPosition().x), ToMM(t.GetPosition().y))
            items.append(({F, B}, Point(c).buffer(ToMM(t.GetWidth()) / 2 - 0.01), 'via', '', '', c, True))
        else:
            a = (ToMM(t.GetStart().x), ToMM(t.GetStart().y)); c = (ToMM(t.GetEnd().x), ToMM(t.GetEnd().y))
            items.append(({t.GetLayer()}, LineString([a, c]).buffer(ToMM(t.GetWidth()) / 2 - 0.005), 'track', '', '', a, False))
    for z in b.Zones():
        if z.GetNetCode() != code:
            continue
        for L in z.GetLayerSet().Seq():
            if not z.HasFilledPolysForLayer(L):
                continue
            ps = z.GetFilledPolysList(L)
            for i in range(ps.OutlineCount()):
                o = ps.Outline(i)
                holes = [[(ToMM(ps.Hole(i, h).CPoint(k).x), ToMM(ps.Hole(i, h).CPoint(k).y)) for k in range(ps.Hole(i, h).PointCount())]
                         for h in range(ps.HoleCount(i))]
                pg = Polygon([(ToMM(o.CPoint(k).x), ToMM(o.CPoint(k).y)) for k in range(o.PointCount())], holes).buffer(0)
                items.append(({L}, pg, 'pour', b.GetLayerName(L), '', (pg.representative_point().x, pg.representative_point().y), False))
    par = list(range(len(items)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    geoms = [it[1] for it in items]
    tree = STRtree(geoms)
    for i, it in enumerate(items):
        for j in tree.query(it[1]):
            j = int(j)
            if j > i and (it[0] & items[j][0]) and it[1].intersects(geoms[j]):
                par[find(i)] = find(j)
    comp = {}
    for i in range(len(items)):
        comp.setdefault(find(i), []).append(items[i])
    cs = sorted(comp.values(), key=len, reverse=True)
    return name, cs[0], [c for c in cs[1:] if any(it[2] == 'pad' for it in c)]


def main(path):
    ok = True
    for attempt in range(8):
        name, main_g, isl = groups(path)
        if not isl:
            break
        g = isl[0]
        pads = sorted((it for it in g if it[2] == 'pad'), key=lambda it: not it[6])     # through-hole pads first
        src = pads[0]
        sx, sy = src[5]
        # targets: the nearest pads of the main group (through-hole first: reachable on either layer)
        tg = sorted((it for it in main_g if it[2] == 'pad'), key=lambda it: (Point(it[5]).distance(Point(sx, sy)) + (0 if it[6] else 6)))[:10]
        xs = [sx] + [it[5][0] for it in tg]; ys = [sy] + [it[5][1] for it in tg]
        win = [min(xs) - 4, min(ys) - 4, max(xs) + 4, max(ys) + 4]
        # the route may also end in the main ground pour itself, which is usually much nearer than a pad
        goals = path + '.goals'
        with open(goals, 'w') as f:
            for it in main_g:
                if it[2] == 'pour' and it[1].area > 20:
                    f.write(f'{it[3]}|{it[1].wkt}\n')
        done = False
        for tw in ((1.0, 0.8, 0.6, 0.4, 0.3) if src[6] else (0.3, 0.2)):
            env = dict(os.environ, TW=str(tw), CL='0.22', GOALS=goals)
            r = subprocess.run([sys.executable, os.path.join(HERE, 'hand_route.py'), path, path, name] + [f'{v:.2f}' for v in win]
                               + [f'{src[3]}:{src[4]}', ','.join(f'{it[3]}:{it[4]}' for it in tg)], env=env, capture_output=True, text=True)
            if r.returncode == 0:
                print(f'tied {src[3]}.{src[4]} ({sx - OX:.2f}, {sy - OY:.2f}) and {len(pads) - 1} more pad(s) to ground with a {tw} mm track:',
                      [l for l in r.stdout.splitlines() if l.startswith('segments')][-1])
                done = True
                break
        if not done:
            print(f'NO WAY from {src[3]}.{src[4]} ({sx - OX:.2f}, {sy - OY:.2f}) to the main ground: {[f"{it[3]}.{it[4]}" for it in pads]}')
            ok = False
            break
    if os.path.exists(path + '.goals'):
        os.remove(path + '.goals')
    name, main_g, isl = groups(path)
    print('ground groups left unconnected:', [[f'{it[3]}.{it[4]}' for it in g if it[2] == 'pad'] for g in isl])
    sys.exit(0 if ok and not isl else 1)


if __name__ == '__main__':
    main(sys.argv[1])
