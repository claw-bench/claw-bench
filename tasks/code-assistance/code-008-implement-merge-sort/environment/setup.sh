#!/usr/bin/env bash
# Setup script for code-008-implement-merge-sort
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"
echo "Workspace ready – create sorting.py here."
