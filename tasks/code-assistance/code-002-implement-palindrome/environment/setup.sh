#!/usr/bin/env bash
# Setup script for code-002-implement-palindrome
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"
echo "Workspace ready – create palindrome.py here."
