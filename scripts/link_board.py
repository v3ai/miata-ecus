"""Link board footprints to schematic symbols and give nets the schematic's (hierarchical) names,
so Update PCB from Schematic is a no-op.
usage: link_board.py board.kicad_pcb fp_paths.txt netlist.names.json out.kicad_pcb"""
import sys, json, pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
paths = {}
for line in open(sys.argv[2]):
    ref, path, rest = line.rstrip('\n').split(' ', 2)
    title, fname = rest.rsplit(' ', 1)
    paths[ref] = (path, title, fname)
n = 0
for fp in b.GetFootprints():
    ref = fp.GetReference()
    if ref in paths:
        path, title, fname = paths[ref]
        fp.SetPath(pcbnew.KIID_PATH(path))
        try:
            fp.SetSheetname(title); fp.SetSheetfile(fname)
        except AttributeError:
            pass
        n += 1
names = json.load(open(sys.argv[3]))
ren = 0
for short, full in names.items():
    if short != full:
        net = b.FindNet(short)
        if net:
            net.SetNetname(full); ren += 1
b.BuildListOfNets()
pcbnew.SaveBoard(sys.argv[4], b)
print('linked', n, 'footprints; renamed', ren, 'nets')
