#!/usr/bin/env bash
# Setup script for code-015-performance-optimization
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/slow.py" "$WORKSPACE/slow.py"
echo "Workspace ready with slow.py"
