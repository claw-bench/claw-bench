#!/usr/bin/env bash
# Setup script for file-007-json-to-yaml
# Creates workspace and copies config.json into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/config.json" "$WORKSPACE/config.json"
echo "Workspace ready with config.json"
