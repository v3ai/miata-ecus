"""Ordering list for a whole build: every motherboard year plus daughterboards plus the in-car parts.
usage: order_all.py <out.csv> [daughterboards=5] [each motherboard=1] [cars=1]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib, order_bom, mb_common
out = sys.argv[1]
args = [int(a) for a in sys.argv[2:5]]
nd, nm, nc = args + [5, 1, 1][len(args):]
boards = []
for label, mod in (('1989-93', 'mb_na6'), ('1994-95', 'mb_na8'), ('1996-97', 'mb_na96'), ('1999-2000', 'mb_nb1'),
                   ('2001-05', 'mb_nb2')):
    parts = importlib.import_module(mod).build_parts()
    boards.append((label, 'mb', [dict(p) for p in parts], nm))
import design
boards.append(('daughterboard', 'daughter', design.parts, nd))
rows = order_bom.write_order_all(boards, nd, nc, out)
print('wrote', out, len(rows), 'lines')
