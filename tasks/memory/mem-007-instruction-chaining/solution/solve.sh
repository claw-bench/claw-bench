#!/usr/bin/env bash
# Oracle solution for mem-007-instruction-chaining
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

# Step 1: Extract and sort by score descending
# Parse raw_data.txt: "ITEM: <name> | SCORE: <number> | CATEGORY: <cat>"
# Output: <score> <name> [<category>]
sed 's/ITEM: *//;s/ *| *SCORE: */|/;s/ *| *CATEGORY: */|/' "$WORKSPACE/raw_data.txt" | \
  awk -F'|' '{ printf "%d %s [%s]\n", $2, $1, $3 }' | \
  sort -rn > "$WORKSPACE/step1_sorted.txt"

# Step 2: Filter (score >= 50) and group by category alphabetically
python3 -c "
import re
lines = open('$WORKSPACE/step1_sorted.txt').read().strip().split('\n')
groups = {}
for line in lines:
    m = re.match(r'(\d+)\s+(.*?)\s+\[(\w+)\]', line)
    if not m: continue
    score, name, cat = int(m.group(1)), m.group(2), m.group(3)
    if score < 50: continue
    groups.setdefault(cat, []).append((score, name))
out = []
for cat in sorted(groups.keys()):
    if out: out.append('')
    out.append(f'== {cat} ==')
    for score, name in groups[cat]:
        out.append(f'{score} {name}')
print('\n'.join(out))
" > "$WORKSPACE/step2_grouped.txt"

# Step 3: Compute stats per category, sorted by avg descending
python3 -c "
import re
content = open('$WORKSPACE/step2_grouped.txt').read().strip()
sections = re.split(r'\n?== (\w+) ==\n', content)
stats = []
i = 1
while i < len(sections):
    cat = sections[i]
    items = [int(line.split()[0]) for line in sections[i+1].strip().split('\n') if line.strip()]
    avg = sum(items) / len(items)
    stats.append((cat, len(items), avg))
    i += 2
stats.sort(key=lambda x: -x[2])
for cat, count, avg in stats:
    print(f'{cat}: count={count}, avg={avg:.1f}')
" > "$WORKSPACE/step3_stats.txt"

# Step 4: Final report
python3 -c "
import re
lines = open('$WORKSPACE/step3_stats.txt').read().strip().split('\n')
cats = []
for line in lines:
    m = re.match(r'(\w+): count=(\d+), avg=(\d+\.\d+)', line)
    cats.append((m.group(1), int(m.group(2)), float(m.group(3))))
grand = sum(c[2] for c in cats) / len(cats)
print('REPORT GENERATED')
print(f'Total categories: {len(cats)}')
print(f'Highest avg category: {cats[0][0]} ({cats[0][2]:.1f})')
print(f'Lowest avg category: {cats[-1][0]} ({cats[-1][2]:.1f})')
print(f'Grand average: {grand:.1f}')
" > "$WORKSPACE/step4_report.txt"

echo "Solution written to $WORKSPACE/"
