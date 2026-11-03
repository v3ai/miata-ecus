"""Remove dangling track stubs, dangling vias and duplicate (stacked same-net) vias that DRC reports (left by rip-ups and hand routes).
usage: clean_dangling.py in.kicad_pcb out.kicad_pcb   (keep the board's .kicad_pro next to both)
Runs DRC, deletes the reported items, repeats until none are left (at most 6 rounds), then refills the zones.
Each round runs in its own process (pcbnew's SWIG objects go bad after Remove + reload in one process)."""
import sys, os, re, shutil, subprocess, tempfile
here = os.path.dirname(os.path.abspath(__file__))
ITEM = re.compile(r'@\(([-\d.]+) mm, ([-\d.]+) mm\): (Track|Via) \[([^\]]*)\]')


def one_round(path):
    """Delete what one DRC run reports; print the number removed."""
    import pcbnew
    rep = os.path.join(tempfile.mkdtemp(), 'drc.txt')
    subprocess.run([sys.executable, os.path.join(here, 'drc.py'), path, rep], check=True, capture_output=True)
    kill = []          # (kind, net, x, y)
    for blk in re.split(r'\n(?=\[)', open(rep).read()):
        head = blk.split(':')[0]
        items = ITEM.findall(blk)
        if head in ('[track_dangling]', '[via_dangling]') and items:
            x, y, kind, net = items[0]
            kill.append((kind, net, float(x), float(y)))
        elif (head in ('[holes_co_located]', '[hole_near_hole]') and len(items) == 2 and all(i[2] == 'Via' for i in items)
              and items[0][3] == items[1][3]
              and abs(float(items[0][0]) - float(items[1][0])) + abs(float(items[0][1]) - float(items[1][1])) < 0.1):
            x, y, kind, net = items[1]        # a same-net via stacked on another (hand routes): keep one
            kill.append(('Via', net, float(x), float(y)))
    b = pcbnew.LoadBoard(path); mm = pcbnew.ToMM
    tracks = list(b.GetTracks())
    gone = []
    for kind, net, x, y in kill:
        for t in tracks:
            if any(t is g for g in gone) or t.GetNetname() != net:
                continue
            isvia = t.Type() == pcbnew.PCB_VIA_T
            if (kind == 'Via') != isvia:
                continue
            p = t.GetPosition() if isvia else t.GetStart()      # DRC reports a track by its start point
            if abs(mm(p.x) - x) < 1e-3 and abs(mm(p.y) - y) < 1e-3:
                gone.append(t); break
    for t in gone:
        b.Remove(t)
    if gone:
        b.Save(path)
    print('RESULT', len(kill), len(gone))


def refill(path):
    import pcbnew
    b = pcbnew.LoadBoard(path)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(path)


if __name__ == '__main__':
    if sys.argv[1] == '--round':
        one_round(sys.argv[2]); sys.exit()
    if sys.argv[1] == '--refill':
        refill(sys.argv[2]); sys.exit()
    src, out = sys.argv[1], sys.argv[2]
    if os.path.abspath(src) != os.path.abspath(out):
        shutil.copy(src, out)
        shutil.copy(src.replace('.kicad_pcb', '.kicad_pro'), out.replace('.kicad_pcb', '.kicad_pro'))
    for rnd in range(6):
        r = subprocess.run([sys.executable, __file__, '--round', out], check=True, capture_output=True, text=True)
        rep, rm = map(int, re.search(r'RESULT (\d+) (\d+)', r.stdout).groups())
        print(f'round {rnd + 1}: {rep} reported, {rm} removed')
        if not rm:
            break
    subprocess.run([sys.executable, __file__, '--refill', out], check=True, capture_output=True)
    print('cleaned', out)
