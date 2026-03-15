#!/usr/bin/env bash
# Setup script for code-014-multi-file-refactor
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/app"
cp "$TASK_DIR/environment/data/app/__init__.py" "$WORKSPACE/app/__init__.py"
cp "$TASK_DIR/environment/data/app/models.py" "$WORKSPACE/app/models.py"
cp "$TASK_DIR/environment/data/app/views.py" "$WORKSPACE/app/views.py"
cp "$TASK_DIR/environment/data/app/utils.py" "$WORKSPACE/app/utils.py"
echo "Workspace ready with app/ directory"
