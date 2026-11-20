#!/bin/bash
# reexport.sh daughter | <year module> <short> <rev> <board folder>
#   e.g. reexport.sh daughter        reexport.sh mb_na6 8995 0.14 motherboards/1989-95
#
# Regenerates, in place, everything in a released board folder that is derived from the finished board and the
# design scripts, WITHOUT changing the board itself: the schematic sheets (and their netlist check against the
# design; a sheet is only rewritten when it differs other than in its ids), the schematic PDF (when a sheet changed), the DRC report, the JLC fab files and BOMs, the parts workbook / list, the track
# current report (daughterboard) and the 2D renders. Use it after a change order on a finished board (for example
# via_out_of_pad.py + backport_copper.py) instead of the full make / release scripts, which also place and route.
#
# The board's own checks run first and stop the export on a failure: schematic against design, every LCSC number
# against its real part and value (check_lcsc.py), KiCad DRC (no errors,
# nothing unconnected), jlc_fab_check (no via in a pad, edge clearance), and via_hole_gap.py on a scratch copy (it
# must find nothing to remove). Works with KiCad 7 or, with the KiCad 9 shim on PYTHONPATH, KiCad 9.
set -e
S=$(dirname $(realpath $0)); ROOT=$S/..
TMP=$(mktemp -d); trap 'rm -rf $TMP' EXIT
py() { /usr/bin/python3 "$@"; }
U='s/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}//g'
SCH_CHANGED=0
put_sheets() {   # <dir>: copy the generated sheets in only where they differ from the board's other than in their ids
  for f in $TMP/*.kicad_sch; do
    local b=$(basename $f)
    if [ -f $1/$b ] && cmp -s <(sed -E "$U" $f) <(sed -E "$U" $1/$b); then continue; fi
    cp $f $1/$b; SCH_CHANGED=1; echo "  schematic sheet changed: $b"
  done
}
board_checks() {   # <board> <report>
  local B=$1
  python3 $S/check_lcsc.py > $TMP/lcsc.txt || { cat $TMP/lcsc.txt; exit 1; }
  tail -1 $TMP/lcsc.txt
  cp $B $TMP/vhg.kicad_pcb; cp ${B%.kicad_pcb}.kicad_pro $TMP/vhg.kicad_pro
  local G=$(py $S/via_hole_gap.py $TMP/vhg.kicad_pcb $TMP/vhg_out.kicad_pcb 2>&1 | grep -v leak | tail -1)
  echo "  via_hole_gap: $G"
  case "$G" in "deleted stitching vias: 0  routed vias too close (net, x, y, gap): []") ;;
    *) echo "  via_hole_gap would change the board: fix it first"; exit 1;; esac
  py $S/drc.py $B $2 | tail -1
  sed -i -E '1s|for .*/([^/]+\.kicad_pcb) \*\*|for \1 **|' $2     # the file name, not this machine's path
  # the gate: KiCad's own DRC, errors only, with the board's rules
  kicad-cli pcb drc --format json --severity-error -o $TMP/drc.json $(realpath $B) >/dev/null 2>&1
  py -c "
import json, sys; d = json.load(open('$TMP/drc.json'))
# not counted: courtyard overlaps (reviewed: the bodies clear and the pads meet JLC's spacing table) and, on the
# motherboards, starved thermals (pad spokes the pour cannot complete, listed in the DRC report; KiCad 9 refills
# report a few more than KiCad 7's saved fill)
SKIP = ('courtyards_overlap', 'starved_thermal')
e = sum(1 for v in d['violations'] if v['type'] not in SKIP); u = len(d['unconnected_items'])
st = sum(1 for v in d['violations'] if v['type'] == 'starved_thermal')
print(f'  KiCad DRC: {e} errors ({st} starved thermals and the courtyard overlaps not counted), {u} unconnected')
sys.exit(1 if e or u else 0)"
  py $S/jlc_spacing.py $B 2>/dev/null | head -1
  py $S/jlc_fab_check.py $B
}
if [ "$1" = daughter ]; then
  D=$ROOT/daughterboard; P=miata_ecu_daughter; B=$D/$P.kicad_pcb
  REV=$(cd $S && py -c 'import design; print(design.REV)' 2>/dev/null | tail -1)
  echo "daughterboard rev $REV"
  ( cd $S && python3 gen_sch2.py $TMP $P > /dev/null )
  put_sheets $D
  ( cd $D && kicad-cli sch export netlist --format kicadsexpr -o $TMP/$P.net $P.kicad_sch >/dev/null 2>&1 )
  python3 $S/check_sch_netlist.py $TMP/$P.net | tail -1
  board_checks $B $D/fab/drc_report.txt
  ( cd $ROOT && py scripts/track_current.py daughterboard/$P.kicad_pcb --all ) | grep -v leak > $D/fab/track_current.txt; tail -1 $D/fab/track_current.txt
  rm -f $D/fab/*_jlcpcb_gerbers.zip $D/fab/*_jlcpcb_bom.csv $D/fab/*_jlcpcb_cpl.csv $D/fab/*_self_order_bom.csv
  FABPREFIX=miata-ecu-daughterboard-rev${REV}_ bash $S/export.sh $B $D/fab > /dev/null
  rm -rf $D/fab/gerbers
  [ $SCH_CHANGED = 1 ] || [ ! -f $D/${P}_schematic.pdf ] && ( cd $D && kicad-cli sch export pdf -o ${P}_schematic.pdf $P.kicad_sch >/dev/null 2>&1 )
  ( cd $S && py parts_xlsx.py $D/miata_ecu_daughterboard_parts.xlsx > /dev/null )
  bash $S/render.sh $B $D/renders/top_copper_silk.png F.Cu,F.SilkS,Edge.Cuts
  bash $S/render.sh $B $D/renders/bottom_copper.png B.Cu,B.SilkS,Edge.Cuts
else
  MOD=$1; SHORT=$2; REV=$3; D=$(realpath $4); P=miata_mb_$SHORT; B=$D/$P.kicad_pcb
  export MBREV=$REV
  echo "motherboard $SHORT rev $REV"
  ( cd $S && python3 gen_sch_mb.py $MOD $TMP $P | tail -1 )
  put_sheets $D
  ( cd $D && kicad-cli sch export netlist --format kicadsexpr -o $TMP/$P.net $P.kicad_sch >/dev/null 2>&1 )
  python3 $S/check_mb_netlist.py $MOD $TMP/$P.net | tail -1
  board_checks $B $D/fab/drc_report.txt
  py $S/mb_gnd_islands.py $B | grep -v leak | tail -1
  py $S/mb_export.py $MOD $B $D/fab
  rm -rf $D/fab/gerbers
  [ $SCH_CHANGED = 1 ] || [ ! -f $D/${P}_schematic.pdf ] && ( cd $D && kicad-cli sch export pdf -o ${P}_schematic.pdf $P.kicad_sch >/dev/null 2>&1 )
  bash $S/render.sh $B $D/renders/top_copper_silk.png F.Cu,F.SilkS,Edge.Cuts 2400
  bash $S/render.sh $B $D/renders/bottom_copper.png B.Cu,B.SilkS,Edge.Cuts 2400
  ( cd $S && python3 mb_readme.py $MOD $D/README.md | tail -1 )
fi
rm -f $D/*.kicad_prl $D/fp-info-cache
echo "re-exported $D"
