#!/usr/bin/env bash
# Oracle solution for mem-002-multi-step-instructions
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

# Step 1: Extract 3rd word from each line
awk '{ print $3 }' "$WORKSPACE/words.txt" > "$WORKSPACE/extracted.txt"
echo "STEP 1: extracted third words" > "$WORKSPACE/steps.txt"

# Step 2: Sort alphabetically case-insensitive
sort -f "$WORKSPACE/extracted.txt" -o "$WORKSPACE/extracted.txt"
echo "STEP 2: sorted extracted.txt" >> "$WORKSPACE/steps.txt"

# Step 3: Count total characters (excluding newlines)
char_count=$(tr -d '\n' < "$WORKSPACE/extracted.txt" | wc -c | tr -d ' ')
echo "$char_count" > "$WORKSPACE/char_count.txt"
echo "STEP 3: counted $char_count characters" >> "$WORKSPACE/steps.txt"

# Step 4: Compute remainder mod 7
remainder=$(( char_count % 7 ))
echo "$remainder" > "$WORKSPACE/remainder.txt"
echo "STEP 4: remainder is $remainder" >> "$WORKSPACE/steps.txt"

# Step 5: Create summary
first_word=$(head -1 "$WORKSPACE/extracted.txt")
last_word=$(tail -1 "$WORKSPACE/extracted.txt")
printf "%s\n%s\n%s\n" "$first_word" "$last_word" "$remainder" > "$WORKSPACE/summary.txt"
echo "STEP 5: wrote summary.txt" >> "$WORKSPACE/steps.txt"

echo "Solution written to $WORKSPACE/"
