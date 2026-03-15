#!/usr/bin/env bash
# Oracle solution for doc-013-csv-report-formatter
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import csv
import sys

ws = sys.argv[1]

with open(f'{ws}/data.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Calculate totals for each row
data = []
for row in rows:
    qty = int(row['quantity'])
    price = float(row['price'])
    total = qty * price
    data.append((row['product'], qty, price, total))

# Column widths
pw = max(len('Product'), len('TOTAL'), max(len(d[0]) for d in data)) + 2
qw = max(len('Quantity'), max(len(str(d[1])) for d in data)) + 2
prw = max(len('Price'), max(len(f'{d[2]:.2f}') for d in data)) + 2
tw = max(len('Total'), max(len(f'{d[3]:.2f}') for d in data)) + 2

total_width = pw + qw + prw + tw

sum_qty = sum(d[1] for d in data)
grand_total = sum(d[3] for d in data)

lines = []
lines.append('Sales Report')
lines.append('')
lines.append(f"{'Product':<{pw}}{'Quantity':>{qw}}{'Price':>{prw}}{'Total':>{tw}}")
lines.append('-' * total_width)
for product, qty, price, total in data:
    lines.append(f'{product:<{pw}}{qty:>{qw}}{price:>{prw}.2f}{total:>{tw}.2f}')
lines.append('-' * total_width)
lines.append(f"{'TOTAL':<{pw}}{sum_qty:>{qw}}{' ':>{prw}}{grand_total:>{tw}.2f}")

with open(f'{ws}/report.txt', 'w') as f:
    f.write('\n'.join(lines) + '\n')
PYEOF

echo "Solution written to $WORKSPACE/report.txt"
