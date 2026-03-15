#!/usr/bin/env bash
# Setup script for comm-011-meeting-notes-formatter
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/meeting.txt" "$WORKSPACE/meeting.txt"
echo "Workspace ready with meeting.txt"
