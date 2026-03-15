#!/usr/bin/env bash
# Setup script for mem-004-contradiction-resolution
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="$TASK_DIR/workspace"
mkdir -p "$WORKSPACE"

cp "$TASK_DIR/environment/data/spec.txt" "$WORKSPACE/spec.txt"

echo "Workspace created at $WORKSPACE"
