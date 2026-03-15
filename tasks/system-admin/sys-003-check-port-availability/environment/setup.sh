#!/usr/bin/env bash
# Setup script for sys-003-check-port-availability
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/ports.txt" "$WORKSPACE/ports.txt"
echo "Workspace ready with ports.txt"
