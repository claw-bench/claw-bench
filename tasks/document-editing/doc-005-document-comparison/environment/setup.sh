#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/v1.txt" "$WORKSPACE/v1.txt"
cp "$TASK_DIR/environment/data/v2.txt" "$WORKSPACE/v2.txt"
echo "Workspace ready with v1.txt and v2.txt"
