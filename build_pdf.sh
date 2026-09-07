#!/bin/sh
# usage: ./build_pdf.sh [report.md | report_zh.md]   (default: report.md)
# -implicit_figures keeps the alt text in the .md for GitHub while stopping
# pandoc from turning each image into a floating LaTeX figure with its own caption
set -e
SRC="${1:-report.md}"
OUT="$(basename "$SRC" .md).pdf"
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"

# drop the hand-written contents list; pandoc's --toc has working links
python3 - "$SRC" <<'PY'
import sys,re
s=open(sys.argv[1]).read()
m=re.search(r'^## (Contents|目录)\s*$', s, re.M)
if m:
    j=s.index("---", m.end())+4
    s=s[:m.start()]+s[j:]
open(".report_pdf.md","w").write(s)
PY

# Chinese needs xeCJK plus a CJK font; the Latin face stays the same in both.
# set -- keeps the font name a single argument despite the space in it.
case "$SRC" in
  *_zh.md) set -- -V "CJKmainfont=Songti SC" -V "CJKoptions=Scale=0.95" ;;
  *)       set -- ;;
esac

pandoc .report_pdf.md -o "$OUT" \
  -f markdown-implicit_figures \
  --pdf-engine=xelatex --toc --toc-depth=2 \
  --include-in-header=pandoc-header.tex \
  --resource-path=. \
  -V geometry:margin=2.2cm -V fontsize=10pt \
  -V colorlinks=true -V linkcolor=RoyalBlue -V urlcolor=RoyalBlue \
  -V mainfont="Palatino" -V monofont="Menlo" "$@"
rm -f .report_pdf.md
echo "wrote $OUT"
