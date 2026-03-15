#!/usr/bin/env bash
# Setup script for code-001-write-unittest
# Creates workspace and copies calculator.py into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/calculator.py" "$WORKSPACE/calculator.py"
echo "Workspace ready with calculator.py"
