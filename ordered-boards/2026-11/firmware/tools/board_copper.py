"""Copper connectivity of a routed KiCad board, worked out from the copper geometry alone.

Helper for board_checks.py. Every pad, track, arc, via and filled zone island is turned into a polygon per copper
layer (shapely); items that touch on a layer, or share a plated hole / via barrel, are joined. The net names stored in
the .kicad_pcb are NOT used to join anything, so the result is an independent netlist of what the copper actually
connects: two design nets in one cluster is a short, one design net over two clusters is an open.

Needs KiCad's pcbnew module (KiCad 7) and shapely. Run under /usr/bin/python3.
"""
import pcbnew
from shapely.geometry import LineString, Point, Polygon
from shapely.strtree import STRtree

NM = 1e-6   # KiCad internal units (nm) -> mm


def _chain_pts(chain):
    return [(chain.CPoint(i).x * NM, chain.CPoint(i).y * NM) for i in range(chain.PointCount())]


def _polys(polyset):
    out = []
    for i in range(polyset.OutlineCount()):
        ext = _chain_pts(polyset.Outline(i))
        holes = [_chain_pts(polyset.Hole(i, j)) for j in range(polyset.HoleCount(i))]
        if len(ext) >= 3:
            g = Polygon(ext, [h for h in holes if len(h) >= 3])
            if not g.is_valid:
                g = g.buffer(0)
            out.append(g)
    return out


class _UF:
    def __init__(self):
        self.p = {}

    def find(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def copper_netlist(path):
    """-> dict with
         pads:     {(ref, padnum): cluster id}           (pads with copper only; NPTH skipped)
         pcb_net:  {(ref, padnum): net name stored in the file}
         fps:      {ref: {'value', 'fpid', 'side', 'pads': set(padnum)}}
         clusters: {cluster id: set of (ref, padnum)}
         stats:    counts of items used
    """
    board = pcbnew.LoadBoard(path)
    cu_layers = list(board.GetEnabledLayers().CuStack())
    geoms = {L: [] for L in cu_layers}         # layer -> [(geometry, item key)]
    uf = _UF()
    pad_key, pcb_net, fps = {}, {}, {}
    n_items = dict(pads=0, tracks=0, vias=0, zone_islands=0)

    for fp in board.GetFootprints():
        ref = fp.GetReference()
        fps[ref] = dict(value=fp.GetValue(), fpid=str(fp.GetFPID().GetUniStringLibItemName()),
                        side='B' if fp.IsFlipped() else 'F', pads=set())
        for k, pad in enumerate(fp.Pads()):
            num = pad.GetNumber()
            fps[ref]['pads'].add(num)
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                continue
            key = ('pad', ref, num, k)
            pkey = (ref, num)
            pad_key.setdefault(pkey, []).append(key)
            pcb_net[pkey] = pad.GetNetname()
            n_items['pads'] += 1
            for L in pad.GetLayerSet().CuStack():
                if L not in geoms:
                    continue
                ps = pcbnew.SHAPE_POLY_SET()
                pad.TransformShapeToPolygon(ps, L, 0, 2000)
                for g in _polys(ps):
                    geoms[L].append((g, key))
            uf.find(key)
        # pads with the same number in one footprint are one terminal of the part
        for pkey, keys in pad_key.items():
            if pkey[0] == ref:
                for kk in keys[1:]:
                    uf.union(keys[0], kk)

    for t in board.GetTracks():
        cls = t.GetClass()
        key = ('trk', t.m_Uuid.AsString())
        uf.find(key)
        if cls == 'PCB_VIA':
            n_items['vias'] += 1
            g = Point(t.GetPosition().x * NM, t.GetPosition().y * NM).buffer(t.GetWidth() * NM / 2, 16)
            top, bot = t.TopLayer(), t.BottomLayer()
            idx = {L: i for i, L in enumerate(cu_layers)}
            lo, hi = sorted((idx.get(top, 0), idx.get(bot, len(cu_layers) - 1)))
            for L in cu_layers[lo:hi + 1]:
                geoms[L].append((g, key))
            continue
        n_items['tracks'] += 1
        w = t.GetWidth() * NM
        if cls == 'PCB_ARC':
            s, m, e = t.GetStart(), t.GetMid(), t.GetEnd()
            line = LineString([(s.x * NM, s.y * NM), (m.x * NM, m.y * NM), (e.x * NM, e.y * NM)])
        else:
            s, e = t.GetStart(), t.GetEnd()
            line = LineString([(s.x * NM, s.y * NM), (e.x * NM, e.y * NM)])
            if line.length == 0:
                line = Point(s.x * NM, s.y * NM)
        if t.GetLayer() in geoms:
            geoms[t.GetLayer()].append((line.buffer(w / 2, 8), key))

    for zi, z in enumerate(board.Zones()):
        if z.GetIsRuleArea():
            continue
        for L in z.GetLayerSet().CuStack():
            if L not in geoms:
                continue
            for ii, g in enumerate(_polys(z.GetFilledPolysList(L))):
                key = ('zone', zi, L, ii)
                uf.find(key)
                n_items['zone_islands'] += 1
                geoms[L].append((g, key))

    for L, items in geoms.items():
        if not items:
            continue
        tree = STRtree([g for g, _ in items])
        for i, (g, key) in enumerate(items):
            for j in tree.query(g, predicate='intersects'):
                if j > i:
                    uf.union(key, items[j][1])

    pads = {pkey: uf.find(keys[0]) for pkey, keys in pad_key.items()}
    clusters = {}
    for pkey, c in pads.items():
        clusters.setdefault(c, set()).add(pkey)
    return dict(pads=pads, pcb_net=pcb_net, fps=fps, clusters=clusters, stats=n_items,
                layers=[board.GetLayerName(L) for L in cu_layers])


def compare(cu, design_pads, ignore_refs=()):
    """Compare copper clusters with a design netlist {(ref, pad): net}. -> dict of problem lists."""
    res = dict(opens=[], shorts=[], label=[], missing_fp=[], missing_pad=[], extra_net=[])
    for (ref, pad), net in design_pads.items():
        if ref in ignore_refs:
            continue
        if ref not in cu['fps']:
            res['missing_fp'].append(ref)
            continue
        if pad not in cu['fps'][ref]['pads']:
            res['missing_pad'].append((ref, pad, net))
            continue
        got = cu['pcb_net'].get((ref, pad))
        if net and (got or '').split('/')[-1] != net:
            res['label'].append((ref, pad, net, got))
    # opens: a design net spread over several copper clusters
    by_net = {}
    for (ref, pad), net in design_pads.items():
        if net and (ref, pad) in cu['pads']:
            by_net.setdefault(net, {}).setdefault(cu['pads'][(ref, pad)], []).append(f'{ref}.{pad}')
    for net, cl in by_net.items():
        if len(cl) > 1:
            groups = sorted(cl.values(), key=len, reverse=True)
            res['opens'].append((net, groups))
    # shorts: one copper cluster holding several design nets (an unconnected design pad counts as its own net)
    for c, members in cu['clusters'].items():
        nets = {}
        for m in members:
            if m in design_pads:
                n = design_pads[m] or f'<unconnected {m[0]}.{m[1]}>'
                nets.setdefault(n, []).append(f'{m[0]}.{m[1]}')
        if len(nets) > 1:
            res['shorts'].append(nets)
    # pads on the board that carry a net the design doesn't know for that pad
    fp_refs = set(r for r, _ in design_pads)
    for (ref, pad), n in cu['pcb_net'].items():
        if ref in fp_refs and (ref, pad) not in design_pads and n:
            res['extra_net'].append((ref, pad, n))
    res['extra_fp'] = sorted(set(cu['fps']) - fp_refs - set(ignore_refs))
    return res
