#!/usr/bin/env bash
# Setup script for comm-015-channel-activity-report
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/channels.json" "$WORKSPACE/channels.json"
echo "Workspace ready with channels.json"
