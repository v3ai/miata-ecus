"""Put the wideband block's copper on the daughterboard: the FOME module's own tracks, vias
and heater zones (rotated into place), with its two header rows turned into ports:
  sensor side -> straight drops onto J2 pins 33-40 (1.0 mm for the heater, 0.3 mm signals)
  power side  -> vias the router continues from (+5V, GND, CAN RX/TX, VBAT sense)
Copper that only served dropped parts (module headers, LDO, power LED, ID straps, BOOT0
pin) is removed as dangling."""
import math
import pcbnew
from pcbnew import FromMM, VECTOR2I
from shapely.geometry import Point, LineString, Polygon, box
import wideband as WB

LAYER = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu, 'In1.Cu': pcbnew.In1_Cu, 'In2.Cu': pcbnew.In2_Cu}
J2_Y = 57.25
PORT_VIA = {'+5V', 'GND', 'WB_CAN_RX', 'WB_CAN_TX', 'VBAT_IN'}
DROP_W = {'HTR_GND': 1.0, 'LSU_HTR_N': 1.0}


def fix_pads(board, OX, OY):
    """KiCad 7 library footprints differ from the module's KiCad 9 ones by up to 0.17 mm;
    copy the module's pad positions and sizes so its tracks land dead centre."""
    refs = {WB.ref(r): r for r in WB.M['fps'] if r not in WB.DROP}
    worst = 0.0
    for fp in board.GetFootprints():
        mr = refs.get(fp.GetReference())
        if not mr:
            continue
        mp = WB.M['fps'][mr]['pads']
        # library origin moved between KiCad versions (TO-252-2): shift the whole footprint
        dl = []
        import collections
        cnt = collections.Counter(p.GetNumber() for p in fp.Pads())
        for p in fp.Pads():
            c = mp.get(p.GetNumber())
            if p.GetNumber() and c and len(c) == 1 and cnt[p.GetNumber()] == 1:
                x, y = WB.xy(c[0][0], c[0][1]); pos = p.GetPosition()
                dl.append((x + OX - pcbnew.ToMM(pos.x), y + OY - pcbnew.ToMM(pos.y)))
        if dl:
            mx = sum(d[0] for d in dl) / len(dl); my = sum(d[1] for d in dl) / len(dl)
            if math.hypot(mx, my) > 0.3 and all(math.hypot(d[0] - mx, d[1] - my) < 0.05 for d in dl):
                fp.Move(VECTOR2I(FromMM(mx), FromMM(my)))
        for p in fp.Pads():
            c = mp.get(p.GetNumber())
            if not p.GetNumber() or not c or len(c) != 1 or cnt[p.GetNumber()] != 1:
                continue
            x, y = WB.xy(c[0][0], c[0][1])
            pos = p.GetPosition()
            d = math.hypot(pcbnew.ToMM(pos.x) - OX - x, pcbnew.ToMM(pos.y) - OY - y)
            assert d < 0.25, (fp.GetReference(), p.GetNumber(), d)
            worst = max(worst, d)
            p.SetPosition(VECTOR2I(FromMM(x + OX), FromMM(y + OY)))
            w, h = c[0][3]
            p.SetSize(VECTOR2I(FromMM(w), FromMM(h)))
    return worst


def pad_shapes(board, OX, OY):
    out = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if not p.GetNetname():
                continue
            o = p.GetEffectivePolygon().Outline(0)
            poly = Polygon([(pcbnew.ToMM(o.CPoint(i).x) - OX, pcbnew.ToMM(o.CPoint(i).y) - OY)
                            for i in range(o.PointCount())])
            lays = [n for n, l in LAYER.items() if p.IsOnLayer(l)]
            out.append((p.GetNetname(), lays, poly))
    return out


def add_block(board, OX, OY):
    worst = fix_pads(board, OX, OY)
    segs, vias, zones = WB.copper()
    ports = WB.ports()
    # sensor-side zones stop just past the port row
    clip = box(0, 0, 125, ports[0]['at'][1] + 1.0)
    for z in zones:
        z['shape'] = Polygon(z['poly']).intersection(clip)
    # ports: where module copper reaches each header pin, and on which layers
    for pt in ports:
        P = Point(pt['at'])
        pt['layers'] = sorted({s['layer'] for s in segs if s['net'] == pt['net'] and pt['net'] and
                               min(P.distance(Point(s['a'])), P.distance(Point(s['b']))) < 0.02} |
                              {z['layer'][0] for z in zones if z['net'] == pt['net'] and pt['net'] and
                               z['shape'].contains(P)})
    drops, pvias = [], []
    for pt in ports:
        if not pt['net']:
            continue
        x, y = pt['at']
        if pt['side'] == 'S':
            lay = 'F.Cu' if ('F.Cu' in pt['layers'] or not pt['layers']) else 'B.Cu'
            drops.append(dict(a=(x, y), b=(x, J2_Y), w=DROP_W.get(pt['net'], 0.3), layer=lay, net=pt['net']))
        elif pt['net'] in PORT_VIA or len(pt['layers']) == 2:   # the header pad was a layer change
            pvias.append(dict(at=(x, y), size=0.6, drill=0.3, net=pt['net']))

    # remove copper that dangles once the dropped parts and header pads are gone
    pads = pad_shapes(board, OX, OY)
    segs = [s for s in segs if s['net']]
    vias = [v for v in vias if v['net']] + pvias
    allsegs = segs + drops

    def connected(pt, s, live):
        P = Point(pt)
        for n, lays, poly in pads:
            if n == s['net'] and s['layer'] in lays and poly.buffer(0.01).contains(P):
                return True
        for v in vias:
            if v['net'] == s['net'] and P.distance(Point(v['at'])) < v['size'] / 2:
                return True
        for z in zones:
            if z['net'] == s['net'] and z['layer'][0] == s['layer'] and z['shape'].buffer(0.01).contains(P):
                return True
        for o in live:
            if o is not s and o['net'] == s['net'] and o['layer'] == s['layer'] and \
                    LineString([o['a'], o['b']]).distance(P) < 0.01:
                return True
        return False

    removed = 0
    while True:
        dead = [s for s in segs if not (connected(s['a'], s, allsegs) and connected(s['b'], s, allsegs))]
        if not dead:
            break
        removed += len(dead)
        segs = [s for s in segs if s not in dead]
        allsegs = segs + drops
    # vias that now touch nothing but a plane they are not on
    plane = {'GND', '+3V3'}
    keepv = []
    for v in vias:
        P = Point(v['at'])
        used = v['net'] in plane or any(
            s['net'] == v['net'] and LineString([s['a'], s['b']]).distance(P) < v['size'] / 2 for s in allsegs) or any(
            z['net'] == v['net'] and z['shape'].contains(P) for z in zones)
        if used:
            keepv.append(v)
    vias = keepv

    nets = board.GetNetsByName()
    for s in allsegs:
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(VECTOR2I(FromMM(s['a'][0] + OX), FromMM(s['a'][1] + OY)))
        t.SetEnd(VECTOR2I(FromMM(s['b'][0] + OX), FromMM(s['b'][1] + OY)))
        t.SetWidth(FromMM(s['w'])); t.SetLayer(LAYER[s['layer']]); t.SetNet(nets[s['net']])
        t.SetLocked(True)
        board.Add(t)
    for v in vias:
        vi = pcbnew.PCB_VIA(board)
        vi.SetPosition(VECTOR2I(FromMM(v['at'][0] + OX), FromMM(v['at'][1] + OY)))
        vi.SetWidth(FromMM(v['size'])); vi.SetDrill(FromMM(v['drill'])); vi.SetNet(nets[v['net']])
        vi.SetLocked(True)
        board.Add(vi)
    for z in zones:
        zz = pcbnew.ZONE(board)
        zz.SetLayer(LAYER[z['layer'][0]]); zz.SetNet(nets[z['net']])
        ol = zz.Outline(); ol.NewOutline()
        for x, y in list(z['shape'].exterior.coords)[:-1]:
            ol.Append(FromMM(x + OX), FromMM(y + OY))
        zz.SetAssignedPriority(2 if z['net'] == 'HTR_GND' else 1)   # as on the module: source pour over drain pour
        zz.SetLocalClearance(FromMM(0.2))
        zz.SetMinThickness(FromMM(0.2))
        zz.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        zz.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        board.Add(zz)
    # silkscreen frame + title around the block
    xs = [WB.xy(x, y)[0] for x, y in ((81.03, 73.15), (81.03, 94.04), (109.98, 73.15), (109.98, 94.04))]
    ys = [WB.xy(x, y)[1] for x, y in ((81.03, 73.15), (81.03, 94.04), (109.98, 73.15), (109.98, 94.04))]
    print(f'wideband block: {len(allsegs)} tracks ({removed} dangling removed, {len(drops)} drops), '
          f'{len(vias)} vias, {len(zones)} zones, pad fix max {worst:.3f} mm, '
          f'box x {min(xs):.2f}-{max(xs):.2f} y {min(ys):.2f}-{max(ys):.2f}')
    for pt in ports:
        print('  port', pt['side'], pt['num'], pt['net'] or '-', pt['layers'])
    return (min(xs), min(ys), max(xs), max(ys))
