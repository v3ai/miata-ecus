"""
Wired KiCad 7 schematic for the Miata ECU daughterboard.

Local circuits (input conditioning, drivers, buck, LDOs, crystal, reset, LEDs...) are drawn
with real wires, junctions and power symbols. Connections that leave a block (MCU pins,
header pins, signals going to another sheet) use net labels, as a person would draw it.
Any pin not explicitly wired gets a stub + label / power symbol / no-connect automatically,
so the netlist always matches design.py exactly (checked by check_sch_netlist.py).
"""
import os, sys, math, re
sys.path.insert(0, os.path.dirname(__file__))
import design
from gen_sch import (lib_symbol, custom_symbol, power_symbol, choose, dump, Q, U, POWER, SHEETS,
                     SHEET_OF, PROJECT as _P)

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
PROJECT = sys.argv[2] if len(sys.argv) > 2 else 'miata_ecu_daughter'
G = 2.54
PARTS = {p['ref']: p for p in design.parts}


def sheet_of(ref):
    return SHEET_OF.get(ref, 'inputs')


NET_SHEETS = {}
for p in design.parts:
    for n in p['pads'].values():
        if n:
            NET_SHEETS.setdefault(n, set()).add(sheet_of(p['ref']))


def r2(v):
    return round(v, 3)


def base(ref):
    return ref.split('#')[0]


def unit_pins(sym, unit):
    """pins of one unit of a multi-unit symbol (plus the shared unit 0)"""
    from gen_sch import pins_of
    out = []
    for e in sym:
        if isinstance(e, list) and e and e[0] == 'symbol':
            u = int(e[1][1].rsplit('_', 2)[1])
            if u in (0, unit):
                out += pins_of(e)
    return out


class Sheet:
    def __init__(self, key, title, root_uuid, page):
        self.key, self.title = key, title
        self.fname = key + '.kicad_sch'
        self.uuid = U()
        self.sheet_uuid = U()
        self.path = f'/{root_uuid}/{self.sheet_uuid}'
        self.page = page
        self.items, self.libs = [], {}
        self.parts = {}          # ref -> dict
        self.touched = set()
        self.wires = []
        self.texts = []
        self.netpts = []
        self.fields = {}
        self.paper = 'A3'

    # ------------------------------------------------------------ symbols
    def place(self, ref, x, y, rot=0, unit=None):
        p = PARTS[ref]
        spec = choose(p)
        if spec[0] is None:
            sym, pins = custom_symbol(spec[1]); lib_id = f'ECU:{spec[1]}'
        else:
            sym, pins = lib_symbol(*spec); lib_id = f'{spec[0]}:{spec[1]}'
        self.libs.setdefault(lib_id, sym)
        key = ref
        if unit is not None:
            pins = unit_pins(sym, unit); key = f'{ref}#{unit}'
        x, y = r2(x), r2(y)
        self.parts[key] = dict(p=p, sym=sym, pins=pins, lib_id=lib_id, x=x, y=y, rot=rot, unit=unit or 1, ref=ref)
        return self

    def key_of(self, ref, num):
        if ref in self.parts:
            return ref
        for k, d in self.parts.items():
            if d['ref'] == ref and any(q[0] == num for q in d['pins']):
                return k
        raise KeyError((ref, num))

    def o2(self, ref, x, y, o):
        """two-pin part: o = 'v' pin1 on top, 'v-' pin1 bottom, 'h' pin1 left, 'h-' pin1 right"""
        for rot in (0, 90, 180, 270):
            self.place(ref, x, y, rot)
            px, py, _, _ = self.pin(ref, '1', mark=False)
            cx, cy = self.parts[ref]['x'], self.parts[ref]['y']
            ok = {'v': py < cy - 0.1, 'v-': py > cy + 0.1, 'h': px < cx - 0.1, 'h-': px > cx + 0.1}[o]
            if ok:
                return self
        raise ValueError(ref)

    def pin(self, ref, num, mark=True):
        ref = self.key_of(ref, num)
        d = self.parts[ref]
        for (n, nm, px, py, ang, ln) in d['pins']:
            if n == num:
                a = math.radians(d['rot'])
                x, y = px, -py
                xr = x * math.cos(a) + y * math.sin(a)
                yr = -x * math.sin(a) + y * math.cos(a)
                oa = math.radians(ang + 180)
                ox, oy = math.cos(oa), -math.sin(oa)
                dx = ox * math.cos(a) + oy * math.sin(a)
                dy = -ox * math.sin(a) + oy * math.cos(a)
                if mark:
                    self.touched.add((ref, num))
                return r2(d['x'] + xr), r2(d['y'] + yr), round(dx), round(dy)
        raise KeyError((ref, num))

    def P(self, s):
        if isinstance(s, str):
            ref, num = s.rsplit('.', 1)
            x, y, _, _ = self.pin(ref, num)
            return (x, y)
        return (r2(s[0]), r2(s[1]))

    # --------------------------------------------------------------- wiring
    def wire(self, *pts):
        refs = [s for s in pts if isinstance(s, str)]
        nets = {PARTS[base(s.rsplit('.', 1)[0])]['pads'].get(s.rsplit('.', 1)[1]) for s in refs}
        assert len(nets) <= 1, ('wire joins different nets', refs, nets)
        def pdir(sp):
            if isinstance(sp, str):
                ref, num = sp.rsplit('.', 1)
                return self.pin(ref, num)[2:]
            return None
        q = [self.P(s) for s in pts]
        for i, (a, b) in enumerate(zip(q, q[1:])):
            if a == b:
                continue
            if a[0] == b[0] or a[1] == b[1]:
                self.wires.append((a, b)); continue
            db, da = pdir(pts[i + 1]), pdir(pts[i])
            if db is not None:
                c = (b[0], a[1]) if db[0] == 0 else (a[0], b[1])
            elif da is not None:
                c = (a[0], b[1]) if da[0] == 0 else (b[0], a[1])
            else:
                c = (b[0], a[1])
            self.wires.append((a, c)); self.wires.append((c, b))

    def pwr(self, net, at, d='down'):
        """power symbol at a point; d = direction the symbol body points"""
        x, y = self.P(at)
        self.netpts.append(((x, y), net))
        psym, _ = power_symbol(POWER[net])
        self.libs.setdefault(f'power:{POWER[net]}', psym)
        if net == 'GND':
            rot = {'down': 0, 'up': 180, 'left': 270, 'right': 90}[d]
        else:
            rot = {'up': 0, 'down': 180, 'left': 90, 'right': 270}[d]
        CNT[0] += 1
        ref = f'#PWR{CNT[0]:03d}'
        vx, vy, vj = x, y, ''
        if d == 'down':
            vy = r2(y + 3.8)
        elif d == 'up':
            vy = r2(y - 3.8)
        else:
            vx = r2(x + (4.2 if d == 'right' else -4.2)); vj = ' (justify ' + ('left' if d == 'right' else 'right') + ')'
        self.items.append(
            f'(symbol (lib_id {Q("power:" + POWER[net])}) (at {x} {y} {rot}) (unit 1) (in_bom yes) (on_board yes) (dnp no) '
            f'(uuid {U()}) (property "Reference" {Q(ref)} (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide)) '
            f'(property "Value" {Q(POWER[net])} (at {vx} {vy} {({0: 0, 90: 270, 180: 0, 270: 90}[rot])}) (effects (font (size 1.27 1.27)){vj})) '
            f'(property "Footprint" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide)) '
            f'(property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide)) '
            f'(pin "1" (uuid {U()})) '
            f'(instances (project {Q(PROJECT)} (path {Q(self.path)} (reference {Q(ref)}) (unit 1)))))')

    def lab(self, net, at, d='right'):
        """net label; text extends in direction d from the point"""
        x, y = self.P(at)
        self.netpts.append(((x, y), net))
        ang = {'right': 0, 'up': 90, 'left': 180, 'down': 270}[d]
        just = 'left' if d in ('right', 'up') else 'right'
        if len(NET_SHEETS.get(net, ())) > 1 or net in ('VBAT_IN', 'VIGN_IN'):
            self.items.append(
                f'(global_label {Q(net)} (shape bidirectional) (at {x} {y} {ang}) (fields_autoplaced) '
                f'(effects (font (size 1.27 1.27)) (justify {just})) (uuid {U()}) '
                f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide)))')
        else:
            self.items.append(f'(label {Q(net)} (at {x} {y} {ang}) (fields_autoplaced) '
                              f'(effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid {U()}))')

    def text(self, s, x, y, size=1.8):
        self.texts.append(f'(text {Q(s)} (at {x} {y} 0) (effects (font (size {size} {size}) bold) (justify left bottom)) (uuid {U()}))')

    def stub(self, pinref, net=None, L=G):
        """short stub off a pin, ending in a label or power symbol"""
        ref, num = pinref.rsplit('.', 1)
        x, y, dx, dy = self.pin(ref, num)
        net = net or PARTS[base(ref)]['pads'].get(num, '')
        if not net:
            self.items.append(f'(no_connect (at {x} {y}) (uuid {U()}))')
            return
        ex, ey = r2(x + dx * L), r2(y + dy * L)
        self.wires.append(((x, y), (ex, ey)))
        d = {(1, 0): 'right', (-1, 0): 'left', (0, -1): 'up', (0, 1): 'down'}[(dx, dy)]
        if net in POWER:
            self.pwr(net, (ex, ey), d)
        else:
            self.lab(net, (ex, ey), d)

    def rail(self, ref, net, L=5.08, sym_at='start', pins=None):
        """tie every pin of ref on net (same side) with a short bus line and one power symbol"""
        d = self.parts[ref]
        nums = pins or [n for n, v in d['p']['pads'].items() if v == net]
        pts = [self.pin(ref, n) for n in nums]
        dx, dy = pts[0][2], pts[0][3]
        ends = []
        for (x, y, _, _) in pts:
            e = (r2(x + dx * L), r2(y + dy * L))
            self.wires.append(((x, y), e)); ends.append(e)
        ends.sort()
        if len(ends) > 1:
            self.wires.append((ends[0], ends[-1]))
        if net in POWER:
            if dy:  # top/bottom pins: horizontal bus, symbol at left end
                self.pwr(net, ends[0], 'up' if dy < 0 else 'down')
            else:   # side pins: vertical bus, symbol at the end that suits the net
                e = ends[-1] if net == 'GND' else ends[0]
                self.pwr(net, e, 'down' if net == 'GND' else 'up')
        else:
            self.lab(net, ends[0], 'up' if dy < 0 else 'down' if dy > 0 else ('right' if dx > 0 else 'left'))
        return ends

    # ------------------------------------------------------------- finalize
    def finish(self):
        for ref, d in self.parts.items():
            for (n, nm, px, py, ang, ln) in d['pins']:
                if (ref, n) not in self.touched:
                    self.stub(f'{ref}.{n}')
        # symbols
        fp_paths = {}
        for key, d in self.parts.items():
            ref = d['ref']
            p = d['p']; su = U()
            x, y, rot = d['x'], d['y'], d['rot']
            pp = [self.pin(key, n, mark=False)[:2] for n in dict.fromkeys(q[0] for q in d['pins'])]
            if key in self.fields:
                rp, vp, jr = self.fields[key]
            elif len(pp) == 2 and abs(pp[0][0] - pp[1][0]) < 0.01:
                rp, vp, jr = (x + 2.54, y - 1.27), (x + 2.54, y + 1.27), 'left'
            elif len(pp) == 2:
                big = 3.3 if d['lib_id'].split(':')[1].startswith(('LED', 'D_', 'SW', 'Crystal')) else 2.3
                rp, vp, jr = (x, y - big), (x, y + big), None
            else:
                def fpos(name):
                    for e in d['sym']:
                        if isinstance(e, list) and e and e[0] == 'property' and e[1][1] == name:
                            at = next(a for a in e if isinstance(a, list) and a[0] == 'at')
                            px, py = float(at[1]), -float(at[2])
                            a = math.radians(rot)
                            return (x + px * math.cos(a) + py * math.sin(a), y - px * math.sin(a) + py * math.cos(a))
                    return (x, y)
                rp, vp, jr = fpos('Reference'), fpos('Value'), None
            jj = f' (justify {jr})' if jr else ''
            fa = {0: 0, 90: 270, 180: 0, 270: 90}[rot]
            props = [f'(property "Reference" {Q(ref)} (at {r2(rp[0])} {r2(rp[1])} {fa}) (effects (font (size 1.27 1.27)){jj}))',
                     f'(property "Value" {Q(p["value"])} (at {r2(vp[0])} {r2(vp[1])} {fa}) (effects (font (size 1.27 1.27)){jj}))',
                     f'(property "Footprint" {Q(p["fp"])} (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))',
                     f'(property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))']
            if p['lcsc']:
                props.append(f'(property "LCSC" {Q(p["lcsc"])} (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))')
            if p.get('desc'):
                props.append(f'(property "Note" {Q(p["desc"])} (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))')
            pin_s = ' '.join(f'(pin {Q(n)} (uuid {U()}))' for n in dict.fromkeys(pp[0] for pp in d['pins']))
            self.items.append(
                f'(symbol (lib_id {Q(d["lib_id"])}) (at {x} {y} {rot}) (unit {d["unit"]}) (in_bom yes) (on_board yes) (dnp no) '
                f'(uuid {su}) ' + ' '.join(props) + ' ' + pin_s +
                f' (instances (project {Q(PROJECT)} (path {Q(self.path)} (reference {Q(ref)}) (unit {d["unit"]})))))')
            if ref not in fp_paths or d['unit'] == 1:
                fp_paths[ref] = f'/{self.sheet_uuid}/{su}'
        # wires (merge duplicates) and junctions
        segs = list(dict.fromkeys(tuple(sorted(s)) for s in self.wires))
        ends = {}
        for a, b in segs:
            ends[a] = ends.get(a, 0) + 1
            ends[b] = ends.get(b, 0) + 1
        pinpts = set()
        for ref, d in self.parts.items():
            for (n, *_r) in d['pins']:
                x, y, _, _ = self.pin(ref, n, mark=False)
                pinpts.add((x, y))
        junc = set()
        for pt, c in ends.items():
            if c + (1 if pt in pinpts else 0) >= 3:
                junc.add(pt)
        for a, b in segs:
            for pt in list(ends) + list(pinpts):
                if pt in (a, b):
                    continue
                if a[0] == b[0] == pt[0] and min(a[1], b[1]) < pt[1] < max(a[1], b[1]):
                    junc.add(pt)
                if a[1] == b[1] == pt[1] and min(a[0], b[0]) < pt[0] < max(a[0], b[0]):
                    junc.add(pt)
        # split segments at junctions/points lying on them so every connection is an endpoint
        pts_all = set(ends) | pinpts
        out = []
        for a, b in segs:
            cut = [a, b] + [pt for pt in pts_all if pt not in (a, b) and (
                (a[0] == b[0] == pt[0] and min(a[1], b[1]) < pt[1] < max(a[1], b[1])) or
                (a[1] == b[1] == pt[1] and min(a[0], b[0]) < pt[0] < max(a[0], b[0])))]
            cut.sort()
            out += list(zip(cut, cut[1:]))
        # connectivity self-check
        par = {}
        def f(x):
            while par.setdefault(x, x) != x:
                x = par[x]
            return x
        for a, b in out:
            par[f(a)] = f(b)
        nets = {}
        for ref, d in self.parts.items():
            for (n, *_r) in d['pins']:
                x, y, _, _ = self.pin(ref, n, mark=False)
                net = d['p']['pads'].get(n)
                if net:
                    nets.setdefault(f((x, y)), set()).add((net, f'{ref}.{n}'))
        for pt, net in self.netpts:
            nets.setdefault(f(pt), set()).add((net, 'label'))
        for k, v in nets.items():
            if len({a for a, _ in v}) > 1:
                print('SHORT on', self.key, sorted(v))
        named = {f(pt) for pt, _ in self.netpts}
        for k, v in nets.items():
            if k in named:
                continue
            net = next(iter(v))[0]
            segs_k = [(a, b) for a, b in out if f(a) == k and a[1] == b[1]] or \
                     [(a, b) for a, b in out if f(a) == k]
            if not segs_k:
                continue
            a, b = max(segs_k, key=lambda s: abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]))
            if a[1] == b[1]:
                x = round(((a[0] + b[0]) / 2) / 1.27) * 1.27
                x = min(max(x, min(a[0], b[0])), max(a[0], b[0]))
                self.items.append(f'(label {Q(net)} (at {r2(x)} {a[1]} 0) (fields_autoplaced) '
                                  f'(effects (font (size 1.0 1.0)) (justify left bottom)) (uuid {U()}))')
            else:
                y = round(((a[1] + b[1]) / 2) / 1.27) * 1.27
                y = min(max(y, min(a[1], b[1])), max(a[1], b[1]))
                self.items.append(f'(label {Q(net)} (at {a[0]} {r2(y)} 90) (fields_autoplaced) '
                                  f'(effects (font (size 1.0 1.0)) (justify left bottom)) (uuid {U()}))')
        for a, b in out:
            self.items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {U()}))')
        for j in junc:
            self.items.append(f'(junction (at {j[0]} {j[1]}) (diameter 0) (color 0 0 0 0) (uuid {U()}))')
        tb = (f'(title_block (title {Q(TITLE_PREFIX + self.title)}) (date {Q(DATE)}) (rev {Q(REV)}) '
              f'(comment 1 {Q(COMMENT)}))')
        txt = (f'(kicad_sch (version 20230121) (generator eeschema) (uuid {self.uuid}) (paper {Q(self.paper)}) {tb} '
               f'(lib_symbols {" ".join(dump(s) for s in self.libs.values())}) '
               + '\n'.join(self.items + self.texts) + ')')
        open(os.path.join(OUT, self.fname), 'w').write(txt)
        return fp_paths


CNT = [0]
REV, DATE = '0.4', '2026-10-29'
TITLE_PREFIX = 'Miata ECU daughterboard - '
COMMENT = 'Generated from scripts/design.py; netlist identical to the routed board'


def find(a, b=None, value=None):
    for p in design.parts:
        nets = list(p['pads'].values())
        if len(p['pads']) == 2 and (set(nets) == {a, b} if b else a in nets) and (value is None or p['value'] == value):
            return p['ref']
    raise KeyError((a, b, value))


def pin_of(ref, net):
    return f"{ref}." + next(k for k, v in PARTS[ref]['pads'].items() if v == net)


# ======================================================================= sheets
def sheet_inputs(s):
    s.text('Analog sensor inputs: 0-5 V -> 0-3.2 V for the ADC (5.6k / 10k, 10 nF)', 20.32, 22.86)

    def channel(x0, y0, n, kind):
        IN = 'IN_' + n
        AN = 'AN_' + n if kind == 'analog' else n
        ser = find(IN, AN)
        node = (x0 + 20.32, y0)
        s.o2(ser, x0 + 10.16, y0, 'h' if PARTS[ser]['pads']['1'] == IN else 'h-')
        s.lab(IN, (x0 - 2.54, y0), 'left')
        s.wire((x0 - 2.54, y0), pin_of(ser, IN))
        s.wire(pin_of(ser, AN), node)
        legs = []
        if kind in ('analog', 'switch'):
            legs = [find(AN, 'GND', '10k'), find(AN, 'GND', '10n')]
        elif kind == 'hall':
            legs = [find(AN, 'GND')]
        xs = [x0 + 20.32, x0 + 27.94][:len(legs)]
        for xx, r in zip(xs, legs):
            s.o2(r, xx, y0 + 6.35, 'v' if PARTS[r]['pads']['1'] == AN else 'v-')
            s.wire((xx, y0), pin_of(r, AN))
            s.stub(pin_of(r, 'GND'))
        s.wire(node, (x0 + 35.56, y0))
        s.lab(AN, (x0 + 35.56, y0), 'right')
        if kind == 'hall' or n in ('CLT', 'IAT'):
            pu = find('V5_SENS', IN)
            s.o2(pu, x0 + 2.54, y0 - 6.35, 'v' if PARTS[pu]['pads']['1'] == 'V5_SENS' else 'v-')
            s.wire(pin_of(pu, IN), (x0 + 2.54, y0))
            tp = s.P(pin_of(pu, 'V5_SENS'))
            s.wire(tp, (tp[0], tp[1] - 2.54), (tp[0] + 5.08, tp[1] - 2.54))
            s.lab('V5_SENS', (tp[0] + 5.08, tp[1] - 2.54), 'right')

    rows = lambda y: [y + i * 25.4 for i in range(5)]
    for (n, y) in zip(['TPS', 'MAP', 'CLT', 'IAT'], rows(40.64)):
        channel(30.48, y, n, 'analog')
    for (n, y) in zip(['AFR', 'AUX1', 'AUX2', 'AUX3'], rows(40.64)):
        channel(106.68, y, n, 'analog')
    s.text('Hall (open collector, 1k pull-up) and 12 V switch inputs', 182.88, 22.86)
    for (n, y, k) in zip(['HALL1', 'HALL2', 'SW1', 'SW2', 'SW3'], rows(40.64), ['hall', 'hall', 'switch', 'switch', 'switch']):
        channel(187.96, y, n, k)

    # ---- knock amplifier
    s.text('Knock: AC-coupled, biased to 1.65 V, gain 5.7', 271.78, 22.86)
    UX, UY = 320.04, 50.8
    s.place('U8', UX, UY)
    c_in = find('IN_KNOCK', 'KN_P')
    s.o2(c_in, UX - 30.48, UY - 2.54, 'h' if PARTS[c_in]['pads']['1'] == 'IN_KNOCK' else 'h-')
    s.lab('IN_KNOCK', (UX - 40.64, UY - 2.54), 'left')
    s.wire((UX - 40.64, UY - 2.54), pin_of(c_in, 'IN_KNOCK'))
    s.wire(pin_of(c_in, 'KN_P'), (UX - 20.32, UY - 2.54), 'U8.1')
    r45 = find('KN_P', 'KN_BIAS')
    s.o2(r45, UX - 20.32, UY + 6.35, 'v' if PARTS[r45]['pads']['1'] == 'KN_P' else 'v-')
    s.wire((UX - 20.32, UY - 2.54), pin_of(r45, 'KN_P'))
    s.stub(pin_of(r45, 'KN_BIAS'))
    r48 = find('KN_OUT', 'KN_N')
    r49 = find('KN_N', 'KN_BIAS')
    s.o2(r48, UX, UY + 20.32, 'h-' if PARTS[r48]['pads']['1'] == 'KN_OUT' else 'h')
    s.wire('U8.3', (UX - 10.16, UY + 2.54), (UX - 10.16, UY + 20.32), pin_of(r48, 'KN_N'))
    s.o2(r49, UX - 10.16, UY + 27.94, 'v' if PARTS[r49]['pads']['1'] == 'KN_N' else 'v-')
    s.wire((UX - 10.16, UY + 20.32), pin_of(r49, 'KN_N'))
    s.stub(pin_of(r49, 'KN_BIAS'))
    r50 = find('KN_OUT', 'AN_KNOCK')
    s.o2(r50, UX + 17.78, UY, 'h' if PARTS[r50]['pads']['1'] == 'KN_OUT' else 'h-')
    s.wire('U8.4', pin_of(r50, 'KN_OUT'))
    s.wire((UX + 10.16, UY), (UX + 10.16, UY + 20.32), pin_of(r48, 'KN_OUT'))
    c46 = find('AN_KNOCK', 'GND')
    s.o2(c46, UX + 27.94, UY + 6.35, 'v' if PARTS[c46]['pads']['1'] == 'AN_KNOCK' else 'v-')
    s.wire(pin_of(r50, 'AN_KNOCK'), (UX + 35.56, UY))
    s.wire((UX + 27.94, UY), pin_of(c46, 'AN_KNOCK'))
    s.stub(pin_of(c46, 'GND'))
    s.lab('AN_KNOCK', (UX + 35.56, UY), 'right')
    s.o2('C47', UX + 5.08, UY - 12.7, 'h')
    s.wire('U8.5', (UX - 2.54, UY - 12.7), 'C47.1')
    s.pwr('+3V3', (UX - 2.54, UY - 12.7), 'up')
    s.wire('C47.2', (UX + 12.7, UY - 12.7), (UX + 12.7, UY - 10.16))
    s.pwr('GND', (UX + 12.7, UY - 10.16), 'down')
    # bias divider
    bx, by = UX - 38.1, UY + 30.48
    r46 = find('+3V3', 'KN_BIAS'); r47 = find('KN_BIAS', 'GND', '100k'); c45 = find('KN_BIAS', 'GND', '1u')
    s.o2(r46, bx, by, 'v' if PARTS[r46]['pads']['1'] == '+3V3' else 'v-')
    s.o2(r47, bx, by + 12.7, 'v' if PARTS[r47]['pads']['1'] == 'KN_BIAS' else 'v-')
    s.o2(c45, bx + 7.62, by + 12.7, 'v' if PARTS[c45]['pads']['1'] == 'KN_BIAS' else 'v-')
    s.stub(pin_of(r46, '+3V3'))
    s.wire(pin_of(r46, 'KN_BIAS'), (bx, by + 6.35), pin_of(r47, 'KN_BIAS'))
    s.wire((bx, by + 6.35), (bx + 7.62, by + 6.35), pin_of(c45, 'KN_BIAS'))
    s.wire((bx + 7.62, by + 6.35), (bx + 15.24, by + 6.35))
    s.lab('KN_BIAS', (bx + 15.24, by + 6.35), 'right')
    s.stub(pin_of(r47, 'GND')); s.stub(pin_of(c45, 'GND'))

    # ---- VR conditioner
    s.text('Crank / cam VR inputs: MAX9926 (outputs inverted, so harness + goes to IN-)', 271.78, 129.54)
    VX, VY = 355.6, 175.26
    s.place('U9', VX, VY)
    nodex = VX - 38.1
    rows = [('VR1_N', 'VR1_A', 'VR1_INP', '16', VY - 20.32, VX - 25.4),
            ('VR1_P', 'VR1_B', 'VR1_INN', '15', VY - 12.7, VX - 30.48),
            ('VR2_N', 'VR2_A', 'VR2_INP', '9', VY + 5.08, VX - 30.48),
            ('VR2_P', 'VR2_B', 'VR2_INN', '10', VY + 12.7, VX - 25.4)]
    for (src, mid, dst, pn, y, jx) in rows:
        ra, rb = find(src, mid), find(mid, dst)
        s.o2(ra, nodex - 17.78, y, 'h' if PARTS[ra]['pads']['1'] == src else 'h-')
        s.o2(rb, nodex - 7.62, y, 'h' if PARTS[rb]['pads']['1'] == mid else 'h-')
        s.lab(src, (nodex - 25.4, y), 'left')
        s.wire((nodex - 25.4, y), pin_of(ra, src))
        s.wire(pin_of(ra, mid), pin_of(rb, mid))
        s.wire(pin_of(rb, dst), (nodex, y), (jx, y))
        px, py = s.P(f'U9.{pn}')
        s.wire((jx, y), (jx, py), f'U9.{pn}')
    for (cap_a, cap_b, y) in [('VR1_INP', 'VR1_INN', VY - 20.32), ('VR2_INP', 'VR2_INN', VY + 5.08)]:
        c = find(cap_a, cap_b)
        s.o2(c, nodex, y + 3.81, 'v' if PARTS[c]['pads']['1'] == cap_a else 'v-')
    for (pn, net, yy) in [('4', 'VR1_OUT', VY - 10.16), ('5', 'VR2_OUT', VY - 7.62)]:
        pu = find('+3V3', net)
        px, py = s.P(f'U9.{pn}')
        xx = VX + 22.86 if pn == '4' else VX + 30.48
        s.o2(pu, xx, py - 7.62, 'v' if PARTS[pu]['pads']['1'] == '+3V3' else 'v-')
        s.wire(f'U9.{pn}', (xx, py), (VX + 38.1, py))
        s.wire((xx, py), pin_of(pu, net))
        s.stub(pin_of(pu, '+3V3'))
        s.lab(net, (VX + 38.1, py), 'right')
    s.o2('C50', VX - 21.59, VY + 24.13, 'v')
    s.wire('U9.14', (VX - 21.59, VY), 'C50.1')
    s.wire('C50.1', (VX - 27.94, VY + 20.32)); s.pwr('+5V', (VX - 27.94, VY + 20.32), 'up')
    s.stub('C50.2')
    s.wire('U9.11', (VX - 19.05, VY + 2.54), (VX - 19.05, VY + 5.08)); s.pwr('GND', (VX - 19.05, VY + 5.08), 'down')
    s.rail('U9', 'GND', pins=['1', '8', '3', '6', '13', '12'])


def sheet_outputs(s):
    s.text('Protected low-side drivers (AUIPS2041L): injectors, IACV, VVT, boost, alternator', 20.32, 22.86)

    def lowside(q, n, x0, y0):
        CTL, OUT = n + '_CTL', 'OUT_' + n
        s.place(q, x0 + 22.86, y0)
        pd = find(CTL, 'GND')
        s.lab(CTL, (x0 - 2.54, y0), 'left')
        s.wire((x0 - 2.54, y0), f'{q}.1')
        s.o2(pd, x0 + 2.54, y0 + 6.35, 'v' if PARTS[pd]['pads']['1'] == CTL else 'v-')
        s.wire((x0 + 2.54, y0), pin_of(pd, CTL))
        s.stub(pin_of(pd, 'GND'))
        s.wire(f'{q}.3', (x0 + 12.7, y0 + 2.54), (x0 + 12.7, y0 + 7.62))
        s.pwr('GND', (x0 + 12.7, y0 + 7.62), 'down')
        s.wire(f'{q}.2', (x0 + 35.56, y0), (x0 + 40.64, y0))
        s.wire(f'{q}.4', (x0 + 35.56, y0 + 2.54), (x0 + 35.56, y0))
        s.lab(OUT, (x0 + 40.64, y0), 'right')

    for i, n in enumerate(design.HS_OUT):
        col, row = divmod(i, 4)
        lowside(f'Q{i + 1}', n, 30.48 + col * 101.6, 45.72 + row * 22.86)

    s.text('Coil-on-plug logic outputs (TC4427, 5 V push-pull through 100 R)', 20.32, 147.32)
    for k, (u, a, b, cvdd) in enumerate([('U6', 'IGN1', 'IGN2', 'C34'), ('U7', 'IGN3', 'IGN4', 'C35')]):
        X, Y = 60.96 + k * 101.6, 170.18
        s.place(u, X, Y)
        for pn, n in (('2', a), ('4', b)):
            s.stub(f'{u}.{pn}')
        r_a, r_b = find(a + '_DRV', 'OUT_' + a), find(b + '_DRV', 'OUT_' + b)
        s.o2(r_a, X + 25.4, Y - 2.54, 'h' if PARTS[r_a]['pads']['1'] == a + '_DRV' else 'h-')
        s.o2(r_b, X + 25.4, Y + 5.08, 'h' if PARTS[r_b]['pads']['1'] == b + '_DRV' else 'h-')
        s.wire(f'{u}.7', (X + 15.24, Y - 2.54), pin_of(r_a, a + '_DRV'))
        s.wire(f'{u}.5', (X + 15.24, Y), (X + 15.24, Y + 5.08), pin_of(r_b, b + '_DRV'))
        for r, n in ((r_a, a), (r_b, b)):
            p = s.P(pin_of(r, 'OUT_' + n))
            s.wire(p, (p[0] + 5.08, p[1]))
            s.lab('OUT_' + n, (p[0] + 5.08, p[1]), 'right')
        s.o2(cvdd, X - 17.78, Y + 16.51, 'v')
        s.fields[cvdd] = ((X - 20.32, Y + 15.24), (X - 20.32, Y + 17.78), 'right')
        s.wire(f'{u}.6', (X - 17.78, Y + 2.54), f'{cvdd}.1')
        s.wire(f'{cvdd}.1', (X - 25.4, Y + 12.7))
        s.pwr('+5V', (X - 25.4, Y + 12.7), 'up')
        s.stub(f'{cvdd}.2')
        s.wire(f'{u}.3', (X - 13.97, Y + 5.08), (X - 13.97, Y + 10.16))
        s.pwr('GND', (X - 13.97, Y + 10.16), 'down')
    s.place('RN1', 60.96, 215.9, 90)
    s.rail('RN1', 'GND')
    s.text('Ignition inputs pulled low (coils stay off while the MCU boots)', 20.32, 200.66, 1.27)

    s.text('Relay, lamp and tach outputs (ULN2003, flyback to +12V)', 254.0, 147.32)
    s.place('U5', 299.72, 180.34)


def sheet_power(s):
    Y0 = 50.8
    s.text('Input protection and 5 V buck (LMR14020, 5 V / 2 A)', 20.32, 30.48)
    s.lab('VBAT_IN', (25.4, Y0), 'left')
    s.o2('D6', 38.1, Y0 + 6.35, 'v')
    s.o2('D7', 48.26, Y0, 'h-')
    s.wire((25.4, Y0), 'D6.1')
    s.wire((38.1, Y0), 'D7.2')
    s.stub('D6.2')
    B = (58.42, Y0)
    s.wire('D7.1', B)
    s.pwr('+12V', B, 'up')
    s.o2('D8', 48.26, Y0 + 20.32, 'h-')
    s.lab('VIGN_IN', (30.48, Y0 + 20.32), 'left')
    s.wire((30.48, Y0 + 20.32), 'D8.2')
    s.wire('D8.1', (58.42, Y0 + 20.32), B)
    s.o2('R7', 66.04, Y0 + 6.35, 'v'); s.o2('C16', 66.04, Y0 + 16.51, 'v')
    s.wire(B, (66.04, Y0), 'R7.1'); s.wire('R7.2', 'C16.1'); s.stub('C16.2')
    s.o2('L1', 78.74, Y0, 'h')
    s.wire((66.04, Y0), 'L1.1')
    s.o2('C17', 91.44, Y0 + 6.35, 'v'); s.o2('C18', 104.14, Y0 + 6.35, 'v')
    X = 142.24
    s.place('U2', X, Y0 + 5.08)
    L = X - 13.97
    s.wire('L1.2', (91.44, Y0), (104.14, Y0), 'U2.2')
    s.wire((91.44, Y0), 'C17.1'); s.wire((104.14, Y0), 'C18.1'); s.stub('C17.2'); s.stub('C18.2')
    s.wire('U2.3', (L - 3.81, Y0 + 2.54), (L - 3.81, Y0))
    s.o2('R8', 111.76, Y0 + 22.86, 'v'); s.o2('C20', 121.92, Y0 + 22.86, 'v')
    s.wire('U2.4', 'R8.1'); s.stub('R8.2')
    s.wire('U2.6', 'C20.1'); s.stub('C20.2')
    s.wire('U2.7', (L - 3.81, Y0 + 10.16), (L - 3.81, Y0 + 15.24))
    s.wire('U2.9', (L - 3.81, Y0 + 12.7))
    s.pwr('GND', (L - 3.81, Y0 + 15.24), 'down')
    R = X + 13.97
    s.o2('C19', R + 7.62, Y0 - 7.62, 'h')
    s.wire('U2.1', (R + 2.54, Y0), (R + 2.54, Y0 - 7.62), 'C19.1')
    s.wire('C19.2', (R + 12.7, Y0 - 7.62), (R + 12.7, Y0 + 2.54))
    s.o2('D9', R + 12.7, Y0 + 10.16, 'v'); s.o2('L2', R + 22.86, Y0 + 2.54, 'h')
    s.wire('U2.8', (R + 12.7, Y0 + 2.54), 'L2.1')
    s.wire((R + 12.7, Y0 + 2.54), 'D9.1'); s.stub('D9.2')
    VO = R + 33.02
    s.o2('R10', R + 5.08, Y0 + 38.1, 'v')
    s.wire('U2.5', (R + 5.08, Y0 + 5.08), (R + 5.08, Y0 + 30.48))
    s.wire((R + 5.08, Y0 + 30.48), 'R10.1'); s.stub('R10.2')
    s.o2('R9', R + 19.05, Y0 + 30.48, 'h-'); s.o2('C21', R + 19.05, Y0 + 22.86, 'h-')
    s.wire((R + 5.08, Y0 + 30.48), 'R9.2')
    s.wire((R + 5.08, Y0 + 22.86), 'C21.2')
    s.wire('R9.1', (VO, Y0 + 30.48), (VO, Y0 + 2.54))
    s.wire('C21.1', (VO, Y0 + 22.86))
    s.o2('C22', VO + 7.62, Y0 + 8.89, 'v'); s.o2('C23', VO + 17.78, Y0 + 8.89, 'v')
    s.o2('D10', VO + 33.02, Y0 + 2.54, 'h')
    s.wire('L2.2', (VO, Y0 + 2.54), (VO + 7.62, Y0 + 2.54), (VO + 17.78, Y0 + 2.54), 'D10.1')
    s.wire((VO + 7.62, Y0 + 2.54), 'C22.1'); s.wire((VO + 17.78, Y0 + 2.54), 'C23.1')
    s.stub('C22.2'); s.stub('C23.2')
    s.pwr('+5V', (VO, Y0 + 2.54), 'up')
    s.wire('D10.2', (VO + 45.72, Y0 + 2.54)); s.lab('USB_VBUS', (VO + 45.72, Y0 + 2.54), 'right')
    s.text('USB VBUS powers the logic on the bench', VO + 22.86, Y0 + 22.86, 1.27)
    s.text('Fsw ~ 1 MHz (RT 10k); Vout = 0.75 V x (1 + 68k/12k) = 5.0 V', X - 12.7, Y0 + 55.88, 1.27)

    Y1 = 134.62
    s.text('3.3 V LDO', 106.68, Y1 - 17.78)
    s.place('U4', 127.0, Y1)
    s.fields['U4'] = ((127.0, Y1 - 7.62), (127.0, Y1 - 5.08), None)
    s.o2('C26', 111.76, Y1 + 6.35, 'v'); s.o2('C27', 142.24, Y1 + 6.35, 'v')
    s.wire((111.76, Y1), 'U4.3'); s.wire((111.76, Y1), 'C26.1'); s.pwr('+5V', (111.76, Y1), 'up')
    s.wire('U4.2', (142.24, Y1), 'C27.1'); s.pwr('+3V3', (142.24, Y1), 'up')
    s.stub('C26.2'); s.stub('C27.2'); s.stub('U4.1')
    s.text('Protected 5 V sensor supply (TLS115 tracks +5V)', 167.64, Y1 - 17.78)
    UX = 195.58
    s.place('U3', UX, Y1)
    s.o2('C24', UX - 27.94, Y1 - 1.27, 'v')
    s.wire('U3.8', (UX - 13.97, Y1 - 5.08), (UX - 27.94, Y1 - 5.08), 'C24.1')
    s.wire('U3.7', (UX - 13.97, Y1 - 2.54), (UX - 13.97, Y1 - 5.08))
    s.pwr('+12V', (UX - 13.97, Y1 - 5.08), 'up'); s.stub('C24.2')
    s.stub('U3.5', L=5.08)
    s.wire('U3.9', (UX - 13.97, Y1 + 5.08), (UX - 13.97, Y1 + 2.54), 'U3.3')
    s.wire((UX - 13.97, Y1 + 5.08), (UX - 13.97, Y1 + 7.62))
    s.pwr('GND', (UX - 13.97, Y1 + 7.62), 'down')
    s.o2('C25', UX + 15.24, Y1 + 1.27, 'v')
    s.wire('U3.1', (UX + 15.24, Y1 - 5.08), (UX + 22.86, Y1 - 5.08)); s.wire((UX + 15.24, Y1 - 5.08), 'C25.1'); s.stub('C25.2')
    s.lab('V5_SENS', (UX + 22.86, Y1 - 5.08), 'right')

    s.text('Battery / ignition sense (divide by 5.85)', 20.32, Y1 - 17.78)
    for k, (rin, rg, cf, node) in enumerate([('R11', 'R12', 'C28', 'AN_VBATT'), ('R13', 'R14', 'C29', 'AN_VIGN')]):
        x = 30.48 + k * 38.1
        s.o2(rin, x, Y1, 'v'); s.o2(rg, x, Y1 + 12.7, 'v'); s.o2(cf, x + 10.16, Y1 + 12.7, 'v')
        s.stub(f'{rin}.1')
        s.wire(f'{rin}.2', (x, Y1 + 6.35), f'{rg}.1')
        s.wire((x, Y1 + 6.35), (x + 10.16, Y1 + 6.35), f'{cf}.1')
        s.wire((x + 10.16, Y1 + 6.35), (x + 17.78, Y1 + 6.35)); s.lab(node, (x + 17.78, Y1 + 6.35), 'right')
        s.stub(f'{rg}.2'); s.stub(f'{cf}.2')


def sheet_mcu(s):
    s.paper = 'A3'
    s.place('U1', 215.9, 147.32)
    top3 = [n for n, v in PARTS['U1']['pads'].items() if v == '+3V3' and s.pin('U1', n, mark=False)[3] < 0]
    s.rail('U1', '+3V3', pins=top3)
    s.rail('U1', 'GND')
    ytop = min(s.pin('U1', n, mark=False)[1] for n in top3)
    s.fields['U1'] = ((215.9 + 10.16, ytop - 1.27), (215.9 + 10.16, ytop + 1.27), 'left')
    s.text('Decoupling: one 100 nF per VDD pin, 2 x 4.7 uF bulk', 20.32, 22.86)
    caps = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
    for i, c in enumerate(caps):
        x = 30.48 + i * 7.62
        s.o2(c, x, 38.1, 'v')
        s.wire((x, 31.75), f'{c}.1'); s.wire(f'{c}.2', (x, 44.45))
    s.wire((25.4, 31.75), (30.48 + 7 * 7.62, 31.75)); s.wire((25.4, 44.45), (30.48 + 7 * 7.62, 44.45))
    s.pwr('+3V3', (25.4, 31.75), 'up'); s.pwr('GND', (25.4, 44.45), 'down')
    s.text('Core regulator caps', 101.6, 22.86, 1.27)
    for i, (c, n) in enumerate([('C9', 'VCAP1'), ('C10', 'VCAP2')]):
        s.o2(c, 106.68 + i * 10.16, 38.1, 'v')
        s.stub(f'{c}.1'); s.stub(f'{c}.2')
    s.text('Analog supply filter', 20.32, 60.96)
    s.o2('FB1', 33.02, 71.12, 'h'); s.o2('C11', 43.18, 77.47, 'v'); s.o2('C12', 50.8, 77.47, 'v')
    s.wire((25.4, 71.12), 'FB1.1'); s.pwr('+3V3', (25.4, 71.12), 'up')
    s.wire('FB1.2', (43.18, 71.12), (50.8, 71.12), (58.42, 71.12))
    s.wire((43.18, 71.12), 'C11.1'); s.wire((50.8, 71.12), 'C12.1'); s.stub('C11.2'); s.stub('C12.2')
    s.lab('+3V3A', (58.42, 71.12), 'right')
    s.text('8 MHz HSE crystal', 20.32, 96.52)
    s.o2('Y1', 40.64, 106.68, 'h'); s.o2('C13', 30.48, 114.3, 'v'); s.o2('C14', 50.8, 114.3, 'v')
    s.wire((22.86, 106.68), (30.48, 106.68), 'Y1.1'); s.wire((30.48, 106.68), 'C13.1')
    s.wire('Y1.2', (50.8, 106.68), (58.42, 106.68)); s.wire((50.8, 106.68), 'C14.1')
    s.stub('C13.2'); s.stub('C14.2')
    s.lab('HSE_IN', (22.86, 106.68), 'left'); s.lab('HSE_OUT', (58.42, 106.68), 'right')
    s.text('BOOT0 (hold for DFU) and reset', 20.32, 132.08)
    s.o2('SW1', 33.02, 142.24, 'h'); s.o2('R1', 45.72, 148.59, 'v')
    s.wire((25.4, 142.24), 'SW1.1'); s.pwr('+3V3', (25.4, 142.24), 'up')
    s.wire('SW1.2', (45.72, 142.24), (53.34, 142.24)); s.wire((45.72, 142.24), 'R1.1'); s.stub('R1.2')
    s.lab('BOOT0', (53.34, 142.24), 'right')
    s.o2('SW2', 40.64, 167.64, 'h'); s.o2('C15', 25.4, 173.99, 'v')
    s.wire((17.78, 167.64), (25.4, 167.64), 'SW2.1'); s.wire((25.4, 167.64), 'C15.1'); s.stub('C15.2')
    s.lab('NRST', (17.78, 167.64), 'left')
    s.wire('SW2.2', (50.8, 167.64), (50.8, 170.18)); s.pwr('GND', (50.8, 170.18), 'down')
    s.text('SWD (Tag-Connect TC2030-NL pads)', 20.32, 195.58)
    s.place('J3', 38.1, 218.44)
    s.text('Status LEDs', 330.2, 22.86)
    for i, (r, d, net) in enumerate([('R2', 'D1', 'LED_RUN'), ('R3', 'D2', 'LED_COMM'), ('R4', 'D3', 'LED_WARN'),
                                     ('R5', 'D4', 'LED_ERR'), ('R6', 'D5', '+3V3')]):
        y = 35.56 + i * 12.7
        s.o2(r, 345.44, y, 'h' if PARTS[r]['pads']['1'] == net else 'h-')
        s.o2(d, 360.68, y, 'h-')
        if net == '+3V3':
            s.wire((335.28, y), pin_of(r, net)); s.pwr('+3V3', (335.28, y), 'up')
        else:
            s.wire((335.28, y), pin_of(r, net)); s.lab(net, (335.28, y), 'left')
        s.wire(pin_of(r, PARTS[d]['pads']['2']), f'{d}.2')
        s.wire(f'{d}.1', (368.3, y), (368.3, y + 2.54)); s.pwr('GND', (368.3, y + 2.54), 'down')


def sheet_connectors(s):
    s.text('J1: power in and outputs (top edge)', 20.32, 22.86)
    s.place('J1', 50.8, 86.36)
    s.text('J2: sensor inputs and comms (bottom edge)', 127.0, 22.86)
    s.place('J2', 157.48, 86.36)
    s.text('CAN transceiver (termination on the motherboard)', 233.68, 22.86)
    s.place('U10', 271.78, 55.88)
    s.o2('C56', 281.94, 44.45, 'h')
    s.wire('U10.3', (271.78, 44.45), 'C56.1'); s.pwr('+3V3', (271.78, 44.45), 'up')
    s.wire('C56.2', (289.56, 44.45), (289.56, 46.99)); s.pwr('GND', (289.56, 46.99), 'down')
    s.text('Mounting holes', 233.68, 101.6)
    for i in range(4):
        s.place(f'H{i + 1}', 238.76 + i * 12.7, 111.76)


def sheet_wideband(s):
    """On-board wideband controller, drawn like the FOME module schematic it comes from
    (github.com/mck1117/wideband, hardware/board_module rev C). Refs = module refs + 100."""
    s.paper = 'A3'
    s.text('Wideband O2 controller: FOME / rusEFI open-source wideband module (MIT), rev C circuit, laid out on this board', 20.32, 20.32)
    s.text('Refs are the module refs + 100 (module R31 = R131). Talks to the main MCU over the shared CAN bus.', 20.32, 25.4, 1.27)

    def oa(ref, unit, X, Y):
        s.place(ref, X, Y, 0, unit)
        return (X - 7.62, Y - 2.54), (X - 7.62, Y + 2.54), (X + 7.62, Y)     # +, -, out

    # ---- A: virtual ground (VM = VDDA/2, buffered) --------------------------------
    s.text('Virtual ground', 20.32, 35.56)
    P, N, O = oa('U101', 4, 55.88, 50.8)          # + 48.26, - 53.34, out 63.5
    s.o2('R101', 33.02, 43.18, 'v'); s.o2('R102', 33.02, 58.42, 'v'); s.o2('C101', 22.86, 58.42, 'v')
    s.stub('R101.1')
    s.wire('R101.2', (33.02, P[1]), 'U101.12')
    s.wire((33.02, P[1]), 'R102.1'); s.stub('R102.2')
    s.wire((33.02, P[1]), (22.86, P[1]), 'C101.1'); s.stub('C101.2')
    s.wire('U101.13', (45.72, N[1]), (45.72, 62.23), (66.04, 62.23), (66.04, O[1]))
    s.wire('U101.14', (66.04, O[1]))
    s.o2('R109', 73.66, O[1], 'h-')
    s.wire((66.04, O[1]), 'R109.2'); s.wire((66.04, O[1]), (66.04, 43.18)); s.lab('WB_VM', (66.04, 43.18), 'up')
    s.o2('C104', 83.82, 57.15, 'v')
    s.wire('R109.1', (83.82, O[1]), 'C104.1'); s.stub('C104.2')
    s.wire((83.82, O[1]), (91.44, O[1])); s.lab('LSU_VM', (91.44, O[1]), 'right')

    # ---- B: Nernst sense, Un_sense = 2.7 x (Un - Vm) ------------------------------
    s.text('Nernst sense', 116.84, 35.56)
    P, N, O = oa('U101', 2, 147.32, 50.8)          # + (139.7,48.26) - (139.7,53.34) out (154.94,50.8)
    s.o2('R104', 127.0, P[1], 'h'); s.stub('R104.1'); s.wire('R104.2', 'U101.5')
    s.o2('R105', 134.62, 40.64, 'v-')
    s.wire((134.62, P[1]), 'R105.1')
    s.wire('R105.2', (134.62, 35.56 + 1.27)); s.pwr('GND', (134.62, 36.83), 'up')
    s.o2('R103', 124.46, 58.42, 'h'); s.stub('R103.1'); s.wire('R103.2', (134.62, 58.42))
    s.wire((134.62, N[1]), 'U101.6')
    s.o2('R107', 147.32, 63.5, 'h')
    s.wire((134.62, N[1]), (134.62, 63.5), 'R107.1')
    s.wire('R107.2', (160.02, 63.5), (160.02, O[1]))
    s.wire('U101.7', (160.02, O[1]), (167.64, O[1])); s.lab('WB_UN_SENSE', (167.64, O[1]), 'right')

    # ---- C: analog reference (VDDA = 3.3 V REF3033 from +5V) ------------------------
    s.text('ADC / analog reference', 200.66, 35.56)
    s.place('U103', 220.98, 53.34)                 # IN (218.44,45.72) OUT (228.6,53.34) GND (218.44,60.96)
    s.o2('C117', 205.74, 49.53, 'v'); s.o2('C108', 198.12, 49.53, 'v')
    s.wire('U103.1', (218.44, 43.18), (205.74, 43.18), 'C117.1'); s.wire((205.74, 43.18), (198.12, 43.18), 'C108.1')
    s.pwr('+5V', (218.44, 43.18), 'up'); s.stub('C117.2'); s.stub('C108.2'); s.stub('U103.3')
    s.o2('C107', 236.22, 59.69, 'v'); s.o2('C109', 246.38, 59.69, 'v')
    s.wire('U103.2', (236.22, 53.34), (246.38, 53.34), (254.0, 53.34))
    s.wire((236.22, 53.34), 'C107.1'); s.wire((246.38, 53.34), 'C109.1'); s.stub('C107.2'); s.stub('C109.2')
    s.lab('WB_VDDA', (254.0, 53.34), 'right')

    # ---- D: CAN transceiver on the shared bus --------------------------------------
    s.text('CAN (same bus as the main MCU; rusEFI reads lambda over CAN)', 289.56, 35.56)
    s.place('U106', 322.58, 55.88)
    s.o2('C118', 332.74, 43.18, 'h')
    s.wire('U106.3', (322.58, 43.18), 'C118.1'); s.pwr('+3V3', (322.58, 43.18), 'up')
    s.wire('C118.2', (340.36, 43.18), (340.36, 45.72)); s.pwr('GND', (340.36, 45.72), 'down')
    s.stub('U106.1'); s.stub('U106.4'); s.stub('U106.5'); s.stub('U106.8'); s.stub('U106.2')
    s.stub('U106.6'); s.stub('U106.7')

    # ---- E: pump current driver ----------------------------------------------------
    s.text('Pump current driver (Ip DAC -> LSU pump cell)', 20.32, 86.36)
    P, N, O = oa('U101', 1, 63.5, 111.76)          # + (55.88,109.22) - (55.88,114.3) out (71.12,111.76)
    s.o2('R132', 40.64, 104.14, 'h-'); s.stub('R132.2'); s.wire('R132.1', (50.8, 104.14))
    s.wire((50.8, P[1]), 'U101.3')
    s.o2('R131', 40.64, N[1], 'h'); s.stub('R131.1'); s.wire('R131.2', 'U101.2')
    s.o2('R133', 63.5, 127.0, 'h-'); s.o2('C103', 63.5, 134.62, 'h-')
    s.wire((50.8, N[1]), (50.8, 134.62), 'C103.2'); s.wire((50.8, 127.0), 'R133.2')
    s.wire('R133.1', (76.2, 127.0)); s.wire('C103.1', (76.2, 134.62), (76.2, O[1]))
    s.wire('U101.1', (76.2, O[1]), (83.82, O[1]))
    s.o2('R108', 83.82, 119.38, 'v-')
    s.wire((83.82, O[1]), 'R108.2')
    s.wire('R108.1', (83.82, 127.0), (99.06, 127.0)); s.lab('LSU_RT', (99.06, 127.0), 'right')
    s.o2('R134', 63.5, 99.06, 'h-')
    s.wire((50.8, P[1]), (50.8, 99.06), 'R134.2')
    s.wire('R134.1', (83.82, 99.06)); s.lab('LSU_RT', (83.82, 99.06), 'right')

    # ---- F: pump current sense, Ip_sense = 10 x (LSU_Ip - LSU_Rtrim) -----------------
    s.text('Pump current sense', 121.92, 86.36)
    s.place('U105', 167.64, 111.76)                # + (160.02,109.22) - (160.02,114.3) out (175.26,111.76)
    s.o2('R110', 129.54, 111.76, 'v-')
    s.o2('R112', 147.32, 104.14, 'h-'); s.o2('R111', 147.32, 119.38, 'h-')
    s.wire('R110.2', (129.54, 104.14), 'R112.2')
    s.wire((129.54, 104.14), (121.92, 104.14)); s.lab('LSU_IP', (121.92, 104.14), 'left')
    s.wire('R110.1', (129.54, 119.38), 'R111.2')
    s.wire((129.54, 119.38), (121.92, 119.38)); s.lab('LSU_RT', (121.92, 119.38), 'left')
    s.wire('R112.1', (154.94, 104.14), (154.94, 109.22), 'U105.3')
    s.wire('R111.1', (154.94, 119.38), (154.94, 114.3), 'U105.4')
    s.o2('R115', 147.32, 96.52, 'h-')
    s.wire((154.94, 104.14), (154.94, 96.52), 'R115.1'); s.stub('R115.2')
    s.o2('R117', 167.64, 127.0, 'h-')
    s.wire((154.94, 119.38), (154.94, 127.0), 'R117.2')
    s.wire('R117.1', (180.34, 127.0), (180.34, 111.76))
    s.o2('R124', 187.96, 111.76, 'h')
    s.wire('U105.1', 'R124.1')
    s.o2('C111', 198.12, 119.38, 'v')
    s.wire('R124.2', (198.12, 111.76), 'C111.1'); s.stub('C111.2')
    s.wire((198.12, 111.76), (205.74, 111.76)); s.lab('WB_IP_SENSE', (205.74, 111.76), 'right')
    s.stub('U105.5'); s.stub('U105.2')

    # ---- G: Nernst buffer, bias current, ESR measurement ----------------------------
    s.text('Nernst buffer, bias current and cell resistance (ESR) drive', 228.6, 86.36)
    P, N, O = oa('U101', 3, 276.86, 111.76)         # + 10 (269.24,109.22) - 9 (269.24,114.3) out 8 (284.48,111.76)
    s.wire('U101.9', (266.7, 114.3), (266.7, 121.92), (289.56, 121.92), (289.56, O[1]))
    s.wire('U101.8', (289.56, O[1]), (297.18, O[1])); s.lab('WB_UN_BUF', (297.18, O[1]), 'right')
    s.wire('U101.10', (254.0, P[1]))
    s.o2('R114', 254.0, 99.06, 'v')
    s.wire('R114.2', (254.0, P[1])); s.pwr('+3V3', 'R114.1', 'up')
    s.o2('C102', 243.84, 116.84, 'v')
    s.wire((254.0, P[1]), (243.84, P[1]), 'C102.1')
    s.wire((243.84, P[1]), (236.22, P[1])); s.lab('LSU_UN', (236.22, P[1]), 'left')
    for k, r in enumerate(['R106', 'R116', 'R119']):
        y = 129.54 + k * 7.62
        s.o2(r, 261.62, y, 'h')
        s.wire((243.84, y), f'{r}.1')
        s.stub(f'{r}.2')
    s.wire('C102.2', (243.84, 144.78))
    s.text('ESR drive: R106 22k / R116 6.8k / R119 47k, through C102 into the Nernst cell', 228.6, 154.94, 1.27)

    # ---- H: controller MCU ---------------------------------------------------------
    s.text('Controller MCU (STM32F042, FOME wideband firmware; first flash over SWD, then over CAN)', 20.32, 162.56)
    MX, MY = 101.6, 223.52
    s.place('U102', MX, MY)
    s.fields['U102'] = ((MX + 7.62, MY - 31.75), (MX + 7.62, MY - 29.21), 'left')
    s.rail('U102', '+3V3', pins=['1', '17'])
    s.stub('U102.5'); s.rail('U102', 'GND', pins=['16', '32'])
    for c, x in (('C105', 22.86), ('C112', 30.48), ('C113', 38.1), ('C114', 45.72), ('C110', 53.34)):
        s.o2(c, x, 182.88, 'v')
        s.wire((x, 176.53), f'{c}.1'); s.wire(f'{c}.2', (x, 189.23))
    s.wire((17.78, 176.53), (53.34, 176.53)); s.wire((17.78, 189.23), (53.34, 189.23))
    s.pwr('+3V3', (17.78, 176.53), 'up'); s.pwr('GND', (17.78, 189.23), 'down')
    # NRST cap, BOOT0 pull-down
    s.o2('C116', 78.74, 207.01, 'v')
    s.wire('U102.4', 'C116.1', (66.04, 203.2)); s.pwr('GND', 'C116.2', 'down')
    s.lab('WB_NRST', (66.04, 203.2), 'left')
    s.o2('R129', 73.66, 241.3, 'v-')
    s.wire('U102.31', (73.66, 233.68)); s.wire((73.66, 233.68), 'R129.2'); s.stub('R129.1')
    s.wire((73.66, 233.68), (68.58, 233.68)); s.lab('WB_BOOT0', (68.58, 233.68), 'left')   # main MCU drives it (prog link)
    # battery divider into PB0
    s.o2('R120', 50.8, 208.28, 'v'); s.o2('R121', 50.8, 223.52, 'v'); s.o2('C106', 40.64, 223.52, 'v')
    s.stub('R120.1'); s.wire('R120.2', (50.8, 215.9), 'R121.1')
    s.wire((50.8, 215.9), 'U102.14'); s.wire((50.8, 215.9), (40.64, 215.9), 'C106.1')
    s.stub('R121.2'); s.stub('C106.2')
    s.text('Battery sense / 11', 30.48, 200.66, 1.27)
    for n in ['2', '3', '15', '18', '19', '20', '10', '11', '25']:
        s.stub(f'U102.{n}')
    # status LEDs
    s.text('Status LEDs', 147.32, 233.68, 1.27)
    for k, (d, r) in enumerate([('D102', 'R130'), ('D103', 'R113')]):
        y = 241.3 + k * 7.62
        s.o2(d, 160.02, y, 'h-'); s.o2(r, 175.26, y, 'h-')
        s.stub(f'{d}.2'); s.wire(f'{d}.1', f'{r}.2')
        s.wire(f'{r}.1', (185.42, y), (185.42, y + 2.54)); s.pwr('GND', (185.42, y + 2.54), 'down')
    # SWD pads
    s.text('SWD (Tag-Connect TC2030-NL pads, bottom side)', 147.32, 177.8, 1.27)
    s.place('J102', 165.1, 205.74)

    # ---- I: heater -----------------------------------------------------------------
    s.text('LSU heater low side (protected OMNIFET)', 254.0, 162.56)
    s.place('Q101', 312.42, 200.66)               # G (307.34,200.66) D (314.96,195.58) S (314.96,205.74)
    s.fields['Q101'] = ((320.04, 199.39), (320.04, 201.93), 'left')
    s.o2('R125', 297.18, 200.66, 'h-')
    s.wire('R125.1', 'Q101.1')
    s.wire('R125.2', (284.48, 200.66))
    s.o2('R126', 287.02, 210.82, 'v-'); s.wire((287.02, 200.66), 'R126.2'); s.stub('R126.1')
    s.o2('R127', 274.32, 210.82, 'v-'); s.o2('D101', 274.32, 223.52, 'v-')
    s.wire((284.48, 200.66), (274.32, 200.66), 'R127.2'); s.wire('R127.1', 'D101.2'); s.stub('D101.1')
    s.wire((274.32, 200.66), (264.16, 200.66)); s.lab('WB_HTR_PWM', (264.16, 200.66), 'left')
    s.wire('Q101.2', (314.96, 187.96), (325.12, 187.96)); s.lab('LSU_HTR_N', (325.12, 187.96), 'right')
    s.wire('Q101.3', (314.96, 213.36), (325.12, 213.36)); s.lab('HTR_GND', (325.12, 213.36), 'right')
    s.text('Heater return HTR_GND goes straight to J2 39/40 (motherboard GND), not through this board\'s plane', 289.56, 223.52, 1.27)
    s.text('Op-amp supply', 254.0, 243.84, 1.27)
    s.place('U101', 264.16, 259.08, 0, 5)
    s.stub('U101.4'); s.stub('U101.11')


BUILD = {'mcu': sheet_mcu, 'power': sheet_power, 'outputs': sheet_outputs, 'inputs': sheet_inputs,
         'connectors': sheet_connectors, 'wideband': sheet_wideband}


def main():
    root_uuid = U()
    sheets, fp_paths = [], {}
    for page, (key, title, _) in enumerate(SHEETS, start=2):
        s = Sheet(key, title, root_uuid, page)
        BUILD[key](s)
        placed = {d['ref'] for d in s.parts.values()}
        missing = [p['ref'] for p in design.parts if sheet_of(p['ref']) == key and p['ref'] not in placed]
        assert not missing, (key, missing)
        fp_paths.update({r: (v, s.title, s.fname) for r, v in s.finish().items()})
        sheets.append(s)
    items = []
    for i, s in enumerate(sheets):
        x, y = 30.48 + (i % 3) * 81.28, 50.8 + (i // 3) * 50.8
        items.append(f'(sheet (at {x} {y}) (size 66.04 30.48) (fields_autoplaced) (stroke (width 0.1524) (type solid)) '
                     f'(fill (color 0 0 0 0.0000)) (uuid {s.sheet_uuid}) '
                     f'(property "Sheetname" {Q(s.title)} (at {x} {r2(y - 0.71)} 0) (effects (font (size 1.524 1.524)) (justify left bottom))) '
                     f'(property "Sheetfile" {Q(s.fname)} (at {x} {r2(y + 31.07)} 0) (effects (font (size 1.27 1.27)) (justify left top))) '
                     f'(instances (project {Q(PROJECT)} (path {Q("/" + root_uuid)} (page {Q(str(s.page))})))))')
    note = ('Miata ECU daughterboard rev 0.4 (on-board wideband controller, flashed through the main MCU). Block sheets connect through global labels; GND, +3V3, +5V and +12V '
            'are power symbols. J1 = power in and outputs (top edge), J2 = inputs and comms (bottom edge). '
            '4-layer board: In1 GND plane, In2 +3V3 plane.')
    items.append(f'(text {Q(note)} (at 30.48 165.1 0) (effects (font (size 1.524 1.524)) (justify left bottom)) (uuid {U()}))')
    root = (f'(kicad_sch (version 20230121) (generator eeschema) (uuid {root_uuid}) (paper "A4") '
            f'(title_block (title "Miata ECU daughterboard") (date "2026-10-29") (rev "0.4")) (lib_symbols) '
            + '\n'.join(items) + ' (sheet_instances (path "/" (page "1"))))')
    open(os.path.join(OUT, PROJECT + '.kicad_sch'), 'w').write(root)
    with open(os.path.join(OUT, 'fp_paths.txt'), 'w') as f:
        for ref, (path, title, fname) in fp_paths.items():
            f.write(f'{ref} {path} {title} {fname}\n')
    print('sheets', [s.fname for s in sheets], 'symbols', len(fp_paths), 'power symbols', CNT[0])


if __name__ == '__main__':
    main()
