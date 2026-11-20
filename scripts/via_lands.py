"""via_lands.py <in.kicad_pcb> <out.kicad_pcb> (KiCad 9): join the motherboard's bottom-copper tracks to the
castellated module's lands.

Up to motherboard rev 0.15 / 0.11, JD1 / JD2 were through-hole sockets, so a track could reach a pin on either copper
layer. The lands that replace them (castellate_mb.py) are on the top copper only, so every bottom-copper track that
ended at a pin now ends in nothing. Rather than rip those tracks out (they run up to 100 mm across the board, and
nothing else about them changed), this keeps each one (a track ending anywhere inside the old 1.7 mm pad met the
pin) and adds a via just beyond the end of its land, on the side the track comes from (under the module for a track
from inside, beyond the module's edge for one from outside), VIA_GAP from the land's copper: a bottom-copper link from the track's end to the via, and a top-copper link from the via
into the land. A track wider than WIDE gets the larger via. DRC afterwards shows any via that has landed on another
net; rip_conflicts.py removes those (each via with its links, listed in <out>.new.txt) and finish_route.py joins
those pins instead."""
import gc
import math
import sys
import pcbnew

gc.disable()      # pcbnew's SWIG temporaries crash the cyclic collector under KiCad 9

ROW = {'JD1': 94.75, 'JD2': 165.25}       # the module's long edges = the old pin rows (motherboard coordinates)
INWARD = {'JD1': +1, 'JD2': -1}           # direction from the row towards the module's middle
LAND_IN, LAND_OUT = 1.2, 1.8              # the land reaches this far under the module / beyond its edge
VIA_GAP = 0.2                             # copper gap from via to land (JLCPCB's no-via-in-pad check wants 0.1)
VIA, VIA_BIG, WIDE = (0.6, 0.3), (0.8, 0.4), 0.45
OLD_PAD = 0.86                            # the sockets' round pads (1.7 mm): a track whose copper reached one met the pin
mm, MM = pcbnew.ToMM, pcbnew.FromMM


def main(src, dst):
    b = pcbnew.LoadBoard(src)
    pins = {}
    for ref in ROW:
        for p in b.FindFootprintByReference(ref).Pads():
            pins[(ref, round(mm(p.GetPosition().x), 2))] = (p.GetNetname(), p.GetNet())
    todo = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T or t.GetLayer() != pcbnew.B_Cu:
            continue
        for e, o in ((t.GetStart(), t.GetEnd()), (t.GetEnd(), t.GetStart())):
            for (ref, x), (name, net) in pins.items():
                row = ROW[ref]
                if name == t.GetNetname() and math.hypot(mm(e.x) - x, mm(e.y) - row) <= OLD_PAD + mm(t.GetWidth()) / 2:
                    inward = (mm(o.y) - row) * INWARD[ref] > 0
                    todo.append((ref, x, row, inward, mm(t.GetWidth()), net, (mm(e.x), mm(e.y))))
    done, groups = set(), []
    for ref, x, row, inward, w, net, end in todo:
        if (ref, x) in done:
            continue
        done.add((ref, x))
        size, drill = VIA_BIG if w > WIDE else VIA
        s = INWARD[ref] if inward else -INWARD[ref]
        reach = LAND_IN if inward else LAND_OUT
        vy = row + s * (reach + VIA_GAP + size / 2)
        land_y = row - INWARD[ref] * (LAND_OUT - LAND_IN) / 2          # the land's centre
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(vy)))
        v.SetWidth(MM(size))
        v.SetDrill(MM(drill))
        v.SetNet(net)
        b.Add(v)
        group = [v]
        for layer, (x0, y0), y1 in ((pcbnew.B_Cu, end, vy), (pcbnew.F_Cu, (x, vy), land_y)):
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(MM(x0), MM(y0)))
            t.SetEnd(pcbnew.VECTOR2I(MM(x), MM(y1)))
            t.SetWidth(MM(min(w, size)))
            t.SetLayer(layer)
            t.SetNet(net)
            b.Add(t)
            group.append(t)
        groups.append(' '.join(o.m_Uuid.AsString() for o in group))
        print(f'{ref} at x {x:.2f} ({net.GetNetname()}, {w:.2f} mm): via {size}/{drill} at y {vy:.2f}, '
              + ('under the module' if inward else 'beyond its edge'))
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)
    # the via and its two links, one group per line: rip_conflicts.py removes a group whole, before older copper
    open(dst[:-len('.kicad_pcb')] + '.new.txt', 'w').write('\n'.join(groups) + '\n')
    print(f'{len(done)} vias beside the lands')


if __name__ == '__main__':
    main(*sys.argv[1:3])
