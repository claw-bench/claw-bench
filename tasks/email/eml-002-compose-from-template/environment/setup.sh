#!/usr/bin/env bash
# Setup script for eml-002-compose-from-template
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$(dirname "$0")/data/template.txt" "$WORKSPACE/template.txt"
cp "$(dirname "$0")/data/contacts.json" "$WORKSPACE/contacts.json"

echo "Workspace created at $WORKSPACE"
