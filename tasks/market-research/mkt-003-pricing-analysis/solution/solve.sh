#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
import math

csv_path = f"{WORKSPACE}/pricing_history.csv"
json_path = f"{WORKSPACE}/pricing_analysis.json"

months = []
prices = []
units = []
revenues = []

with open(csv_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        months.append(row["month"])
        prices.append(float(row["price"]))
        units.append(int(row["units_sold"]))
        revenues.append(float(row["revenue"]))

elasticities = []
for i in range(len(prices) - 1):
    p0, p1 = prices[i], prices[i+1]
    q0, q1 = units[i], units[i+1]

    # Calculate percent changes safely
    if p0 == 0 or q0 == 0 or (p1 - p0) == 0:
        # Avoid division by zero, skip or set elasticity to 0
        elasticity = 0.0
    else:
        pct_change_q = (q1 - q0) / q0
        pct_change_p = (p1 - p0) / p0
        if pct_change_p == 0:
            elasticity = 0.0
        else:
            elasticity = pct_change_q / pct_change_p
    elasticities.append(elasticity)

# Average elasticity
avg_elasticity = sum(elasticities) / len(elasticities) if elasticities else 0.0

# Use absolute value of avg elasticity
abs_avg_elasticity = abs(avg_elasticity)

# Last observed price and units
p_last = prices[-1]
q_last = units[-1]

# Calculate optimal price
if abs_avg_elasticity + 1 == 0:
    optimal_price = p_last
else:
    optimal_price = (abs_avg_elasticity / (abs_avg_elasticity + 1)) * p_last

# Calculate estimated units sold at optimal price
# Q* = Q_last * (P*/P_last)^E
# Use avg_elasticity (can be negative), so power is avg_elasticity
if p_last == 0:
    q_opt = q_last
else:
    q_opt = q_last * (optimal_price / p_last) ** avg_elasticity

# Revenue estimate
max_revenue_estimate = optimal_price * q_opt

# Round floats to reasonable precision
elasticities_rounded = [round(e, 5) for e in elasticities]
avg_elasticity_rounded = round(avg_elasticity, 5)
optimal_price_rounded = round(optimal_price, 5)
max_revenue_rounded = round(max_revenue_estimate, 5)

output = {
    "elasticities": elasticities_rounded,
    "avg_elasticity": avg_elasticity_rounded,
    "optimal_price": optimal_price_rounded,
    "max_revenue_estimate": max_revenue_rounded
}

with open(json_path, "w") as f:
    json.dump(output, f, indent=2)
EOF
