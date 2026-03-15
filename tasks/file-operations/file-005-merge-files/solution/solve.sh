#!/usr/bin/env bash
# Oracle solution for file-005-merge-files
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

# Write header once, then all data lines (skip header from each file)
head -1 "$WORKSPACE/part1.txt" > "$WORKSPACE/merged.txt"
tail -n +2 "$WORKSPACE/part1.txt" >> "$WORKSPACE/merged.txt"
tail -n +2 "$WORKSPACE/part2.txt" >> "$WORKSPACE/merged.txt"
tail -n +2 "$WORKSPACE/part3.txt" >> "$WORKSPACE/merged.txt"

echo "Solution written to $WORKSPACE/merged.txt"
