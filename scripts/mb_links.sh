#!/bin/bash
# mb_links.sh <1989-95 motherboard rev 0.19 .kicad_pcb (KiCad 7), with the headers JP1-JP4> <out.kicad_pcb> [work dir]
#
# The year links of the 1989-95 motherboard (rev 0.19): the year headers JP1-JP4 become the 0R links R38-R42 that
# JLCPCB fits for the car's years (mb_na6.LINKS); JP5 / JP6 stay headers.
#   1. mb_links.py        (KiCad 7 text) JP1-JP4 and their position captions out, R38-R42 and their names in
#   2. j5_clear.py writes the no-via rectangles round J5's names (mb_links.py --novia adds the links' names),
#      rip_conflicts.py cuts what DRC finds too near the new pads, finish_route.py joins the links to their nets (at each net's own track width first), drop_orphans.py
#      and tidy_dangling.py take away the copper that only reached the old headers' pins, via_out_of_pad.py,
#      stitch_islands.py, j5_clear.py --check, backport_copper.py into the text from step 1
#   3. silk_clean.py      no silkscreen on a pad, a part, another silkscreen item or the edge; the daughterboard's
#                         outline counts as a part
#   4. silk_clean.py --check
# Steps 2-4 need pcbnew 9 ($K9). Afterwards: KiCad DRC, then reexport.sh.
set -e
SRC=$(realpath "$1"); OUT=$2; T=${3:-$(mktemp -d)}
S=$(cd "$(dirname "$0")" && pwd)
PRO=${SRC%.kicad_pcb}.kicad_pro
K9=${K9:-python3}
MODULE=114.5,94.75,239.5,165.25
NETS="OUT_INJ3 HARN_2Y OUT_INJ4 HARN_2Z OUT_LS7 HARN_1R HARN_2S OUT_ALT HARN_2R"
q() { "$@" 2>&1 | grep --line-buffered -v "Debug\|swig\|leak"; }
fin() { TW=${TW:-0.25} TW_MIN=${TW_MIN:-0.2} CL=0.22 LIMIT=${LIMIT:-3000000} NOVIA=$T/novia.txt q $K9 $S/finish_route.py "$@"; }
python3 $S/mb_links.py "$SRC" $T/a.kicad_pcb
for f in a s c c1 c2 c3 c4 c5 c6 d o g t t2 b; do cp "$PRO" $T/$f.kicad_pro; done
q $K9 $S/j5_clear.py $T/a.kicad_pcb $T/s.kicad_pcb $T/novia.txt
python3 $S/mb_links.py --novia >> $T/novia.txt        # no via under the links' names either
q $K9 $S/rip_conflicts.py $T/s.kicad_pcb $T/c.kicad_pcb | tail -1
q $K9 $S/rip_conflicts.py $T/c.kicad_pcb $T/c1.kicad_pcb | tail -1
q $K9 $S/drop_orphans.py $T/c1.kicad_pcb $T/c2.kicad_pcb > $T/finish.log
fin $T/c2.kicad_pcb $T/c3.kicad_pcb $NETS >> $T/finish.log || true
fin $T/c3.kicad_pcb $T/c4.kicad_pcb >> $T/finish.log || true
q $K9 $S/rip_conflicts.py $T/c4.kicad_pcb $T/c5.kicad_pcb >> $T/finish.log
fin $T/c5.kicad_pcb $T/c6.kicad_pcb >> $T/finish.log || true
q $K9 $S/drop_orphans.py $T/c6.kicad_pcb $T/d.kicad_pcb >> $T/finish.log
grep "NO PATH\|NO VIA" $T/finish.log || true
q $K9 $S/via_out_of_pad.py $T/d.kicad_pcb $T/o.kicad_pcb | tail -1
NOVIA=$T/novia.txt q $K9 $S/stitch_islands.py $T/o.kicad_pcb $T/g.kicad_pcb | tail -3
q $K9 $S/tidy_dangling.py $T/g.kicad_pcb $T/t2.kicad_pcb | tail -1
q $K9 $S/tidy_dangling.py $T/t2.kicad_pcb $T/t.kicad_pcb | tail -1
$K9 $S/j5_clear.py $T/t.kicad_pcb /dev/null $T/novia.txt --check 2>&1 | grep -v "Debug\|swig\|leak"; [ "${PIPESTATUS[0]}" = 0 ]
python3 $S/backport_copper.py $T/a.kicad_pcb $T/t.kicad_pcb $T/b.kicad_pcb
q $K9 $S/silk_clean.py $T/b.kicad_pcb "$OUT" --keepout $MODULE
cp "$PRO" "${OUT%.kicad_pcb}.kicad_pro" 2>/dev/null || true
$K9 $S/silk_clean.py "$OUT" --check --keepout $MODULE 2>&1 | grep -v "Debug\|swig\|leak"; [ "${PIPESTATUS[0]}" = 0 ]
