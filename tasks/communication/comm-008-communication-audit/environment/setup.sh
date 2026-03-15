#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/communications"
cp "$TASK_DIR/environment/data/communications/"*.json "$WORKSPACE/communications/"
echo "Workspace ready with communications/ directory"
