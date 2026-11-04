"""Heat-spreading copper for the eight low-side drivers Q1-Q8 (ST VND7NV04, DPAK; rev 0.8 on a strip above J1, since rev
0.9 on the strip just below it, tab up).

Each driver's drain tab is its output net, so the spreading copper is that net: a column of OUT_x copper as wide as
the driver pitch allows (6.9 mm of the 7.62 mm pitch, leaving the gap the driver's input line climbs through), from
the strip's top edge down onto the driver's own J1 pad, on F.Cu, B.Cu and In2.Cu (the +3V3 plane layer: the strip
has no 3.3 V parts, and the drain islands take priority over the plane there). A field of thermal vias joins the
three layers under and around the tab, including vias in the tab pad itself (order the board with the vias plugged /
filled, or accept a little solder wicking into the 0.3 mm holes). Other nets' copper inside a column keeps its clearance (the zone fills
around it), and vias are only placed where they clear everything.

(Rev 0.7 had F.Cu/B.Cu zones for the four injector drivers only, on SOT-223 parts below J1.)

Used by daughter_finish.py after routing: add(board) returns the number of thermal vias per driver, area(board) the
filled drain copper per driver and layer.
"""
import math
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

OX, OY = 100.0, 50.0
DRIVERS = {'Q1': 'OUT_INJ1', 'Q2': 'OUT_INJ2', 'Q3': 'OUT_INJ3', 'Q4': 'OUT_INJ4',
           'Q5': 'OUT_IACV', 'Q6': 'OUT_VVT', 'Q7': 'OUT_BOOST', 'Q8': 'OUT_ALT'}
HALF_W = 3.45               # column half width (drivers are 7.62 mm apart; the IN line climbs the 0.72 mm gap)
Y_TOP = 0.6                 # board edge clearance
LAYERS = (pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu)
VIA_D, VIA_DRILL, VIA_PITCH, CLEAR = 0.6, 0.3, 1.0, 0.2


def _j1_pad(board, net):
    j1 = board.FindFootprintByReference('J1')
    p = next(p for p in j1.Pads() if p.GetNetname() == net)
    return ToMM(p.GetPosition().x) - OX, ToMM(p.GetPosition().y) - OY


def _zone(board, net, layer, x0, y0, x1, y1):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        ol.Append(FromMM(x + OX), FromMM(y + OY))
    z.SetAssignedPriority(1)                    # above the board-wide GND pours and the +3V3 plane (priority 0)
    z.SetLocalClearance(FromMM(0.25))
    z.SetMinThickness(FromMM(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(z)
    return z


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _clear(board, x, y, netcode, own=None, own_ref=None):
    """True if a via at board-mm (x, y) clears every other net's copper on F/B and every hole"""
    r = VIA_D / 2 + CLEAR
    X, Y = x + OX, y + OY
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            d = math.hypot(ToMM(t.GetPosition().x) - X, ToMM(t.GetPosition().y) - Y)
            if t.GetNetCode() != netcode and d < r + ToMM(t.GetWidth()) / 2:
                return False
            if t.GetNetCode() == netcode and d < VIA_PITCH * 0.9:
                return False
        elif t.GetNetCode() != netcode:
            d = _seg_dist(X, Y, ToMM(t.GetStart().x), ToMM(t.GetStart().y), ToMM(t.GetEnd().x), ToMM(t.GetEnd().y))
            if d < r + ToMM(t.GetWidth()) / 2:
                return False
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if own is not None and p.GetNetCode() == netcode and fp.GetReference() == own_ref:
                continue                    # vias in the driver's own tab pad are wanted (thermal via-in-pad)
            bb = p.GetBoundingBox()
            dx = max(ToMM(bb.GetLeft()) - X, 0, X - ToMM(bb.GetRight()))
            dy = max(ToMM(bb.GetTop()) - Y, 0, Y - ToMM(bb.GetBottom()))
            if math.hypot(dx, dy) < r + (0.1 if p.GetNetCode() == netcode else 0.0):
                return False
    return True


def _tab(fp):
    return next(p for p in fp.Pads() if p.GetNumber() == '2' and p.GetSize().x > FromMM(5))


def columns(board):
    """(ref, net, x0, y0, x1, y1) of each driver's copper column, board mm: from the J1 pad to the tab side of the
    driver. Rev 0.8 had the drivers above J1 (column from the board edge down to the pad); since rev 0.9 they stand
    below it (column from just above the pad down to the bottom of the tab)."""
    out = []
    for ref, nn in DRIVERS.items():
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            continue
        cx = ToMM(fp.GetPosition().x) - OX
        _, jy = _j1_pad(board, nn)
        tb = _tab(fp).GetBoundingBox()
        t0, t1 = ToMM(tb.GetTop()) - OY, ToMM(tb.GetBottom()) - OY
        if t1 < jy:                                   # driver above J1 (rev 0.8)
            out.append((ref, nn, cx - HALF_W, Y_TOP, cx + HALF_W, jy + 0.5))
        else:                                         # driver below J1 (rev 0.9): board edge down past the leads
            # (the fill keeps its clearance around the input and source leads and their tracks)
            lead_bottom = max(ToMM(p.GetBoundingBox().GetBottom()) - OY for p in fp.Pads() if p.GetNumber() != '2')
            out.append((ref, nn, cx - HALF_W, Y_TOP, cx + HALF_W, max(t1 + 0.6, lead_bottom + 0.3)))
    return out


def add(board):
    out = {}
    for ref, nn, x0, y0, x1, y1 in columns(board):
        net = board.FindNet(nn)        # (GetNetsByName() can come back as a bare SWIG object after items are removed)
        for layer in LAYERS:
            _zone(board, net, layer, x0, y0, x1, y1)
        # thermal vias over the tab and the copper below it (not in the lead area at the top of the column)
        fp = board.FindFootprintByReference(ref)
        tab = _tab(fp)
        tby0, tby1 = ToMM(tab.GetBoundingBox().GetTop()) - OY, ToMM(tab.GetBoundingBox().GetBottom()) - OY
        if tby1 < y1 - 1.0:                           # rev 0.8: tab and the copper below it, down to J1
            ty0, ty1 = tby0 - 0.6, y1 - 1.2
        else:                                         # rev 0.9: J1 down to the bottom of the tab
            ty0, ty1 = y0 + 0.6, tby1 - 0.4
        n = 0
        y = ty0
        while y <= ty1:
            x = x0 + 0.6
            while x <= x1 - 0.6:
                tb = tab.GetBoundingBox()
                in_tab = (ToMM(tb.GetLeft()) - OX + 0.6 <= x <= ToMM(tb.GetRight()) - OX - 0.6 and
                          ToMM(tb.GetTop()) - OY + 0.6 <= y <= ToMM(tb.GetBottom()) - OY - 0.6)
                near_tab = (ToMM(tb.GetLeft()) - OX - 0.2 <= x <= ToMM(tb.GetRight()) - OX + 0.2 and
                            ToMM(tb.GetTop()) - OY - 0.2 <= y <= ToMM(tb.GetBottom()) - OY + 0.2)
                if (in_tab or not near_tab) and _clear(board, x, y, net.GetNetCode(), tab if in_tab else None, ref):
                    v = pcbnew.PCB_VIA(board)
                    v.SetPosition(VECTOR2I(FromMM(x + OX), FromMM(y + OY)))
                    v.SetWidth(FromMM(VIA_D)); v.SetDrill(FromMM(VIA_DRILL))
                    v.SetNet(net)
                    board.Add(v)
                    n += 1
                x += VIA_PITCH
            y += VIA_PITCH
        out[ref] = n
    return out


def area(board):
    """filled drain copper of each driver per layer (mm^2), after a zone fill"""
    res = {}
    names = {pcbnew.F_Cu: 'F', pcbnew.In2_Cu: 'In2', pcbnew.B_Cu: 'B'}
    for ref, nn in DRIVERS.items():
        a = {}
        for z in board.Zones():
            if z.GetNetname() == nn and z.GetLayer() in names:
                a[names[z.GetLayer()]] = round(a.get(names[z.GetLayer()], 0) + z.GetFilledArea() / 1e12, 1)
        res[ref] = a
    return res
