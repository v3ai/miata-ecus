"""Move the mezzanine headers J1/J2 to the bottom side (body under the board, pins pointing down
into the motherboard) without moving any pad, so routing is untouched.
usage: flip_headers.py in.kicad_pcb out.kicad_pcb"""
import sys, pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
for fp in b.GetFootprints():
    if fp.GetReference() not in ('J1', 'J2') or fp.IsFlipped():
        continue
    want = {p.GetNumber(): (p.GetPosition().x, p.GetPosition().y) for p in fp.Pads()}
    pos = fp.GetPosition()
    fp.Flip(pos, False)
    for _ in range(4):
        got = {p.GetNumber(): (p.GetPosition().x, p.GetPosition().y) for p in fp.Pads()}
        if all(abs(got[n][0] - want[n][0]) < 1000 and abs(got[n][1] - want[n][1]) < 1000 for n in want):
            break
        fp.Rotate(pos, pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    else:
        raise SystemExit(f'{fp.GetReference()}: could not keep pads in place')
    print(fp.GetReference(), 'now on', fp.GetLayerName(), 'rot', fp.GetOrientationDegrees())
pcbnew.SaveBoard(sys.argv[2], b)
