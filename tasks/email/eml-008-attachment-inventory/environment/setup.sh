#!/usr/bin/env bash
# Setup script for eml-008-attachment-inventory
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/emails"

for f in "$(dirname "$0")/data/emails/"*.json; do
    cp "$f" "$WORKSPACE/emails/"
done

echo "Workspace created at $WORKSPACE"
