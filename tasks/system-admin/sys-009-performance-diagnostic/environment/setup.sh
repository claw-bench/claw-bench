#!/usr/bin/env bash
# Setup script for sys-009-performance-diagnostic
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/metrics"
cp "$TASK_DIR/environment/data/cpu.csv" "$WORKSPACE/metrics/cpu.csv"
cp "$TASK_DIR/environment/data/memory.csv" "$WORKSPACE/metrics/memory.csv"
cp "$TASK_DIR/environment/data/disk_io.csv" "$WORKSPACE/metrics/disk_io.csv"
echo "Workspace ready with metrics/"
