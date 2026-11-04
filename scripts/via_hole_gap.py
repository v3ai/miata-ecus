"""via_hole_gap.py in out [gap]: keep every via hole at least `gap` mm (default 0.47; JLCPCB asks 0.45 mm between a
pad hole and another hole) from the plated and non-plated pad holes. A GND or +3V3 via with no track on it (a
stitching via: the planes connect it) is deleted; any other via moves straight away from the hole, dragging the
track ends on it. Zones refilled."""
import sys, math, pcbnew
mm, IU = pcbnew.ToMM, pcbnew.FromMM
src, out = sys.argv[1], sys.argv[2]
GAP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.47
b = pcbnew.LoadBoard(src)
holes = [(mm(p.GetPosition().x), mm(p.GetPosition().y), mm(min(p.GetDrillSize().x, p.GetDrillSize().y)) / 2)
         for fp in b.GetFootprints() for p in fp.Pads() if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)]
tracks = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
dele, moved = [], []
for v in [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]:
    vx, vy, vr = mm(v.GetPosition().x), mm(v.GetPosition().y), mm(v.GetDrillValue()) / 2
    for hx, hy, hr in holes:
        d = math.hypot(vx - hx, vy - hy) - vr - hr
        if d < GAP:
            ends = [(t, e) for t in tracks if t.GetNetname() == v.GetNetname() for e in ('Start', 'End')
                    if abs(mm(getattr(t, 'Get' + e)().x) - vx) < 1e-3 and abs(mm(getattr(t, 'Get' + e)().y) - vy) < 1e-3]
            if not ends and v.GetNetname() in ('GND', '+3V3'):
                dele.append(v)
            else:
                k = (GAP - d) / max(math.hypot(vx - hx, vy - hy), 1e-6)
                dx, dy = (vx - hx) * k, (vy - hy) * k
                v.SetPosition(pcbnew.VECTOR2I(IU(vx + dx), IU(vy + dy)))
                for t, e in ends:
                    getattr(t, 'Set' + e)(pcbnew.VECTOR2I(IU(vx + dx), IU(vy + dy)))
                moved.append((v.GetNetname(), round(vx, 2), round(vy, 2), round(dx, 3), round(dy, 3)))
            break
for v in dele:
    b.Remove(v)
print('deleted stitching vias:', len(dele), ' moved:', moved)
b.Save(out)
b = pcbnew.LoadBoard(out); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(out)
