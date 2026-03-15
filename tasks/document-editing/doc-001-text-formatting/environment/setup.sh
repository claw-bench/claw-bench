#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/document.txt" "$WORKSPACE/document.txt"
cp "$TASK_DIR/environment/data/rules.json" "$WORKSPACE/rules.json"
echo "Workspace ready with document.txt and rules.json"
