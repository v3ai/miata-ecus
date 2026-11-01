#!/bin/bash
# Build + route + finish the daughterboard into <workdir>.
# usage: daughter_make.sh <workdir>
set -e
W=$1
S=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$W"; cd "$W"
python3 "$S/build_pcb.py" daughter.kicad_pcb > build.log 2>&1
python3 "$S/route.py" daughter.kicad_pcb routed.kicad_pcb > route.log 2>&1
if [ "$(python3 -c "import json; print(len(json.load(open('routed.kicad_pcb.failed.json'))))")" != "0" ]; then
  RESUME=1 FINISH=1 python3 "$S/route.py" daughter.kicad_pcb routed.kicad_pcb >> route.log 2>&1
fi
python3 "$S/flip_headers.py" routed.kicad_pcb flipped.kicad_pcb > finish.log 2>&1
python3 "$S/daughter_finish.py" flipped.kicad_pcb finished.kicad_pcb >> finish.log 2>&1
python3 "$S/drc.py" finished.kicad_pcb drc.txt > drc.log 2>&1 || true
echo "made $W/finished.kicad_pcb (rev 0.5b: then run daughter_patch_05b.py finished.kicad_pcb patched.kicad_pcb)"
