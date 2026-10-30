"""Compare an exported motherboard schematic netlist with the year module, pad by pad.
usage: check_mb_netlist.py <year module> net.net"""
import sys, os, re, collections, importlib, json
sys.path.insert(0, os.path.dirname(__file__))
M = importlib.import_module(sys.argv[1])
parts = M.build_parts()
txt = open(sys.argv[2]).read()
sch, FULL = {}, {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', txt, re.S):
    full = m.group(1); name = full.split('/')[-1]; FULL[name] = full
    for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)):
        sch[(r, p)] = name
exp = {(p['ref'], k): v for p in parts for k, v in p['pads'].items() if v}
bad = [(k, v, sch.get(k)) for k, v in exp.items() if sch.get(k) != v]
merged = collections.defaultdict(set)
for k, v in sch.items():
    if k in exp:
        merged[v].add(exp[k])
mix = {k: v for k, v in merged.items() if len(v) > 1}
extra = [(k, v) for k, v in sch.items() if k not in exp and not v.startswith('unconnected') and not k[0].startswith('#')]
print('pads checked', len(exp), 'mismatches', len(bad), 'extra', len(extra), 'merged', len(mix))
for b in bad[:20]: print('  BAD', b)
for e in extra[:10]: print('  EXTRA', e)
for k, v in list(mix.items())[:5]: print('  MERGED', k, v)
json.dump(FULL, open(sys.argv[2] + '.names.json', 'w'), indent=0)
