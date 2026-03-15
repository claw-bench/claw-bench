#!/usr/bin/env bash
# Setup script for doc-017-weekly-status-report
# Creates workspace and copies daily standup files into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/standups"
for day in monday tuesday wednesday thursday friday; do
    cp "$TASK_DIR/environment/data/${day}.txt" "$WORKSPACE/standups/${day}.txt"
done
echo "Workspace ready with standups/monday.txt through standups/friday.txt"
