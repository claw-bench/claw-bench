#!/usr/bin/env bash
# Setup script for sec-013-threat-model-generation
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/architecture.json" "$WORKSPACE/architecture.json"
echo "Workspace ready with architecture.json"
