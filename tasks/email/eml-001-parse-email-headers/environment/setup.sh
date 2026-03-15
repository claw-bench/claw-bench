#!/usr/bin/env bash
# Setup script for eml-001-parse-email-headers
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cp "$(dirname "$0")/data/email.txt" "$WORKSPACE/email.txt"

echo "Workspace created at $WORKSPACE"
