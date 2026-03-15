#!/usr/bin/env bash
# Setup script for sec-002-validate-password-strength
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/passwords.txt" "$WORKSPACE/passwords.txt"
echo "Workspace ready with passwords.txt"
