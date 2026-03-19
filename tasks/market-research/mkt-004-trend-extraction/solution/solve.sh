#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
import datetime
from statistics import mean

# Read data
months = []
sales = []
with open(f"{WORKSPACE}/monthly_sales.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        months.append(row["month"])
        sales.append(float(row["sales"]))

# Compute moving averages
# 3-month moving average
ma3 = [mean(sales[i-3:i]) for i in range(3, len(sales)+1)]
# 6-month moving average
ma6 = [mean(sales[i-6:i]) for i in range(6, len(sales)+1)]

# Seasonality detection
# Calculate seasonal indices as average ratio of actual sales to 6-month moving average for each month
# Align months with ma6 (starts at index 5)
ratios_by_month = {f'{m:02d}': [] for m in range(1, 13)}
for i in range(5, len(sales)):
    month_str = months[i]
    month_num = month_str[5:7]
    if ma6[i-6] != 0:
        ratio = sales[i] / ma6[i-6]
        ratios_by_month[month_num].append(ratio)

seasonal_indices = {}
for m in ratios_by_month:
    vals = ratios_by_month[m]
    if vals:
        seasonal_indices[m] = sum(vals) / len(vals)
    else:
        seasonal_indices[m] = 1.0  # fallback

# Overall trend determination using linear regression slope on 6-month moving average
# Simple slope: (last - first) / number of points
slope = (ma6[-1] - ma6[0]) / (len(ma6) - 1)
threshold = 0.1  # threshold for trend
if slope > threshold:
    overall_trend = "increasing"
elif slope < -threshold:
    overall_trend = "decreasing"
else:
    overall_trend = "stable"

# Forecast next 3 months
# Use last 6-month MA value as base, extend trend linearly, adjust by seasonal index
last_month = datetime.datetime.strptime(months[-1], "%Y-%m")
forecast = []
for i in range(1, 4):
    next_month = last_month + datetime.timedelta(days=31 * i)  # approximate next months
    # Correct month and year
    year = next_month.year
    month = next_month.month
    # Adjust month/year correctly
    # Because timedelta days can overshoot, fix month/year manually
    month = (last_month.month + i - 1) % 12 + 1
    year = last_month.year + (last_month.month + i - 1) // 12
    month_str = f"{year:04d}-{month:02d}"

    # Linear trend extension
    base_forecast = ma6[-1] + slope * i
    # Adjust by seasonal index
    season_factor = seasonal_indices.get(f"{month:02d}", 1.0)
    forecasted_sales = base_forecast * season_factor
    forecast.append({"month": month_str, "forecasted_sales": round(forecasted_sales, 2)})

# Prepare output
output = {
    "moving_averages": {
        "3_month": [round(v, 2) for v in ma3],
        "6_month": [round(v, 2) for v in ma6]
    },
    "seasonal_indices": {k: round(v, 4) for k, v in seasonal_indices.items()},
    "forecast": forecast,
    "overall_trend": overall_trend
}

with open(f"{WORKSPACE}/trend_analysis.json", "w") as f:
    json.dump(output, f, indent=2)
EOF
