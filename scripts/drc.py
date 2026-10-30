"""Run KiCad DRC through the python API (KiCad 7 CLI has no drc command)."""
import sys, re, collections
import pcbnew

board = pcbnew.LoadBoard(sys.argv[1])
out = sys.argv[2]
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
ok = pcbnew.WriteDRCReport(board, out, pcbnew.EDA_UNITS_MILLIMETRES, True)
txt = open(out).read()
types = collections.Counter(re.findall(r'^\[(\w+)\]', txt, re.M))
print('report written:', ok)
for m in re.findall(r'^\*\* (.*)$', txt, re.M):
    print(m)
print(dict(types))
