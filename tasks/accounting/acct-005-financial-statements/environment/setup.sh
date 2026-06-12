#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"
python3 -c "
import csv
accounts = [
    ('Cash', 'asset', 45000, 0), ('Accounts Receivable', 'asset', 28000, 0),
    ('Inventory', 'asset', 35000, 0), ('Equipment', 'asset', 80000, 0),
    ('Accounts Payable', 'liability', 0, 22000), ('Notes Payable', 'liability', 0, 80000),
    ('Common Stock', 'equity', 0, 50000), ('Retained Earnings', 'equity', 0, 30000),
    ('Sales Revenue', 'revenue', 0, 95000), ('Service Revenue', 'revenue', 0, 25000),
    ('COGS', 'expense', 52000, 0), ('Salary Expense', 'expense', 38000, 0),
    ('Rent Expense', 'expense', 12000, 0), ('Utilities Expense', 'expense', 4000, 0),
    ('Depreciation Expense', 'expense', 8000, 0)
]
with open('$WORKSPACE/trial_balance.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['account','type','debit_balance','credit_balance'])
    for a in accounts:
        w.writerow(a)
"
