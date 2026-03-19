#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
from collections import defaultdict

high_risk_countries = {'XYZ', 'ABC', 'DEF', 'GHI'}

transactions_path = f'{WORKSPACE}/transactions.csv'
alerts_path = f'{WORKSPACE}/aml_alerts.json'

# Read transactions
transactions = []
with open(transactions_path, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['amount'] = float(row['amount'])
        transactions.append(row)

# Index transactions by txn_id
txn_map = {t['txn_id']: t for t in transactions}

# Structuring detection: group by sender and date, filter amounts 9000-9999
structuring_groups = defaultdict(list)
for t in transactions:
    if 9000 <= t['amount'] < 10000:
        key = (t['sender'], t['date'])
        structuring_groups[key].append(t['txn_id'])

# Rapid movement detection: sender, date, amount -> set of receivers
rapid_map = defaultdict(lambda: defaultdict(set))
for t in transactions:
    key = (t['sender'], t['date'])
    rapid_map[key][t['amount']].add(t['receiver'])

# Prepare alerts
alerts = []

for t in transactions:
    reasons = []

    # High-risk country
    if t['country'] in high_risk_countries:
        reasons.append('high-risk country')

    # Structuring
    key = (t['sender'], t['date'])
    if t['txn_id'] in structuring_groups.get(key, []) and len(structuring_groups[key]) > 1:
        reasons.append('structuring')

    # Rapid movement
    receivers = rapid_map.get(key, {}).get(t['amount'], set())
    if len(receivers) >= 3:
        reasons.append('rapid movement')

    if reasons:
        alerts.append({'txn_id': t['txn_id'], 'reasons': reasons})

# Write alerts
with open(alerts_path, 'w') as f:
    json.dump(alerts, f, indent=2)
EOF
