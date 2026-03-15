#!/usr/bin/env bash
# Setup script for doc-013-csv-report-formatter
# Creates workspace and copies data.csv into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/data.csv" "$WORKSPACE/data.csv"
echo "Workspace ready with data.csv"
