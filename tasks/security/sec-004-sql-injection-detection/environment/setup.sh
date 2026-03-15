#!/usr/bin/env bash
# Setup script for sec-004-sql-injection-detection
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/queries.py" "$WORKSPACE/queries.py"
echo "Workspace ready with queries.py"
