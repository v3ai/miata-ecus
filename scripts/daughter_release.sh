#!/bin/bash
# daughter_release.sh <finished board> <outdir>
# Wired schematic, schematic <-> design netlist check, board linked to the schematic, DRC, JLC fab files,
# schematic PDF, parts workbook, renders and a copy of the design scripts.
set -e
BRD=$(realpath $1); OUT=$(realpath -m $2)
S=$(dirname $(realpath $0))
P=miata_ecu_daughter
SCH=$(mktemp -d)
mkdir -p $OUT/fab $OUT/renders
( cd $S && python3 gen_sch2.py $SCH $P > /dev/null )
cp $SCH/*.kicad_sch $OUT/
cp $S/$P.kicad_pro $OUT/$P.kicad_pro          # project template: net classes, 0.15 mm rules
( cd $OUT && kicad-cli sch export netlist --format kicadsexpr -o $SCH/$P.net $P.kicad_sch >/dev/null 2>&1 )
python3 $S/check_sch_netlist.py $SCH/$P.net
cp $BRD $OUT/${P}_in.kicad_pcb
cp $OUT/$P.kicad_pro $OUT/${P}_in.kicad_pro      # the board's rules (0.15 mm clearance) load with it
/usr/bin/python3 $S/link_board.py $OUT/${P}_in.kicad_pcb $SCH/fp_paths.txt $SCH/$P.net.names.json $OUT/$P.kicad_pcb
rm -f $OUT/${P}_in.kicad_pcb $OUT/${P}_in.kicad_pro $OUT/*.kicad_prl
/usr/bin/python3 $S/drc.py $OUT/$P.kicad_pcb $OUT/fab/drc_report.txt | tail -1
bash $S/export.sh $OUT/$P.kicad_pcb $OUT/fab > /dev/null
rm -rf $OUT/fab/gerbers
( cd $OUT && kicad-cli sch export pdf -o ${P}_schematic.pdf $P.kicad_sch >/dev/null 2>&1 )
( cd $S && /usr/bin/python3 parts_xlsx.py $OUT/miata_ecu_daughterboard_parts.xlsx > /dev/null )
bash $S/render.sh $OUT/$P.kicad_pcb $OUT/renders/top_copper_silk.png F.Cu,F.SilkS,Edge.Cuts
bash $S/render.sh $OUT/$P.kicad_pcb $OUT/renders/bottom_copper.png B.Cu,B.SilkS,Edge.Cuts
mkdir -p $OUT/scripts
for f in bom.py order_bom.py build_pcb.py check_sch_netlist.py daughter_finish.py daughter_make.sh daughter_release.sh design.py drc.py \
         export.sh flip_headers.py gen_sch.py gen_sch2.py link_board.py mpn.json parts_xlsx.py placement.py render.sh \
         route.py hand_route.py daughter_patch_05b.py sympins.py $P.kicad_pro stm32f407v_lqfp100_pins.txt wb_build.py wb_module.py wideband.py wb_clean.py wb_preview.py daughter_readme_v03.py daughter_readme_v04.py daughter_readme_v05.py; do
  cp $S/$f $OUT/scripts/
done
cp -r $S/wideband_ref $OUT/scripts/
rm -rf $SCH
echo released $OUT
