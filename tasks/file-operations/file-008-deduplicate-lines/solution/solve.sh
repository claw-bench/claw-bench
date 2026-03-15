#!/usr/bin/env bash
# Oracle solution for file-008-deduplicate-lines
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

awk '!seen[$0]++' "$WORKSPACE/data.txt" > "$WORKSPACE/unique.txt"

echo "Solution written to $WORKSPACE/unique.txt"
