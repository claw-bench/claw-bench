#!/usr/bin/env bash
# Setup script for file-012-csv-stats
# Creates workspace and copies sales.csv into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/sales.csv" "$WORKSPACE/sales.csv"
echo "Workspace ready with sales.csv"
