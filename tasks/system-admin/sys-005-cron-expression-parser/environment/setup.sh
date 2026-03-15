#!/usr/bin/env bash
# Setup script for sys-005-cron-expression-parser
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/crontab.txt" "$WORKSPACE/crontab.txt"
echo "Workspace ready with crontab.txt"
