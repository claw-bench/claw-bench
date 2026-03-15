#!/usr/bin/env bash
# Setup script for file-004-sort-lines
# Creates workspace and copies names.txt into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/names.txt" "$WORKSPACE/names.txt"
echo "Workspace ready with names.txt"
