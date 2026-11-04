"""jlc_fab_check.py board.kicad_pcb [...]: a board's geometry against JLCPCB's published PCB capabilities
(https://jlcpcb.com/capabilities/pcb-capabilities, 1 oz copper; multilayer values for 4 layers, 2-layer values
otherwise). Copper clearances themselves are KiCad DRC's job (the boards' 0.15 mm rule is above JLC's 0.09/0.10 mm);
this covers what the DRC rule set doesn't: track width, via and hole sizes, PTH annular ring, hole-to-hole spacing,
copper to the board edge, silkscreen line width and text height. Exit status 1 if anything is below a minimum."""
import sys, math
import pcbnew

mm = pcbnew.ToMM


def check(path):
    b = pcbnew.LoadBoard(path)
    layers = b.GetCopperLayerCount()
    multi = layers > 2
    lim = dict(track=0.09 if multi else 0.10, via_hole=0.15, via_dia=0.25, via_ring_diff=0.10, pth_ring=0.15 if multi else 0.18,
               via_gap=0.20, pad_hole_gap=0.45, edge=0.20, silk_w=0.15, silk_h=1.0)
    bad = []
    # tracks and vias
    holes = []
    edge = b.GetBoardEdgesBoundingBox()
    from shapely.geometry import LineString, Point, Polygon
    outline = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(outline)
    ol = outline.Outline(0)
    board_poly = Polygon([(mm(ol.CPoint(i).x), mm(ol.CPoint(i).y)) for i in range(ol.PointCount())])
    border = board_poly.exterior
    min_edge = (9e9, None)
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            d, h = mm(t.GetWidth()), mm(t.GetDrillValue())
            if h < lim['via_hole'] - 1e-6 or d < lim['via_dia'] - 1e-6 or d - h < lim['via_ring_diff'] - 1e-6:
                bad.append(f'via {d:.2f}/{h:.2f} mm at {mm(t.GetPosition().x):.2f},{mm(t.GetPosition().y):.2f}')
            p = Point(mm(t.GetPosition().x), mm(t.GetPosition().y))
            holes.append((p, h / 2, 'via'))
            e = border.distance(p) - d / 2
        else:
            w = mm(t.GetWidth())
            if w < lim['track'] - 1e-6:
                bad.append(f'track {w:.3f} mm on {t.GetNetname()}')
            s, e_ = t.GetStart(), t.GetEnd()
            e = border.distance(LineString([(mm(s.x), mm(s.y)), (mm(e_.x), mm(e_.y))])) - w / 2
        if e < min_edge[0]:
            min_edge = (e, t.GetNetname())
    # pads: PTH ring, holes, copper to edge
    for fp in b.GetFootprints():
        for p in fp.Pads():
            a = p.GetAttribute()
            if a in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                h = mm(min(p.GetDrillSize().x, p.GetDrillSize().y))
                c = Point(mm(p.GetPosition().x), mm(p.GetPosition().y))
                holes.append((c, h / 2, 'pad'))
                if a == pcbnew.PAD_ATTRIB_PTH:
                    ring = (mm(min(p.GetSize().x, p.GetSize().y)) - h) / 2
                    if ring < lim['pth_ring'] - 1e-6:
                        bad.append(f'PTH ring {ring:.3f} mm: {fp.GetReference()}.{p.GetNumber()}')
            if p.IsOnCopperLayer() and a != pcbnew.PAD_ATTRIB_NPTH:
                bb = p.GetBoundingBox()
                g = Polygon([(mm(bb.GetLeft()), mm(bb.GetTop())), (mm(bb.GetRight()), mm(bb.GetTop())),
                             (mm(bb.GetRight()), mm(bb.GetBottom())), (mm(bb.GetLeft()), mm(bb.GetBottom()))])
                e = border.distance(g)
                if e < min_edge[0]:
                    min_edge = (e, f'{fp.GetReference()}.{p.GetNumber()}')
    # zones: their own edge clearance
    for z in b.Zones():
        for lid in z.GetLayerSet().Seq():
            fp_ = z.GetFilledPolysList(lid)
            for k in range(fp_.OutlineCount()):
                o = fp_.Outline(k)
                g = Polygon([(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())])
                e = border.distance(g) if g.is_valid else border.distance(g.buffer(0))
                if e < min_edge[0]:
                    min_edge = (e, f'zone {z.GetNetname()}')
    if min_edge[0] < lim['edge'] - 1e-3:
        bad.append(f'copper {min_edge[0]:.3f} mm from the board edge ({min_edge[1]})')
    # hole to hole (edge to edge)
    from shapely.strtree import STRtree
    pts = [h[0].buffer(h[1]) for h in holes]
    tr = STRtree(pts)
    worst = {}
    for i, g in enumerate(pts):
        for j in tr.query(g.buffer(0.5)):
            if j <= i:
                continue
            d = g.distance(pts[j])
            kind = 'via' if holes[i][2] == holes[j][2] == 'via' else 'pad'
            need = lim['via_gap'] if kind == 'via' else lim['pad_hole_gap']
            if d < need - 1e-3 and d > 1e-6:
                worst.setdefault(kind, []).append(round(d, 3))
            elif d <= 1e-6 and holes[i][0].distance(holes[j][0]) > 1e-3:
                worst.setdefault(kind, []).append(0.0)
    for kind, ds in worst.items():
        bad.append(f'{len(ds)} {kind} holes closer than {lim["via_gap"] if kind == "via" else lim["pad_hole_gap"]} mm (min {min(ds):.3f})')
    # silkscreen
    silk = (pcbnew.F_SilkS, pcbnew.B_SilkS)
    small_txt, thin = [], []
    def text_ok(t, owner):
        if not t.IsVisible() or t.GetLayer() not in silk:
            return
        h = mm(t.GetTextHeight())
        if h < lim['silk_h'] - 1e-3:
            small_txt.append(f'{owner}:{t.GetText()} {h:.2f}')
        if mm(t.GetTextThickness()) < lim['silk_w'] - 1e-3:
            thin.append(f'{owner}:{t.GetText()} line {mm(t.GetTextThickness()):.2f}')
    for d in b.GetDrawings():
        if d.GetClass() == 'PCB_TEXT':
            text_ok(d, 'board')
        elif d.GetLayer() in silk and d.GetClass() == 'PCB_SHAPE' and mm(d.GetWidth()) < lim['silk_w'] - 1e-3 and mm(d.GetWidth()) > 0:
            thin.append(f'board line {mm(d.GetWidth()):.2f}')
    for fp in b.GetFootprints():
        text_ok(fp.Reference(), fp.GetReference())
        for it in fp.GraphicalItems():
            if it.GetClass() in ('PCB_TEXT', 'FP_TEXT'):
                text_ok(it, fp.GetReference())
            elif it.GetLayer() in silk and hasattr(it, 'GetWidth') and 0 < mm(it.GetWidth()) < lim['silk_w'] - 1e-3:
                thin.append(f'{fp.GetReference()} line {mm(it.GetWidth()):.2f}')
    if small_txt:
        bad.append(f'{len(small_txt)} silkscreen texts under {lim["silk_h"]} mm high: ' + ', '.join(small_txt[:12]) + (' ...' if len(small_txt) > 12 else ''))
    if thin:
        bad.append(f'{len(thin)} silkscreen lines under {lim["silk_w"]} mm: ' + ', '.join(sorted(set(thin))[:12]) + (' ...' if len(thin) > 12 else ''))
    return layers, min_edge, bad


if __name__ == '__main__':
    fail = False
    for path in sys.argv[1:]:
        layers, edge, bad = check(path)
        print(f'{path}: {layers} layers, copper {edge[0]:.2f} mm from the edge at closest: ' + ('OK' if not bad else f'{len(bad)} issues'))
        for x in bad:
            print('   ', x)
        fail |= bool(bad)
    sys.exit(1 if fail else 0)
