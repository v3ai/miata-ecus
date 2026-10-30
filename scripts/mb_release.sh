#!/bin/bash
# mb_release.sh <year module> <short name, e.g. 8993> <routed board> <schematic dir> <outdir>
# Links the board to the schematic, runs DRC, exports fab files and the schematic PDF.
set -e
TMP=$(mktemp -d)
MOD=$1; SHORT=$2; BRD=$(realpath $3); SCH=$(realpath $4); OUT=$5
S=$(dirname $(realpath $0))
P=miata_mb_$SHORT
mkdir -p $OUT/fab
cp $SCH/*.kicad_sch $OUT/
cp $BRD $OUT/$P.kicad_pcb.tmp
cp $(ls $(dirname $BRD)/*_placed.kicad_pro | head -1) $OUT/$P.kicad_pro
cp $OUT/$P.kicad_pro $OUT/$P.kicad_pcb.kicad_pro 2>/dev/null || true
( cd $OUT && kicad-cli sch export netlist --format kicadsexpr -o $TMP/$P.net $P.kicad_sch >/dev/null 2>&1 )
python3 $S/check_mb_netlist.py $MOD $TMP/$P.net
cp $OUT/$P.kicad_pro $OUT/${P}_in.kicad_pro
mv $OUT/$P.kicad_pcb.tmp $OUT/${P}_in.kicad_pcb
/usr/bin/python3 $S/link_board.py $OUT/${P}_in.kicad_pcb $SCH/fp_paths.txt $TMP/$P.net.names.json $OUT/$P.kicad_pcb
rm -f $OUT/${P}_in.kicad_pcb $OUT/${P}_in.kicad_pro $OUT/$P.kicad_pcb.kicad_pro $OUT/*.kicad_prl
/usr/bin/python3 $S/mb_cleanup.py $OUT/$P.kicad_pcb
/usr/bin/python3 $S/drc.py $OUT/$P.kicad_pcb $OUT/fab/drc_report.txt | tail -1
/usr/bin/python3 $S/mb_export.py $MOD $OUT/$P.kicad_pcb $OUT/fab
( cd $OUT && kicad-cli sch export pdf -o ${P}_schematic.pdf $P.kicad_sch >/dev/null 2>&1 )
mkdir -p $OUT/ecu_mb.pretty && cp $S/../mb/ecu_mb.pretty/*.kicad_mod $OUT/ecu_mb.pretty/
cat > $OUT/fp-lib-table <<EOF
(fp_lib_table
  (lib (name "ecu_mb")(type "KiCad")(uri "\${KIPRJMOD}/ecu_mb.pretty")(options "")(descr "Miata ECU motherboard footprints"))
)
EOF
echo released $OUT
