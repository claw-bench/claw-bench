#!/usr/bin/env bash
# Setup script for code-006-refactor-comprehensions
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/process.py" "$WORKSPACE/process.py"
echo "Workspace ready with process.py"
