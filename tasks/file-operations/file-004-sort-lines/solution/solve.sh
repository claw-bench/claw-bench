#!/usr/bin/env bash
# Oracle solution for file-004-sort-lines
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

sort "$WORKSPACE/names.txt" > "$WORKSPACE/sorted.txt"

echo "Solution written to $WORKSPACE/sorted.txt"
