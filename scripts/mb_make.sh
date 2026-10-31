#!/bin/bash
# mb_make.sh <year module> <short name> <rev>  ->  mb/<short>/ work files, mb/release_<short>/ , mb/miata_mb_<short>_rev<rev>.zip
set -e
MOD=$1; SHORT=$2; REV=$3; export MBREV=$REV
S=$(dirname $(realpath $0)); ROOT=$S/..
W=$ROOT/mb/work_$SHORT; R=$ROOT/mb/release_$SHORT; P=miata_mb_$SHORT
mkdir -p $W; rm -rf $R $W/sch; mkdir -p $W/sch
cp $S/miata_mb_template.kicad_pro $W/${SHORT}_placed.kicad_pro      # project template: net classes, rules
/usr/bin/python3 $S/mb_build.py $MOD $W/${SHORT}_placed.kicad_pcb
cp $W/${SHORT}_placed.kicad_pro $W/${SHORT}_routed.kicad_pro
(cd $W && /usr/bin/python3 $S/mb_route.py $MOD ${SHORT}_placed.kicad_pcb ${SHORT}_routed.kicad_pcb > route.log 2>&1)
grep "routed in" $W/route.log
/usr/bin/python3 $S/mb_cleanup.py $W/${SHORT}_routed.kicad_pcb 2>&1 | grep -v leak || true
python3 $S/gen_sch_mb.py $MOD $W/sch $P | tail -1
bash $S/mb_release.sh $MOD $SHORT $W/${SHORT}_routed.kicad_pcb $W/sch $R 2>&1 | grep -v leak
mkdir -p $R/renders $R/scripts
$S/render.sh $R/$P.kicad_pcb $R/renders/top_copper_silk.png F.Cu,F.SilkS,Edge.Cuts 2400
$S/render.sh $R/$P.kicad_pcb $R/renders/bottom_copper.png B.Cu,B.SilkS,Edge.Cuts 2400
for f in check_mb_netlist.py design.py drc.py gen_sch.py gen_sch2.py gen_sch_mb.py link_board.py mb_build.py mb_cleanup.py \
         mb_common.py mb_export.py order_bom.py mpn.json miata_mb_template.kicad_pro mb_na6.py mb_na8.py mb_later.py mk_hdr_fp.py mb_readme.py mb_release.sh mb_route.py mb_make.sh route.py wideband.py wb_module.py; do
  [ -f $S/$f ] && cp $S/$f $R/scripts/
done
cp $S/$MOD.py $R/scripts/ 2>/dev/null || true
cp -r $S/wideband_ref $R/scripts/
rm -rf $R/fab/gerbers $R/*.kicad_prl
echo "made $R"
