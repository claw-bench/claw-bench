#!/usr/bin/env bash
# Setup script for file-005-merge-files
# Creates workspace and copies part files into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/part1.txt" "$WORKSPACE/part1.txt"
cp "$TASK_DIR/environment/data/part2.txt" "$WORKSPACE/part2.txt"
cp "$TASK_DIR/environment/data/part3.txt" "$WORKSPACE/part3.txt"
echo "Workspace ready with part1.txt, part2.txt, part3.txt"
