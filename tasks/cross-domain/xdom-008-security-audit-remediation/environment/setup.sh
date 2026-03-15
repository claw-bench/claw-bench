#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/app_code"

cp "$TASK_DIR/environment/data/auth.py" "$WORKSPACE/app_code/auth.py"
cp "$TASK_DIR/environment/data/api.py" "$WORKSPACE/app_code/api.py"
cp "$TASK_DIR/environment/data/utils.py" "$WORKSPACE/app_code/utils.py"

echo "Workspace ready at $WORKSPACE"
