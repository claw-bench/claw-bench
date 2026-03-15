#!/usr/bin/env bash
# Setup script for mem-001-recall-given-name
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="$TASK_DIR/workspace"
mkdir -p "$WORKSPACE"

cp "$TASK_DIR/environment/data/inventory.csv" "$WORKSPACE/inventory.csv"
cp "$TASK_DIR/environment/data/notes.txt" "$WORKSPACE/notes.txt"

echo "Workspace created at $WORKSPACE"
