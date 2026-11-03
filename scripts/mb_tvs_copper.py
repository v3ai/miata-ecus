"""Heat-spreading copper for the 1989-93 batch-injector clamps D3/D4 (SMCJ30A). usage: mb_tvs_copper.py board.kicad_pcb

Each clamp takes all the turn-off energy of the two injectors on its harness wire: about 1.5 W at 7200 rpm with 8 mH
injectors, steady state. On its bare pads an SMC package is rated about 75 C/W junction to ambient, too hot for that
at a high cabin temperature. So, after routing:
  - the cathode (OUT_INJ1 / OUT_INJ2) gets a copper island on both layers around its pad, as large as the free board
    around it allows, joined by a field of vias (other nets' copper keeps its clearance: the zone fills around it, and
    vias are only placed where they clear everything);
  - the anode pad joins the GND pours solidly (no thermal relief), and gets its own vias to the bottom pour.
Prints the filled copper per clamp and layer. Does nothing on a board without D3/D4.
"""
import math
import sys
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I

CLAMPS = ('D3', 'D4')
ISLAND = (4.0, 4.5)              # island extent (mm) from the cathode pad centre: away from / toward the anode
DOWN = 12.0                      # and below it
VIA_D, VIA_DRILL, VIA_PITCH, CLEAR = 0.6, 0.3, 1.2, 0.25


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def clear(board, x, y, netcode):
    r = VIA_D / 2 + CLEAR
    for t in board.GetTracks():
        tx, ty = ToMM(t.GetPosition().x), ToMM(t.GetPosition().y)
        if t.GetClass() == 'PCB_VIA':
            d = math.hypot(tx - x, ty - y)
            if d < r + ToMM(t.GetWidth()) / 2 or (t.GetNetCode() == netcode and d < VIA_PITCH * 0.9):
                return False
        elif t.GetNetCode() != netcode:
            if seg_dist(x, y, ToMM(t.GetStart().x), ToMM(t.GetStart().y), ToMM(t.GetEnd().x),
                        ToMM(t.GetEnd().y)) < r + ToMM(t.GetWidth()) / 2:
                return False
    for fp in board.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            dx = max(ToMM(bb.GetLeft()) - x, 0, x - ToMM(bb.GetRight()))
            dy = max(ToMM(bb.GetTop()) - y, 0, y - ToMM(bb.GetBottom()))
            hole = p.GetDrillSize().x > 0
            if math.hypot(dx, dy) < r + (0.1 if p.GetNetCode() == netcode and not hole else 0.0) + (0.3 if hole else 0):
                return False
    return True


def via(board, net, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(VECTOR2I(FromMM(x), FromMM(y)))
    v.SetWidth(FromMM(VIA_D)); v.SetDrill(FromMM(VIA_DRILL))
    v.SetNet(net)
    board.Add(v)


def main(path):
    b = pcbnew.LoadBoard(path)
    found = [b.FindFootprintByReference(r) for r in CLAMPS]
    if not all(found):
        print('no D3/D4: nothing to do')
        return
    for fp in found:
        k = next(p for p in fp.Pads() if p.GetNetname().startswith('OUT_INJ'))
        a = next(p for p in fp.Pads() if p.GetNetname() == 'GND')
        net = k.GetNet()
        cx, cy = ToMM(k.GetPosition().x), ToMM(k.GetPosition().y)
        ax = ToMM(a.GetPosition().x)
        # the island runs from the cathode pad down into the free board below the clamps (away from JD1 and the
        # pairing links above them), no further toward the anode than the cathode pad's inner edge plus a margin, and
        # no further the other way than the neighbouring clamp's anode allows
        sgn = 1 if ax > cx else -1                  # direction of the anode
        x0, x1 = sorted((cx - sgn * ISLAND[0], cx + sgn * ISLAND[1]))
        y0, y1 = cy - 2.5, cy + DOWN
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            z = pcbnew.ZONE(b)
            z.SetLayer(layer); z.SetNet(net)
            ol = z.Outline(); ol.NewOutline()
            for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
                ol.Append(FromMM(x), FromMM(y))
            z.SetAssignedPriority(1)
            z.SetLocalClearance(FromMM(0.3))
            z.SetMinThickness(FromMM(0.25))
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
            b.Add(z)
        a.SetZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
        n_k = n_a = 0
        y = y0 + 0.7
        while y <= y1 - 0.7:
            x = x0 + 0.7
            while x <= x1 - 0.7:
                if clear(b, x, y, net.GetNetCode()):
                    via(b, net, x, y); n_k += 1
                x += VIA_PITCH
            y += VIA_PITCH
        # anode vias just outside the anode pad, into both GND pours
        bb = a.GetBoundingBox()
        gx = ToMM(bb.GetLeft()) - 0.8 if sgn > 0 else ToMM(bb.GetRight()) + 0.8
        for dy in (-1.8, -0.6, 0.6, 1.8):
            if clear(b, gx, ToMM(a.GetPosition().y) + dy, a.GetNetCode()):
                via(b, a.GetNet(), gx, ToMM(a.GetPosition().y) + dy); n_a += 1
        print(f'{fp.GetReference()}: {n_k} cathode vias, {n_a} anode vias')
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    for fp in found:
        nn = next(p for p in fp.Pads() if p.GetNetname().startswith('OUT_INJ')).GetNetname()
        a = {pcbnew.LayerName(z.GetLayer()): round(z.GetFilledArea() / 1e12, 1) for z in b.Zones() if z.GetNetname() == nn}
        print(f'{fp.GetReference()} {nn} island mm2: {a}')
    pcbnew.SaveBoard(path, b)


if __name__ == '__main__':
    main(sys.argv[1])
