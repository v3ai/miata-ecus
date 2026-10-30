"""Post-route finishing for the daughterboard (after flip_headers.py):
- drop wideband port vias that ended up joining copper on one layer only
- tidy the wideband block silkscreen: frame + title, LED labels, part refs hidden
- refresh the LCSC field of every footprint from design.py
- refill zones
usage: daughter_finish.py in.kicad_pcb out.kicad_pcb"""
import sys, math
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I
import design, wideband as WB, wb_clean
CLEAN = wb_clean.ENABLED

OX, OY = 100.0, 50.0
b = pcbnew.LoadBoard(sys.argv[1])
P = lambda x, y: VECTOR2I(FromMM(OX + x), FromMM(OY + y))

# 2. silkscreen
block = set(WB.placement())
for fp in b.GetFootprints():
    r = fp.GetReference()
    if r in block:
        # clean layout: same rule as the rest of the board (ICs / switch visible); LEDs get function labels
        fp.Reference().SetVisible(CLEAN and r[0] in 'UQ')
x0, y0, x1, y1 = 92.9, 25.3, 113.4, 53.2


def seg(a, c, layer=pcbnew.F_SilkS, w=0.15):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(*a)); s.SetEnd(P(*c)); s.SetLayer(layer); s.SetWidth(FromMM(w)); b.Add(s)


def text(t, x, y, size=0.8, rot=0, just=0):
    tx = pcbnew.PCB_TEXT(b); tx.SetText(t); tx.SetLayer(pcbnew.F_SilkS)
    tx.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); tx.SetTextThickness(FromMM(size * 0.15))
    tx.SetPosition(P(x, y)); tx.SetTextAngle(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
    if just:
        tx.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT if just < 0 else pcbnew.GR_TEXT_H_ALIGN_RIGHT)
    b.Add(tx)


if not CLEAN:     # rev 0.2 transplant: frame + title around the block, LSU pin names above the J2 drops
    for a, c in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        seg(a, c)
    text('WIDEBAND', x1 - 0.4, y0 + 0.9, 0.9, 0, 1)
    for pt in WB.ports():
        if pt['side'] == 'S' and pt['num'] in (5, 6, 7, 8):
            text({5: 'IP', 6: 'VM', 7: 'RT', 8: 'UN'}[pt['num']], pt['at'][0] - 1.0, pt['at'][1] + 2.6, 0.8, 90)
LEDLAB = wb_clean.LED_LABELS if CLEAN else {'D101': ('HTR', 0, 1.6), 'D102': ('OK', 0, 1.6), 'D103': ('ACT', 0, 1.6)}
for ref, (lab, dx, dy) in LEDLAB.items():
    fp = b.FindFootprintByReference(ref)
    x, y = ToMM(fp.GetPosition().x) - OX, ToMM(fp.GetPosition().y) - OY
    text(lab, x + dx, y + dy, 0.8, 0, -1 if dx > 0 else (1 if dx < 0 else 0))

# reference labels moved off copper / other labels: block ICs, and the BOOT / RESET switches (their
# default spot above the switch collided with the LED column's labels)
REF_POS = dict(wb_clean.REF_POS if CLEAN else {}, SW1=(119.5, 41.45, 0), SW2=(119.5, 49.25, 0))
for ref, (x, y, a) in REF_POS.items():
    fp = b.FindFootprintByReference(ref)
    t = fp.Reference()
    t.SetPosition(P(x, y)); t.SetTextAngle(pcbnew.EDA_ANGLE(a, pcbnew.DEGREES_T))

# 3. LCSC fields
lc = {p['ref']: p['lcsc'] for p in design.parts}
for fp in b.GetFootprints():
    v = lc.get(fp.GetReference())
    if v:
        fp.SetProperty('LCSC', v)

# 1. port vias touching copper on one layer only
ports = set() if CLEAN else {tuple(round(c, 2) for c in pt['at']) for pt in WB.ports()}
tracks = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK']
removed = []
for v in [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']:
    if v.GetNetname() in ('GND', '+3V3'):
        continue
    x, y = ToMM(v.GetPosition().x) - OX, ToMM(v.GetPosition().y) - OY
    if (round(x, 2), round(y, 2)) not in ports:
        continue
    lays = {t.GetLayer() for t in tracks if t.GetNetCode() == v.GetNetCode() and
            min(math.hypot(ToMM(t.GetStart().x) - OX - x, ToMM(t.GetStart().y) - OY - y),
                math.hypot(ToMM(t.GetEnd().x) - OX - x, ToMM(t.GetEnd().y) - OY - y)) < 0.31}
    ends = []
    for t in tracks:
        if t.GetNetCode() != v.GetNetCode():
            continue
        for p in (t.GetStart(), t.GetEnd()):
            if math.hypot(ToMM(p.x) - OX - x, ToMM(p.y) - OY - y) < 0.31:
                ends.append((ToMM(p.x), ToMM(p.y)))
    joined = all(math.dist(e, ends[0]) < 0.02 for e in ends)    # tracks meet without the via
    if len(lays) < 2 and joined:
        removed.append(v.GetNetname()); b.Remove(v)
print('port vias removed (single layer):', removed)

# 4. zones
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(sys.argv[2], b)
print('saved', sys.argv[2])
