#!/usr/bin/env bash
# Oracle solution for mem-001-recall-given-name
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

# Count items with quantity > 50
count=$(awk -F',' 'NR>1 && $3+0 > 50 { n++ } END { print n }' "$WORKSPACE/inventory.csv")
echo "$count" > "$WORKSPACE/high_quantity_count.txt"

# Convert notes to uppercase
tr '[:lower:]' '[:upper:]' < "$WORKSPACE/notes.txt" > "$WORKSPACE/notes_upper.txt"

# List original files
printf "inventory.csv\nnotes.txt\n" > "$WORKSPACE/file_list.txt"

# Recall the name
echo "Cassandra Whitfield" > "$WORKSPACE/recall.txt"

echo "Solution written to $WORKSPACE/"
