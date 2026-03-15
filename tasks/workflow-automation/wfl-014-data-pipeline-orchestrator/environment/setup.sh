#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/sources"
cp "$TASK_DIR/environment/data/sources/"*.csv "$WORKSPACE/sources/"
cp "$TASK_DIR/environment/data/transforms.json" "$WORKSPACE/"
