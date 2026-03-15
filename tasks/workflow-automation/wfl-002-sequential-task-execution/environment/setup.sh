#!/usr/bin/env bash
# Setup script for wfl-002-sequential-task-execution
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/tasks.json" "$WORKSPACE/tasks.json"
cp "$TASK_DIR/environment/data/input.txt" "$WORKSPACE/input.txt"
echo "Workspace ready with tasks.json and input.txt"
