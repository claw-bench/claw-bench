#!/usr/bin/env bash
# Setup script for wfl-004-retry-with-backoff
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/jobs.json" "$WORKSPACE/jobs.json"
echo "Workspace ready with jobs.json"
