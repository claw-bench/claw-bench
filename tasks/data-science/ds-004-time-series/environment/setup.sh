#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# Generate 120 daily dates starting from 2020-01-01
start_date = datetime(2020, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(120)]

# Create seasonal pattern: weekly seasonality (7-day period)
seasonal_pattern = 10 * np.sin(2 * np.pi * (np.arange(120) % 7) / 7)

# Create trend: linear increase
trend = np.linspace(50, 70, 120)

# Residual noise
residual = np.random.normal(0, 2, 120)

# Combine to form value
values = trend + seasonal_pattern + residual

# Create DataFrame
df = pd.DataFrame({
    'date': [d.strftime('%Y-%m-%d') for d in dates],
    'value': values
})

# Save to CSV
csv_path = f'{WORKSPACE}/timeseries.csv'
df.to_csv(csv_path, index=False)
EOF
