"""castellate_hand.py <in.kicad_pcb> <out.kicad_pcb> <8995 | 9697 | 9900 | 0105> (KiCad 9): the hand fixes of the
motherboards' castellation change order, for the joins finish_route.py cannot find.

2001-05, OUT_TACH (JD1-11): its bottom-copper track from the harness ends under land 11, and there is no room for a
via above the land (OUT_MAINRLY runs at y 92.25) or below it (V5_EXT at y 97). A 0.5 / 0.3 mm via goes between
lands 11 and 12 (1.04 mm apart): 0.22 mm from land 11, 0.32 mm from land 12, 0.23 mm from OUT_IACV's bottom track."""
import gc
import sys
import pcbnew

gc.disable()      # pcbnew's SWIG temporaries crash the cyclic collector under KiCad 9
MM = pcbnew.FromMM

# per board: (net, via (x, y), size, drill, [(layer, (x0, y0), (x1, y1), width)])
HAND = {
    '0105': [('OUT_TACH', (154.12, 93.5), 0.5, 0.3,
              [('B.Cu', (153.5, 94.25), (154.12, 93.5), 0.3), ('F.Cu', (154.12, 93.5), (152.9, 93.5), 0.3)])],
}


def main(src, dst, short):
    b = pcbnew.LoadBoard(src)
    for net, (x, y), size, drill, tracks in HAND.get(short, []):
        n = b.FindNet(net)
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        v.SetWidth(MM(size))
        v.SetDrill(MM(drill))
        v.SetNet(n)
        b.Add(v)
        for layer, (x0, y0), (x1, y1), w in tracks:
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(MM(x0), MM(y0)))
            t.SetEnd(pcbnew.VECTOR2I(MM(x1), MM(y1)))
            t.SetWidth(MM(w))
            t.SetLayer(b.GetLayerID(layer))
            t.SetNet(n)
            b.Add(t)
        print(f'{short}: {net} via at ({x}, {y}) and {len(tracks)} tracks')
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)


if __name__ == '__main__':
    main(*sys.argv[1:4])
