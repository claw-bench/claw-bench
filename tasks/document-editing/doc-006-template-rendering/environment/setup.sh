#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/template.md" "$WORKSPACE/template.md"
cp "$TASK_DIR/environment/data/data.json" "$WORKSPACE/data.json"
echo "Workspace ready with template.md and data.json"
