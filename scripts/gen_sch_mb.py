"""Wired KiCad schematic for a year-specific motherboard (reuses the daughterboard
schematic engine in gen_sch2.py). usage: gen_sch_mb.py <year module> <outdir> <project>"""
import sys, os, importlib
sys.path.insert(0, os.path.dirname(__file__))
YEAR, OUTDIR, PROJ = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = [sys.argv[0], OUTDIR, PROJ]
import gen_sch
import gen_sch2 as S
import mb_common as C

M = importlib.import_module(YEAR)
parts = M.build_parts()
S.PARTS = {p['ref']: p for p in parts}
S.PROJECT = PROJ
S.OUT = OUTDIR
S.REV, S.DATE = os.environ.get('MBREV', '0.3'), '2026-10-29'

# header symbol: terminals in OEM order (plug, then A..Z, AA..), first half on the left, the rest on the right
_keys = sorted(M.HARNESS, key=lambda k: (k[0], len(k), k))
_plugs = sorted({k[0] for k in _keys})
_cut = len(_keys) // 2
if len(_plugs) == 2:                     # two plugs: one per side, as before
    _cut = sum(1 for k in _keys if k[0] == _plugs[0])
HARN_L, HARN_R = _keys[:_cut], _keys[_cut:]
gen_sch.CUSTOM['HARNESS'] = {
    'left': [(k, k + (' ' + M.HARNESS[k] if M.HARNESS[k] else ''), 'passive') for k in HARN_L],
    'right': [(k, k + (' ' + M.HARNESS[k] if M.HARNESS[k] else ''), 'passive') for k in HARN_R],
    'desc': 'Stock Miata ECU harness header'}
gen_sch.CUSTOM['MPX5700'] = {
    'left': [('3', 'VS', 'power_in'), ('2', 'GND', 'power_in')],
    'right': [('1', 'VOUT', 'output'), ('4', 'NC', 'no_connect'), ('5', 'NC', 'no_connect'), ('6', 'NC', 'no_connect')],
    'desc': 'NXP MPX5700 integrated pressure sensor (0-700 kPa)'}
gen_sch.CUSTOM['WBO_MODULE'] = {
    'left': [('A1', '+5V', 'power_in'), ('A2', 'GND', 'power_in'), ('A3', 'SEL1', 'input'), ('A4', 'SEL2', 'input'),
             ('A5', 'CAN_RX', 'output'), ('A6', 'CAN_TX', 'input'), ('A7', 'VBATT_SENSE', 'input'), ('A8', 'BOOT0', 'input')],
    'right': [('B1', 'GND', 'power_in'), ('B2', 'GND', 'power_in'), ('B3', 'HEATER-', 'passive'), ('B4', 'HEATER-', 'passive'),
              ('B5', 'LSU_IP', 'passive'), ('B6', 'LSU_VM', 'passive'), ('B7', 'LSU_RTRIM', 'passive'), ('B8', 'LSU_UN', 'passive')],
    'desc': 'FOME/rusEFI wideband module socket'}


def choose(p):
    r, v, fpn = p['ref'], p['value'], p['fp'].split(':')[1]
    if r == 'J1':
        return None, 'HARNESS'
    if r == 'U2':
        return None, 'MPX5700'
    if r.startswith('H'):
        return 'Mechanical', 'MountingHole_Pad' if p['pads'] else 'MountingHole'
    if r in ('JD1', 'JD2'):
        return 'Connector_Generic', 'Conn_01x40'
    if r in ('JW1', 'JW2'):
        return 'Connector_Generic', 'Conn_01x08'
    if r == 'J2':
        return 'Connector_Generic', 'Conn_02x03_Odd_Even'
    if r == 'J3':
        return 'Connector_Generic', 'Conn_01x02'
    if r == 'J4':
        return 'Connector', 'USB_C_Receptacle'
    if r == 'J5':
        return 'Connector_Generic', 'Conn_02x08_Odd_Even'
    if r == 'J6':
        return 'Connector_Generic', 'Conn_01x06'
    if r.startswith('JP'):
        return 'Jumper', 'SolderJumper_2_Open'
    if r.startswith('F'):
        return 'Device', 'Polyfuse'
    if r == 'U3':
        return 'Interface_CAN_LIN', 'SN65HVD230'
    if r == 'U4':
        return 'Power_Protection', 'USBLC6-2SC6'
    return gen_sch.choose(p)


S.choose = choose
S.TITLE_PREFIX = M.TITLE.split(' (')[0] + ' - '
S.COMMENT = 'Generated from scripts/' + YEAR + '.py; netlist identical to the routed board'
SHEET = {'J1': 'harness', 'H': 'harness', 'JD1': 'daughter', 'JD2': 'daughter', 'HD': 'daughter'}


def sheet_of(ref):
    if ref in SHEET:
        return SHEET[ref]
    if ref.startswith('HD'):
        return 'daughter'
    if ref.startswith('H'):
        return 'harness'
    return 'io'


S.sheet_of = sheet_of
S.NET_SHEETS.clear()
for p in parts:
    for n in p['pads'].values():
        if n:
            S.NET_SHEETS.setdefault(n, set()).add(sheet_of(p['ref']))
G = 2.54


def sheet_harness(s):
    s.paper = 'A3'
    s.text(f'Stock harness header ({M.TITLE.split("(")[0].strip()}): every pin labelled with the daughterboard signal it drives', 20.32, 22.86)
    s.place('J1', 160.02, 132.08)
    # unconnected harness pins get no-connect flags automatically; GND pins tie to one ground
    gnd = [k for k, v in M.HARNESS.items() if v == 'GND']
    for side in (HARN_L, HARN_R):
        g = [k for k in gnd if k in side]
        if g:
            s.rail('J1', 'GND', pins=g)
    s.text('Case mounting bosses (M4), tied to ground', 279.4, 22.86)
    for i, ref in enumerate(sorted(r for r in S.PARTS if r.startswith('H') and not r.startswith('HD'))):
        s.place(ref, 287.02 + (i % 3) * 15.24, 38.1 + (i // 3) * 20.32)


def sheet_daughter(s):
    s.paper = 'A3'
    s.text('Daughterboard sockets: pin-for-pin with the daughterboard J1 (top) and J2 (bottom)', 20.32, 22.86)
    s.place('JD1', 101.6, 120.65)
    s.place('JD2', 236.22, 120.65)
    s.rail('JD1', 'GND', pins=[k for k, v in S.PARTS['JD1']['pads'].items() if v == 'GND'])
    s.rail('JD2', 'GND', pins=[k for k, v in S.PARTS['JD2']['pads'].items() if v == 'GND'])
    s.text('Daughterboard standoffs (M3)', 309.88, 22.86)
    for i in range(4):
        s.place(f'HD{i + 1}', 312.42 + i * 12.7, 38.1)


def sheet_io(s):
    s.paper = 'A3'
    # ---- LSU 4.9 connector (controller is on the daughterboard) + CAN termination
    s.text('LSU 4.9 wideband sensor (controller on the daughterboard)', 20.32, 22.86)
    s.place('J2', 60.96, 55.88)
    s.text('LSU 4.9: 1 IP  2 VM  3 H-  4 H+  5 RT  6 UN', 45.72, 43.18, 1.27)
    s.text('IP/VM/RT/UN and H- run to daughterboard J2 33-38; the heater current returns on J2 39/40', 20.32, 96.52, 1.27)
    # heater fuse from VBAT
    s.o2('F1', 40.64, 78.74, 'h')
    s.lab('VBAT_IN', (30.48, 78.74), 'left')
    s.wire((30.48, 78.74), 'F1.1')
    s.text('Heater fuse: 2 A hold, 30 V PTC', 30.48, 86.36, 1.27)
    X, Y = 66.04, 127.0
    s.text('CAN bus termination at the ECU end', 20.32, 116.84)
    s.o2('R1', X, Y + 6.35, 'v'); s.o2('R6', X, Y + 17.78, 'v')
    s.wire((X - 12.7, Y), (X, Y), 'R1.1'); s.lab('CAN_H', (X - 12.7, Y), 'left')
    s.wire('R1.2', 'R6.1')
    s.wire('R6.2', (X, Y + 25.4), (X - 12.7, Y + 25.4)); s.lab('CAN_L', (X - 12.7, Y + 25.4), 'left')
    s.text('120R; remove R6 if the bus is terminated elsewhere', X + 7.62, Y + 12.7, 1.27)

    # ---- MAP
    s.text('MAP sensor', 193.04, 22.86)
    MX, MY = 218.44, 50.8
    s.place('U2', MX, MY)
    s.o2('C1', MX - 25.4, MY + 2.54, 'v'); s.o2('C2', MX - 17.78, MY + 2.54, 'v')
    s.wire('U2.3', (MX - 17.78, MY - 2.54), (MX - 25.4, MY - 2.54), 'C1.1')
    s.wire((MX - 17.78, MY - 2.54), 'C2.1')
    s.lab('V5_SENS', (MX - 30.48, MY - 2.54), 'left'); s.wire((MX - 30.48, MY - 2.54), (MX - 25.4, MY - 2.54))
    s.stub('C1.2'); s.stub('C2.2')
    s.o2('C3', MX + 17.78, MY + 2.54, 'v')
    s.wire('U2.1', (MX + 17.78, MY - 2.54), (MX + 25.4, MY - 2.54)); s.wire((MX + 17.78, MY - 2.54), 'C3.1')
    s.stub('C3.2'); s.lab('IN_MAP', (MX + 25.4, MY - 2.54), 'right')

    # ---- IAT
    s.text('IAT: onboard connector (R4, default) or stock harness (R5)', 193.04, 86.36)
    s.place('J3', 203.2, 104.14, 180)
    s.o2('R4', 220.98, 101.6, 'h'); s.o2('R5', 220.98, 111.76, 'h')
    s.wire('R4.2', (231.14, 101.6), (231.14, 111.76), 'R5.2'); s.wire((231.14, 101.6), (238.76, 101.6))
    s.lab('IN_IAT', (238.76, 101.6), 'right')
    s.text('R5 not fitted', 213.36, 116.84, 1.27)

    # ---- USB
    s.text('USB-C (device): tuning, logs, DFU firmware update', 279.4, 22.86)
    UX, UY = 297.18, 66.04
    s.place('J4', UX, UY)
    s.place('U4', UX + 48.26, UY - 7.62)
    s.o2('R2', UX + 20.32, UY + 22.86, 'v'); s.o2('R3', UX + 27.94, UY + 22.86, 'v')

    # ---- AUX / SWD
    fz = sorted(r for r in S.PARTS if r.startswith('F') and r != 'F1')
    if fz:
        s.text('Fused +12 V feeds to harness actuators', 20.32, 172.72)
        for k, r in enumerate(fz):
            y = 185.42 + k * 10.16
            s.o2(r, 40.64, y, 'h')
            s.wire((30.48, y), f'{r}.1'); s.lab('VBAT_IN', (30.48, y), 'left')
            s.wire(f'{r}.2', (53.34, y)); s.lab(S.PARTS[r]['pads']['2'], (53.34, y), 'right')
    s.text('AUX: add-on I/O the stock harness has no pins for', 193.04, 147.32)
    s.place('J5', 220.98, 177.8)


BUILD = [('harness', 'Harness', sheet_harness), ('daughter', 'Daughterboard', sheet_daughter),
         ('io', 'LSU, MAP, IAT, USB, AUX', sheet_io)]


def main():
    root_uuid = gen_sch.U()
    sheets, fp_paths = [], {}
    for page, (key, title, fn) in enumerate(BUILD, start=2):
        s = S.Sheet(key, title, root_uuid, page)
        fn(s)
        missing = [r for r in S.PARTS if sheet_of(r) == key and r not in s.parts]
        assert not missing, (key, missing)
        fp_paths.update({r: (v, s.title, s.fname) for r, v in s.finish().items()})
        sheets.append(s)
    Q, r2 = gen_sch.Q, S.r2
    items = []
    for i, s in enumerate(sheets):
        x, y = 30.48 + i * 81.28, 50.8
        items.append(f'(sheet (at {x} {y}) (size 66.04 30.48) (fields_autoplaced) (stroke (width 0.1524) (type solid)) '
                     f'(fill (color 0 0 0 0.0000)) (uuid {s.sheet_uuid}) '
                     f'(property "Sheetname" {Q(s.title)} (at {x} {r2(y - 0.71)} 0) (effects (font (size 1.524 1.524)) (justify left bottom))) '
                     f'(property "Sheetfile" {Q(s.fname)} (at {x} {r2(y + 31.07)} 0) (effects (font (size 1.27 1.27)) (justify left top))) '
                     f'(instances (project {Q(PROJ)} (path {Q("/" + root_uuid)} (page {Q(str(s.page))})))))')
    note = (f'{M.TITLE}. Carries the year-specific harness header and the year-independent I/O '
            '(wideband, MAP, IAT, USB-C). All engine control is on the daughterboard.')
    items.append(f'(text {Q(note)} (at 30.48 100.0 0) (effects (font (size 1.524 1.524)) (justify left bottom)) (uuid {gen_sch.U()}))')
    root = (f'(kicad_sch (version 20230121) (generator eeschema) (uuid {root_uuid}) (paper "A4") '
            f'(title_block (title {Q(M.TITLE)}) (date "2026-10-29") (rev "' + os.environ.get('MBREV', '0.3') + '")) (lib_symbols) '
            + '\n'.join(items) + ' (sheet_instances (path "/" (page "1"))))')
    open(os.path.join(OUTDIR, PROJ + '.kicad_sch'), 'w').write(root)
    with open(os.path.join(OUTDIR, 'fp_paths.txt'), 'w') as f:
        for ref, (path, title, fname) in fp_paths.items():
            f.write(f'{ref} {path} {title} {fname}\n')
    print('schematic sheets', [s.fname for s in sheets], 'symbols', len(fp_paths))


main()
