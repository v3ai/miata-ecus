#!/bin/bash
# castellate_daughter.sh <daughterboard.kicad_pcb (KiCad 7, rev 0.12 layout)> <out.kicad_pcb (KiCad 7)>
# The rev 0.13 change order: castellated J1 / J2 edges. Footprints and outline in the KiCad 7 text
# (castellate_daughter.py), track ends and zone fills under KiCad 9 (castellate_copper.py), copper carried back into
# the KiCad 7 file (backport_copper.py). Needs pcbnew 9 on PYTHONPATH (the KiCad 9 shim) for the middle step.
set -e
S=$(dirname $(realpath $0)); TMP=$(mktemp -d); trap 'rm -rf $TMP' EXIT
IN=$(realpath $1); OUT=$2
python3 $S/castellate_daughter.py $IN $TMP/a.kicad_pcb
cp $(dirname $IN)/*.kicad_pro $TMP/a.kicad_pro 2>/dev/null || true
/usr/bin/python3 $S/castellate_copper.py $TMP/a.kicad_pcb $TMP/b.kicad_pcb 2>&1 | grep -v "Debug\|swig\|leak"
/usr/bin/python3 $S/backport_copper.py $TMP/a.kicad_pcb $TMP/b.kicad_pcb $OUT 2>&1 | grep -v "Debug\|swig\|leak"
