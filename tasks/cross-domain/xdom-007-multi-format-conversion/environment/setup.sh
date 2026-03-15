#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/source"

cp "$TASK_DIR/environment/data/data.csv" "$WORKSPACE/source/data.csv"
cp "$TASK_DIR/environment/data/notes.md" "$WORKSPACE/source/notes.md"
cp "$TASK_DIR/environment/data/config.json" "$WORKSPACE/source/config.json"

echo "Workspace ready at $WORKSPACE"
