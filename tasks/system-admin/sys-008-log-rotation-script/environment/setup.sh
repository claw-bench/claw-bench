#!/usr/bin/env bash
# Setup script for sys-008-log-rotation-script
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/logs"
cp "$TASK_DIR/environment/data/log_manifest.json" "$WORKSPACE/logs/log_manifest.json"
echo "Workspace ready with logs/log_manifest.json"
