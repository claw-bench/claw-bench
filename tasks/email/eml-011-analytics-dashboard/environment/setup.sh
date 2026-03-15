#!/usr/bin/env bash
# Setup script for eml-011-analytics-dashboard
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$(dirname "$0")/data/email_archive.json" "$WORKSPACE/email_archive.json"

echo "Workspace created at $WORKSPACE"
