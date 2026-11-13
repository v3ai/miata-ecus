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
  # one rip-up pass (it also repairs the plane vias), then the exact-geometry finisher joins what is still open
  RESUME=1 FINISH=1 FPASSES=${FPASSES:-1} python3 "$S/route.py" daughter.kicad_pcb routed.kicad_pcb >> route.log 2>&1
fi
cp routed.kicad_pro routed_u.kicad_pro; cp routed.kicad_pro routed_f.kicad_pro
python3 "$S/finish_route.py" --unclose routed.kicad_pcb routed_u.kicad_pcb > finish_route.log 2>&1
for round in 1 2 3; do
  # stubs left by a removal go first, or a new join could land on one and be trimmed away with it later
  python3 "$S/clean_dangling.py" routed_u.kicad_pcb routed_u.kicad_pcb >> finish_route.log 2>&1 || true
  PLANE_FIRST=1 python3 "$S/finish_route.py" routed_u.kicad_pcb routed_f.kicad_pcb > finish_round.log 2>&1 || true
  cat finish_round.log >> finish_route.log
  BLOCKED=$(grep -o "BLOCKED [A-Za-z0-9]*\.[0-9A-Za-z]*" finish_round.log | cut -d" " -f2 | tr "\n" " ")
  [ -z "$BLOCKED" ] && break
  # a plane pad with no room for its via, not even in the pad: clear the tracks under it and finish again
  python3 "$S/finish_route.py" --free routed_u.kicad_pcb routed_u2.kicad_pcb $BLOCKED >> finish_route.log 2>&1
  mv routed_u2.kicad_pcb routed_u.kicad_pcb
done
python3 "$S/clean_dangling.py" routed_f.kicad_pcb routed_f.kicad_pcb >> finish_route.log 2>&1 || true
python3 "$S/flip_headers.py" routed_f.kicad_pcb flipped.kicad_pcb > finish.log 2>&1
python3 "$S/daughter_finish.py" flipped.kicad_pcb finished.kicad_pcb >> finish.log 2>&1
python3 "$S/drc.py" finished.kicad_pcb drc.txt > drc.log 2>&1 || true
echo "made $W/finished.kicad_pcb (then run daughter_patch.py finished.kicad_pcb patched.kicad_pcb)"
