#!/usr/bin/env bash
# Setup script for xdom-001-email-to-calendar
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$TASK_DIR/environment/data/emails.json" "$WORKSPACE/emails.json"

echo "Workspace ready at $WORKSPACE"
