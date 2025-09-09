#!/usr/bin/env bash
set -euo pipefail
SRC=${1:-figures/drawio/system_architecture.drawio}
OUT_DIR=${2:-figures/drawio/exports}
DRAWIO_CLI=${DRAWIO_CLI:-"npx --yes @drawio/cli"}
mkdir -p "$OUT_DIR"
if [[ ! -f "$SRC" ]]; then
  echo "Draw.io source not found: $SRC" >&2
  echo "Create it (see figures/system_architecture_outline.md) or provide path as first arg." >&2
  exit 1
fi
$DRAWIO_CLI -x -f svg -o "$OUT_DIR/system_architecture.svg" "$SRC"
$DRAWIO_CLI -x -f png -o "$OUT_DIR/system_architecture.png" "$SRC"
$DRAWIO_CLI -x -f html -o "$OUT_DIR/system_architecture.html" "$SRC"
cp "$SRC" "$OUT_DIR/system_architecture.xml"
echo "Exported to $OUT_DIR"
