#!/usr/bin/env bash
# Setup script for eml-010-auto-reply-generator
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$(dirname "$0")/data/incoming.json" "$WORKSPACE/incoming.json"
cp "$(dirname "$0")/data/rules.json" "$WORKSPACE/rules.json"

echo "Workspace created at $WORKSPACE"
