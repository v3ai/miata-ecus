"""Hand-route a list of open connections with hand_route.py, chaining boards.
usage: hand_route_all.py in.kicad_pcb out.kicad_pcb NET:REF:PAD ...   (window grows until a path is found)"""
import sys, subprocess, shutil, math, os
import pcbnew

src, out = sys.argv[1], sys.argv[2]
HR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hand_route.py')
cur = out + '.tmp.kicad_pcb'
shutil.copy(src, cur)
left = []
for spec in sys.argv[3:]:
    net, ref, pad = spec.split(':')
    b = pcbnew.LoadBoard(cur)
    mm = pcbnew.ToMM
    pads = [(fp.GetReference(), p.GetNumber(), mm(p.GetPosition().x), mm(p.GetPosition().y))
            for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname() == net]
    me = next(p for p in pads if p[0] == ref and p[1] == pad)
    others = sorted((p for p in pads if p[:2] != me[:2]), key=lambda p: math.dist(p[2:], me[2:]))
    ok = False
    for k, margin in ((1, 3.0), (2, 5.0), (3, 8.0), (len(others), 12.0)):
        dst = others[:k]
        xs = [me[2]] + [p[2] for p in dst]; ys = [me[3]] + [p[3] for p in dst]
        win = [min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin]
        r = subprocess.run(['python3', HR, cur, cur + '.n.kicad_pcb', net] + [f'{v:.2f}' for v in win] +
                           [f'{ref}:{pad}', ','.join(f'{p[0]}:{p[1]}' for p in dst)], capture_output=True, text=True)
        if r.returncode == 0 and 'no path' not in r.stdout:
            shutil.move(cur + '.n.kicad_pcb', cur)
            print(spec, 'OK', r.stdout.strip().splitlines()[0] if r.stdout.strip() else '')
            ok = True
            break
    if not ok:
        print(spec, 'NO PATH')
        left.append(spec)
shutil.move(cur, out)
print('left:', left)
