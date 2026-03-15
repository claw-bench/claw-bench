#!/usr/bin/env bash
# Setup script for file-015-data-pipeline
# Creates workspace and copies raw_data.csv into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/raw_data.csv" "$WORKSPACE/raw_data.csv"
echo "Workspace ready with raw_data.csv"
