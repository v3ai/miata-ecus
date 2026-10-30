"""Read the FOME/rusEFI wideband module layout (KiCad 9 .kicad_pcb, parsed as text) so it can be
transplanted onto the daughterboard as a block.

load() -> dict(fps, segs, vias, zones, outline) in module coordinates (mm, KiCad y down).
  fps:   {ref: dict(lib, name, x, y, rot, side, pads={num: (x, y, net)})}
  segs:  [dict(a=(x,y), b=(x,y), w, layer, net)]
  vias:  [dict(at=(x,y), size, drill, net)]
  zones: [dict(net, layer, poly=[(x,y)...], ...)]
"""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))


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

# FOME/rusEFI wideband module rev C board (MIT licence, Copyright (c) 2023 Matthew Kennedy),
# copied into wideband_ref/ from github.com/mck1117/wideband hardware/board_module
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wideband_ref', 'wideband_controller.kicad_pcb')


def s(x): return x[1] if isinstance(x, tuple) else x
def items(node, tag): return [e for e in node if isinstance(e, list) and e and e[0] == tag]
def first(node, tag):
    r = items(node, tag)
    return r[0] if r else None


def load(path=SRC):
    t = parse(open(path).read())[0]
    netname = {}
    for n in items(t, 'net'):
        netname[n[1]] = s(n[2])
    out = dict(fps={}, segs=[], vias=[], zones=[], outline=[])

    def nn(node):
        n = first(node, 'net')
        if n is None:
            return ''
        v = s(n[1])
        return netname.get(v, v) if not isinstance(n[1], tuple) else s(n[1])

    for fp in items(t, 'footprint'):
        lib = s(fp[1])
        at = first(fp, 'at'); x, y = float(at[1]), float(at[2]); rot = float(at[3]) if len(at) > 3 else 0.0
        side = 'B' if s(first(fp, 'layer')[1]).startswith('B') else 'F'
        props = {s(p[1]): s(p[2]) for p in items(fp, 'property')}
        ref = props.get('Reference')
        pads = {}
        for p in items(fp, 'pad'):
            num = s(p[1]); pa = first(p, 'at'); px, py = float(pa[1]), float(pa[2])
            # pad position: rotate by footprint rotation (KiCad: CCW in degrees, y down)
            a = math.radians(rot)
            X = x + px * math.cos(a) + py * math.sin(a)
            Y = y - px * math.sin(a) + py * math.cos(a)
            sz = first(p, 'size')
            pads.setdefault(num, []).append((round(X, 4), round(Y, 4), nn(p), (float(sz[1]), float(sz[2])),
                                             (px, py)))
        out['fps'][ref] = dict(lib=lib, x=x, y=y, rot=rot, side=side, pads=pads, value=props.get('Value'))
    for seg in items(t, 'segment'):
        a = first(seg, 'start'); b = first(seg, 'end')
        out['segs'].append(dict(a=(float(a[1]), float(a[2])), b=(float(b[1]), float(b[2])),
                                w=float(first(seg, 'width')[1]), layer=s(first(seg, 'layer')[1]), net=nn(seg)))
    for v in items(t, 'via'):
        at = first(v, 'at')
        out['vias'].append(dict(at=(float(at[1]), float(at[2])), size=float(first(v, 'size')[1]),
                                drill=float(first(v, 'drill')[1]), net=nn(v)))
    for z in items(t, 'zone'):
        lay = first(z, 'layer') or first(z, 'layers')
        poly = first(first(z, 'polygon'), 'pts')
        pts = [(float(p[1]), float(p[2])) for p in poly[1:] if p[0] == 'xy']
        kw = first(z, 'keepout')
        out['zones'].append(dict(net=nn(z), layer=[s(l) for l in lay[1:]], poly=pts, keepout=kw is not None,
                                 raw=z))
    for g in items(t, 'gr_line') + items(t, 'gr_rect') + items(t, 'gr_arc'):
        if s(first(g, 'layer')[1]) == 'Edge.Cuts':
            st = first(g, 'start'); en = first(g, 'end')
            out['outline'].append((g[0], (float(st[1]), float(st[2])), (float(en[1]), float(en[2]))))
    return out


if __name__ == '__main__':
    m = load()
    print(len(m['fps']), 'fps', len(m['segs']), 'segs', len(m['vias']), 'vias')
    print('outline', m['outline'])
    for z in m['zones']:
        print('zone', z['net'], z['layer'], z['keepout'], [tuple(round(c, 2) for c in p) for p in z['poly']][:8])
    for r, f in sorted(m['fps'].items()):
        print(r, f['lib'], f['x'], f['y'], f['rot'], f['side'], {k: v for k, v in f['pads'].items()})
