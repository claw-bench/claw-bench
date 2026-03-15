#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$TASK_DIR/environment/data/source_schema.json" "$WORKSPACE/source_schema.json"
cp "$TASK_DIR/environment/data/target_schema.json" "$WORKSPACE/target_schema.json"
cp "$TASK_DIR/environment/data/sample_data.csv" "$WORKSPACE/sample_data.csv"

echo "Workspace ready at $WORKSPACE"
