#!/usr/bin/env bash
# Setup script for wfl-017-standup-aggregator
# Creates workspace with individual standup reports.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/standups"
cp "$TASK_DIR/environment/data/alice.json" "$WORKSPACE/standups/alice.json"
cp "$TASK_DIR/environment/data/bob.json" "$WORKSPACE/standups/bob.json"
cp "$TASK_DIR/environment/data/carol.json" "$WORKSPACE/standups/carol.json"
cp "$TASK_DIR/environment/data/dave.json" "$WORKSPACE/standups/dave.json"
echo "Workspace ready with standup reports"
