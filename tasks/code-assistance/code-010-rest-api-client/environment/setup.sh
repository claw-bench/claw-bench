#!/usr/bin/env bash
# Setup script for code-010-rest-api-client
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"
pip install requests 2>/dev/null || true
echo "Workspace ready – create api_client.py here."
