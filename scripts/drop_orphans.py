"""drop_orphans.py <in.kicad_pcb> <out.kicad_pcb> (KiCad 9): remove the pieces of copper that hold no pad.

After rip_conflicts.py cuts a track in two places and finish_route.py joins the ends around it, the stretch between
the cuts can be left floating: tracks and vias that join nothing (KiCad lists them as unconnected). A piece of a
signal net with no pad, by finish_route.py's own reckoning of pieces (KiCad's rule: an item joins another when one of
its anchor points lies in the other's copper; a pour joins what its filled islands hold), is removed whole. Plane nets
(GND, +3V3) are left alone. Zones are refilled."""
import gc
import os
import sys

gc.disable()      # pcbnew's SWIG temporaries crash the cyclic collector under KiCad 9
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew                    # noqa: E402
import finish_route as F         # noqa: E402

mm = pcbnew.ToMM


def main(src, dst):
    B = F.Board(src)
    kill = []                    # (net, kind, anchors)
    for net in sorted(B.items):
        if not net or net in F.PLANES:
            continue
        it = B.items[net]
        for p in B.pieces(net):
            if not any(it[i][0] == 'p' for i in p):
                kill += [(net, it[i][0], B.anchors[net][i]) for i in p]
    want = {(n, k, tuple((round(x, 4), round(y, 4)) for x, y in a)) for n, k, a in kill}
    gone = 0
    for t in list(B.b.GetTracks()):
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            key = (t.GetNetname(), 'v', ((round(mm(p.x), 4), round(mm(p.y), 4)),))
        elif t.GetLayerName() in B.lid:
            s, e = t.GetStart(), t.GetEnd()
            key = (t.GetNetname(), 't', ((round(mm(s.x), 4), round(mm(s.y), 4)), (round(mm(e.x), 4), round(mm(e.y), 4))))
        else:
            continue
        if key in want:
            print('removed', key[1], key[0], key[2][0])
            B.b.Remove(t)
            gone += 1
    pcbnew.ZONE_FILLER(B.b).Fill(B.b.Zones())
    B.b.Save(dst)
    print(f'{gone} floating tracks and vias removed')


if __name__ == '__main__':
    main(*sys.argv[1:3])
