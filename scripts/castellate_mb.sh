#!/bin/bash
# castellate_mb.sh <socketed motherboard.kicad_pcb (KiCad 7)> <out.kicad_pcb> <8995 | 9697 | 9900 | 0105> [work dir]
#
# The change order that takes a finished, socketed motherboard (rev 0.15 / 0.11) to the castellated daughterboard
# (motherboard rev 0.16 / 0.12), keeping the board's routing:
#   1. castellate_mb.py    (KiCad 7 text) JD1 / JD2 become SMD lands, HD1-HD4 go, the parts that sat under the
#                          module move out; silkscreen outline, orientation marks and revision
#   2. via_lands.py        a via beside each land for every bottom-copper track that met a pin (the lands are top only)
#   3. strip_stubs.py      dead copper: what led to the moved parts' old places
#   4. rip_conflicts.py    cuts what DRC finds too near the new lands and parts (only the stretch near the conflict)
#   5. finish_route.py     joins the pieces again, at the motherboard's rules (0.25 mm track, 0.2 mm clearance):
#                          first the moved parts' own nets, then their 12 V feed and the sensor heater's 1 mm return
#                          in explicit windows, then everything; drop_orphans.py removes what is left floating, and
#                          one more rip / finish / drop round takes out the finisher's own near misses
#   6. castellate_hand.py  the joins the finisher cannot find (2001-05: OUT_TACH's via between two lands)
#   7. via_out_of_pad.py   moves the old vias that now sit in or against a land or a moved part's pad
#      stitch_islands.py   a via for each GND pour island left without one; tidy_dangling.py removes what KiCad
#                          calls dangling, as long as nothing comes open
#   8. backport_copper.py  carries the copper into the KiCad 7 file from step 1
# Steps 2-7 need pcbnew 9 (the KiCad 9 shim). Afterwards: KiCad DRC, jlc_fab_check.py, then reexport.sh.
set -e
SRC=$(realpath "$1"); OUT=$2; Y=$3; T=${4:-$(mktemp -d)}
S=$(cd "$(dirname "$0")" && pwd)
PRO=${SRC%.kicad_pcb}.kicad_pro
q() { "$@" 2>&1 | grep --line-buffered -v "Debug\|swig\|leak"; }
fin() { TW=${TW:-0.25} TW_MIN=${TW_MIN:-0.2} CL=0.22 LIMIT=${LIMIT:-3000000} q python3 $S/finish_route.py "$@"; }
python3 $S/castellate_mb.py "$SRC" $T/a.kicad_pcb $Y
for f in a v c1 c c2 c3 c4 c5 c6 c7 c8 d h o g t; do cp "$PRO" $T/$f.kicad_pro; done
q python3 $S/via_lands.py $T/a.kicad_pcb $T/v.kicad_pcb | tail -1
q python3 $S/strip_stubs.py $T/v.kicad_pcb $T/c1.kicad_pcb
q python3 $S/rip_conflicts.py $T/c1.kicad_pcb $T/c.kicad_pcb $T/v.new.txt | tail -1
NETS=$(python3 - $T/c.kicad_pcb $Y $S <<'PY'
import re, sys
sys.path.insert(0, sys.argv[3])
from castellate_mb import MOVES
t = open(sys.argv[1]).read()
nets = set()
for ref in MOVES[sys.argv[2]]:
    i = t.index(f'"Reference" "{ref}"') if f'"Reference" "{ref}"' in t else t.index(f'reference "{ref}"')
    j = t.rfind('(footprint', 0, i)
    k = t.find('\n\t(footprint', i)
    nets |= set(re.findall(r'\(net (?:\d+ )?"([^"]+)"\)', t[j:k]))
print(' '.join(sorted(nets - {'GND', 'VBAT_IN', '+3V3'})))
PY
)
fin $T/c.kicad_pcb $T/c2.kicad_pcb $NETS > $T/finish.log
WINDOW=112,84,242,173 fin $T/c2.kicad_pcb $T/c3.kicad_pcb VBAT_IN >> $T/finish.log
WINDOW=112,158,232,205 TW=1.0 TW_MIN=0.6 LIMIT=6000000 fin $T/c3.kicad_pcb $T/c4.kicad_pcb LSU_HTR_N >> $T/finish.log
fin $T/c4.kicad_pcb $T/c5.kicad_pcb >> $T/finish.log
q python3 $S/drop_orphans.py $T/c5.kicad_pcb $T/c6.kicad_pcb >> $T/finish.log
q python3 $S/rip_conflicts.py $T/c6.kicad_pcb $T/c7.kicad_pcb >> $T/finish.log
fin $T/c7.kicad_pcb $T/c8.kicad_pcb >> $T/finish.log
q python3 $S/drop_orphans.py $T/c8.kicad_pcb $T/d.kicad_pcb >> $T/finish.log
grep "NO PATH\|NO VIA" $T/finish.log || true
q python3 $S/castellate_hand.py $T/d.kicad_pcb $T/h.kicad_pcb $Y
q python3 $S/via_out_of_pad.py $T/h.kicad_pcb $T/o.kicad_pcb
q python3 $S/stitch_islands.py $T/o.kicad_pcb $T/g.kicad_pcb
q python3 $S/tidy_dangling.py $T/g.kicad_pcb $T/t.kicad_pcb
python3 $S/backport_copper.py $T/a.kicad_pcb $T/t.kicad_pcb "$OUT"
