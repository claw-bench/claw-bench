#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/contacts_a.json" "$WORKSPACE/contacts_a.json"
cp "$TASK_DIR/environment/data/contacts_b.json" "$WORKSPACE/contacts_b.json"
echo "Workspace ready with contacts_a.json and contacts_b.json"
