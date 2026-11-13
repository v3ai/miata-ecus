"""Heat-spreading copper for the injector clamp TVSs D46-D49 (daughterboard rev 0.10, SMCJ14A, SMC package).

Each TVS takes the turn-off energy of one injector: 0.2-0.5 W at 7200 rpm sequential, up to about 1 W in batch mode
with 20 mH injectors (firmware/tools/sim_inj_clamp.py). On its bare pads an SMC part is about 75 C/W junction to
ambient. After routing, each TVS gets copper on every signal layer under its own column (the part stands upright
under its injector driver, 7.62 mm from its neighbours):
  - around the battery-side pad (pad 2, VBAT_IN): the upper half of the column;
  - around the clamp-node pad (pad 1, INJn_CL): the lower half, down past the clamp diode;
joined through the board by vias in and beside the pads (JLCPCB fills and caps vias in pads on six-layer boards).
Other nets' copper keeps its clearance (the zones fill around it) and vias go only where they clear everything on
every layer. The zones are named clamp_<ref>_A / _K so area() can find them again.

Used by daughter_finish.py after routing. add(board) returns the vias placed per TVS; area(board) the filled copper
per TVS and layer and the effective area the thermal estimate uses (top copper plus half of the other layers).
"""
import math
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

OX, OY = 100.0, 50.0
CLAMPS = ('D46', 'D47', 'D48', 'D49')
DIODE = {'D46': 'D42', 'D47': 'D43', 'D48': 'D44', 'D49': 'D45'}
HALF_W = 3.35
VIA_D, VIA_DRILL, VIA_PITCH, CLEAR = 0.6, 0.3, 1.2, 0.22


def _layers(board):
    n = board.GetCopperLayerCount()
    inner = [pcbnew.In2_Cu, pcbnew.In3_Cu] if n == 6 else []
    return [pcbnew.F_Cu] + inner + [pcbnew.B_Cu]


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _clear(board, x, y, netcode, own_pad):
    """True if a via at sheet-mm (x, y) clears every other net's copper on every layer and every hole. A via inside
    own_pad (a pad of its own net) is wanted; one that only clips a pad edge is not."""
    r = VIA_D / 2 + CLEAR
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            d = math.hypot(ToMM(t.GetPosition().x) - x, ToMM(t.GetPosition().y) - y)
            if d < r + ToMM(t.GetWidth()) / 2 or (t.GetNetCode() == netcode and d < VIA_PITCH * 0.9):
                return False
        elif t.GetNetCode() != netcode:
            if _seg_dist(x, y, ToMM(t.GetStart().x), ToMM(t.GetStart().y), ToMM(t.GetEnd().x),
                         ToMM(t.GetEnd().y)) < r + ToMM(t.GetWidth()) / 2:
                return False
    for fp in board.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            l, t_, r_, b_ = ToMM(bb.GetLeft()), ToMM(bb.GetTop()), ToMM(bb.GetRight()), ToMM(bb.GetBottom())
            if p is own_pad or (own_pad is not None and p.GetPosition() == own_pad.GetPosition() and p.GetNetCode() == netcode):
                if l + 0.5 <= x <= r_ - 0.5 and t_ + 0.5 <= y <= b_ - 0.5:
                    continue                      # well inside its own pad
                if math.hypot(max(l - x, 0, x - r_), max(t_ - y, 0, y - b_)) < VIA_D / 2 + 0.1:
                    return False                  # straddling the pad edge
                continue
            hole = p.GetDrillSize().x > 0
            if math.hypot(max(l - x, 0, x - r_), max(t_ - y, 0, y - b_)) < r + (0.3 if hole else 0.0):
                return False
    return True


def _zone(board, net, layer, x0, y0, x1, y1, name):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetZoneName(name)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        ol.Append(FromMM(x), FromMM(y))
    z.SetAssignedPriority(1)                    # above the board-wide pours and planes
    z.SetLocalClearance(FromMM(0.25))
    z.SetMinThickness(FromMM(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(z)


def add(board):
    out = {}
    for ref in CLAMPS:
        fp = board.FindFootprintByReference(ref)
        dio = board.FindFootprintByReference(DIODE[ref])
        if fp is None or dio is None:
            continue
        pads = {p.GetNumber(): p for p in fp.Pads()}
        k, a = pads['1'], pads['2']                       # cathode (INJn_CL), anode (VBAT_IN)
        cx = ToMM(fp.GetPosition().x)
        ky, ay = ToMM(k.GetPosition().y), ToMM(a.GetPosition().y)
        assert abs(ToMM(k.GetPosition().x) - cx) < 0.01 and ay < ky, f'{ref}: expected upright, battery pad on top'
        mid = (ky + ay) / 2
        dbb = dio.GetBoundingBox(False, False)
        rects = {'A': (cx - HALF_W, ToMM(a.GetBoundingBox().GetTop()) - 0.9, cx + HALF_W, mid - 0.3),
                 'K': (cx - HALF_W, mid + 0.3, cx + HALF_W, ToMM(dbb.GetBottom()) + 0.2)}
        n = 0
        for side, pad in (('A', a), ('K', k)):
            x0, y0, x1, y1 = rects[side]
            net = pad.GetNet()
            for layer in _layers(board):
                _zone(board, net, layer, x0, y0, x1, y1, f'clamp_{ref}_{side}')
            y = y0 + 0.6
            while y <= y1 - 0.6 + 1e-6:
                x = x0 + 0.6
                while x <= x1 - 0.6 + 1e-6:
                    if _clear(board, x, y, net.GetNetCode(), pad):
                        v = pcbnew.PCB_VIA(board)
                        v.SetPosition(VECTOR2I(FromMM(x), FromMM(y)))
                        v.SetWidth(FromMM(VIA_D)); v.SetDrill(FromMM(VIA_DRILL))
                        v.SetNet(net)
                        board.Add(v)
                        n += 1
                    x += VIA_PITCH
                y += VIA_PITCH
        out[ref] = n
    return out


def area(board):
    """{ref: {layer name: mm^2, ..., 'effective': top + half of the rest}} of the filled clamp copper, after a fill"""
    res = {}
    for ref in CLAMPS:
        a = {}
        for z in board.Zones():
            if z.GetZoneName().startswith(f'clamp_{ref}_'):
                nm = board.GetLayerName(z.GetLayer())
                a[nm] = round(a.get(nm, 0.0) + z.GetFilledArea() / 1e12, 1)
        if a:
            a['effective'] = round(a.get('F.Cu', 0.0) + 0.5 * sum(v for k, v in a.items() if k != 'F.Cu'), 1)
            res[ref] = a
    return res
