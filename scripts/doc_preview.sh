#!/usr/bin/env bash
# Simple local preview of repository Markdown documentation.
# Usage: ./scripts/doc_preview.sh [DIRECTORY] [PORT]

set -euo pipefail

DOC_DIR=${1:-docs}
PORT=${2:-8000}

printf "\nServing '%s' at http://localhost:%s  (press Ctrl+C to stop)\n" "$DOC_DIR" "$PORT"
python -m http.server --directory "$DOC_DIR" "$PORT" 