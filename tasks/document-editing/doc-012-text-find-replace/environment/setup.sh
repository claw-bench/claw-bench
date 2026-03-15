#!/usr/bin/env bash
# Setup script for doc-012-text-find-replace
# Creates workspace and copies data files into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/document.txt" "$WORKSPACE/document.txt"
cp "$TASK_DIR/environment/data/replacements.json" "$WORKSPACE/replacements.json"
echo "Workspace ready with document.txt and replacements.json"
