"""castellate_mb.py <motherboard.kicad_pcb (KiCad 7)> <out.kicad_pcb> <short name: 8995 | 9697 | 9900 | 0105>

The footprint half of the change order that takes a finished motherboard to the castellated daughterboard
(daughterboard rev 0.13, which reflows flat onto the motherboard instead of plugging into sockets on standoffs).
Pin positions and nets do not change: the daughterboard's castellations sit where its header pins were.

  - JD1 / JD2: the 1x40 sockets become rows of SMD lands, one per castellation, LAND_W along the edge and LAND_L
    across it, reaching LAND_IN under the module and LAND_L - LAND_IN beyond its edge (for the solder fillet and an
    iron). Same pad numbers and nets; top copper, paste and mask only; not a part to buy. The ground lands join the
    pour solidly (a thermal relief's spokes would be starved between the neighbouring lands).
  - HD1-HD4 (the M3 standoff holes) are removed.
  - The parts that sat under the daughterboard move out from under it (MOVES; a new angle turns the part).
  - 1989-95: the injector clamps' tab pours (left under the module) go (DROP_ZONES), and the board's title moves up
    clear of the clamps' new place (TITLE_AT).
  - The DAUGHTERBOARD outline on the silkscreen follows the module's new outline: the short edges in full, the long
    edges as corner marks outside the lands.

The copper half (castellate_mb.sh) rips what no longer connects or fits and joins it again on the finished board."""
import re
import sys

ROW1, ROW2 = 94.75, 165.25          # JD1 / JD2 pad rows = the module's long edges (motherboard coordinates)
MOD_X0, MOD_X1 = 114.5, 239.5       # the module's short edges
LAND_W, LAND_L, LAND_IN = 1.5, 3.0, 1.2
LAND_OFF = LAND_L / 2 - LAND_IN     # land centre beyond the edge
REV = {'8995': '0.16', '9697': '0.12', '9900': '0.12', '0105': '0.12'}   # the castellated release
MARK = 11.0                         # mm of long-edge silkscreen at each corner (the first land starts 13 mm in)

# ref -> (x, y, angle): new place for each part that sat under the daughterboard, per board
# (mb_common.protection_place has the same: freewheel diodes just above their JD1 lands, pull-ups just below their JD2
# lands; on 1989-95 the injector clamps D3 / D4 above JD1 by their injector pins, and the TPS links R29 / R30 beside
# them, nearest the 2L harness wire; spots found clear of every courtyard by a search, 2026-11-20.)
_COMMON = {'D1': (203.7, 90.6, 0), 'R20': (163.06, 169.0, 90), 'R21': (165.6, 169.0, 90), 'R22': (168.14, 169.0, 90)}
MOVES = {
    '9697': dict(_COMMON),
    '9900': dict(_COMMON),
    '0105': dict(_COMMON, D2=(211.32, 90.6, 0)),
    '8995': dict(_COMMON, D2=(211.32, 90.6, 0), R27=(147.82, 169.0, 90), D3=(173.41, 88.33, 0), D4=(183.91, 88.33, 0),
                 R29=(166.16, 90.93, 90), R30=(162.16, 90.93, 0)),
}
# 1989-95: the injector clamps' tab pours stay under the module when D3 / D4 move out (and the clamps are not fitted
# with a rev 0.10 or later daughterboard): the pours go, the ground pour fills their place
DROP_ZONES = {'8995': ('OUT_INJ1', 'OUT_INJ2')}
# 1989-95: the board's title sat where D3 / D4 now are (their courtyards start at y 84.9): it moves up 2.5 mm
TITLE_AT = {'8995': (177, 81.5)}


def blocks(text, head):
    out = []
    for m in re.finditer(r'^  \(' + re.escape(head) + r'\b', text, re.M):
        i, depth = m.start() + 2, 0
        while True:
            c = text[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            elif c == '"':
                i += 1
                while text[i] != '"':
                    i += 2 if text[i] == '\\' else 1
            i += 1
        j = i + 1
        if text[j] == '\n':
            j += 1
        out.append((m.start(), j))
    return out


def fmt(v):
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def ref_of(blk):
    m = re.search(r'\(fp_text reference "([^"]+)"', blk)
    return m.group(1) if m else None


def lands(blk, ref):
    """Socket footprint text -> land footprint text. The sockets sit at 90 degrees: local +x points up the board,
    so JD1's lands move +LAND_OFF (outward = up) and JD2's -LAND_OFF (outward = down)."""
    assert re.search(r'\n    \(at [-\d.]+ [-\d.]+ 90\)', blk), ref
    off = LAND_OFF if ref == 'JD1' else -LAND_OFF
    side = 'TopEdge' if ref == 'JD1' else 'BottomEdge'     # mb/ecu_mb.pretty/CastellatedLand_1x40_P2.54mm_<side>
    blk = blk.replace('(footprint "Connector_PinSocket_2.54mm:PinSocket_1x40_P2.54mm_Vertical"',
                      f'(footprint "ecu_mb:CastellatedLand_1x40_P2.54mm_{side}"')
    blk = re.sub(r'\(descr "[^"]*"\)', '(descr "Lands for a castellated module edge, 40 pads, 2.54 mm pitch")', blk)
    blk = re.sub(r'\(tags "[^"]*"\)', '(tags "castellated land")', blk)
    blk = re.sub(r'\n    \(property "LCSC" "[^"]*"\)', '', blk)
    blk = blk.replace('(attr through_hole)', '(attr smd exclude_from_pos_files exclude_from_bom)')
    blk = re.sub(r'    \(model "[^"]*PinSocket_1x40[^"]*"\n(?:      [^\n]*\n)*    \)\n', '', blk)   # the socket's 3D model goes with it
    blk, n = re.subn(
        r'\(pad "(\d+)" thru_hole (?:rect|oval|circle) \(at ([-\d.]+) ([-\d.]+) 90\) \(size 1\.7 1\.7\) \(drill 1\) '
        r'\(layers "\*\.Cu" "\*\.Mask"\)',
        lambda q: (f'(pad "{q.group(1)}" smd roundrect (at {fmt(float(q.group(2)) + off)} {q.group(3)} 90) '
                   f'(size {fmt(LAND_L)} {fmt(LAND_W)}) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.15) (zone_connect 2)'),
        blk)
    assert n == 40, (ref, n)
    # the socket body's outline goes; a courtyard round the lands takes its place
    blk = re.sub(r'    \(fp_line [^\n]*\n[^\n]*\(layer "F\.(SilkS|CrtYd|Fab)"\)[^\n]*\n', '', blk)
    x0, x1 = sorted((off - LAND_L / 2 - 0.25, off + LAND_L / 2 + 0.25))
    y0, y1 = -LAND_W / 2 - 0.25, 39 * 2.54 + LAND_W / 2 + 0.25
    crt = ''.join(f'    (fp_line (start {fmt(a)} {fmt(b)}) (end {fmt(c)} {fmt(d)})\n'
                  f'      (stroke (width 0.05) (type solid)) (layer "F.CrtYd"))\n'
                  for a, b, c, d in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)))
    # the reference would sit on the lands' outer ends: hide it (the board's silkscreen names the module)
    blk = re.sub(r'(\(fp_text reference "JD[12]" \(at [^)]*\) \(layer "F\.SilkS"\))', r'\1 hide', blk)
    i = blk.index('    (pad ')
    return blk[:i] + crt + blk[i:]


def move(blk, x, y, a):
    m = re.search(r'\n    \(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
    old = float(m.group(3) or 0)
    d = a - old
    blk = blk[:m.start()] + f'\n    (at {fmt(x)} {fmt(y)}{"" if a == 0 else " " + fmt(a)})' + blk[m.end():]
    if d:
        # KiCad 7 stores pad and field angles as board angles: turn them with the part
        def ang(v):
            na = (float(v or 0) + d) % 360
            return '' if na == 0 else ' ' + fmt(na)
        blk = re.sub(r'\(pad ("[^"]*") (\w+) (\w+) \(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)',
                     lambda q: f'(pad {q[1]} {q[2]} {q[3]} (at {q[4]} {q[5]}{ang(q[6])})', blk)
        blk = re.sub(r'\(fp_text (\w+) ("[^"]*") \(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)',
                     lambda q: f'(fp_text {q[1]} {q[2]} (at {q[3]} {q[4]}{ang(q[5])})', blk)
    return blk


def main(src, dst, short):
    text = open(src).read()
    moves = MOVES[short]
    done = []
    for a, b in sorted(blocks(text, 'footprint'), reverse=True):
        blk = text[a:b]
        r = ref_of(blk)
        if r in ('HD1', 'HD2', 'HD3', 'HD4'):
            text = text[:a] + text[b:]
            done.append(r)
        elif r in ('JD1', 'JD2'):
            text = text[:a] + lands(blk, r) + text[b:]
            done.append(r)
        elif r in moves:
            text = text[:a] + move(blk, *moves[r]) + text[b:]
            done.append(r)
    want = {'HD1', 'HD2', 'HD3', 'HD4', 'JD1', 'JD2'} | set(moves)
    assert set(done) == want, sorted(want - set(done))

    # silkscreen outline of the module: the old one was 114.5..239.5 x 92..168
    n = 0
    for a, b in sorted(blocks(text, 'gr_line'), reverse=True):
        blk = text[a:b]
        if '"F.SilkS"' not in blk:
            continue
        m = re.match(r'  \(gr_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\)', blk)
        xs, ys, xe, ye = map(float, m.groups())
        if {round(ys, 2), round(ye, 2)} <= {92.0, 168.0} and {round(xs, 2), round(xe, 2)} <= {MOD_X0, MOD_X1}:
            tail = blk[m.end():]
            tail = re.sub(r' \(tstamp [^)]*\)', '', tail)
            mapy = {92.0: ROW1, 168.0: ROW2}
            if xs == xe:                                    # short edge: full length
                new = f'  (gr_line (start {fmt(xs)} {fmt(mapy[round(ys, 2)])}) (end {fmt(xe)} {fmt(mapy[round(ye, 2)])})' + tail
            else:                                           # long edge: a mark at each corner
                y = mapy[round(ys, 2)]
                new = (f'  (gr_line (start {fmt(MOD_X0)} {fmt(y)}) (end {fmt(MOD_X0 + MARK)} {fmt(y)})' + tail +
                       f'  (gr_line (start {fmt(MOD_X1 - MARK)} {fmt(y)}) (end {fmt(MOD_X1)} {fmt(y)})' + tail)
            text = text[:a] + new + text[b:]
            n += 1
    assert n == 4, n
    for a, b in sorted(blocks(text, 'zone'), reverse=True):
        m = re.match(r'  \(zone \(net \d+\) \(net_name "([^"]*)"\)', text[a:b])
        if m and m.group(1) in DROP_ZONES.get(short, ()):
            text = text[:a] + text[b:]
            done.append('zone ' + m.group(1))
    if short in TITLE_AT:
        text, k = re.subn(r'(\(gr_text "Miata ECU motherboard [^"]*" \(at )[-\d.]+ [-\d.]+\)',
                          lambda q: q[1] + ' '.join(map(fmt, TITLE_AT[short])) + ')', text)
        assert k == 1, k
    # the revision in the board's title on the silkscreen
    text, k = re.subn(r'(\(gr_text "Miata ECU motherboard [^"]*  rev )[\d.]+"', lambda q: q[1] + REV[short] + '"', text)
    assert k == 1, k
    # name the land rows as the module names its edges (castellate_daughter.py): it fits turned round too
    import uuid
    marks = ''.join(f'  (gr_text "{t}" (at {x} {y}) (layer "F.SilkS") (tstamp {uuid.uuid4()})\n'
                    f'    (effects (font (size 1.5 1.5) (thickness 0.2)) (justify left))\n  )\n'
                    for t, x, y in (('J1', MOD_X0 + 1.0, ROW1 - 3.0), ('J2', MOD_X0 + 1.0, ROW2 + 3.0)))
    i = text.rindex('\n)')
    text = text[:i + 1] + marks + text[i + 1:]
    open(dst, 'w').write(text)
    zs = sorted(z[5:] for z in done if z.startswith('zone '))
    print(f'{short}: lands JD1 / JD2, removed HD1-HD4, moved {", ".join(sorted(moves))}, silkscreen outline updated'
          + (f'; removed the {" / ".join(sorted(set(zs)))} pours ({len(zs)} zones)' if zs else '')
          + (f'; title moved to {TITLE_AT[short]}' if short in TITLE_AT else ''))


if __name__ == '__main__':
    main(*sys.argv[1:4])
