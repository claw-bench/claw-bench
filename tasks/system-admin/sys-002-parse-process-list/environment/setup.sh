#!/usr/bin/env bash
# Setup script for sys-002-parse-process-list
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/processes.txt" "$WORKSPACE/processes.txt"
echo "Workspace ready with processes.txt"
