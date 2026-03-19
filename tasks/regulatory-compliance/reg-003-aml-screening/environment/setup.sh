#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
from datetime import datetime, timedelta
random.seed(42)

# Parameters
num_transactions = 50
start_date = datetime(2024, 1, 1)
high_risk_countries = ['XYZ', 'ABC', 'DEF', 'GHI']
other_countries = ['USA', 'CAN', 'GBR', 'FRA', 'DEU', 'JPN', 'AUS']
currencies = ['USD', 'CAD', 'GBP', 'EUR', 'JPY', 'AUD']
senders = [f'SND{i:03d}' for i in range(1, 16)]
receivers = [f'RCV{i:03d}' for i in range(1, 21)]

transactions = []

# Helper to generate txn_id

def txn_id(i):
    return f'TXN{i:05d}'

# Generate normal transactions
for i in range(30):
    date = start_date + timedelta(days=random.randint(0, 4))
    sender = random.choice(senders)
    receiver = random.choice(receivers)
    amount = round(random.uniform(100, 20000), 2)
    country = random.choice(other_countries)
    currency = random.choice(currencies)
    transactions.append({
        'txn_id': txn_id(i),
        'date': date.strftime('%Y-%m-%d'),
        'sender': sender,
        'receiver': receiver,
        'amount': amount,
        'country': country,
        'currency': currency
    })

# Add transactions from high-risk countries
for i in range(30, 35):
    date = start_date + timedelta(days=random.randint(0, 4))
    sender = random.choice(senders)
    receiver = random.choice(receivers)
    amount = round(random.uniform(500, 15000), 2)
    country = random.choice(high_risk_countries)
    currency = random.choice(currencies)
    transactions.append({
        'txn_id': txn_id(i),
        'date': date.strftime('%Y-%m-%d'),
        'sender': sender,
        'receiver': receiver,
        'amount': amount,
        'country': country,
        'currency': currency
    })

# Add structuring transactions: multiple txns just under 10,000 by same sender same day
structuring_sender = 'SND999'
structuring_date = start_date + timedelta(days=1)
for i in range(35, 42):
    amount = round(random.uniform(9000, 9999), 2)
    receiver = random.choice(receivers)
    transactions.append({
        'txn_id': txn_id(i),
        'date': structuring_date.strftime('%Y-%m-%d'),
        'sender': structuring_sender,
        'receiver': receiver,
        'amount': amount,
        'country': 'USA',
        'currency': 'USD'
    })

# Add rapid movement transactions: same sender sends same amount to multiple receivers same day (>=3)
rapid_sender = 'SND888'
rapid_date = start_date + timedelta(days=2)
rapid_amount = 1234.56
for i, receiver in enumerate(receivers[:4], start=42):
    transactions.append({
        'txn_id': txn_id(i),
        'date': rapid_date.strftime('%Y-%m-%d'),
        'sender': rapid_sender,
        'receiver': receiver,
        'amount': rapid_amount,
        'country': 'CAN',
        'currency': 'CAD'
    })

# Shuffle all transactions
random.shuffle(transactions)

# Write to CSV
with open(f'{WORKSPACE}/transactions.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['txn_id', 'date', 'sender', 'receiver', 'amount', 'country', 'currency'])
    writer.writeheader()
    for txn in transactions:
        writer.writerow(txn)
EOF
