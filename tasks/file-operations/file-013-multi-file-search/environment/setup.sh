#!/usr/bin/env bash
# Setup script for file-013-multi-file-search
# Creates workspace with docs/ directory containing text files with TODO items.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/docs"

for f in design.txt api_notes.txt meeting_notes.txt backlog.txt changelog.txt; do
    cp "$TASK_DIR/environment/data/$f" "$WORKSPACE/docs/$f"
done

echo "Workspace ready with docs/ directory"
