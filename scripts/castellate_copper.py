"""castellate_copper.py <board after castellate_daughter.py, KiCad 9> <out, KiCad 9>

The second half of the castellation change: the cut puts the new long edges through the old J1 / J2 pin rows, so
some track ends that ran into those pads (and the short pad-to-pad links along the row) now sit closer to the edge
than the copper-to-edge rule (EDGE, 0.3 mm in the project). Every such track end lies inside its castellated pad, so
it can move straight inward, to EDGE + half the track width + MARGIN from the edge, and stay connected through the
pad. A track end that would leave its pad, or a track too close to the edge that does not end in a J1 / J2 pad, is
reported and left for a hand fix. Then the zones are refilled and the board saved. Carry the result into the KiCad 7
file with backport_copper.py."""
import sys
import pcbnew

TOP, BOT = 52.75, 123.25
EDGE, MARGIN = 0.30, 0.03
mm, MM = pcbnew.ToMM, pcbnew.FromMM
# Hand fixes: (net, old end) -> new end, mm. IN_CLT met J2 pad 6 at the pad's corner, outside its rounded copper.
HAND = {('IN_CLT', (126.5, 123.0)): (126.2, 122.65)}


def main(src, dst):
    b = pcbnew.LoadBoard(src)
    pads = [p for r in ('J1', 'J2') for p in b.FindFootprintByReference(r).Pads()]

    def pad_at(pt, net):
        for p in pads:
            if p.GetNetname() == net and p.HitTest(pt):
                return p
        return None

    moved, problems = 0, []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            continue
        for get, put in ((t.GetStart, t.SetStart), (t.GetEnd, t.SetEnd)):
            k = (t.GetNetname(), (round(mm(get().x), 3), round(mm(get().y), 3)))
            if k in HAND:
                put(pcbnew.VECTOR2I(MM(HAND[k][0]), MM(HAND[k][1])))
                moved += 1
    for t in list(b.GetTracks()):
        if t.Type() == pcbnew.PCB_VIA_T:
            continue
        w = mm(t.GetWidth())
        need = EDGE + w / 2 + MARGIN
        for get, put in ((t.GetStart, t.SetStart), (t.GetEnd, t.SetEnd)):
            pt = get()
            y = mm(pt.y)
            if y - TOP < need:
                ny = TOP + need
            elif BOT - y < need:
                ny = BOT - need
            else:
                continue
            p = pad_at(pt, t.GetNetname())
            np_ = pcbnew.VECTOR2I(pt.x, MM(ny))
            if p is None:
                problems.append(f'{t.GetNetname()} {b.GetLayerName(t.GetLayer())} end ({mm(pt.x):.2f}, {y:.2f}) '
                                f'is {min(y - TOP, BOT - y):.2f} mm from the edge and not in a J1 / J2 pad')
            elif not p.HitTest(np_):
                problems.append(f'{t.GetNetname()} end ({mm(pt.x):.2f}, {y:.2f}) would leave pad '
                                f'{p.GetParentFootprint().GetReference()}.{p.GetNumber()} at y {ny:.2f}: make that pad longer')
            else:
                put(np_)
                moved += 1
    # a segment whose two ends both moved onto the same point is now zero length
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_VIA_T and t.GetStart() == t.GetEnd():
            b.Remove(t)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)
    print(f'track ends moved inward {moved}')
    for p in problems:
        print('HAND FIX:', p)


if __name__ == '__main__':
    main(*sys.argv[1:3])
