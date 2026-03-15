#!/usr/bin/env bash
# Setup script for file-008-deduplicate-lines
# Creates workspace and copies data.txt into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/data.txt" "$WORKSPACE/data.txt"
echo "Workspace ready with data.txt"
