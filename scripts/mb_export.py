"""Fab outputs for a motherboard: JLC gerbers + drill zip, BOM, CPL, parts list CSV.
usage: mb_export.py <year module> board.kicad_pcb outdir"""
import sys, os, csv, subprocess, importlib, collections, shutil
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew

M = importlib.import_module(sys.argv[1])
board_path, out = sys.argv[2], sys.argv[3]
parts = M.build_parts()
import mb_common
PRE = mb_common.fab_prefix(sys.argv[1], os.environ.get('MBREV', '0.0'))   # e.g. miata-ecu-motherboard-1989-93-rev0.9_
for f in os.listdir(out) if os.path.isdir(out) else []:                  # older names (unprefixed or another rev)
    if f.endswith(('jlcpcb_gerbers.zip', 'jlcpcb_bom.csv', 'jlcpcb_cpl.csv', 'parts_list.csv', 'self_order_bom.csv')):
        os.remove(os.path.join(out, f))
os.makedirs(out + '/gerbers', exist_ok=True)
for f in os.listdir(out + '/gerbers'):
    os.remove(out + '/gerbers/' + f)
subprocess.run(['kicad-cli', 'pcb', 'export', 'gerbers', '-l',
                'F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts',
                '--subtract-soldermask', '--no-x2', '-o', out + '/gerbers/', board_path], check=True, capture_output=True)
subprocess.run(['kicad-cli', 'pcb', 'export', 'drill', '--format', 'excellon', '--excellon-separate-th',
                '--generate-map', '--map-format', 'gerberx2', '-o', out + '/gerbers/', board_path], check=True,
               capture_output=True)
shutil.make_archive(out + '/' + PRE + 'jlcpcb_gerbers', 'zip', out + '/gerbers')

# JLC BOM: the SMD parts JLC assembles. Through-hole parts and everything without an LCSC number go in the
# self-order BOM (order_bom.py)
import order_bom
agg = collections.OrderedDict()
for p in parts:
    if order_bom.is_jlc('mb', p):
        agg.setdefault((p['value'], p['fp'].split(':')[1], p['lcsc']), []).append(p['ref'])
with open(out + '/' + PRE + 'jlcpcb_bom.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
    for (v, fp, l), refs in agg.items():
        w.writerow([v, ','.join(refs), fp, l])

b = pcbnew.LoadBoard(board_path)
lcsc = {p['ref'] for p in parts if order_bom.is_jlc('mb', p)}
with open(out + '/' + PRE + 'jlcpcb_cpl.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for fp in b.GetFootprints():
        r = fp.GetReference()
        if r not in lcsc:
            continue
        w.writerow(order_bom.cpl_row(fp))         # gerber coordinates, JLC rotation offsets

# full parts list (incl. hand-fitted parts) for the README / ordering
with open(out + '/' + PRE + 'parts_list.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Ref', 'Value', 'Footprint', 'LCSC', 'Assembly', 'Description'])
    for p in parts:
        asm = 'JLC' if order_bom.is_jlc('mb', p) else ('mechanical' if p['ref'].startswith('H') else
                                                        ('hand-fit' if p['lcsc'] else 'hand-fit / not fitted'))
        w.writerow([p['ref'], p['value'], p['fp'], p['lcsc'], asm, p['desc']])
order_bom.write_self_bom('mb', parts, out + '/' + PRE + 'self_order_bom.csv')
print('exported', out, len(agg), 'BOM lines')
