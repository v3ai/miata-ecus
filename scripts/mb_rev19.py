"""mb_rev19.py <motherboard.kicad_pcb (KiCad 7), rev 0.18 / 0.14> <out.kicad_pcb> <8995 | 9697 | 9900 | 0105>

First step of the change order to motherboards rev 0.19 (1989-95) / 0.15 (1996-2005), scripts/mb_rev19.sh:
  - 1996-2005: R37, a tachometer pull-up (2.2 kOhm 1206 from VBAT_IN to OUT_TACH), NOT FITTED: the tach output is an
    open-drain driver, and whether the cluster needs the ECU to pull its wire up is not known until a car is measured
    (quickstart/1996-97.md). Same reference as the 1989-95 board's tach pull-up. Placed on free board near the tach
    track and VBAT_IN (TACH_R); the tracks it lands on are ripped and joined again by mb_rev19.sh.
  - The daughterboard's two land rows are labelled JD1 / JD2 (they were "J1" / "J2", the names of the harness header and
    the wideband plug), and the "DAUGHTERBOARD" text inside the module's outline goes: the module covers it.
  - The MAP sensor's two hint lines become one, "MPX5700AP marking up", which silk_clean.py then places beside the part
    (it was printed under the sensor's body).
  - 1989-95: the harness header's own captions ("48 PIN CONNECTOR", "174917-6") go, as on the other three boards.
  - The board title's revision.
Silkscreen clean-up (scripts/silk_clean.py) runs after the copper (mb_rev19.sh).
"""
import re
import sys
import uuid

REV = {'8995': '0.19', '9697': '0.15', '9900': '0.15', '0105': '0.15'}
TACH_R = {'9697': (161.0, 89.0, 0), '9900': (133.5, 89.5, 0), '0105': (158.5, 78.5, 90)}


def u():
    return str(uuid.uuid4())


def resistor_1206(ref, value, x, y, ang, n1, net1, n2, net2):
    a = f' {ang}' if ang else ''
    return f'''  (footprint "Resistor_SMD:R_1206_3216Metric" (layer "F.Cu")
    (tstamp {u()})
    (at {x} {y}{a})
    (descr "Resistor SMD 1206 (3216 Metric), square (rectangular) end terminal, IPC_7351 nominal, generated with kicad-footprint-generator")
    (tags "resistor")
    (attr smd)
    (fp_text reference "{ref}" (at 0 -1.82{a}) (layer "F.SilkS")
        (effects (font (size 1 1) (thickness 0.15)))
      (tstamp {u()})
    )
    (fp_text value "{value}" (at 0 1.82{a}) (layer "F.Fab")
        (effects (font (size 1 1) (thickness 0.15)))
      (tstamp {u()})
    )
    (fp_line (start -0.727064 -0.91) (end 0.727064 -0.91)
      (stroke (width 0.15) (type solid)) (layer "F.SilkS") (tstamp {u()}))
    (fp_line (start -0.727064 0.91) (end 0.727064 0.91)
      (stroke (width 0.15) (type solid)) (layer "F.SilkS") (tstamp {u()}))
    (fp_line (start -2.28 -1.12) (end 2.28 -1.12)
      (stroke (width 0.05) (type solid)) (layer "F.CrtYd") (tstamp {u()}))
    (fp_line (start -2.28 1.12) (end -2.28 -1.12)
      (stroke (width 0.05) (type solid)) (layer "F.CrtYd") (tstamp {u()}))
    (fp_line (start 2.28 -1.12) (end 2.28 1.12)
      (stroke (width 0.05) (type solid)) (layer "F.CrtYd") (tstamp {u()}))
    (fp_line (start 2.28 1.12) (end -2.28 1.12)
      (stroke (width 0.05) (type solid)) (layer "F.CrtYd") (tstamp {u()}))
    (fp_line (start -1.6 -0.8) (end 1.6 -0.8)
      (stroke (width 0.1) (type solid)) (layer "F.Fab") (tstamp {u()}))
    (fp_line (start -1.6 0.8) (end -1.6 -0.8)
      (stroke (width 0.1) (type solid)) (layer "F.Fab") (tstamp {u()}))
    (fp_line (start 1.6 -0.8) (end 1.6 0.8)
      (stroke (width 0.1) (type solid)) (layer "F.Fab") (tstamp {u()}))
    (fp_line (start 1.6 0.8) (end -1.6 0.8)
      (stroke (width 0.1) (type solid)) (layer "F.Fab") (tstamp {u()}))
    (pad "1" smd roundrect (at -1.4625 0{a}) (size 1.125 1.75) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.222222)
      (net {n1} "{net1}") (tstamp {u()}))
    (pad "2" smd roundrect (at 1.4625 0{a}) (size 1.125 1.75) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.222222)
      (net {n2} "{net2}") (tstamp {u()}))
    (model "${{KICAD6_3DMODEL_DIR}}/Resistor_SMD.3dshapes/R_1206_3216Metric.wrl"
      (offset (xyz 0 0 0))
      (scale (xyz 1 1 1))
      (rotate (xyz 0 0 0))
    )
  )
'''


def drop_block(t, start_pat):
    """Removes the (...) block that starts with start_pat (exactly one), with its line."""
    assert t.count(start_pat) == 1, (start_pat, t.count(start_pat))
    i = t.index(start_pat)
    j, d = i, 0
    while True:
        c = t[j]
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0:
                break
        elif c == '"':
            j = t.index('"', j + 1)
        j += 1
    a = t.rfind('\n', 0, i)
    return t[:a] + t[j + 1:]


def main(src, dst, short):
    t = open(src).read()
    assert f'rev {REV[short]}"' not in t, 'already at the new revision'
    done = []
    # module land labels
    for old, new, y in (('J1', 'JD1', '91.75'), ('J2', 'JD2', '168.25')):
        pat = f'(gr_text "{old}" (at 115.5 {y}'
        assert t.count(pat) == 1, pat
        t = t.replace(pat, f'(gr_text "{new}" (at 115.5 {y}')
    t = drop_block(t, '(gr_text "DAUGHTERBOARD"')
    done.append('JD1 / JD2 labels, DAUGHTERBOARD text removed')
    # the MAP sensor's hint: one line
    i = t.index('(fp_text reference "U2"')
    a = t.rfind('\n  (footprint', 0, i) + 1
    b = t.find('\n  (footprint', i) + 1
    fp = t[a:b]
    fp = drop_block(fp, '(fp_text user "marking up"')
    assert fp.count('(fp_text user "MPX5700AP"') == 1
    fp = fp.replace('(fp_text user "MPX5700AP"', '(fp_text user "MPX5700AP marking up"')
    t = t[:a] + fp + t[b:]
    done.append('MAP hint in one line')
    if short == '8995':
        i = t.index('(fp_text reference "J1"')
        a = t.rfind('\n  (footprint', 0, i) + 1
        b = t.find('\n  (footprint', i) + 1
        fp = t[a:b]
        fp = drop_block(fp, '(fp_text user "48 PIN CONNECTOR"')
        fp = drop_block(fp, '(fp_text user "174917-6"')
        t = t[:a] + fp + t[b:]
        done.append('J1 captions removed')
    if short in TACH_R:
        assert '(fp_text reference "R37"' not in t
        nets = {m[2]: m[1] for m in re.finditer(r'\n  \(net (\d+) "([^"]*)"\)', t)}
        x, y, ang = TACH_R[short]
        fp = resistor_1206('R37', '2.2k', x, y, ang, nets['VBAT_IN'], 'VBAT_IN', nets['OUT_TACH'], 'OUT_TACH')
        k = t.index('\n  (gr_')       # footprints come before the board graphics
        t = t[:k + 1] + fp + t[k + 1:]
        done.append(f'R37 tach pull-up (not fitted) at {x}, {y}')
    t, n = re.subn(r'(\(gr_text "Miata ECU motherboard [^"]*  rev )[\d.]+"', lambda q: q[1] + REV[short] + '"', t)
    assert n == 1, n
    open(dst, 'w').write(t)
    print(f'{short}: ' + '; '.join(done) + f'; rev {REV[short]}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
