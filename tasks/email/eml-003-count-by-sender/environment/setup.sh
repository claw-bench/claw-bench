#!/usr/bin/env bash
# Setup script for eml-003-count-by-sender
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$(dirname "$0")/data/inbox.json" "$WORKSPACE/inbox.json"

echo "Workspace created at $WORKSPACE"
