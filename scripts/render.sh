#!/bin/bash
# render.sh board.kicad_pcb out.png [layers]
L=${3:-F.Cu,B.Cu,F.SilkS,F.Fab,Edge.Cuts}
SVG=$(mktemp --suffix=.svg)
kicad-cli pcb export svg --exclude-drawing-sheet --page-size-mode 2 -l "$L" -o $SVG "$1" >/dev/null 2>&1 || kicad-cli pcb export svg -l "$L" -o $SVG "$1"
rsvg-convert -w ${4:-2400} -b white $SVG -o "$2"
