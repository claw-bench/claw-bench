#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$TASK_DIR/environment/data/pull_request.py" "$WORKSPACE/pull_request.py"

echo "Workspace ready at $WORKSPACE"
