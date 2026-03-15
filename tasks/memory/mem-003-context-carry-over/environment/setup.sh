#!/usr/bin/env bash
# Setup script for mem-003-context-carry-over
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="$TASK_DIR/workspace"
mkdir -p "$WORKSPACE"

cp "$TASK_DIR/environment/data/config.json" "$WORKSPACE/config.json"

echo "Workspace created at $WORKSPACE"
