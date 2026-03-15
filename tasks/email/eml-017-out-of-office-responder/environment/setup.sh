#!/usr/bin/env bash
# Setup script for eml-017-out-of-office-responder
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/incoming"

cp "$(dirname "$0")/data/ooo_config.json" "$WORKSPACE/ooo_config.json"

for f in "$(dirname "$0")/data"/incoming_*.json; do
    cp "$f" "$WORKSPACE/incoming/"
done

echo "Workspace created at $WORKSPACE"
