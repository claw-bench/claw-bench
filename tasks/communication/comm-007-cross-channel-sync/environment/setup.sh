#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/channels.json" "$WORKSPACE/channels.json"
cp "$TASK_DIR/environment/data/sync_rules.json" "$WORKSPACE/sync_rules.json"
echo "Workspace ready with channels.json and sync_rules.json"
