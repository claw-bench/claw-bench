#!/usr/bin/env bash
# Setup script for code-004-fix-syntax-errors
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/broken.py" "$WORKSPACE/broken.py"
echo "Workspace ready with broken.py"
