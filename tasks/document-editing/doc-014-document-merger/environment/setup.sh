#!/usr/bin/env bash
# Setup script for doc-014-document-merger
# Creates workspace and copies part files into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/parts"
cp "$TASK_DIR/environment/data/part1.txt" "$WORKSPACE/parts/part1.txt"
cp "$TASK_DIR/environment/data/part2.txt" "$WORKSPACE/parts/part2.txt"
cp "$TASK_DIR/environment/data/part3.txt" "$WORKSPACE/parts/part3.txt"
cp "$TASK_DIR/environment/data/part4.txt" "$WORKSPACE/parts/part4.txt"
echo "Workspace ready with parts/part1.txt through parts/part4.txt"
