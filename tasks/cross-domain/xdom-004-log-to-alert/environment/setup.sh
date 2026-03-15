#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$TASK_DIR/environment/data/application.log" "$WORKSPACE/application.log"
cp "$TASK_DIR/environment/data/alert_rules.json" "$WORKSPACE/alert_rules.json"

echo "Workspace ready at $WORKSPACE"
