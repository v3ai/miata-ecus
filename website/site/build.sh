#!/bin/bash
# build.sh <out dir>: the static website for singularityboards.com (GitHub Pages; .github/workflows/pages.yaml runs it
# on every push to main that touches website/ or viewer/).
#   - the Mono theme's pages, rendered without a store (preview/render.js with SITE=1): the homepage, a page per
#     product (shown as coming soon), the shop page and the 404 page
#   - the 3D board viewer at /viewer/ (viewer/index.html and its assets as committed)
#   - CNAME (the custom domain) and .nojekyll (serve the files as they are)
# Needs node and liquidjs on NODE_PATH (npm i liquidjs@10.30.0).
set -e
OUT=$(realpath -m "$1"); W=$(cd "$(dirname "$0")/.." && pwd); R=$(cd "$W/.." && pwd)
rm -rf "$OUT"; mkdir -p "$OUT/viewer"
SITE=1 node "$W/preview/render.js" "$W/theme" "$OUT"
( cd "$R" && git ls-files viewer | grep -v '\.py$' | while read -r f; do cp "$f" "$OUT/$f"; done )
echo singularityboards.com > "$OUT/CNAME"
touch "$OUT/.nojekyll"
echo "site in $OUT: $(find "$OUT" -type f | wc -l) files, $(du -sh "$OUT" | cut -f1)"
