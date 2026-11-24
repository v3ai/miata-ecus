#!/bin/bash
# daughter_rev14.sh <daughterboard rev 0.13 .kicad_pcb (KiCad 7)> <out.kicad_pcb> [work dir]
#
# The change order to daughterboard rev 0.14 (silkscreen only; same copper, parts and pinout):
#   1. daughter_rev14.py  the status lights named RUN / COMM / WARN / ERR / PWR, their references to F.Fab, J4's
#                         upside-down reference turned upright
#   2. silk_clean.py --fab-refs   the silkscreen rule: nothing on a pad, a part, other silkscreen or the edge; a
#                         reference with no room left beside its part goes to F.Fab (the assembly drawing)
#   3. silk_clean.py --check
# Needs pcbnew 9 ($K9) for steps 2-3. Afterwards: bump design.REV, reexport.sh daughter.
set -e
SRC=$(realpath "$1"); OUT=$2; T=${3:-$(mktemp -d)}
S=$(cd "$(dirname "$0")" && pwd)
K9=${K9:-python3}
q() { "$@" 2>&1 | grep --line-buffered -v "Debug\|swig\|leak"; }
python3 $S/daughter_rev14.py "$SRC" $T/a.kicad_pcb
cp "${SRC%.kicad_pcb}.kicad_pro" $T/a.kicad_pro
q $K9 $S/silk_clean.py $T/a.kicad_pcb "$OUT" --fab-refs
cp "${SRC%.kicad_pcb}.kicad_pro" "${OUT%.kicad_pcb}.kicad_pro" 2>/dev/null || true
$K9 $S/silk_clean.py "$OUT" --check 2>&1 | grep -v "Debug\|swig\|leak" | tail -12; [ "${PIPESTATUS[0]}" = 0 ]
