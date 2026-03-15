#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/notifications.json" "$WORKSPACE/notifications.json"
cp "$TASK_DIR/environment/data/preferences.json" "$WORKSPACE/preferences.json"
echo "Workspace ready with notifications.json and preferences.json"
