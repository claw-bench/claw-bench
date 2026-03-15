#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$TASK_DIR/environment/data/input.csv" "$WORKSPACE/input.csv"
cp "$TASK_DIR/environment/data/pipeline_config.json" "$WORKSPACE/pipeline_config.json"

echo "Workspace ready at $WORKSPACE"
