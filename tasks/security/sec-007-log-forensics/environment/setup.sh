#!/usr/bin/env bash
# Setup script for sec-007-log-forensics
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/access.log" "$WORKSPACE/access.log"
echo "Workspace ready with access.log"
