#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/site"
cp "$TASK_DIR/environment/data/site/"*.html "$WORKSPACE/site/"
echo "Workspace ready with site/ directory"
