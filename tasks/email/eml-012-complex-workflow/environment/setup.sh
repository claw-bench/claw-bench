#!/usr/bin/env bash
# Setup script for eml-012-complex-workflow
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$(dirname "$0")/data/incoming_batch.json" "$WORKSPACE/incoming_batch.json"
cp "$(dirname "$0")/data/routing_rules.json" "$WORKSPACE/routing_rules.json"

echo "Workspace created at $WORKSPACE"
