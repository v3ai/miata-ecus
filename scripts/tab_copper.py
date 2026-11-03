"""Rev 0.7: heat-spreading copper for the injector drivers Q1-Q4 (NCV8406A, SOT-223).

On 1989-93 cars each harness injector wire is driven by two of these in parallel, and at high duty a driver with
only its own tab pad (about 20 mm^2) runs hot: about 142 C junction at 90 % duty and 60 C ambient, and thermal
shutdown at 85 C (firmware/tools/circuit_sim_full.py). The drain tab is the output net, so the spreading copper
is that net: a zone of OUT_INJn around the tab on the top and bottom layers, above the ground pour in priority,
from the header row down to the driver's pins, joined by a field of thermal vias. Other nets' copper inside the
area keeps its clearance (the zone fills around it), and the vias are only placed where they clear everything.

Used by daughter_finish.py after routing: add(board) returns the copper area added per driver.
"""
import math
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

OX, OY = 100.0, 50.0
DRIVERS = {'Q1': 'OUT_INJ1', 'Q2': 'OUT_INJ2', 'Q3': 'OUT_INJ3', 'Q4': 'OUT_INJ4'}
HALF_W = 3.4            # zone half width (drivers are 7.62 mm apart)
Y_TOP, Y_BOT = 4.0, 11.2  # below the J1 header pads, above the driver's three pins
VIA_D, VIA_DRILL, VIA_PITCH, CLEAR = 0.6, 0.3, 1.0, 0.2


def _zone(board, net, layer, x0, y0, x1, y1):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        ol.Append(FromMM(x + OX), FromMM(y + OY))
    z.SetAssignedPriority(1)                    # above the board-wide GND pours (priority 0)
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


def _clear(board, x, y, netcode):
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
            bb = p.GetBoundingBox()
            dx = max(ToMM(bb.GetLeft()) - X, 0, X - ToMM(bb.GetRight()))
            dy = max(ToMM(bb.GetTop()) - Y, 0, Y - ToMM(bb.GetBottom()))
            if math.hypot(dx, dy) < r + (0.1 if p.GetNetCode() == netcode else 0.0):
                return False
    return True


def add(board):
    nets = board.GetNetsByName()
    out = {}
    for ref, nn in DRIVERS.items():
        fp = board.FindFootprintByReference(ref)
        cx = ToMM(fp.GetPosition().x) - OX
        net = nets[nn]
        x0, x1 = cx - HALF_W, cx + HALF_W
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            _zone(board, net, layer, x0, Y_TOP, x1, Y_BOT)
        n = 0
        y = Y_TOP + 0.6
        while y <= Y_BOT - 0.6:
            x = x0 + 0.6
            while x <= x1 - 0.6:
                if _clear(board, x, y, net.GetNetCode()):
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
    """filled copper area of each driver's output net on F.Cu and B.Cu (mm^2), after a zone fill"""
    res = {}
    for ref, nn in DRIVERS.items():
        a = 0.0
        for z in board.Zones():
            if z.GetNetname() == nn and z.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu):
                a += z.GetFilledArea() / 1e12
        res[ref] = round(a, 1)
    return res
