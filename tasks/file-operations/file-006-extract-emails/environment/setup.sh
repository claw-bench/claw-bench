#!/usr/bin/env bash
# Setup script for file-006-extract-emails
# Creates workspace and copies document.txt into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/document.txt" "$WORKSPACE/document.txt"
echo "Workspace ready with document.txt"
