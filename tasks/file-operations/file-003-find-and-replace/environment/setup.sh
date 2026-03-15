#!/usr/bin/env bash
# Setup script for file-003-find-and-replace
# Creates workspace and copies input.txt into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/input.txt" "$WORKSPACE/input.txt"
echo "Workspace ready with input.txt"
