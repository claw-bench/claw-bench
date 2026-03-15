#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/pages"
cp "$TASK_DIR/environment/data/pages/"*.html "$WORKSPACE/pages/"
echo "Workspace ready with pages/ directory"
