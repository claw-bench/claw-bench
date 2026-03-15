#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="$TASK_DIR/workspace"
mkdir -p "$WORKSPACE"
if [ -d "$TASK_DIR/environment/data" ]; then
    cp -r "$TASK_DIR/environment/data/"* "$WORKSPACE/" 2>/dev/null || true
fi
