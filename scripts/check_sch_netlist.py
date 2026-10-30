"""Compare the schematic's exported netlist to design.py, pad by pad."""
import sys, re, collections
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design
txt = open(sys.argv[1]).read()
sch = {}
FULL = {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', txt, re.S):
    full = m.group(1); name = full.split('/')[-1]; FULL[name] = full
    for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)):
        sch[(r, p)] = name
exp = {(p['ref'], k): v for p in design.parts for k, v in p['pads'].items() if v}
bad = [(k, v, sch.get(k)) for k, v in exp.items() if sch.get(k) != v]
extra = [(k, v) for k, v in sch.items() if k not in exp and not v.startswith('unconnected')
         and not k[0].startswith('#')]
# a net in the schematic must not merge two design nets
merged = collections.defaultdict(set)
for k, v in sch.items():
    if k in exp:
        merged[v].add(exp[k])
mix = {k: v for k, v in merged.items() if len(v) > 1}
# ...and a design net must not be split over several schematic nets (e.g. a local label on one sheet)
full = {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', txt, re.S):
    for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)):
        full[(r, p)] = m.group(1)
split = collections.defaultdict(set)
for k, v in exp.items():
    if k in full:
        split[v].add(full[k])
split = {k: v for k, v in split.items() if len(v) > 1}
print('pads checked', len(exp), 'mismatches', len(bad), 'extra', len(extra), 'merged nets', len(mix), 'split nets', len(split))
for k, v in list(split.items())[:10]: print('  SPLIT', k, v)
for b in bad[:15]: print('  BAD', b)
for e in extra[:15]: print('  EXTRA', e)
for k, v in list(mix.items())[:5]: print('  MERGED', k, v)

import json
json.dump(FULL, open(sys.argv[1] + '.names.json', 'w'), indent=0)
