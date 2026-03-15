#!/usr/bin/env bash
# Oracle solution for file-003-find-and-replace
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

sed 's/foo/bar/g' "$WORKSPACE/input.txt" > "$WORKSPACE/output.txt"

echo "Solution written to $WORKSPACE/output.txt"
