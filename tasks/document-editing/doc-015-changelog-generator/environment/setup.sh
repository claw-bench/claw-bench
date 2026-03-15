#!/usr/bin/env bash
# Setup script for doc-015-changelog-generator
# Creates workspace and copies commits.jsonl into it.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/commits.jsonl" "$WORKSPACE/commits.jsonl"
echo "Workspace ready with commits.jsonl"
