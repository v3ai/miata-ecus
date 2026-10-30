#!/bin/bash
# README + research notes + zip for one built motherboard release.
# usage: mb_finish.sh <year module> <short> <rev>     e.g. mb_nb1 9900 0.1
set -e
M=$1; S=$2; REV=$3
ROOT=$(cd "$(dirname "$0")/.." && pwd)
REL=$ROOT/mb/release_$S
cd $ROOT/scripts
MBREV=$REV python3 mb_readme.py $M $REL/README.md
if [ -f $ROOT/research/pinouts_9605.md ] && [ "$S" != 8993 ] && [ "$S" != 9495 ]; then
  mkdir -p $REL/research && cp $ROOT/research/pinouts_9605.md $REL/research/
fi
NAME=miata_mb_${S}_rev${REV}
cd $ROOT/mb
rm -rf pkg_$S && mkdir pkg_$S && cp -r $REL pkg_$S/$NAME
(cd pkg_$S && rm -f ../$NAME.zip && zip -qr ../$NAME.zip $NAME)
rm -rf pkg_$S
echo "zipped $ROOT/mb/$NAME.zip"
