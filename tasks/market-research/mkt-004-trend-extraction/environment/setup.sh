#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
import datetime

random.seed(42)

start_date = datetime.date(2020, 1, 1)
months = 36

# Generate synthetic sales data with seasonality and trend
sales_data = []
for i in range(months):
    current_month = (start_date.month + i - 1) % 12 + 1
    year = start_date.year + (start_date.month + i - 1) // 12
    month_str = f"{year:04d}-{current_month:02d}"

    # Base sales with upward trend
    base = 1000 + i * 10

    # Seasonality factors (higher sales in Nov, Dec; lower in Feb)
    seasonality = {
        1: 0.9, 2: 0.8, 3: 1.0, 4: 1.1, 5: 1.0, 6: 0.95,
        7: 1.05, 8: 1.1, 9: 1.0, 10: 1.05, 11: 1.2, 12: 1.3
    }[current_month]

    # Random noise
    noise = random.gauss(0, 30)

    sales = int(base * seasonality + noise)
    sales = max(sales, 0)  # no negative sales

    sales_data.append((month_str, sales))

with open(f"{WORKSPACE}/monthly_sales.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["month", "sales"])
    writer.writerows(sales_data)
EOF
