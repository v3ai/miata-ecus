#!/bin/bash
# j5_mb.sh <motherboard rev 0.16 / 0.12 .kicad_pcb (KiCad 7)> <out.kicad_pcb> <8995 | 9697 | 9900 | 0105> [work dir]
#
# The change order that names J5's pins on both sides of the header (motherboard rev 0.18 / 0.14):
#   1. j5_labels.py      (KiCad 7 text) the names and pin numbers, R35 / R36 moved left of J5, the stitching vias
#                        under the even names moved onto the gaps between columns, revision
#   2. strip_stubs.py    the tracks that led to R35 / R36's old places
#   3. j5_clear.py       the no-via rectangles round the names (novia.txt); any via under a name goes (a lone ground
#                        via moves aside instead), and strip_stubs.py again takes what led to it
#   4. rip_conflicts.py  cuts what DRC finds too near R35 / R36 in their new places
#   5. finish_route.py   joins the pieces, never with a via under a name (NOVIA): R35 / R36's nets first, then
#                        everything; drop_orphans.py, then one more rip / finish / drop round
#   6. via_out_of_pad.py, stitch_islands.py (NOVIA), tidy_dangling.py as castellate_mb.sh; two last joins (J5's
#                        ground pins; 1999-2000's main relay output); j5_clear.py --check
#   7. backport_copper.py carries the copper into the KiCad 7 file from step 1
# Steps 2-6 need pcbnew 9 (the KiCad 9 shim, $K9). Afterwards: KiCad DRC, jlc_fab_check.py, then reexport.sh.
set -e
SRC=$(realpath "$1"); OUT=$2; Y=$3; T=${4:-$(mktemp -d)}
S=$(cd "$(dirname "$0")" && pwd)
PRO=${SRC%.kicad_pcb}.kicad_pro
K9=${K9:-python3}
q() { "$@" 2>&1 | grep --line-buffered -v "Debug\|swig\|leak"; }
fin() { TW=${TW:-0.25} TW_MIN=${TW_MIN:-0.2} CL=0.22 LIMIT=${LIMIT:-3000000} NOVIA=$T/novia.txt q $K9 $S/finish_route.py "$@"; }
python3 $S/j5_labels.py "$SRC" $T/a.kicad_pcb $Y
for f in a s1 s2 s3 c c1 c2 c3 c4 c5 c6 c7 d o g t; do cp "$PRO" $T/$f.kicad_pro; done
q $K9 $S/strip_stubs.py $T/a.kicad_pcb $T/s1.kicad_pcb | tail -1
q $K9 $S/j5_clear.py $T/s1.kicad_pcb $T/s2.kicad_pcb $T/novia.txt
q $K9 $S/strip_stubs.py $T/s2.kicad_pcb $T/s3.kicad_pcb | tail -1
q $K9 $S/rip_conflicts.py $T/s3.kicad_pcb $T/c.kicad_pcb | tail -1
q $K9 $S/rip_conflicts.py $T/c.kicad_pcb $T/c1.kicad_pcb | tail -1
fin $T/c1.kicad_pcb $T/c2.kicad_pcb IN_FLEX IN_N2O V5_EXT > $T/finish.log || true
fin $T/c2.kicad_pcb $T/c3.kicad_pcb >> $T/finish.log || true
q $K9 $S/drop_orphans.py $T/c3.kicad_pcb $T/c4.kicad_pcb >> $T/finish.log
q $K9 $S/rip_conflicts.py $T/c4.kicad_pcb $T/c5.kicad_pcb >> $T/finish.log
fin $T/c5.kicad_pcb $T/c6.kicad_pcb >> $T/finish.log || true
q $K9 $S/drop_orphans.py $T/c6.kicad_pcb $T/d.kicad_pcb >> $T/finish.log
grep "NO PATH\|NO VIA" $T/finish.log || true
q $K9 $S/via_out_of_pad.py $T/d.kicad_pcb $T/o.kicad_pcb | tail -1
NOVIA=$T/novia.txt q $K9 $S/stitch_islands.py $T/o.kicad_pcb $T/g.kicad_pcb | tail -3
q $K9 $S/tidy_dangling.py $T/g.kicad_pcb $T/t0.kicad_pcb | tail -1
# J5's ground pins can be left on a pour island the new tracks cut off (no room there for a stitching via): a track
# to the rest. 1999-2000's main relay output lost its whole run to J5 (the via under RELAY went, strip_stubs.py took
# the rest back to y 90): rejoined in an explicit window
cp "$PRO" $T/t1.kicad_pro; cp "$PRO" $T/t.kicad_pro
fin $T/t0.kicad_pcb $T/t1.kicad_pcb GND:J5:16 GND:J5:18 >> $T/finish.log || true
if [ "$Y" = 9900 ]; then WINDOW=125,84,200,182 LIMIT=20000000 fin $T/t1.kicad_pcb $T/t.kicad_pcb OUT_MAINRLY >> $T/finish.log || true
else cp $T/t1.kicad_pcb $T/t.kicad_pcb; fi
$K9 $S/j5_clear.py $T/t.kicad_pcb /dev/null $T/novia.txt --check 2>&1 | grep -v "Debug\|swig\|leak"; [ "${PIPESTATUS[0]}" = 0 ]
python3 $S/backport_copper.py $T/a.kicad_pcb $T/t.kicad_pcb "$OUT"
