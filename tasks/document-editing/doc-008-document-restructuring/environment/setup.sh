#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/messy_doc.md" "$WORKSPACE/messy_doc.md"
cp "$TASK_DIR/environment/data/outline.json" "$WORKSPACE/outline.json"
echo "Workspace ready with messy_doc.md and outline.json"
