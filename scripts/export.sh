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
(cd "$O/gerbers" && zip -q ../jlcpcb_gerbers.zip *)


SCRIPTS=$(dirname "$0")
(cd "$SCRIPTS" && /usr/bin/python3 bom.py "$O" "$B")
