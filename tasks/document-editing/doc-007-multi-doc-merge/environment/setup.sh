#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/chapters"
cp "$TASK_DIR/environment/data/chapters/"*.md "$WORKSPACE/chapters/"
echo "Workspace ready with chapters/ directory"
