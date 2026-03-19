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

# Generate 24 months of data starting from 2022-01
start_date = datetime.strptime("2022-01", "%Y-%m")
months = [(start_date + timedelta(days=30*i)).strftime("%Y-%m") for i in range(24)]

# Simulate price and units_sold with some realistic fluctuations
prices = []
units_sold = []
revenue = []

base_price = 20.0
base_units = 500

for i in range(len(months)):
    # Price fluctuates mildly around base price
    price = base_price + random.uniform(-2.0, 2.0)
    price = round(price, 2)
    prices.append(price)

    # Units sold inversely related to price with noise
    # units = base_units * (base_price / price) ^ elasticity + noise
    # Assume elasticity ~ -1.5
    elasticity = -1.5
    units = base_units * (base_price / price) ** (-elasticity)
    units += random.gauss(0, 20)  # noise
    units = max(1, int(round(units)))
    units_sold.append(units)

    revenue.append(round(price * units, 2))

# Write CSV
with open(f"{WORKSPACE}/pricing_history.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["month", "price", "units_sold", "revenue"])
    for m, p, u, r in zip(months, prices, units_sold, revenue):
        writer.writerow([m, f"{p:.2f}", u, f"{r:.2f}"])
EOF
