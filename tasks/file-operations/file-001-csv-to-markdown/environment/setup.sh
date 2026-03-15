#!/usr/bin/env bash
# Setup script for file-001-csv-to-markdown
# Creates workspace and copies sample.csv into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/sample.csv" "$WORKSPACE/sample.csv"
echo "Workspace ready with sample.csv"
