#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/file_list.json" "$WORKSPACE/"
cp "$TASK_DIR/environment/data/rename_rules.json" "$WORKSPACE/"
