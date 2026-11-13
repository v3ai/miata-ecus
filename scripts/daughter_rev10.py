"""Rev 0.10 as a change order on the released rev 0.9 board: add the new parts at their placement.py positions, give the
re-used pads their new nets and rename the two serial nets. The proven rev 0.9 copper stays; the new nets are then
routed with hand_route_all.py.   usage: daughter_rev10.py rev09.kicad_pcb out.kicad_pcb"""
import sys
import pcbnew
from pcbnew import VECTOR2I, FromMM
import design
from placement import PLACE

OX, OY = 100.0, 50.0
FPROOT = '/usr/share/kicad/footprints/'
b = pcbnew.LoadBoard(sys.argv[1])
RENAME = {'UART_TX': 'IN_FLEX', 'UART_RX': 'IN_N2O', 'UART_TX_M': 'FLEX_M', 'UART_RX_M': 'N2O_ARM_M'}
# the released board's nets carry their schematic sheet path ("/MCU/NRST"): match on the last part
BYNAME = {}
for code, ni in b.GetNetsByNetcode().items():
    BYNAME[ni.GetNetname().split('/')[-1]] = ni
for old, new in RENAME.items():
    ni = BYNAME.pop(old)
    ni.SetNetname(ni.GetNetname()[:-len(old)] + new)
    BYNAME[new] = ni


def net(n):
    if n not in BYNAME:
        ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); BYNAME[n] = ni
    return BYNAME[n]


have = {fp.GetReference(): fp for fp in b.GetFootprints()}
added = []
for part in design.parts:
    ref = part['ref']
    if ref in have:
        fp = have[ref]
        for pad in fp.Pads():
            want = part['pads'].get(pad.GetNumber(), '') or ''
            if pad.GetNetname().split('/')[-1] != want and pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                if want == '' and pad.GetNetname() == '':
                    continue
                print('re-net', ref, pad.GetNumber(), repr(pad.GetNetname()), '->', repr(want))
                pad.SetNet(net(want)) if want else pad.SetNetCode(0)
        continue
    lib, name = part['fp'].split(':')
    fp = pcbnew.FootprintLoad(FPROOT + lib + '.pretty', name)
    fp.SetReference(ref); fp.SetValue(part['value']); fp.SetFPID(pcbnew.LIB_ID(lib, name))
    if part['lcsc']:
        fp.SetProperty('LCSC', part['lcsc'])
    for pad in fp.Pads():
        n = part['pads'].get(pad.GetNumber())
        if n:
            pad.SetNet(net(n))
    x, y, rot = PLACE[ref][:3]
    b.Add(fp)
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(VECTOR2I(FromMM(OX + x), FromMM(OY + y)))
    r = fp.Reference(); r.SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8))); r.SetTextThickness(FromMM(0.12))
    r.SetVisible(ref[0] in 'UJQYDL'); fp.Value().SetVisible(False)
    added.append(ref)
print('added', added)
pcbnew.SaveBoard(sys.argv[2], b)
