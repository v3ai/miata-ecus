#!/bin/bash
# export.sh board.kicad_pcb outdir  -> gerbers+drill zip, DRC report, BOM/CPL
set -e
B=$1; O=$2
mkdir -p "$O/gerbers"
rm -f "$O"/gerbers/*
kicad-cli pcb export gerbers -l F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --no-x2 -o "$O/gerbers/" "$B" >/dev/null
kicad-cli pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 \
  -o "$O/gerbers/" "$B" >/dev/null
# fab files carry the board and revision, e.g. miata-ecu-daughterboard-rev0.9_jlcpcb_gerbers.zip
SCRIPTS=$(dirname "$0")
export FABPREFIX=${FABPREFIX:-miata-ecu-daughterboard-rev$(cd "$SCRIPTS" && python3 -c 'import design; print(design.REV)' 2>/dev/null | tail -1)_}
rm -f "$O"/*jlcpcb_gerbers.zip "$O"/*jlcpcb_bom.csv "$O"/*jlcpcb_cpl.csv "$O"/*self_order_bom.csv
(cd "$O/gerbers" && zip -q ../${FABPREFIX}jlcpcb_gerbers.zip *)

(cd "$SCRIPTS" && /usr/bin/python3 bom.py "$O" "$B")
