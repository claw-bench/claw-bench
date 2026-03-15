#!/usr/bin/env bash
# Setup script for comm-013-announcement-generator
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/template.txt" "$WORKSPACE/template.txt"
cp "$TASK_DIR/environment/data/data.json" "$WORKSPACE/data.json"
echo "Workspace ready with template.txt and data.json"
