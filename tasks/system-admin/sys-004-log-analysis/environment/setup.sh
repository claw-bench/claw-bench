#!/usr/bin/env bash
# Setup script for sys-004-log-analysis
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/syslog.txt" "$WORKSPACE/syslog.txt"
echo "Workspace ready with syslog.txt"
