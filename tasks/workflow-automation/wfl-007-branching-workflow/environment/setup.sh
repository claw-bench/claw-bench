#!/usr/bin/env bash
# Setup script for wfl-007-branching-workflow
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/applications.json" "$WORKSPACE/applications.json"
cp "$TASK_DIR/environment/data/workflow.json" "$WORKSPACE/workflow.json"
echo "Workspace ready with applications.json and workflow.json"
