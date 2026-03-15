#!/usr/bin/env bash
# Setup script for mem-002-multi-step-instructions
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="$TASK_DIR/workspace"
mkdir -p "$WORKSPACE"

cp "$TASK_DIR/environment/data/words.txt" "$WORKSPACE/words.txt"

echo "Workspace created at $WORKSPACE"
