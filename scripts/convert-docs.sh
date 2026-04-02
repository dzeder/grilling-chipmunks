#!/bin/bash
# Converts Markdown files to DOCX and HTML (triple deliverable format)
# Usage:
#   ./scripts/convert-docs.sh                    # Convert all docs
#   ./scripts/convert-docs.sh docs/end-user/x.md # Convert specific file
# Dependencies: pandoc (brew install pandoc)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE="$PROJECT_ROOT/docs/templates/demo-template.html"
REFERENCE_DOCX="$PROJECT_ROOT/docs/templates/reference.docx"

convert_file() {
  local mdfile="$1"
  local dir=$(dirname "$mdfile")
  local base=$(basename "$mdfile" .md)

  echo "Converting: $mdfile"

  # Generate DOCX (with branded reference template)
  if [ -f "$REFERENCE_DOCX" ]; then
    pandoc "$mdfile" -o "${dir}/${base}.docx" \
      --reference-doc="$REFERENCE_DOCX"
  else
    pandoc "$mdfile" -o "${dir}/${base}.docx"
  fi
  echo "  -> ${dir}/${base}.docx"

  # Generate HTML with demo template
  if [ -f "$TEMPLATE" ]; then
    pandoc "$mdfile" -o "${dir}/${base}.html" \
      --standalone \
      --template="$TEMPLATE"
  else
    pandoc "$mdfile" -o "${dir}/${base}.html" --standalone \
      --metadata title="$base" \
      --css="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css"
  fi
  echo "  -> ${dir}/${base}.html"
}

if [ $# -gt 0 ]; then
  # Convert specific file
  convert_file "$1"
else
  # Convert all docs (excluding README files)
  COUNT=0
  while read mdfile; do
    convert_file "$mdfile"
    COUNT=$((COUNT + 1))
  done < <(find "$PROJECT_ROOT/docs" -name "*.md" -not -name "README.md")
  echo ""
  echo "Done. Converted $COUNT files."
fi
