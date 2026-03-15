#!/usr/bin/env bash
# Setup script for doc-016-meeting-minutes
# Creates workspace and copies raw_notes.txt into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/raw_notes.txt" "$WORKSPACE/raw_notes.txt"
echo "Workspace ready with raw_notes.txt"
