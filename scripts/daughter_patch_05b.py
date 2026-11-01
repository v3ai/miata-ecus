"""Rev 0.5b post-route fixes, run on daughter_make.sh's finished board:
  1. HALL1 (U1 pin 38) is the one net the autorouter left open: route it with hand_route.py (two-layer A* over the
     real copper; a via under the MCU, the bottom layer to D13).
  2. AN_AUX3's long top-layer run sits 0.05 mm from the D17/D18 GND pads: move it up 0.125 mm (0.175 mm both sides).
  3. Part values for the rev 0.5b swaps (D9 B360A).
usage: daughter_patch_05b.py finished.kicad_pcb out.kicad_pcb   (keep the board's .kicad_pro next to both)"""
import sys, os, subprocess, shutil
import pcbnew
src, out = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
shutil.copy(src.replace('.kicad_pcb', '.kicad_pro'), out.replace('.kicad_pcb', '.kicad_pro'))
subprocess.run([sys.executable, os.path.join(here, 'hand_route.py'), src, out, 'HALL1', '140.5', '86.0', '164.5', '105.0',
                'U1:38', 'D13:2,C51:1,R61:2'], check=True)
b = pcbnew.LoadBoard(out); mm, IU = pcbnew.ToMM, pcbnew.FromMM
P = lambda x, y: pcbnew.VECTOR2I(IU(x), IU(y))
at = lambda p, x, y: abs(mm(p.x) - x) < 1e-3 and abs(mm(p.y) - y) < 1e-3
Y = 95.875
moved = 0
for t in b.GetTracks():
    if t.GetNetname() != 'AN_AUX3' or t.Type() == pcbnew.PCB_VIA_T:
        continue
    s, e = t.GetStart(), t.GetEnd()
    if at(s, 160.0, 91.75) and at(e, 155.75, 96.0):
        t.SetEnd(P(155.875, Y)); moved += 1
    elif at(s, 155.75, 96.0) and at(e, 138.5, 96.0):
        t.SetStart(P(155.875, Y)); t.SetEnd(P(138.5, Y)); moved += 1
    elif at(s, 138.5, 96.0):
        t.SetStart(P(138.5, Y)); moved += 1
assert moved == 3, ('AN_AUX3 route not as expected', moved)
sys.path.insert(0, here)
import design
vals = {p['ref']: p['value'] for p in design.parts}
for fp in b.GetFootprints():
    r = fp.GetReference()
    if r in vals and fp.GetValue() != vals[r]:
        print('value', r, fp.GetValue(), '->', vals[r]); fp.SetValue(vals[r])
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(out)
print('patched', out)
