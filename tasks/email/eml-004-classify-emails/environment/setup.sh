#!/usr/bin/env bash
# Setup script for eml-004-classify-emails
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$(dirname "$0")/data/emails.json" "$WORKSPACE/emails.json"

echo "Workspace created at $WORKSPACE"
