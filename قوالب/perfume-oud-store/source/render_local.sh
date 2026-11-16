#!/bin/sh
# Rebuild sections + homepage, export the HTML copy, capture it (needs the 8817 server on .clone/ec6481/tpl).
set -e
S="$(cd "$(dirname "$0")" && pwd)"; T="$S/../theme"; W="$T/.clone/ec6481/tpl"
K=/c/dev/shopify-clone-kit/plugins/shopify-clone-kit/skills/theme-clone/scripts
cd "$T"; python "$S/gen.py" sections >/dev/null; python "$S/build_index.py" . 
cp sections/ck-ec-*.liquid "$W/sections/"; cp templates/index.json "$W/templates/"
cd "$W"; python $K/export_html.py . --lang ar --dir rtl --shop-name "أساس" --nav "العطور|العود والبخور|الهدايا" --head-html head.html --noindex
cd ..; python $K/capture.py "http://127.0.0.1:8817/html/index.html" --mode local --no-assets --no-behaviors --out local | tail -1
python $K/diff.py --source desktop.png --candidate local/desktop.png --out diff --label desktop | tail -15
python $K/diff.py --source mobile.png --candidate local/mobile.png --out diff --label mobile | tail -15
