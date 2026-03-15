#!/usr/bin/env bash
# Setup script for doc-011-markdown-toc-generator
# Creates workspace and copies document.md into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/document.md" "$WORKSPACE/document.md"
echo "Workspace ready with document.md"
