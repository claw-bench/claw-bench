#!/usr/bin/env bash
# Setup script for wfl-009-scheduled-workflow-plan
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/tasks.json" "$WORKSPACE/tasks.json"
echo "Workspace ready with tasks.json"
