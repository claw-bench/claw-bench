#!/usr/bin/env bash
# Setup script for code-003-add-type-annotations
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/utils.py" "$WORKSPACE/utils.py"
echo "Workspace ready with utils.py"
