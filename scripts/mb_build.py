"""Build a motherboard .kicad_pcb (outline, holes, footprints, nets, placement).
usage: mb_build.py <year module, e.g. mb_na6> <out.kicad_pcb>"""
import sys, os, importlib, math
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
sys.path.insert(0, os.path.dirname(__file__))
import mb_common as C

OX, OY = 100.0, 50.0
FPROOT = '/usr/share/kicad/footprints/'


def P(x, y):
    return VECTOR2I(FromMM(OX + x), FromMM(OY + y))


def edge(board, kind, a, b, c=None):
    s = pcbnew.PCB_SHAPE(board)
    if kind == 'L':
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(P(*a)); s.SetEnd(P(*b))
    else:
        r = math.dist(a, c)
        a0 = math.atan2(a[1] - c[1], a[0] - c[0]); a1 = math.atan2(b[1] - c[1], b[0] - c[0])
        d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi          # short way round (90 deg arcs)
        am = a0 + d / 2
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetArcGeometry(P(*a), P(c[0] + r * math.cos(am), c[1] + r * math.sin(am)), P(*b))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1))
    board.Add(s)


def outline_polygon(outline, n=8):
    pts = []
    for seg in outline:
        if seg[0] == 'L':
            pts.append(seg[1])
        else:
            a, b, c = seg[1], seg[2], seg[3]
            r = math.dist(a, c)
            a0 = math.atan2(a[1] - c[1], a[0] - c[0]); a1 = math.atan2(b[1] - c[1], b[0] - c[0])
            d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
            for k in range(n):
                t = a0 + d * k / n
                pts.append((c[0] + r * math.cos(t), c[1] + r * math.sin(t)))
    return pts


def load_fp(spec):
    lib, name = spec.split(':')
    path = C.MBLIB if lib == 'ecu_mb' else FPROOT + lib + '.pretty'
    fp = pcbnew.FootprintLoad(path, name)
    assert fp is not None, spec
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def build(modname, out):
    M = importlib.import_module(modname)
    parts = M.build_parts()
    place = M.placement()
    board = pcbnew.NewBoard(out)
    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(2); board.SetCopperLayerCount(2)
    nc = ds.m_NetSettings.m_DefaultNetClass
    nc.SetClearance(FromMM(0.2)); nc.SetTrackWidth(FromMM(0.25))
    nc.SetViaDiameter(FromMM(0.7)); nc.SetViaDrill(FromMM(0.35))
    ds.m_TrackMinWidth = FromMM(0.2); ds.m_ViasMinSize = FromMM(0.6); ds.m_MinThroughDrill = FromMM(0.3)
    ds.m_CopperEdgeClearance = FromMM(0.4); ds.m_HoleToHoleMin = FromMM(0.25); ds.m_HoleClearance = FromMM(0.25)
    for seg in M.OUTLINE:
        edge(board, *seg)
    nets = {}
    for n in C.nets():
        ni = pcbnew.NETINFO_ITEM(board, n); board.Add(ni); nets[n] = ni
    for part in parts:
        fp = load_fp(part['fp'])
        fp.SetReference(part['ref']); fp.SetValue(part['value'])
        if part['lcsc']:
            fp.SetField('LCSC', part['lcsc']) if hasattr(fp, 'SetField') else fp.SetProperty('LCSC', part['lcsc'])
        for pad in fp.Pads():
            num = pad.GetNumber()
            n = part['pads'].get(num) if num else part['pads'].get('SHELL')
            if n:
                pad.SetNet(nets[n])
            elif num and num not in part['pads'] and part['pads']:
                # unlisted numbered pads (e.g. header plug-2 pins we leave open) stay unconnected
                pass
        pl = place[part['ref']]
        if pl[0] == 'centre':           # (centre, cx, cy, rot): place by courtyard centre
            _, cx, cy, rot = pl
            fp.SetOrientationDegrees(rot); fp.SetPosition(P(0, 0))
            bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox() if fp.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else fp.GetBoundingBox(False, False)
            ox, oy = ToMM(bb.Centre().x) - OX, ToMM(bb.Centre().y) - OY
            x, y = cx - ox, cy - oy
        else:
            x, y, rot = pl
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(P(x, y))
        if part.get('side') == 'B':
            fp.Flip(fp.GetPosition(), False)
        ref = fp.Reference()
        ref.SetTextSize(VECTOR2I(FromMM(1.0), FromMM(1.0))); ref.SetTextThickness(FromMM(0.15))
        fp.Value().SetVisible(False)
        board.Add(fp)
    # assembly outlines for the boards that plug in
    def rect(x, y, w, h, label):
        for a, c in (((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)), ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))):
            s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(P(*a)); s.SetEnd(P(*c)); s.SetLayer(pcbnew.F_SilkS); s.SetWidth(FromMM(0.15))
            board.Add(s)
        t = pcbnew.PCB_TEXT(board); t.SetText(label); t.SetLayer(pcbnew.F_SilkS)
        t.SetPosition(P(x + w / 2, y + h / 2)); t.SetTextSize(VECTOR2I(FromMM(1.5), FromMM(1.5)))
        t.SetTextThickness(FromMM(0.2)); board.Add(t)
    rect(*M.DAUGHTER, 125.0, 60.0, 'DAUGHTERBOARD')
    t = pcbnew.PCB_TEXT(board); t.SetText(M.TITLE + '  rev ' + os.environ.get('MBREV', '0.3')); t.SetLayer(pcbnew.F_SilkS)
    t.SetPosition(P(M.W / 2, M.DAUGHTER[1] + 81.0)); t.SetTextSize(VECTOR2I(FromMM(1.6), FromMM(1.6))); t.SetTextThickness(FromMM(0.22))
    board.Add(t)
    # sanity: daughter sockets must sit exactly under the daughter's header pins
    import design as daughter
    dx, dy = M.DAUGHTER
    for ref, yy in (('JD1', 2.75), ('JD2', 57.25)):
        fp = board.FindFootprintByReference(ref)
        for pad in fp.Pads():
            k = int(pad.GetNumber())
            ex, ey = dx + 13.0 + (k - 1) * 2.54, dy + yy
            gx, gy = ToMM(pad.GetPosition().x) - OX, ToMM(pad.GetPosition().y) - OY
            assert abs(gx - ex) < 0.01 and abs(gy - ey) < 0.01, (ref, k, gx, gy, ex, ey)
    board.Save(out)
    print('built', out, len(parts), 'parts', len(nets), 'nets')
    return board


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
