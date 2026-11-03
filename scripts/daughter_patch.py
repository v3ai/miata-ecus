"""Post-route fixes, run on daughter_make.sh's finished board (rev 0.5b on):
  1. If the autorouter left HALL1 (U1 pin 38) open, route it with hand_route.py (two-layer A* over the real copper; a
     via under the MCU, the bottom layer to D13). Any other open net stops the script.
  2. AN_AUX3's long top-layer run sits 0.05 mm from the D17/D18 GND pads: move it up 0.125 mm (0.175 mm both sides).
  3. Part values from design.py where the board's differ (part swaps made after routing).
usage: daughter_patch.py finished.kicad_pcb out.kicad_pcb   (keep the board's .kicad_pro next to both)"""
import sys, os, subprocess, shutil
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from placement import DY
src, out = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
shutil.copy(src.replace('.kicad_pcb', '.kicad_pro'), out.replace('.kicad_pcb', '.kicad_pro'))
import re, tempfile
rep = os.path.join(tempfile.mkdtemp(), 'drc.txt')
subprocess.run([sys.executable, os.path.join(here, 'drc.py'), src, rep], check=True, capture_output=True)
open_nets = set(re.findall(r'\[unconnected_items\].*?\n.*?\n.*?\[(\S+)\]', open(rep).read()))
if open_nets - {'HALL1'}:
    sys.exit(f'open nets the patch does not handle: {sorted(open_nets)}')
if 'HALL1' in open_nets:
    subprocess.run([sys.executable, os.path.join(here, 'hand_route.py'), src, out, 'HALL1', '140.5', str(86.0 + DY), '164.5',
                    str(105.0 + DY), 'U1:38', 'D13:2,C51:1,R61:2'], check=True)
else:
    shutil.copy(src, out)
    print('HALL1 routed by the autorouter')
b = pcbnew.LoadBoard(out); mm, IU = pcbnew.ToMM, pcbnew.FromMM
P = lambda x, y: pcbnew.VECTOR2I(IU(x), IU(y))
at = lambda p, x, y: abs(mm(p.x) - x) < 1e-3 and abs(mm(p.y) - y) < 1e-3
Y = 95.875 + DY
moved = 0
for t in b.GetTracks():
    if t.GetNetname() != 'AN_AUX3' or t.Type() == pcbnew.PCB_VIA_T:
        continue
    s, e = t.GetStart(), t.GetEnd()
    if at(s, 160.0, 91.75 + DY) and at(e, 155.75, 96.0 + DY):
        t.SetEnd(P(155.875, Y)); moved += 1
    elif at(s, 155.75, 96.0 + DY) and at(e, 138.5, 96.0 + DY):
        t.SetStart(P(155.875, Y)); t.SetEnd(P(138.5, Y)); moved += 1
    elif at(s, 138.5, 96.0 + DY):
        t.SetStart(P(138.5, Y)); moved += 1
print('AN_AUX3 moved clear of D17/D18' if moved == 3 else f'AN_AUX3 not at the expected place ({moved} segments): check DRC')
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
