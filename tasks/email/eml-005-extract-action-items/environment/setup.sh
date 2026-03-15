#!/usr/bin/env bash
# Setup script for eml-005-extract-action-items
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$(dirname "$0")/data/email_thread.json" "$WORKSPACE/email_thread.json"

echo "Workspace created at $WORKSPACE"
