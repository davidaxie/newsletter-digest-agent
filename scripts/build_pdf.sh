#!/bin/bash
# Merge a report body HTML fragment into the template and render a PDF with headless Chrome.
# Usage: build_pdf.sh <body_fragment.html> <title> <output.pdf>
set -euo pipefail

BODY_FILE="$1"
TITLE="$2"
OUT_PDF="$3"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$REPO_DIR/template/report_template.html"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

WORK_HTML="$(mktemp -t digest).html"

python3 - "$TEMPLATE" "$BODY_FILE" "$TITLE" "$WORK_HTML" <<'PY'
import sys
template_path, body_path, title, out_path = sys.argv[1:5]
with open(template_path, encoding="utf-8") as f:
    template = f.read()
with open(body_path, encoding="utf-8") as f:
    body = f.read()
html = template.replace("{{TITLE}}", title).replace("{{CONTENT}}", body)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
PY

"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$OUT_PDF" "file://$WORK_HTML" 2>/dev/null

echo "Wrote $OUT_PDF"
