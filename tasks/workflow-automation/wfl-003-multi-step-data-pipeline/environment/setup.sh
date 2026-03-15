#!/usr/bin/env bash
# Setup script for wfl-003-multi-step-data-pipeline
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/pipeline.json" "$WORKSPACE/pipeline.json"
cp "$TASK_DIR/environment/data/data.csv" "$WORKSPACE/data.csv"
echo "Workspace ready with pipeline.json and data.csv"
