#!/usr/bin/env bash
# Setup script for doc-018-invoice-generator
# Creates workspace and copies order.json into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/order.json" "$WORKSPACE/order.json"
echo "Workspace ready with order.json"
