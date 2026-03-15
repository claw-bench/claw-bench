#!/usr/bin/env bash
# Setup script for eml-006-generate-summary
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$(dirname "$0")/data/long_email.txt" "$WORKSPACE/long_email.txt"

echo "Workspace created at $WORKSPACE"
