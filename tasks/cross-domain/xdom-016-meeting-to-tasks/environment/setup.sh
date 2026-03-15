#!/usr/bin/env bash
# Setup script for xdom-016-meeting-to-tasks
# Creates workspace with meeting notes.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/meeting_notes.md" "$WORKSPACE/meeting_notes.md"
echo "Workspace ready with meeting_notes.md"
