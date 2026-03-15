#!/usr/bin/env bash
# Setup script for sec-001-detect-hardcoded-credentials
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/source_code"
cp "$TASK_DIR/environment/data/config.py" "$WORKSPACE/source_code/config.py"
cp "$TASK_DIR/environment/data/api_client.py" "$WORKSPACE/source_code/api_client.py"
cp "$TASK_DIR/environment/data/auth_service.py" "$WORKSPACE/source_code/auth_service.py"
echo "Workspace ready with source code files"
