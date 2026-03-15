#!/usr/bin/env bash
# Setup script for file-014-file-diff
# Creates workspace and copies original.txt and modified.txt into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/original.txt" "$WORKSPACE/original.txt"
cp "$TASK_DIR/environment/data/modified.txt" "$WORKSPACE/modified.txt"
echo "Workspace ready with original.txt and modified.txt"
