#!/usr/bin/env bash
# Setup script for wfl-008-error-handling-workflow
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/workflow_steps.json" "$WORKSPACE/workflow_steps.json"
echo "Workspace ready with workflow_steps.json"
