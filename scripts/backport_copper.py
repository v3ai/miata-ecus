"""backport_copper.py <kicad 7 board> <routed board, any newer KiCad> <out, kicad 7>: carry a re-route back into the
KiCad 7 file the release scripts use.

The routing scripts can run under a newer KiCad (9), whose pcbnew saves boards in a format KiCad 7 cannot open. This
takes every track and via, and every zone's fill, from the routed board and writes them into the KiCad 7 file in its
own syntax; everything else (footprints, zone outlines and settings, graphics, net table, setup) stays exactly as in
the KiCad 7 file. Nets are matched by name, zones by UUID. Footprints, zone outlines and nets must not have changed
between the two (it stops if a net or zone is missing). usage as above; prints what it replaced."""
import re
import sys
import pcbnew

mm = pcbnew.ToMM


def num(v):
    s = f'{v:.6f}'.rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def main(old_path, new_path, out_path):
    text = open(old_path).read()
    nets = {name: int(code) for code, name in re.findall(r'^  \(net (\d+) "((?:[^"\\]|\\.)*)"\)$', text, re.M)}
    nets[''] = 0
    b = pcbnew.LoadBoard(new_path)
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    lines = []
    nseg = nvia = 0
    for t in b.GetTracks():
        n = t.GetNetname()
        if n not in nets:
            sys.exit(f'net {n!r} is not in the KiCad 7 board')
        u = t.m_Uuid.AsString()
        if t.Type() == pcbnew.PCB_VIA_T:
            if t.GetViaType() != pcbnew.VIATYPE_THROUGH:
                sys.exit('only through vias are handled')
            p = t.GetPosition()
            lines.append(f'  (via (at {num(mm(p.x))} {num(mm(p.y))}) (size {num(mm(t.GetWidth(F)))}) '
                         f'(drill {num(mm(t.GetDrillValue()))}) (layers "F.Cu" "B.Cu") (net {nets[n]}) (tstamp {u}))')
            nvia += 1
        elif t.Type() == pcbnew.PCB_TRACE_T:
            s, e = t.GetStart(), t.GetEnd()
            lines.append(f'  (segment (start {num(mm(s.x))} {num(mm(s.y))}) (end {num(mm(e.x))} {num(mm(e.y))}) '
                         f'(width {num(mm(t.GetWidth()))}) (layer "{b.GetLayerName(t.GetLayer())}") (net {nets[n]}) '
                         f'(tstamp {u}))')
            nseg += 1
        else:
            sys.exit('arcs are not handled')
    fills = {}
    for z in b.Zones():
        out = []
        for lay in z.GetLayerSet().CuStack():
            ps = z.GetFilledPolysList(lay)
            if ps is None:
                continue
            ps = pcbnew.SHAPE_POLY_SET(ps)
            ps.Fracture()
            for i in range(ps.OutlineCount()):
                o = ps.Outline(i)
                pts = [f'(xy {num(mm(o.CPoint(k).x))} {num(mm(o.CPoint(k).y))})' for k in range(o.PointCount())]
                rows = ['        ' + ' '.join(pts[k:k + 6]) for k in range(0, len(pts), 6)]
                out.append(f'    (filled_polygon\n      (layer "{b.GetLayerName(lay)}")\n      (pts\n'
                           + '\n'.join(rows) + '\n      )\n    )')
        fills[z.m_Uuid.AsString()] = out
    # rebuild the KiCad 7 text: drop its tracks and vias, put the routed ones where the first of them was
    src = text.split('\n')
    res, placed, nz = [], False, 0
    i = 0
    while i < len(src):
        ln = src[i]
        if ln.startswith('  (segment ') or ln.startswith('  (via '):
            if not placed:
                res.extend(lines); placed = True
            i += 1
            continue
        if ln.startswith('  (zone '):
            j = i
            depth = 0
            while True:
                depth += src[j].count('(') - src[j].count(')')
                if depth == 0:
                    break
                j += 1
            block = src[i:j + 1]
            uid = re.search(r'\(tstamp ([0-9a-f-]+)\)', block[0])
            if not uid or uid.group(1) not in fills:
                sys.exit(f'zone {uid and uid.group(1)} is not in the routed board')
            # keep everything up to the first filled_polygon, then the routed fill, then the closing paren
            keep = []
            k = 0
            while k < len(block) - 1 and not block[k].startswith('    (filled_polygon'):
                keep.append(block[k]); k += 1
            res.extend(keep)
            res.extend('\n'.join(fills[uid.group(1)]).split('\n') if fills[uid.group(1)] else [])
            res.append(block[-1])
            nz += 1
            i = j + 1
            continue
        res.append(ln)
        i += 1
    if not placed:
        sys.exit('no tracks in the KiCad 7 board to replace')
    open(out_path, 'w').write('\n'.join(res))
    print(f'{nseg} segments, {nvia} vias, {nz} zone fills written into {out_path}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
