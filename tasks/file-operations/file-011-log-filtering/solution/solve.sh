#!/usr/bin/env bash
# Oracle solution for file-011-log-filtering
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

grep -E '\[(ERROR|WARN)\]' "$WORKSPACE/app.log" > "$WORKSPACE/errors.txt"

echo "Solution written to $WORKSPACE/errors.txt"
