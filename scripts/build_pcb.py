"""Create the daughterboard .kicad_pcb: outline, footprints, nets, placement."""
import sys
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM
import design
from placement import PLACE, BOARD_W, BOARD_H

OX, OY = 100.0, 50.0          # board origin inside the KiCad sheet
FPROOT = '/usr/share/kicad/footprints/'


def P(x, y):
    return VECTOR2I(FromMM(OX + x), FromMM(OY + y))


def build(out):
    board = pcbnew.NewBoard(out)
    ds = board.GetDesignSettings()
    import os; NLAY = int(os.environ.get('LAYERS', '4')); ds.SetCopperLayerCount(NLAY); board.SetCopperLayerCount(NLAY)
    nc = ds.m_NetSettings.m_DefaultNetClass
    nc.SetClearance(FromMM(0.15))
    nc.SetTrackWidth(FromMM(0.2))
    nc.SetViaDiameter(FromMM(0.6))
    nc.SetViaDrill(FromMM(0.3))
    ds.m_TrackMinWidth = FromMM(0.15)
    ds.m_ViasMinSize = FromMM(0.5)
    ds.m_MinThroughDrill = FromMM(0.3)
    ds.m_CopperEdgeClearance = FromMM(0.3)
    ds.m_HoleToHoleMin = FromMM(0.25)
    ds.m_HoleClearance = FromMM(0.2)
    ds.m_SolderMaskMinWidth = FromMM(0.0)

    # outline with 2mm corner radius
    r = 2.0
    W, H = BOARD_W, BOARD_H
    segs = [((r, 0), (W - r, 0)), ((W, r), (W, H - r)), ((W - r, H), (r, H)), ((0, H - r), (0, r))]
    for a, b in segs:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(P(*a)); s.SetEnd(P(*b))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1))
        board.Add(s)
    k = r * (1 - 0.70710678)
    arcs = [((0, r), (k, k), (r, 0)), ((W - r, 0), (W - k, k), (W, r)),
            ((W, H - r), (W - k, H - k), (W - r, H)), ((r, H), (k, H - k), (0, H - r))]
    for a, m, e in arcs:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetArcGeometry(P(*a), P(*m), P(*e))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FromMM(0.1))
        board.Add(s)

    nets = {}
    for n in design.nets():
        ni = pcbnew.NETINFO_ITEM(board, n)
        board.Add(ni)
        nets[n] = ni

    missing = []
    for part in design.parts:
        lib, name = part['fp'].split(':')
        fp = pcbnew.FootprintLoad(FPROOT + lib + '.pretty', name)
        fp.SetReference(part['ref'])
        fp.SetValue(part['value'])
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        if part['lcsc']:
            fp.SetProperty('LCSC', part['lcsc'])
        for pad in fp.Pads():
            n = part['pads'].get(pad.GetNumber())
            if n:
                pad.SetNet(nets[n])
        side = 'F'
        if part['ref'] not in PLACE:
            missing.append(part['ref'])
            x, y, rot = 130, 10 + len(missing) * 3, 0
        else:
            x, y, rot = PLACE[part['ref']][:3]
            side = PLACE[part['ref']][3] if len(PLACE[part['ref']]) > 3 else 'F'
        board.Add(fp)
        if side == 'B':
            fp.Flip(fp.GetPosition(), False)
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(P(x, y))
        # small, tidy silkscreen
        ref = fp.Reference()
        ref.SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8)))
        ref.SetTextThickness(FromMM(0.12))
        ref.SetVisible(part['ref'][0] in 'UJQYDL' or part['ref'].startswith('SW'))
        fp.Value().SetVisible(False)
    if missing:
        print('UNPLACED:', missing)
    import wb_clean
    if not wb_clean.ENABLED:
        import wb_build
        wb_build.add_block(board, OX, OY)
    board.Save(out)
    return board


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'daughter.kicad_pcb')
