"""Remove useless GND stitching vias (inside mounting-hole pads, or not landing in the GND
pour on both layers), then refill the zones. usage: mb_cleanup.py board.kicad_pcb"""
import sys, math
import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
holes = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetDrillSize().x > 0:
            r = pcbnew.ToMM(max(p.GetSize().x, p.GetDrillSize().x)) / 2
            holes.append((pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y), r))
zones = {z.GetLayer(): z for z in b.Zones() if z.GetNetname() == 'GND'}
gtracks = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK' and t.GetNetname() == 'GND']
gpads = [p for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname() == 'GND' and p.GetDrillSize().x == 0]
removed = 0
for v in list(b.GetTracks()):
    if v.GetClass() != 'PCB_VIA' or v.GetNetname() != 'GND':
        continue
    x, y = pcbnew.ToMM(v.GetPosition().x), pcbnew.ToMM(v.GetPosition().y)
    bad = any(math.hypot(x - hx, y - hy) < hr + 0.3 + 0.35 for hx, hy, hr in holes)
    if not bad:
        pos = v.GetPosition()
        on_track = any(t.HitTest(pos) for t in gtracks) or any(p.HitTest(pos) for p in gpads)
        in_fill = all(L in zones and zones[L].GetFilledPolysList(L).Contains(pos) for L in (pcbnew.F_Cu, pcbnew.B_Cu))
        bad = not in_fill and not on_track
    if bad:
        b.Remove(v); removed += 1
filler.Fill(b.Zones())
pcbnew.SaveBoard(sys.argv[1], b)
print('removed', removed, 'GND vias')
