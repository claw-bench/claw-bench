#!/usr/bin/env bash
# Setup script for code-013-file-parser
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/sample.conf" "$WORKSPACE/sample.conf"
echo "Workspace ready with sample.conf"
