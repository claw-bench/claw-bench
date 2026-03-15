#!/usr/bin/env bash
# Setup script for sys-001-disk-usage-report
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/filesystem.txt" "$WORKSPACE/filesystem.txt"
echo "Workspace ready with filesystem.txt"
