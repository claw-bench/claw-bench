#!/usr/bin/env bash
# Setup script for wfl-006-event-driven-workflow
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/events.json" "$WORKSPACE/events.json"
cp "$TASK_DIR/environment/data/rules.json" "$WORKSPACE/rules.json"
echo "Workspace ready with events.json and rules.json"
