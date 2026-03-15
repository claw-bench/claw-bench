#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/q1.csv" "$WORKSPACE/q1.csv"
cp "$TASK_DIR/environment/data/q2.csv" "$WORKSPACE/q2.csv"
cp "$TASK_DIR/environment/data/q3.csv" "$WORKSPACE/q3.csv"
echo "Workspace ready with q1.csv, q2.csv, q3.csv"
