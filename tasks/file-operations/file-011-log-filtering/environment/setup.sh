#!/usr/bin/env bash
# Setup script for file-011-log-filtering
# Creates workspace and copies app.log into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/app.log" "$WORKSPACE/app.log"
echo "Workspace ready with app.log"
