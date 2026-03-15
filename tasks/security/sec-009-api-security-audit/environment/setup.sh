#!/usr/bin/env bash
# Setup script for sec-009-api-security-audit
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/api_spec.json" "$WORKSPACE/api_spec.json"
echo "Workspace ready with api_spec.json"
