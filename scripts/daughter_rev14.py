"""daughter_rev14.py <daughterboard.kicad_pcb (KiCad 7), rev 0.13> <out.kicad_pcb>

Change order to daughterboard rev 0.14, first step (then silk_clean.py --fab-refs, see daughter_rev14.sh):
  - the status lights are named on the silkscreen: RUN (D1, green), COMM (D2, blue), WARN (D3, yellow), ERR (D4, red)
    and PWR (D5, green, the 3.3 V supply), each under its light where its reference was, and the buttons BOOT (SW1) and
    RESET (SW2); the references D1-D5, SW1 and SW2 go to F.Fab (the assembly drawing). The wideband controller's lights are already named (HTR / OK / ACT).
  - no silkscreen text reads upside down: a footprint text marked "unlocked" (KiCad 7's flag for "not kept upright")
    at 90-270 degrees turns by 180 and loses the flag (J4's reference was printed upside down).
The revision itself is design.REV (it names the fab files); the board carries no revision text.
"""
import re
import sys
import uuid

# ref -> (label, dx, dy from the light's centre, mm). The lights are a column at x 219.6, 3 mm apart, the board edge
# 5.4 mm to the right and their series resistors to the left, so each name sits under its light (centred in the 1.4 mm
# between two lights' outlines), nudged right to clear
# the resistors; PWR goes right of D5 (the BOOT button is under it).
LABELS = {'D1': ('RUN', 0.4, 1.55), 'D2': ('COMM', 0.4, 1.55), 'D3': ('WARN', 0.4, 1.55), 'D4': ('ERR', 0.4, 1.55),
          'D5': ('PWR', 3.2, 0.0),
          # the two buttons, named where their references were (under each); BUILD.md says "hold BOOT, tap RESET"
          'SW1': ('BOOT', 0.0, 3.85), 'SW2': ('RESET', 0.0, 3.85)}


def fp_block(t, ref):
    i = t.index(f'(fp_text reference "{ref}"')
    a = t.rfind('\n  (footprint', 0, i) + 1
    b = t.find('\n  (', i) + 1
    return a, b


def main(src, dst):
    t = open(src).read()
    labels = []
    for ref, (lab, dx, dy) in LABELS.items():
        a, b = fp_block(t, ref)
        blk = t[a:b]
        x, y = (float(v) for v in re.search(r'\n    \(at ([-\d.]+) ([-\d.]+)', blk).groups())
        blk, n = re.subn(r'(\(fp_text reference "%s" \(at [^)]*\)) \(layer "F\.SilkS"\)' % ref,
                         r'\1 (layer "F.Fab")', blk)
        assert n == 1, ref
        t = t[:a] + blk + t[b:]
        labels.append(f'  (gr_text "{lab}" (at {x + dx:.2f} {y + dy:.2f}) (layer "F.SilkS") (tstamp {uuid.uuid4()})\n'
                      f'    (effects (font (size 1 1) (thickness 0.15)))\n  )\n')
    flipped = []

    def upright(m):
        ang = float(m[4]) % 360
        if 90 < ang <= 270 and 'hide' not in m[6]:
            flipped.append(m[2])
            return f'{m[1]} (at {m[3]} {(ang - 180) % 360:g}){m[5]}{m[6]}'
        return m[0]
    t = re.sub(r'(\(fp_text (?:reference|user|value) "([^"]*)") \(at ([-\d.]+ [-\d.]+) ([-\d.]+) unlocked\)'
               r'( \(layer "F\.SilkS"\))([^\n]*)', upright, t)
    k = t.index('\n  (gr_') + 1
    t = t[:k] + ''.join(labels) + t[k:]
    open(dst, 'w').write(t)
    print('status light names: ' + ', '.join(f'{r} {l[0]}' for r, l in LABELS.items()) + '; turned upright: '
          + (', '.join(flipped) or 'none'))


if __name__ == '__main__':
    main(*sys.argv[1:3])
