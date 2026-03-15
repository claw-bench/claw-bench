#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/source_code"

cp "$TASK_DIR/environment/data/models.py" "$WORKSPACE/source_code/models.py"
cp "$TASK_DIR/environment/data/database.py" "$WORKSPACE/source_code/database.py"
cp "$TASK_DIR/environment/data/api.py" "$WORKSPACE/source_code/api.py"
cp "$TASK_DIR/environment/data/auth.py" "$WORKSPACE/source_code/auth.py"
cp "$TASK_DIR/environment/data/utils.py" "$WORKSPACE/source_code/utils.py"

echo "Workspace ready at $WORKSPACE"
