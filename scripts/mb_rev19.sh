#!/bin/bash
# mb_rev19.sh <motherboard rev 0.18 / 0.14 .kicad_pcb (KiCad 7)> <out.kicad_pcb> <8995 | 9697 | 9900 | 0105> [work dir]
#
# The change order to motherboards rev 0.19 (1989-95) / 0.15 (1996-2005):
#   1. mb_rev19.py        (KiCad 7 text) R37 tach pull-up footprint (1996-2005, not fitted), JD1 / JD2 labels, the
#                         MAP hint in one line, the 1989-95 header captions removed, revision
#   2. 1996-2005 only: j5_clear.py writes the no-via rectangles round J5's names (it finds no via to move: rev 0.18 /
#      0.14 are clean), rip_conflicts.py cuts what DRC finds too near R37's pads, finish_route.py joins R37 and the
#      cut nets (never with a via under a J5 name), drop_orphans.py, via_out_of_pad.py, stitch_islands.py,
#      tidy_dangling.py, j5_clear.py --check, backport_copper.py into the text from step 1
#   3. silk_clean.py      the silkscreen rule: no silkscreen on a pad, a part, another silkscreen item or the edge; the
#                         daughterboard's outline (x 114.5-239.5, y 94.75-165.25) counts as a part
#   4. silk_clean.py --check
# Steps 2-4 need pcbnew 9 ($K9). Afterwards: KiCad DRC, jlc_fab_check.py, then reexport.sh.
set -e
SRC=$(realpath "$1"); OUT=$2; Y=$3; T=${4:-$(mktemp -d)}
S=$(cd "$(dirname "$0")" && pwd)
PRO=${SRC%.kicad_pcb}.kicad_pro
K9=${K9:-python3}
MODULE=114.5,94.75,239.5,165.25
q() { "$@" 2>&1 | grep --line-buffered -v "Debug\|swig\|leak"; }
fin() { TW=${TW:-0.25} TW_MIN=${TW_MIN:-0.2} CL=0.22 LIMIT=${LIMIT:-3000000} NOVIA=$T/novia.txt q $K9 $S/finish_route.py "$@"; }
python3 $S/mb_rev19.py "$SRC" $T/a.kicad_pcb $Y
for f in a s c c1 c2 c3 c4 c5 c6 d o g t b; do cp "$PRO" $T/$f.kicad_pro; done
if [ "$Y" != 8995 ]; then
  q $K9 $S/j5_clear.py $T/a.kicad_pcb $T/s.kicad_pcb $T/novia.txt
  q $K9 $S/rip_conflicts.py $T/s.kicad_pcb $T/c.kicad_pcb | tail -1
  q $K9 $S/rip_conflicts.py $T/c.kicad_pcb $T/c1.kicad_pcb | tail -1
  fin $T/c1.kicad_pcb $T/c2.kicad_pcb OUT_TACH VBAT_IN > $T/finish.log || true
  fin $T/c2.kicad_pcb $T/c3.kicad_pcb >> $T/finish.log || true
  q $K9 $S/drop_orphans.py $T/c3.kicad_pcb $T/c4.kicad_pcb >> $T/finish.log
  q $K9 $S/rip_conflicts.py $T/c4.kicad_pcb $T/c5.kicad_pcb >> $T/finish.log
  fin $T/c5.kicad_pcb $T/c6.kicad_pcb >> $T/finish.log || true
  q $K9 $S/drop_orphans.py $T/c6.kicad_pcb $T/d.kicad_pcb >> $T/finish.log
  grep "NO PATH\|NO VIA" $T/finish.log || true
  q $K9 $S/via_out_of_pad.py $T/d.kicad_pcb $T/o.kicad_pcb | tail -1
  NOVIA=$T/novia.txt q $K9 $S/stitch_islands.py $T/o.kicad_pcb $T/g.kicad_pcb | tail -3
  q $K9 $S/tidy_dangling.py $T/g.kicad_pcb $T/t.kicad_pcb | tail -1
  $K9 $S/j5_clear.py $T/t.kicad_pcb /dev/null $T/novia.txt --check 2>&1 | grep -v "Debug\|swig\|leak"; [ "${PIPESTATUS[0]}" = 0 ]
  python3 $S/backport_copper.py $T/a.kicad_pcb $T/t.kicad_pcb $T/b.kicad_pcb
else
  cp $T/a.kicad_pcb $T/b.kicad_pcb
fi
q $K9 $S/silk_clean.py $T/b.kicad_pcb "$OUT" --keepout $MODULE
cp "$PRO" "${OUT%.kicad_pcb}.kicad_pro" 2>/dev/null || true
$K9 $S/silk_clean.py "$OUT" --check --keepout $MODULE 2>&1 | grep -v "Debug\|swig\|leak"; [ "${PIPESTATUS[0]}" = 0 ]
