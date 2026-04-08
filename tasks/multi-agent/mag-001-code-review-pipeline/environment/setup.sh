#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/src" "$WORKSPACE/agents"
cp "$TASK_DIR/environment/data/calculator.py" "$WORKSPACE/src/"
cp "$TASK_DIR/environment/data/text_utils.py" "$WORKSPACE/src/"
cp "$TASK_DIR/environment/data/data_processor.py" "$WORKSPACE/src/"
