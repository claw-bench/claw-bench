#!/usr/bin/env bash
# Oracle solution for data-016-monthly-budget-analysis
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import csv
import json
from collections import defaultdict

ws = sys.argv[1]

# Read budget
budgets = []
with open(f'{ws}/budget.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        budgets.append({
            'category': row['category'],
            'budget_amount': float(row['budget_amount'])
        })

# Read transactions and sum by category
actuals = defaultdict(float)
with open(f'{ws}/transactions.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        actuals[row['category']] += float(row['amount'])

# Build summary
summary = []
over_budget = []
under_budget = []
total_budget = 0.0
total_actual = 0.0

for b in budgets:
    cat = b['category']
    budget_amt = b['budget_amount']
    actual_amt = round(actuals.get(cat, 0.0), 2)
    diff = round(budget_amt - actual_amt, 2)

    if actual_amt > budget_amt:
        status = "over-budget"
        over_budget.append(cat)
    elif actual_amt < budget_amt:
        status = "under-budget"
        under_budget.append(cat)
    else:
        status = "on-budget"

    summary.append({
        'category': cat,
        'budget': budget_amt,
        'actual': actual_amt,
        'difference': diff,
        'status': status
    })
    total_budget += budget_amt
    total_actual += actual_amt

result = {
    'month': '2026-03',
    'summary': summary,
    'total_budget': round(total_budget, 2),
    'total_actual': round(total_actual, 2),
    'total_difference': round(total_budget - total_actual, 2),
    'over_budget_categories': sorted(over_budget),
    'under_budget_categories': sorted(under_budget)
}

with open(f'{ws}/budget_report.json', 'w') as f:
    json.dump(result, f, indent=2)
PYEOF

echo "Budget report written to $WORKSPACE/budget_report.json"
