"""strip_stubs.py <in.kicad_pcb> <out.kicad_pcb>: remove track stubs and vias that no longer lead anywhere.

After a change order moves or reshapes pads (the castellated daughterboard's lands, parts moved out from under it),
the tracks that ran to the old pads end in nothing. This removes them one segment at a time, walking back along the
chain until it meets something real, and removes vias left joining fewer than two things. Connectivity is decided
here, geometrically, on each copper layer (not from KiCad's DRC report, whose dangling-track list under KiCad 9 is
not usable for this): a segment end is connected if it lies on another segment of its net (end or body), in a via
of its net, in a pad of its net on that layer, or in a zone fill of its net on that layer.
Run it on an unchanged board first: it must remove nothing. Zones are refilled at the end."""
import gc
import os
import re
import sys
import pcbnew

gc.disable()      # pcbnew's SWIG temporaries crash the cyclic collector under KiCad 9

mm = pcbnew.ToMM
DRY = '--dry' in sys.argv




def main(src, dst):
    b = pcbnew.LoadBoard(src)
    pads = [p for f in b.GetFootprints() for p in f.Pads()]
    zones = list(b.Zones())

    # tol: the track's half width (or the via's radius): copper that overlaps the pad or the fill is connected, as in
    # KiCad (a track may end on a pad's edge; a via in a pour sits in its thermal-relief opening)
    def in_pad(pt, layer, net, tol=0):
        return any(p.GetNetname() == net and p.IsOnLayer(layer) and p.HitTest(pt, int(tol)) for p in pads)

    def in_zone(pt, layer, net, tol=0):
        return any(z.GetNetname() == net and z.IsOnLayer(layer) and z.HitTestFilledArea(layer, pt, int(tol))
                   for z in zones)

    removed_s = removed_v = 0
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    if True:
        segs, vias = [], []
        for t in b.GetTracks():
            st, en = t.GetStart(), t.GetEnd()
            rec = dict(obj=t, net=t.GetNetname(), a=(st.x, st.y), e=(en.x, en.y))
            if t.Type() == pcbnew.PCB_VIA_T:
                rec['r'] = t.GetWidth(F) / 2
                vias.append(rec)
            else:
                rec['layer'], rec['w'] = t.GetLayer(), t.GetWidth()
                segs.append(rec)

        def on_seg(o, p):
            (ax, ay), (ex, ey) = o['a'], o['e']
            dx, dy = ex - ax, ey - ay
            L = dx * dx + dy * dy
            t = 0 if L == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L))
            return ((ax + t * dx - p[0]) ** 2 + (ay + t * dy - p[1]) ** 2) ** 0.5 <= o['w'] / 2 + 1000   # 1 um

        def d(p, q):
            return ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5

        kill = []
        for sg in segs:
            net, layer = sg['net'], sg['layer']
            for p in (sg['a'], sg['e']):
                v2 = pcbnew.VECTOR2I(int(p[0]), int(p[1]))
                ok = (any(o is not sg and o['layer'] == layer and o['net'] == net and on_seg(o, p) for o in segs)
                      or any(v['net'] == net and d(v['a'], p) <= v['r'] for v in vias)
                      or in_pad(v2, layer, net, sg['w'] / 2) or in_zone(v2, layer, net, sg['w'] / 2))
                if not ok:
                    kill.append(sg['obj'])
                    break
        for v in vias:
            net, pos = v['net'], v['a']
            v2 = pcbnew.VECTOR2I(int(pos[0]), int(pos[1]))
            links = 0
            for layer in (F, B):
                # a track ending at the via counts once; one running straight through it joins two ways
                for sg in segs:
                    if sg['layer'] == layer and sg['net'] == net:
                        if min(d(sg['a'], pos), d(sg['e'], pos)) <= v['r']:
                            links += 1
                        elif on_seg(dict(sg, w=2 * v['r']), pos):
                            links += 2
                links += in_pad(v2, layer, net, v['r']) + in_zone(v2, layer, net, v['r'])
            if links < 2:
                kill.append(v['obj'])
        if DRY:
            for t in kill:
                st, en = t.GetStart(), t.GetEnd()
                print('WOULD REMOVE', 'via' if t.Type() == pcbnew.PCB_VIA_T else b.GetLayerName(t.GetLayer()), t.GetNetname(),
                      (round(mm(st.x), 3), round(mm(st.y), 3)), (round(mm(en.x), 3), round(mm(en.y), 3)))
            print(f'{len(kill)} would go in the first round')
            return
        for t in kill:
            b.Remove(t)
            if t.Type() == pcbnew.PCB_VIA_T:
                removed_v += 1
            else:
                removed_s += 1
    if removed_s or removed_v:
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)
    return removed_s, removed_v


def rounds(src, dst):
    """One round per process (pcbnew's objects go bad after Remove and a re-read in one process)."""
    import shutil
    import subprocess
    shutil.copy(src, dst)
    pro = src[:-len('.kicad_pcb')] + '.kicad_pro'
    if os.path.exists(pro) and os.path.abspath(src) != os.path.abspath(dst):
        shutil.copy(pro, dst[:-len('.kicad_pcb')] + '.kicad_pro')
    tot_s = tot_v = 0
    for i in range(200):
        r = subprocess.run([sys.executable, os.path.abspath(__file__), '--round', dst], capture_output=True, text=True)
        m = re.search(r'ROUND (\d+) (\d+)', r.stdout)
        if not m:
            sys.exit(f'round {i + 1} failed:\n{r.stdout[-2000:]}{r.stderr[-2000:]}')
        s_, v_ = int(m.group(1)), int(m.group(2))
        tot_s += s_
        tot_v += v_
        if not (s_ or v_):
            break
    print(f'removed {tot_s} track segments and {tot_v} vias in {i} rounds')


if __name__ == '__main__':
    if sys.argv[1] == '--round':
        print('ROUND %d %d' % main(sys.argv[2], sys.argv[2]))
    elif DRY:
        main(sys.argv[1], sys.argv[2])
    else:
        rounds(sys.argv[1], sys.argv[2])
