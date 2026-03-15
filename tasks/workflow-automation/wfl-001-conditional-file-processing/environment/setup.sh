#!/usr/bin/env bash
# Setup script for wfl-001-conditional-file-processing
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/config.json" "$WORKSPACE/config.json"
cp "$TASK_DIR/environment/data/input.txt" "$WORKSPACE/input.txt"
echo "Workspace ready with config.json and input.txt"
