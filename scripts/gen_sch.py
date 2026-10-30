"""
Generate a KiCad 7 hierarchical schematic from design.py.

Every symbol pin gets a short wire stub and a global net label (or a power symbol for
GND/+3V3/+5V/+12V), so the schematic carries exactly the netlist the board was built
from. One sub-sheet per functional block. Unused pins get no-connect flags.
"""
import os, re, sys, uuid, math
sys.path.insert(0, os.path.dirname(__file__))
import design, bom

SYMLIB = '/usr/share/kicad/symbols/'
PROJECT = sys.argv[2] if len(sys.argv) > 2 else 'miata_ecu_daughter'
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
G = 2.54


def U():
    return str(uuid.uuid4())


# --------------------------------------------------------------------- sexpr
def tokenize(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in ' \t\r\n':
            i += 1
        elif c in '()':
            yield c; i += 1
        elif c == '"':
            j = i + 1; buf = []
            while s[j] != '"':
                if s[j] == '\\':
                    buf.append(s[j:j + 2]); j += 2
                else:
                    buf.append(s[j]); j += 1
            yield ('"', ''.join(buf)); i = j + 1
        else:
            j = i
            while j < n and s[j] not in ' \t\r\n()':
                j += 1
            yield s[i:j]; i = j


def parse(s):
    stack = [[]]
    for t in tokenize(s):
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        else:
            stack[-1].append(t)
    return stack[0]


def dump(x, ind=0):
    if isinstance(x, list):
        inner = ' '.join(dump(e, ind + 1) for e in x)
        return '(' + inner + ')'
    if isinstance(x, tuple):
        return '"' + x[1] + '"'
    return x


def Q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


_libcache = {}


def libsyms(lib):
    if lib not in _libcache:
        tree = parse(open(SYMLIB + lib + '.kicad_sym').read())[0]
        _libcache[lib] = {e[1][1]: e for e in tree if isinstance(e, list) and e and e[0] == 'symbol'}
    return _libcache[lib]


def lib_symbol(lib, name):
    """flattened symbol, renamed to Lib:Name, plus its pins [(num, name, x, y, ang, len)]"""
    syms = libsyms(lib)
    s = syms[name]
    ext = [e for e in s if isinstance(e, list) and e and e[0] == 'extends']
    if ext:
        parent = syms[ext[0][1][1]]
        body = [e for e in parent if isinstance(e, list) and e and e[0] == 'symbol']
        props = [e for e in s if isinstance(e, list) and e and e[0] == 'property']
        other = [e for e in parent if isinstance(e, list) and e and e[0] not in ('symbol', 'property', 'extends')]
        pname = ext[0][1][1]
        body = [[b[0], ('"', b[1][1].replace(pname, name, 1))] + b[2:] for b in body]
        s = ['symbol', ('"', name)] + other + props + body
    s = [s[0], ('"', f'{lib}:{name}')] + s[2:]
    return s, pins_of(s)


def pins_of(sym):
    pins = []

    def walk(x):
        if isinstance(x, list):
            if x and x[0] == 'pin':
                at = next(e for e in x if isinstance(e, list) and e[0] == 'at')
                ln = next(e for e in x if isinstance(e, list) and e[0] == 'length')
                nm = next(e for e in x if isinstance(e, list) and e[0] == 'name')
                nu = next(e for e in x if isinstance(e, list) and e[0] == 'number')
                pins.append((nu[1][1], nm[1][1], float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0,
                             float(ln[1])))
            for e in x:
                walk(e)
    walk(sym)
    return pins


# ------------------------------------------------------------- custom symbols
CUSTOM = {
    'LMR14020': {'left': [('2', 'VIN', 'power_in'), ('3', 'EN', 'input'), ('4', 'RT/SYNC', 'passive'),
                          ('6', 'SS', 'passive'), ('7', 'GND', 'power_in'), ('9', 'EP', 'power_in')],
                 'right': [('1', 'BOOT', 'passive'), ('8', 'SW', 'power_out'), ('5', 'FB', 'input')],
                 'desc': 'TI LMR14020 40V 2A synchronous buck (SO-8 PowerPAD)'},
    'TC4427': {'left': [('2', 'IN_A', 'input'), ('4', 'IN_B', 'input'), ('6', 'VDD', 'power_in'),
                        ('3', 'GND', 'power_in')],
               'right': [('7', 'OUT_A', 'output'), ('5', 'OUT_B', 'output'), ('1', 'NC', 'no_connect'),
                         ('8', 'NC', 'no_connect')],
               'desc': 'Microchip TC4427 dual 1.5A non-inverting MOSFET driver'},
    'MAX9926UAEE+': {'left': [('16', 'IN1+', 'input'), ('15', 'IN1-', 'input'), ('9', 'IN2+', 'input'),
                              ('10', 'IN2-', 'input'), ('14', 'VCC', 'power_in'), ('11', 'GND', 'power_in')],
                     'right': [('4', 'COUT1', 'open_collector'), ('5', 'COUT2', 'open_collector'),
                               ('1', 'INT_THRS1', 'input'), ('8', 'INT_THRS2', 'input'),
                               ('3', 'BIAS1', 'input'), ('6', 'BIAS2', 'input'), ('2', 'EXT1', 'input'),
                               ('7', 'EXT2', 'input'), ('13', 'ZERO_EN', 'input'), ('12', 'DIRN', 'input')],
                     'desc': 'Analog Devices MAX9926 dual VR sensor interface'},
    'AUIPS2041LTR': {'left': [('1', 'IN', 'input'), ('3', 'S', 'power_in')],
                     'right': [('2', 'D', 'passive'), ('4', 'D', 'passive')],
                     'desc': 'Infineon AUIPS2041L protected low-side switch, 63-75V active clamp'},
    'SN74LVC4245APWR': {'left': [('21', 'B1', 'bidirectional'), ('20', 'B2', 'bidirectional'),
                                 ('19', 'B3', 'bidirectional'), ('18', 'B4', 'bidirectional'),
                                 ('17', 'B5', 'bidirectional'), ('16', 'B6', 'bidirectional'),
                                 ('15', 'B7', 'bidirectional'), ('14', 'B8', 'bidirectional'),
                                 ('2', 'DIR', 'input'), ('22', '~{OE}', 'input'),
                                 ('23', 'VCCB', 'power_in'), ('24', 'VCCB', 'power_in')],
                        'right': [('3', 'A1', 'bidirectional'), ('4', 'A2', 'bidirectional'),
                                  ('5', 'A3', 'bidirectional'), ('6', 'A4', 'bidirectional'),
                                  ('7', 'A5', 'bidirectional'), ('8', 'A6', 'bidirectional'),
                                  ('9', 'A7', 'bidirectional'), ('10', 'A8', 'bidirectional'),
                                  ('1', 'VCCA', 'power_in'), ('11', 'GND', 'power_in'),
                                  ('12', 'GND', 'power_in'), ('13', 'GND', 'power_in')],
                        'desc': 'TI SN74LVC4245A octal transceiver, 5 V A port / 3.3 V B port (DIR low: B -> A)'},
    'TLS115B0EJ': {'left': [('8', 'I', 'power_in'), ('7', 'EN', 'input'), ('5', 'ADJ', 'input'),
                            ('3', 'GND', 'power_in'), ('9', 'EP', 'power_in')],
                   'right': [('1', 'Q', 'power_out'), ('4', 'PG', 'open_collector'), ('2', 'NC', 'no_connect'),
                             ('6', 'NC', 'no_connect')],
                   'desc': 'Infineon TLS115 protected 5V tracking regulator for sensor supply'},
}


def custom_symbol(name):
    c = CUSTOM[name]
    L, R = c['left'], c['right']
    n = max(len(L), len(R))
    longest = max(len(p[1]) for p in L + R)
    w = max(10.16, math.ceil((longest * 1.27 * 2 + 5) / G) * G)
    h = (n + 1) * G
    top = math.floor(h / 2 / G) * G
    lib_id = f'ECU:{name}'
    pins, pins_s = [], []
    for side, lst in (('L', L), ('R', R)):
        for i, (num, nm, typ) in enumerate(lst):
            y = top - G * (i + 1)
            x = -w / 2 - G if side == 'L' else w / 2 + G
            ang = 0 if side == 'L' else 180
            pins.append((num, nm, x, y, ang, G))
            pins_s.append(f'(pin {typ} line (at {x:.2f} {y:.2f} {ang}) (length {G}) '
                          f'(name {Q(nm)} (effects (font (size 1.27 1.27)))) '
                          f'(number {Q(num)} (effects (font (size 1.27 1.27)))))')
    ybot = top - G * (n + 1)
    s = (f'(symbol {Q(lib_id)} (in_bom yes) (on_board yes) '
         f'(property "Reference" "U" (at 0 {top + 1.27:.2f} 0) (effects (font (size 1.27 1.27))))'
         f'(property "Value" {Q(name)} (at 0 {ybot - 1.27:.2f} 0) (effects (font (size 1.27 1.27))))'
         f'(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
         f'(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
         f'(property "Description" {Q(c["desc"])} (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
         f'(symbol {Q(name + "_0_1")} (rectangle (start {-w / 2:.2f} {top:.2f}) (end {w / 2:.2f} {ybot:.2f}) '
         f'(stroke (width 0.254) (type default)) (fill (type background))))'
         f'(symbol {Q(name + "_1_1")} ' + ' '.join(pins_s) + '))')
    return parse(s)[0], pins


# -------------------------------------------------------------- symbol choice
def choose(p):
    v, fpn = p['value'], p['fp'].split(':')[1]
    r = p['ref']
    if v in CUSTOM:
        return None, v
    if r.startswith('RN'):
        return 'Device', 'R_Pack04'
    if r.startswith('R'):
        return 'Device', 'R'
    if r.startswith('C'):
        return 'Device', 'C'
    if r.startswith('FB'):
        return 'Device', 'FerriteBead'
    if r.startswith('F'):
        return 'Device', 'Fuse'
    if r.startswith('L'):
        return 'Device', 'L'
    if r.startswith('Y'):
        return 'Device', 'Crystal'
    if r.startswith('SW'):
        return 'Switch', 'SW_Push'
    if r.startswith('H'):
        return 'Mechanical', 'MountingHole'
    if r in ('J1', 'J2'):
        return 'Connector_Generic', 'Conn_01x40'
    if r == 'J3':
        return 'Connector', 'Conn_ARM_SWD_TagConnect_TC2030-NL'
    if r.startswith('D'):
        if 'LED' in fpn:
            return 'Device', 'LED'
        if v.startswith(('SMCJ', 'SMAJ', 'MMSZ')):
            return 'Device', 'D_Zener'
        if v.startswith('1N4148'):
            return 'Device', 'D'
        return 'Device', 'D_Schottky'
    if r == 'J102':
        return 'Connector', 'Conn_ARM_SWD_TagConnect_TC2030-NL'
    return {'STM32F407VGT6': ('MCU_ST_STM32F4', 'STM32F407VGTx'),
            'STM32F042K6T6': ('MCU_ST_STM32F0', 'STM32F042K6Tx'),
            'MCP6004': ('Amplifier_Operational', 'MCP6004'),
            'AD8628': ('Amplifier_Operational', 'AD8603'),
            'REF3033': ('Reference_Voltage', 'REF3033'),
            'VND14NV04': ('Device', 'Q_NMOS_GDS'),
            'AMS1117-3.3': ('Regulator_Linear', 'AMS1117-3.3'),
            'ULN2003AD': ('Transistor_Array', 'ULN2003A'),
            'LMV321IDBVR': ('Amplifier_Operational', 'LMV321'),
            'SN65HVD230DR': ('Interface_CAN_LIN', 'SN65HVD230')}[v]


POWER = {'GND': 'GND', '+3V3': '+3V3', '+5V': '+5V', '+12V': '+12V'}

SHEETS = [
    ('mcu', 'MCU', ['MCU & support', 'Status LEDs']),
    ('power', 'Power', ['Power']),
    ('outputs', 'Outputs', ['Injector / solenoid drivers', 'Ignition drivers', 'Relay / lamp drivers']),
    ('inputs', 'Inputs', ['Knock input', 'VR (crank/cam) input', 'Analog / hall / switch inputs']),
    ('connectors', 'Connectors and CAN', ['CAN', 'Mezzanine headers', 'Mechanical', 'Other']),
    ('wideband', 'Wideband controller', ['Wideband (FOME/rusEFI module)']),
]


# ---------------------------------------------------------------- the writer
class Sheet:
    def __init__(self, fname, title, root_uuid, sheet_uuid, page):
        self.fname, self.title = fname, title
        self.uuid = U()
        self.path = f'/{root_uuid}/{sheet_uuid}'
        self.page = page
        self.items = []
        self.libs = {}
        self.npwr = 0

    def lib(self, lib_id, sym):
        self.libs.setdefault(lib_id, sym)


def label_dir(ang):
    """symbol pin angle (towards body) -> outward unit vector in schematic coords and label angle"""
    a = (ang + 180) % 360
    dx, dy = round(math.cos(math.radians(a))), -round(math.sin(math.radians(a)))
    lab = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[(dx, dy)]
    return dx, dy, lab


pwr_syms = {}


def power_symbol(name):
    if name not in pwr_syms:
        pwr_syms[name] = lib_symbol('power', name)
    return pwr_syms[name]


def place_part(sh, p, X, Y, sym, pins, lib_id, pwr_counter, fp_paths):
    sh.lib(lib_id, sym)
    su = U()
    props = [f'(property "Reference" {Q(p["ref"])} (at {X:.2f} {Y - 2:.2f} 0) (effects (font (size 1.27 1.27))))',
             f'(property "Value" {Q(p["value"])} (at {X:.2f} {Y + 2:.2f} 0) (effects (font (size 1.27 1.27))))',
             f'(property "Footprint" {Q(p["fp"])} (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) hide))',
             f'(property "Datasheet" "" (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) hide))']
    if p['lcsc']:
        props.append(f'(property "LCSC" {Q(p["lcsc"])} (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    if p.get('desc'):
        props.append(f'(property "Note" {Q(p["desc"])} (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    # reference/value next to the body
    ys = [y for (_, _, _, y, _, _) in pins] or [0]
    top_y = Y - (max(ys) if ys else 0) - 3.81
    bot_y = Y - (min(ys) if ys else 0) + 3.81
    props[0] = props[0].replace(f'(at {X:.2f} {Y - 2:.2f} 0)', f'(at {X:.2f} {top_y:.2f} 0)')
    props[1] = props[1].replace(f'(at {X:.2f} {Y + 2:.2f} 0)', f'(at {X:.2f} {bot_y:.2f} 0)')
    pin_s = ' '.join(f'(pin {Q(num)} (uuid {U()}))' for num in dict.fromkeys(pp[0] for pp in pins))
    sh.items.append(f'(symbol (lib_id {Q(lib_id)}) (at {X:.2f} {Y:.2f} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) '
                    f'(uuid {su}) ' + ' '.join(props) + ' ' + pin_s +
                    f' (instances (project {Q(PROJECT)} (path {Q(sh.path)} (reference {Q(p["ref"])}) (unit 1)))))')
    fp_paths[p['ref']] = (sh, su)
    done = set()
    for (num, nm, px, py, ang, ln) in pins:
        x, y = X + px, Y - py
        key = (round(x, 2), round(y, 2))
        if key in done:
            continue
        done.add(key)
        net = p['pads'].get(num, '')
        dx, dy, lab = label_dir(ang)
        if not net:
            sh.items.append(f'(no_connect (at {x:.2f} {y:.2f}) (uuid {U()}))')
            continue
        ex, ey = x + dx * G, y + dy * G
        sh.items.append(f'(wire (pts (xy {x:.2f} {y:.2f}) (xy {ex:.2f} {ey:.2f})) (stroke (width 0) (type default)) (uuid {U()}))')
        if net in POWER:
            pname = POWER[net]
            psym, _ = power_symbol(pname)
            sh.lib(f'power:{pname}', psym)
            if pname == 'GND':
                rot = {(0, 1): 0, (0, -1): 180, (-1, 0): 270, (1, 0): 90}[(dx, dy)]
            else:
                rot = {(0, -1): 0, (0, 1): 180, (-1, 0): 90, (1, 0): 270}[(dx, dy)]
            pwr_counter[0] += 1
            ref = f'#PWR{pwr_counter[0]:03d}'
            sh.items.append(
                f'(symbol (lib_id {Q("power:" + pname)}) (at {ex:.2f} {ey:.2f} {rot}) (unit 1) (in_bom yes) (on_board yes) (dnp no) '
                f'(uuid {U()}) (property "Reference" {Q(ref)} (at {ex:.2f} {ey:.2f} 0) (effects (font (size 1.27 1.27)) hide)) '
                f'(property "Value" {Q(pname)} (at {ex:.2f} {ey:.2f} 0) (effects (font (size 1.0 1.0)))) '
                f'(property "Footprint" "" (at {ex:.2f} {ey:.2f} 0) (effects (font (size 1.27 1.27)) hide)) '
                f'(property "Datasheet" "" (at {ex:.2f} {ey:.2f} 0) (effects (font (size 1.27 1.27)) hide)) '
                f'(pin "1" (uuid {U()})) '
                f'(instances (project {Q(PROJECT)} (path {Q(sh.path)} (reference {Q(ref)}) (unit 1)))))')
        else:
            just = 'left' if lab in (0, 90) else 'right'
            sh.items.append(
                f'(global_label {Q(net)} (shape bidirectional) (at {ex:.2f} {ey:.2f} {lab}) (fields_autoplaced) '
                f'(effects (font (size 1.27 1.27)) (justify {just})) (uuid {U()}) '
                f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {ex:.2f} {ey:.2f} 0) '
                f'(effects (font (size 1.27 1.27)) hide)))')


def extents(pins, nets):
    """footprint of a placed symbol incl. stubs + labels, relative to its anchor"""
    if not pins:
        return -5, 5, -5, 5
    xs, ys = [], []
    for (num, nm, px, py, ang, ln) in pins:
        dx, dy, lab = label_dir(ang)
        net = nets.get(num, '')
        L = G + (len(net) * 1.05 + 3.5 if net and net not in POWER else 4.5)
        x, y = px, -py
        xs += [x, x + dx * L]; ys += [y, y + dy * L]
    return min(xs) - 2, max(xs) + 2, min(ys) - 4, max(ys) + 4


def snap(v):
    return round(v / G) * G


SHEET_OF = {}
for r in ['U1', 'FB1', 'Y1', 'R1', 'SW1', 'SW2', 'J3'] + [f'C{i}' for i in range(1, 16)] + \
        [f'R{i}' for i in range(2, 7)] + [f'D{i}' for i in range(1, 6)] + ['R72']:
    SHEET_OF[r] = 'mcu'
for r in ['U2', 'U3', 'U4', 'L1', 'L2'] + [f'D{i}' for i in range(6, 11)] + [f'R{i}' for i in range(7, 15)] + \
        [f'C{i}' for i in range(16, 30)] + ['F1', 'D12', 'C59']:
    SHEET_OF[r] = 'power'
for r in ['U5', 'U6', 'U7', 'RN1', 'C34', 'C35', 'U11', 'C57', 'C58', 'R71', 'D11'] + [f'Q{i}' for i in range(1, 9)] + \
        [f'R{i}' for i in range(15, 27)]:
    SHEET_OF[r] = 'outputs'
for r in ['J1', 'J2', 'U10', 'C56', 'H1', 'H2', 'H3', 'H4']:
    SHEET_OF[r] = 'connectors'
import wideband as _wb
for r in list(_wb.placement()) + ['U106', 'C118']:
    SHEET_OF[r] = 'wideband'
QUIET = {'GND', '+3V3', '+5V', '+12V', '+12V_F', 'V5_SENS', '+3V3A'}


def clusters(plist):
    """parts joined by shared signal nets, largest part first in each cluster"""
    parent = {p['ref']: p['ref'] for p in plist}

    def f(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    bynet = {}
    for p in plist:
        for n in set(p['pads'].values()):
            if n and n not in QUIET:
                bynet.setdefault(n, []).append(p['ref'])
    for refs in bynet.values():
        for r in refs[1:]:
            parent[f(r)] = f(refs[0])
    groups = {}
    for p in plist:
        groups.setdefault(f(p['ref']), []).append(p)
    out = []
    for g in groups.values():
        g.sort(key=lambda p: (-len(p['pads']), [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', p['ref'])]))
        out.append(g)
    out.sort(key=lambda g: (-len(g[0]['pads']), -len(g), g[0]['ref']))
    return out


def main():
    root_uuid = U()
    pwr_counter = [0]
    fp_paths = {}
    sheets = []
    for page, (fname, title, _) in enumerate(SHEETS, start=2):
        sheet_uuid = U()
        sh = Sheet(fname + '.kicad_sch', title, root_uuid, sheet_uuid, page)
        sh.sheet_uuid = sheet_uuid
        plist = [p for p in design.parts if SHEET_OF.get(p['ref'], 'inputs') == fname]
        resolved = {}
        for p in plist:
            spec = choose(p)
            if spec[0] is None:
                sym, pins = custom_symbol(spec[1]); lib_id = f'ECU:{spec[1]}'
            else:
                sym, pins = lib_symbol(*spec); lib_id = f'{spec[0]}:{spec[1]}'
            resolved[p['ref']] = (sym, pins, lib_id, extents(pins, p['pads']))
        # lay each cluster out as: main part, then its small parts in a grid to the right
        blocks = []
        for g in clusters(plist):
            head, rest = g[0], g[1:]
            hx0, hx1, hy0, hy1 = resolved[head['ref']][3]
            cw = max([resolved[p['ref']][3][1] - resolved[p['ref']][3][0] for p in rest] or [0]) + 2.54
            ch = max([resolved[p['ref']][3][3] - resolved[p['ref']][3][2] for p in rest] or [0]) + 2.54
            rows = max(1, int((hy1 - hy0) // ch)) if rest else 1
            ncol = math.ceil(len(rest) / rows) if rest else 0
            if rest and ncol > 6:
                ncol = 6; rows = math.ceil(len(rest) / ncol)
            bw = (hx1 - hx0) + 5.08 + ncol * cw
            bh = max(hy1 - hy0, rows * ch if rest else 0)
            blocks.append((g, bw, bh, cw, ch, rows))
        paper = ('A3', 420, 297)
        if sum(b[1] * b[2] for b in blocks) > 420 * 297 * 0.5:
            paper = ('A2', 594, 420)
        if sum(b[1] * b[2] for b in blocks) > 594 * 420 * 0.5:
            paper = ('A1', 841, 594)
        sh.paper = paper[0]
        W = paper[1] - 30
        x, y, rowh = 20.32, 25.4, 0
        for g, bw, bh, cw, ch, rows in blocks:
            if x + bw > W and x > 20.32:
                x, y, rowh = 20.32, y + rowh + 7.62, 0
            head, rest = g[0], g[1:]
            sym, pins, lib_id, (x0, x1, y0, y1) = resolved[head['ref']]
            place_part(sh, head, snap(x - x0), snap(y - y0), sym, pins, lib_id, pwr_counter, fp_paths)
            gx = x + (x1 - x0) + 5.08
            for i, p in enumerate(rest):
                c, r = divmod(i, rows)
                sym, pins, lib_id, (px0, px1, py0, py1) = resolved[p['ref']]
                cx, cy = gx + c * cw, y + r * ch
                place_part(sh, p, snap(cx - px0), snap(cy - py0), sym, pins, lib_id, pwr_counter, fp_paths)
            x += bw + 7.62
            rowh = max(rowh, bh)
        sheets.append(sh)
        title_block = (f'(title_block (title {Q("Miata ECU daughterboard - " + title)}) (date "2026-10-27") '
                       f'(rev "0.1") (comment 1 "Generated from scripts/design.py - same netlist as the routed board"))')
        libs = ' '.join(dump(s) for s in sh.libs.values())
        txt = (f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sh.uuid}) (paper {Q(sh.paper)}) {title_block} '
               f'(lib_symbols {libs}) ' + '\n'.join(sh.items) + ')')
        open(os.path.join(OUT, sh.fname), 'w').write(txt)
    # root sheet with one sheet symbol per block
    items = []
    for i, sh in enumerate(sheets):
        x, y = 30.48 + (i % 3) * 81.28, 50.8 + (i // 3) * 50.8
        items.append(f'(sheet (at {x:.2f} {y:.2f}) (size 66.04 30.48) (fields_autoplaced) '
                     f'(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid {sh.sheet_uuid}) '
                     f'(property "Sheetname" {Q(sh.title)} (at {x:.2f} {y - 0.71:.2f} 0) (effects (font (size 1.524 1.524)) (justify left bottom))) '
                     f'(property "Sheetfile" {Q(sh.fname)} (at {x:.2f} {y + 31.07:.2f} 0) (effects (font (size 1.27 1.27)) (justify left top))) '
                     f'(instances (project {Q(PROJECT)} (path {Q("/" + root_uuid)} (page {Q(str(sh.page))})))))')
    note = ('Miata ECU daughterboard rev 0.1. Each block sheet connects by global net labels; '
            'GND, +3V3, +5V and +12V use power symbols. J1 = power and outputs (top edge), '
            'J2 = sensor inputs and comms (bottom edge). Stack-up: 4 layers, In1 GND plane, In2 +3V3 plane.')
    items.append(f'(text {Q(note)} (at 30.48 160 0) (effects (font (size 1.524 1.524)) (justify left bottom)) (uuid {U()}))')
    root = (f'(kicad_sch (version 20230121) (generator eeschema) (uuid {root_uuid}) (paper "A4") '
            f'(title_block (title "Miata ECU daughterboard") (date "2026-10-27") (rev "0.1")) (lib_symbols) '
            + '\n'.join(items) + ' (sheet_instances (path "/" (page "1"))))')
    open(os.path.join(OUT, PROJECT + '.kicad_sch'), 'w').write(root)
    # map for back-annotating the board: ref -> /sheet_uuid/symbol_uuid
    with open(os.path.join(OUT, 'fp_paths.txt'), 'w') as f:
        for ref, (sh, su) in fp_paths.items():
            f.write(f'{ref} /{sh.sheet_uuid}/{su} {sh.title} {sh.fname}\n')
    print('sheets:', [s.fname for s in sheets], 'symbols:', len(fp_paths), 'power symbols:', pwr_counter[0])


if __name__ == '__main__':
    main()
