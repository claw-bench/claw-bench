#!/usr/bin/env bash
# Setup script for eml-009-thread-reconstruction
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$(dirname "$0")/data/flat_emails.json" "$WORKSPACE/flat_emails.json"

echo "Workspace created at $WORKSPACE"
