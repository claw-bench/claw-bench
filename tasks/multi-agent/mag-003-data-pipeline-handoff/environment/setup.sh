#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/pipeline"
cp "$TASK_DIR/environment/data/raw_data.csv" "$WORKSPACE/"
