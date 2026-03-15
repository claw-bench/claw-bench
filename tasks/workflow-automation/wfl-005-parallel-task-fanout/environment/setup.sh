#!/usr/bin/env bash
# Setup script for wfl-005-parallel-task-fanout
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/items"
for i in 1 2 3 4 5; do
    cp "$TASK_DIR/environment/data/items/item_${i}.json" "$WORKSPACE/items/item_${i}.json"
done
echo "Workspace ready with items/"
