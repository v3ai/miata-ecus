"""silk_clean.py <board.kicad_pcb (KiCad 7)> <out.kicad_pcb> [--fab-refs] [--keepout x0,y0,x1,y1 ...]
   silk_clean.py <board> --check [--keepout ...]

--keepout: an area a part covers that has no footprint of its own (on the motherboards: the soldered-down
daughterboard), treated as a part's courtyard and body.

The silkscreen rule: nothing on the silkscreen may lie on a pad or on a part. Reads the board with pcbnew 9 (run it
through the KiCad 9 shim), works out the changes, and writes them into the KiCad 7 text so the rest of the file stays
as it is:

  1. Part references (the footprint's reference field on F.SilkS) that touch a pad (with JLCPCB's 0.15 mm pad-to-silk
     gap), another part's courtyard, their own part's courtyard, another silkscreen item or the board edge move to the
     nearest free place round their part (above, below, left or right, upright or turned). One that finds no place goes
     to F.Fab (it stays on the assembly drawing); with --fab-refs every reference on a crowded board that does not
     fit goes there without a warning (the daughterboard: JLCPCB places every part on it).
  2. Board texts (gr_text) that touch a pad or a part nudge up to 1 mm; one that still touches is an error.
  3. Silkscreen lines and arcs (footprint outlines and board graphics) are cut where they cross a pad (0.15 mm gap),
     another part's body (its courtyard less 0.25 mm), a silkscreen text (0.1 mm) or come within 0.3 mm of the board
     edge; pieces shorter than 0.3 mm are dropped. A part's outline on its own body is fine and stays.
  4. Pads that carry the silkscreen layer themselves (a footprint library slip: the pad prints a silk disc) lose it.

--check: changes nothing; prints every silkscreen item that still breaks the rule and exits 1 if there is one.
KiCad's own DRC (silk_over_copper, silk_overlap, silk_edge_clearance) is the second check, in reexport.sh.
"""
import math
import re
import sys
import uuid

import pcbnew
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import polygonize, unary_union

PAD_GAP = 0.15        # JLCPCB: silkscreen to pad
TEXT_GAP = 0.1        # between silkscreen items
READ_GAP = 0.4        # between a part's text and any other text, so two never read as one
EDGE_GAP = 0.3        # silkscreen to board edge
BODY_SHRINK = 0.25    # a courtyard less this is the part's body (IPC courtyard excess)
MIN_PIECE = 0.3
LINE_GAP = 0.05           # between two parts' silkscreen lines
MARK_PAD_GAP = 0.05       # a filled pin-1 mark to a pad (it can't be cut, so it keeps only the solder mask's own gap)
PIN_LABEL_REACH = 3.0     # a pin label (a footprint text named after one of its pads) moves at most this far from it
mm = pcbnew.ToMM
F_SILK, F_CRT = pcbnew.F_SilkS, pcbnew.F_CrtYd


def pt(p):
    return (mm(p.x), mm(p.y))


def polyset(ps):
    out = []
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        pts = [pt(o.CPoint(j)) for j in range(o.PointCount())]
        if len(pts) >= 3:
            g = Polygon(pts)
            out.append(g if g.is_valid else g.buffer(0))
    return unary_union(out) if out else None


def shape_path(s):
    """A silkscreen shape as its centre line (LineString) and stroke half-width, or None for a filled shape."""
    t, w = s.GetShape(), mm(s.GetWidth()) / 2
    if t == pcbnew.SHAPE_T_SEGMENT:
        return LineString([pt(s.GetStart()), pt(s.GetEnd())]), w
    if t == pcbnew.SHAPE_T_RECT:
        (x0, y0), (x1, y1) = pt(s.GetStart()), pt(s.GetEnd())
        if s.IsFilled():
            return None, w
        return LineString([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]), w
    if t == pcbnew.SHAPE_T_CIRCLE:
        c, r = s.GetCenter(), s.GetRadius()
        if s.IsFilled():
            return None, w
        return LineString([(mm(c.x + r * math.cos(2 * math.pi * i / 48)), mm(c.y + r * math.sin(2 * math.pi * i / 48)))
                           for i in range(49)]), w
    if t == pcbnew.SHAPE_T_ARC:
        c, r, a0 = s.GetCenter(), s.GetRadius(), s.GetStart()
        sa, ang = math.atan2(a0.y - c.y, a0.x - c.x), s.GetArcAngle().AsRadians()
        n = max(4, int(abs(ang) / (math.pi / 24)))
        return LineString([(mm(c.x + r * math.cos(sa + ang * i / n)), mm(c.y + r * math.sin(sa + ang * i / n)))
                           for i in range(n + 1)]), w
    if t == pcbnew.SHAPE_T_POLY:
        g = polyset(s.GetPolyShape())
        if g is None or s.IsFilled():
            return None, w
        return g.boundary, w
    return None, w


def shape_fill(s):
    """A filled silkscreen shape (a pin-1 mark) as its area, or None."""
    t = s.GetShape()
    if not s.IsFilled():
        return None
    if t == pcbnew.SHAPE_T_POLY:
        return polyset(s.GetPolyShape())
    if t == pcbnew.SHAPE_T_RECT:
        (x0, y0), (x1, y1) = pt(s.GetStart()), pt(s.GetEnd())
        return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
    if t == pcbnew.SHAPE_T_CIRCLE:
        return Point(pt(s.GetCenter())).buffer(mm(s.GetRadius()))
    return None


def text_geom(t):
    ps = pcbnew.SHAPE_POLY_SET()
    t.TransformTextToPolySet(ps, 0, 5000, pcbnew.ERROR_INSIDE)
    g = polyset(ps)
    if g is None or g.is_empty:
        bb = t.GetBoundingBox()
        g = box(mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
    return g


def courtyard(fp):
    gs = []
    for d in fp.GraphicalItems():
        if d.GetLayer() == F_CRT and isinstance(d, pcbnew.PCB_SHAPE):
            line, w = shape_path(d)
            if d.GetShape() == pcbnew.SHAPE_T_RECT:
                (x0, y0), (x1, y1) = pt(d.GetStart()), pt(d.GetEnd())
                gs.append(box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
            elif d.GetShape() == pcbnew.SHAPE_T_POLY:
                g = polyset(d.GetPolyShape())
                if g is not None:
                    gs.append(g)
            elif line is not None:
                gs.append(line)
    if not gs:
        return None
    polys = [g for g in gs if g.geom_type in ('Polygon', 'MultiPolygon')]
    lines = [g for g in gs if g.geom_type not in ('Polygon', 'MultiPolygon')]
    if lines:
        faces = list(polygonize(unary_union(lines)))
        polys += faces if faces else [unary_union(lines).convex_hull]
    return unary_union(polys)


class Board:
    def __init__(self, path, keepouts=()):
        self.path = path
        self.b = pcbnew.LoadBoard(path)
        self.fps = {fp.GetReference(): fp for fp in self.b.GetFootprints()}
        self.pads, self.padsilk = [], []
        for fp in self.b.GetFootprints():
            for p in fp.Pads():
                if p.IsOnLayer(pcbnew.F_SilkS):
                    self.padsilk.append((fp.GetReference(), p.GetNumber()))
                if not (p.IsOnLayer(pcbnew.F_Cu) or p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)):
                    continue
                g = polyset(p.GetEffectivePolygon(pcbnew.F_Cu) if p.IsOnLayer(pcbnew.F_Cu) else p.GetEffectivePolygon())
                if g is None:
                    g = Point(pt(p.GetPosition())).buffer(mm(p.GetDrillSizeX()) / 2)
                self.pads.append((fp.GetReference(), p.GetNumber(), g))
        self.crt = {r: courtyard(fp) for r, fp in self.fps.items()}
        self.pad_names = {r: {p.GetNumber() for p in fp.Pads()} for r, fp in self.fps.items()}
        self.pad_at = {(r, p.GetNumber()): Point(pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y))
                       for r, fp in self.fps.items() for p in fp.Pads()}
        for k, (x0, y0, x1, y1) in enumerate(keepouts):
            self.crt[f'keep-out {k + 1}'] = box(x0, y0, x1, y1)
        self.body = {r: (c.buffer(-BODY_SHRINK) if c is not None else None) for r, c in self.crt.items()}
        edges = [d for d in self.b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and isinstance(d, pcbnew.PCB_SHAPE)]
        lines = [shape_path(d)[0] for d in edges if shape_path(d)[0] is not None]
        outline = max(polygonize(unary_union(lines)), key=lambda g: g.area)
        self.inside = outline.buffer(-EDGE_GAP)
        self.pad_ko = unary_union([g for _, _, g in self.pads]).buffer(PAD_GAP)
        # a part's own body, for its own texts: the closed outline its silkscreen draws (a connector's courtyard also
        # takes in its pin field, where pin labels belong)
        self.own_body = {}
        for fp in self.b.GetFootprints():
            ls = [shape_path(d)[0] for d in fp.GraphicalItems()
                  if d.GetLayer() == F_SILK and isinstance(d, pcbnew.PCB_SHAPE) and shape_path(d)[0] is not None]
            faces = list(polygonize(unary_union(ls))) if ls else []
            self.own_body[fp.GetReference()] = unary_union(faces) if faces else None
        self.texts = []          # [owner ref or None, kind ('ref' | 'fptext' | 'board'), object, geometry]
        for fp in self.b.GetFootprints():
            r = fp.Reference()
            if r.IsVisible() and r.GetLayer() == F_SILK and r.GetShownText(False).strip():
                self.texts.append([fp.GetReference(), 'ref', r, text_geom(r)])
            for d in fp.GraphicalItems():
                if d.GetLayer() == F_SILK and isinstance(d, pcbnew.PCB_TEXT) and d.IsVisible():
                    self.texts.append([fp.GetReference(), 'fptext', d, text_geom(d)])
            for f in fp.GetFields():
                if f.GetLayer() == F_SILK and f.IsVisible() and not f.IsReference() and f.GetShownText(False).strip():
                    self.texts.append([fp.GetReference(), 'field', f, text_geom(f)])
        for d in self.b.GetDrawings():
            if d.GetLayer() == F_SILK and isinstance(d, pcbnew.PCB_TEXT):
                self.texts.append([None, 'board', d, text_geom(d)])
        self.shapes = []         # (owner ref or None, object, centre line, half width)
        self.fills = []          # (owner ref, object, area): filled marks, which can't be cut
        for fp in self.b.GetFootprints():
            for d in fp.GraphicalItems():
                if d.GetLayer() == F_SILK and isinstance(d, pcbnew.PCB_SHAPE):
                    line, w = shape_path(d)
                    self.shapes.append((fp.GetReference(), d, line, w))
                    f = shape_fill(d) if line is None else None
                    if f is not None and not f.is_empty:
                        self.fills.append([fp.GetReference(), d, f.buffer(w) if w else f])
        for d in self.b.GetDrawings():
            if d.GetLayer() == F_SILK and isinstance(d, pcbnew.PCB_SHAPE):
                line, w = shape_path(d)
                self.shapes.append((None, d, line, w))

    # ---- what a silkscreen text may not touch
    def text_conflicts(self, own, g, skip=None, own_courtyard=True):
        why = []
        label = skip[2].GetShownText(False) if skip is not None else ''
        if not self.inside.contains(g):
            why.append('board edge')
        if g.intersects(self.pad_ko):
            hit = [f'{r}.{n}' for r, n, pg in self.pads if pg.buffer(PAD_GAP).intersects(g)]
            why.append('pad ' + ','.join(hit[:3]))
        for r, c in self.crt.items():
            if r == own:
                if own_courtyard == 'body':
                    c = self.own_body.get(r)
                    # a pin label (named after one of its own pads) belongs by its pin; any other text of the part's
                    # is on the part when a real share of it lies inside the outline the part draws
                    if c is None or label in self.pad_names.get(r, ()) or g.intersection(c).area < 0.3 * g.area:
                        continue
                elif not own_courtyard:
                    continue
            if c is None or c.is_empty:
                continue
            if g.intersects(c) and g.intersection(c).area > 1e-4:
                why.append(('own courtyard' if r == own else 'courtyard ' + r))
        for t in self.texts:
            if t is skip or t[3] is None:
                continue
            gap = TEXT_GAP if (skip is not None and skip[1] == 'board' and t[1] == 'board') else READ_GAP
            if g.distance(t[3]) < gap:
                why.append('text ' + t[2].GetShownText(False)[:12])
        for r, d, line, w in self.shapes:
            if line is None:
                continue
            if line.buffer(w).distance(g) < TEXT_GAP and not self._cut_away(r, line, w, g):
                why.append('silk line of ' + (r or 'board'))
        for r, d, f in self.fills:
            if f is not None and f.distance(g) < TEXT_GAP:
                why.append('silk mark of ' + r)
        return why

    def fill_conflicts(self, own, f):
        """What a filled mark (it can't be cut) lies on: a pad, another part."""
        why = []
        if not hasattr(self, 'pad_mark_ko'):
            self.pad_mark_ko = unary_union([pg for _, _, pg in self.pads]).buffer(MARK_PAD_GAP)
        if f.intersection(self.pad_mark_ko).area > 1e-4:
            why.append('pad')
        for r, b in self.body.items():
            if r != own and b is not None and not b.is_empty and f.intersection(b).area > 1e-4:
                why.append('part ' + r)
        return why

    def _cut_away(self, own, line, w, g):
        """A line that will be cut where it meets this text anyway (step 3) is not a reason to move the text."""
        return True

    def candidates(self, ref, t):
        """Places round the part for its reference, nearest first."""
        fp = self.fps[ref]
        c = self.crt.get(ref)
        if c is None:
            c = Point(pt(fp.GetPosition())).buffer(0.5)
        x0, y0, x1, y1 = c.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        g0 = text_geom(t)
        gx0, gy0, gx1, gy1 = g0.bounds
        tw, th = gx1 - gx0, gy1 - gy0
        a0 = t.GetTextAngleDegrees() % 180
        out = []
        # small nudges from where the text is (first, for any text that is not a reference: a pin label or a hint
        # belongs where it was put), in the text's own angle
        mx, my = (gx0 + gx1) / 2, (gy0 + gy1) / 2
        nudge = -100 if t.GetClass() == 'PCB_TEXT' else 0
        for r in (0.2, 0.4, 0.6, 0.9, 1.2, 1.6, 2.0):
            for k in range(8):
                dx, dy = r * math.cos(k * math.pi / 4), r * math.sin(k * math.pi / 4)
                out.append((nudge + r + 0.01 * k, mx + dx, my + dy, a0))
        for ang in (a0, (a0 + 90) % 180):
            w, h = (tw, th) if ang == a0 else (th, tw)
            for d in (0.2, 0.45, 0.8, 1.3, 2.0):
                for name, (x, y) in (('above', (cx, y0 - d - h / 2)), ('below', (cx, y1 + d + h / 2)),
                                     ('left', (x0 - d - w / 2, cy)), ('right', (x1 + d + w / 2, cy))):
                    span = (x1 - x0) if name in ('above', 'below') else (y1 - y0)
                    n = max(2, min(30, int(span / max(0.5, (w if name in ('above', 'below') else h)))))
                    for s in sorted(range(-n, n + 1), key=abs):
                        step = (w if name in ('above', 'below') else h) * 0.5 * s
                        px, py = (x + step, y) if name in ('above', 'below') else (x, y + step)
                        out.append((math.hypot(px - cx, py - cy) + (0 if ang == a0 else 0.5) + abs(s) * 0.3, px, py, ang))
        out.sort()
        return out

    def place_text(self, t, x, y, ang):
        obj = t[2]
        g = text_geom(obj)
        gx0, gy0, gx1, gy1 = g.bounds
        dx, dy = x - (gx0 + gx1) / 2, y - (gy0 + gy1) / 2
        obj.SetTextAngleDegrees(ang)
        g = text_geom(obj)
        gx0, gy0, gx1, gy1 = g.bounds
        dx, dy = x - (gx0 + gx1) / 2, y - (gy0 + gy1) / 2
        p = obj.GetPosition()
        obj.SetPosition(pcbnew.VECTOR2I(p.x + pcbnew.FromMM(dx), p.y + pcbnew.FromMM(dy)))
        return text_geom(obj)


def clean(path, fab_refs, keepouts=()):
    B = Board(path, keepouts)
    moved, to_fab, board_moved, errors = {}, [], {}, []
    # 0. filled marks on a pad or another part go to F.Fab (they can't be cut)
    B.fills_to_fab = []
    for fl in B.fills:
        why = B.fill_conflicts(fl[0], fl[2])
        if why:
            B.fills_to_fab.append(fl[1])
            to_fab.append(((fl[0], 'mark', 'filled mark'), why[:2]))
            fl[2] = None
    # 1. references
    # references first, so a reference standing on a pin label moves rather than the label
    order = sorted([t for t in B.texts if t[1] in ('ref', 'fptext')], key=lambda t: (t[1] != 'ref', t[0]))
    for t in order:
        ref, obj = t[0], t[2]
        mode = True if t[1] == 'ref' else 'body'
        why = B.text_conflicts(ref, t[3], skip=t, own_courtyard=mode)
        if not why:
            continue
        p0, a0 = obj.GetPosition(), obj.GetTextAngleDegrees()
        done = False
        label = obj.GetShownText(False)
        pin = B.pad_at.get((ref, label)) if t[1] == 'fptext' else None
        for _, x, y, ang in B.candidates(ref, obj):
            if pin is not None and Point(x, y).distance(pin) > PIN_LABEL_REACH:
                continue      # a pin label stays by its pin
            g = B.place_text(t, x, y, ang)
            if not B.text_conflicts(ref, g, skip=t, own_courtyard=mode):
                t[3] = g
                moved[(ref, t[1], obj.GetShownText(False))] = obj
                done = True
                break
            obj.SetPosition(p0)
            obj.SetTextAngleDegrees(a0)
        if not done:
            obj.SetPosition(p0)
            obj.SetTextAngleDegrees(a0)
            to_fab.append(((ref, t[1], obj.GetShownText(False)), why[:2]))
            t[3] = None
    B.texts = [t for t in B.texts if t[3] is not None]
    # 2. board texts and footprint texts: small nudges only
    for t in [t for t in B.texts if t[1] in ('board', 'field')]:
        why = B.text_conflicts(t[0], t[3], skip=t, own_courtyard=False)
        why = [w for w in why if not w.startswith('silk line')]
        if not why:
            continue
        obj = t[2]
        if t[1] != 'board':
            errors.append(f'{t[1]} "{obj.GetShownText(False)}" of {t[0]}: {", ".join(why[:2])}')
            continue
        p0 = obj.GetPosition()
        best = None
        for r in (0.1, 0.2, 0.3, 0.5, 0.7, 1.0):
            for dx, dy in ((0, -r), (0, r), (-r, 0), (r, 0), (-r, -r), (r, -r), (-r, r), (r, r)):
                obj.SetPosition(pcbnew.VECTOR2I(p0.x + pcbnew.FromMM(dx), p0.y + pcbnew.FromMM(dy)))
                g = text_geom(obj)
                w2 = [w for w in B.text_conflicts(t[0], g, skip=t, own_courtyard=False) if not w.startswith('silk line')]
                if not w2:
                    best = g
                    break
            if best is not None:
                break
        if best is None:
            obj.SetPosition(p0)
            errors.append(f'{t[1]} "{obj.GetShownText(False)}" at {pt(p0)}: {", ".join(why[:2])}')
        else:
            t[3] = best
            board_moved[id(obj)] = (t, p0)
    # 3. lines
    text_ko = unary_union([t[3] for t in B.texts]).buffer(TEXT_GAP) if B.texts else None
    cuts = {}
    kept = {}                    # owner -> silk already kept (lines and marks), which other parts' lines must clear
    for r, d, f in B.fills:
        if f is not None:
            kept.setdefault(r, []).append(f)
    # the longest lines first: a part's outline keeps priority over a short tick that meets it
    for own, d, line, w in sorted(B.shapes, key=lambda s: -(s[2].length if s[2] is not None else 0)):
        if line is None:
            continue
        ko = [B.pad_ko.buffer(w)]
        ko += [b.buffer(w) for r, b in B.body.items() if r != own and b is not None and not b.is_empty]
        ko += [g.buffer(w + LINE_GAP) for r, gs in kept.items() if r != own for g in gs]
        if text_ko is not None:
            ko.append(text_ko.buffer(w))
        ko = unary_union(ko)
        keep = line.intersection(B.inside.buffer(-w))
        keep = keep.difference(ko)
        kept.setdefault(own, []).append(keep.buffer(w) if not keep.is_empty else keep)
        if keep.equals(line) or (abs(keep.length - line.length) < 1e-3 and keep.geom_type == 'LineString'):
            continue
        pieces = [g for g in getattr(keep, 'geoms', [keep]) if g.geom_type == 'LineString' and g.length >= MIN_PIECE]
        segs = []
        for g in pieces:
            cs = list(g.coords)
            segs += [(cs[i], cs[i + 1]) for i in range(len(cs) - 1) if math.dist(cs[i], cs[i + 1]) > 1e-3]
        cuts[id(d)] = (own, d, segs, w)
    return B, moved, to_fab, board_moved, cuts, errors


# ---- writing the KiCad 7 text
def fmt(v):
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def blocks(t, kind):
    """(start, end) of every top-level (kind ...) block."""
    out, i = [], 0
    pat = '\n  (' + kind + ' '
    while True:
        i = t.find(pat, i)
        if i < 0:
            return out
        j, depth = i + 3, 0
        while True:
            c = t[j]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            elif c == '"':
                j = t.index('"', j + 1)
            j += 1
        out.append((i + 1, j + 1))
        i = j


def fp_frame(fp):
    p, a = fp.GetPosition(), math.radians(fp.GetOrientationDegrees())
    return mm(p.x), mm(p.y), a


def to_local(fp, x, y):
    fx, fy, a = fp_frame(fp)
    dx, dy = x - fx, y - fy
    return dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)


def write(src, dst, B, moved, to_fab, board_moved, cuts):
    t = open(src).read()
    by_ref = {}
    for a, b in blocks(t, 'footprint'):
        m = re.search(r'\(fp_text reference "([^"]+)"', t[a:b])
        if m:
            by_ref[m[1]] = (a, b)
    edits = []          # (start, end, new text)
    fab = {k for k, _ in to_fab if k[1] != 'mark'}
    # filled marks to F.Fab: the fp_poly whose first point is the mark's
    for d in getattr(B, 'fills_to_fab', []):
        fp = d.GetParentFootprint()
        ref = fp.GetReference()
        assert d.GetShape() == pcbnew.SHAPE_T_POLY, f'filled {d.GetShapeStr()} of {ref}: only polygons are handled'
        x, y = to_local(fp, *pt(d.GetPolyShape().Outline(0).CPoint(0)))
        a, b = by_ref[ref]
        for m in re.finditer(r'\(fp_poly\s*\(pts\s*\(xy ([-\d.]+) ([-\d.]+)\)', t[a:b]):
            if abs(float(m[1]) - x) < 2e-3 and abs(float(m[2]) - y) < 2e-3:
                s0 = a + m.start()
                depth, j = 0, s0
                while True:
                    if t[j] == '(':
                        depth += 1
                    elif t[j] == ')':
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                blk = t[s0:j + 1]
                assert blk.count('(layer "F.SilkS")') == 1
                edits.append((s0, j + 1, blk.replace('(layer "F.SilkS")', '(layer "F.Fab")')))
                break
        else:
            raise SystemExit(f'filled mark of {ref} at {x:.3f},{y:.3f} not found in the file')
    for key in set(moved) | fab:
        ref, kind, txt = key
        a, b = by_ref[ref]
        blk = t[a:b]
        head = f'(fp_text reference "{ref}"' if kind == 'ref' else f'(fp_text user "{txt}"'
        m = re.search(re.escape(head) + r' \(at [^)]*\) \(layer "F\.SilkS"\)', blk)
        assert m, key
        if key in fab:
            new = m[0].replace('(layer "F.SilkS")', '(layer "F.Fab")')
        else:
            obj = moved[key]
            rel = obj.GetFPRelativePosition()
            ang = obj.GetTextAngleDegrees()
            new = (f'{head} (at {fmt(mm(rel.x))} {fmt(mm(rel.y))}'
                   f'{" " + fmt(ang) if abs(ang) > 1e-6 else ""}) (layer "F.SilkS")')
        edits.append((a + m.start(), a + m.end(), new))
    # board texts nudged
    for t_, p0 in board_moved.values():
        obj = t_[2]
        if t_[1] != 'board':
            continue
        s = re.escape(obj.GetShownText(False))
        x0, y0 = pt(p0)
        for m in re.finditer(r'\(gr_text "%s" \(at ([-\d.]+) ([-\d.]+)' % s, t):
            if abs(float(m[1]) - x0) < 2e-3 and abs(float(m[2]) - y0) < 2e-3:
                p = pt(obj.GetPosition())
                edits.append((m.start(), m.end(), f'(gr_text "{obj.GetShownText(False)}" (at {fmt(p[0])} {fmt(p[1])}'))
                break
        else:
            raise SystemExit(f'board text "{obj.GetShownText(False)}" at {x0},{y0} not found in the file')
    # lines
    for own, d, segs, w in cuts.values():
        (sx, sy), (ex, ey) = pt(d.GetStart()), pt(d.GetEnd())
        width = fmt(2 * w)
        if own is None:
            kind, loc = 'gr', lambda x, y: (x, y)
            area = (0, len(t))
        else:
            fp = B.fps[own]
            kind, loc = 'fp', lambda x, y, fp=fp: to_local(fp, x, y)
            area = by_ref[own]
        shp = d.GetShape()
        found = None
        if shp == pcbnew.SHAPE_T_SEGMENT:
            ls, le = loc(sx, sy), loc(ex, ey)
            for m in re.finditer(r'\n *\(%s_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\)' % kind,
                                 t[area[0]:area[1]]):
                v = [float(m[i]) for i in range(1, 5)]
                if (all(abs(p - q) < 2e-3 for p, q in zip(v, ls + le)) or
                        all(abs(p - q) < 2e-3 for p, q in zip(v, le + ls))):
                    s0 = area[0] + m.start()
                    e0 = t.index('\n', s0 + 1)
                    # the line's own block ends at the matching parenthesis
                    depth, j = 0, t.index('(', s0)
                    while True:
                        if t[j] == '(':
                            depth += 1
                        elif t[j] == ')':
                            depth -= 1
                            if depth == 0:
                                break
                        j += 1
                    found = (s0, j + 1)
                    break
        else:
            kw = {pcbnew.SHAPE_T_ARC: 'arc', pcbnew.SHAPE_T_CIRCLE: 'circle', pcbnew.SHAPE_T_RECT: 'rect',
                  pcbnew.SHAPE_T_POLY: 'poly'}[shp]
            if shp in (pcbnew.SHAPE_T_ARC, pcbnew.SHAPE_T_CIRCLE, pcbnew.SHAPE_T_RECT):
                ref_pt = loc(*pt(d.GetStart())) if shp != pcbnew.SHAPE_T_CIRCLE else loc(*pt(d.GetCenter()))
                for m in re.finditer(r'\n *\(%s_%s \((?:start|center) ([-\d.]+) ([-\d.]+)\)' % (kind, kw), t[area[0]:area[1]]):
                    if abs(float(m[1]) - ref_pt[0]) < 2e-3 and abs(float(m[2]) - ref_pt[1]) < 2e-3:
                        s0 = area[0] + m.start()
                        depth, j = 0, t.index('(', s0)
                        while True:
                            if t[j] == '(':
                                depth += 1
                            elif t[j] == ')':
                                depth -= 1
                                if depth == 0:
                                    break
                            j += 1
                        found = (s0, j + 1)
                        break
        if found is None:
            raise SystemExit(f'silk {kind}_{shp} of {own or "board"} at {sx:.3f},{sy:.3f} not found in the file')
        indent = '\n    ' if kind == 'fp' else '\n  '
        new = ''.join(f'{indent}({kind}_line (start {fmt(loc(*p)[0])} {fmt(loc(*p)[1])}) (end {fmt(loc(*q)[0])} '
                      f'{fmt(loc(*q)[1])})\n{indent[1:]}  (stroke (width {width}) (type solid)) (layer "F.SilkS") '
                      f'(tstamp {uuid.uuid4()}))' for p, q in segs)
        edits.append((found[0], found[1], new))
    # pads that print on the silkscreen
    n_padsilk = 0
    for a, b in by_ref.values():
        blk = t[a:b]
        for m in re.finditer(r'\(layers "\*\.Cu" "\*\.Mask" "F\.SilkS"\)', blk):
            edits.append((a + m.start(), a + m.end(), '(layers "*.Cu" "*.Mask")'))
            n_padsilk += 1
    edits.sort()
    for (s0, e0, _), (s1, _, _) in zip(edits, edits[1:]):
        assert e0 <= s1, 'overlapping edits'
    for s0, e0, new in reversed(edits):
        t = t[:s0] + new + t[e0:]
    open(dst, 'w').write(t)
    return n_padsilk


def check(path, keepouts=()):
    B = Board(path, keepouts)
    bad = []
    for t in B.texts:
        why = B.text_conflicts(t[0], t[3], skip=t, own_courtyard={'ref': True, 'fptext': 'body'}.get(t[1], False))
        why = [w for w in why if not w.startswith('silk line')]
        if why:
            bad.append(f'{t[1]} "{t[2].GetShownText(False)}" ({t[0] or "board"}): {", ".join(why[:3])}')
    text_ko = unary_union([t[3] for t in B.texts]) if B.texts else None
    for own, d, f in B.fills:
        why = B.fill_conflicts(own, f)
        if why:
            bad.append(f'filled mark of {own}: {", ".join(why[:3])}')
    silk_by = {}
    for own, d, line, w in B.shapes:
        if line is not None:
            silk_by.setdefault(own, []).append(line.buffer(w))
    for own, d, f in B.fills:
        silk_by.setdefault(own, []).append(f)
    silk_by = {r: unary_union(gs) for r, gs in silk_by.items()}
    for own, d, line, w in B.shapes:
        if line is None:
            continue
        g = line.buffer(w)
        why = [f'silk of {r}' for r, o in silk_by.items() if r != own and g.distance(o) < LINE_GAP - 0.02]
        if not B.inside.buffer(1e-3).contains(g):
            why.append('board edge')
        if g.distance(B.pad_ko) < -1e-6 or g.intersection(B.pad_ko).area > 1e-4:
            why.append('pad')
        for r, b in B.body.items():
            if r != own and b is not None and not b.is_empty and g.intersection(b).area > 1e-4:
                why.append('part ' + r)
        if text_ko is not None and g.intersection(text_ko.buffer(TEXT_GAP - 0.02)).area > 1e-4:
            why.append('text')
        if why:
            bad.append(f'line of {own or "board"} at {pt(d.GetStart())}: {", ".join(why[:3])}')
    for r, n in B.padsilk:
        bad.append(f'pad {r}.{n} carries F.SilkS')
    for line in bad:
        print('  silk:', line)
    print(f'silk_clean --check {path.split("/")[-1]}: {len(bad)} silkscreen items on a pad, a part, another item or the edge')
    return len(bad)


if __name__ == '__main__':
    KO = [tuple(float(v) for v in sys.argv[i + 1].split(',')) for i, a in enumerate(sys.argv) if a == '--keepout']
    if '--check' in sys.argv:
        sys.exit(1 if check(sys.argv[1], KO) else 0)
    src, dst = sys.argv[1], sys.argv[2]
    B, moved, to_fab, board_moved, cuts, errors = clean(src, '--fab-refs' in sys.argv, KO)
    n = write(src, dst, B, moved, to_fab, board_moved, cuts)
    print(f'silk_clean: {len(moved)} references moved, {len(to_fab)} to F.Fab, '
          f'{sum(1 for v in board_moved.values() if v[0][1] == "board")} board texts nudged, {len(cuts)} silk lines cut, '
          f'{n} pads lose F.SilkS')
    if to_fab and '--fab-refs' not in sys.argv:
        for r, why in to_fab:
            print(f'  {r[0]} {r[1]} "{r[2]}" to F.Fab: {", ".join(why)}')
    for e in errors:
        print('  NOT FIXED:', e)
    sys.exit(1 if errors else 0)
