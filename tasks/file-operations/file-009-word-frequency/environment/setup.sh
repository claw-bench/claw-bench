#!/usr/bin/env bash
# Setup script for file-009-word-frequency
# Creates workspace and copies article.txt into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/article.txt" "$WORKSPACE/article.txt"
echo "Workspace ready with article.txt"
