#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/text_summary.txt" "$WORKSPACE/"
cp "$TASK_DIR/environment/data/data_table.csv" "$WORKSPACE/"
cp "$TASK_DIR/environment/data/metadata.json" "$WORKSPACE/"
