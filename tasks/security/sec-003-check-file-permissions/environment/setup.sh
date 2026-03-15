#!/usr/bin/env bash
# Setup script for sec-003-check-file-permissions
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/permissions.txt" "$WORKSPACE/permissions.txt"
echo "Workspace ready with permissions.txt"
