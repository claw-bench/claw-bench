#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import pandas as pd
import numpy as np
import json
from statsmodels.tsa.seasonal import seasonal_decompose
from datetime import datetime, timedelta

# Read input
input_path = f"{WORKSPACE}/timeseries.csv"
df = pd.read_csv(input_path, parse_dates=["date"])

# Determine frequency: data is daily, so weekly seasonality (period=7)
period = 7

# Decompose time series (additive)
result = seasonal_decompose(df["value"], model='additive', period=period, extrapolate_trend='freq')

# Compose decomposition dataframe
decomp_df = pd.DataFrame({
    'date': df['date'],
    'trend': result.trend,
    'seasonal': result.seasonal,
    'residual': result.resid
})

# Fill NaN in trend and residual (edges) with interpolation or forward/backward fill
# Using interpolation for trend
decomp_df['trend'] = decomp_df['trend'].interpolate(method='linear')
# For residual, fill NaN with 0 (residual at edges)
decomp_df['residual'] = decomp_df['residual'].fillna(0)

# Save decomposition.csv
decomp_df.to_csv(f"{WORKSPACE}/decomposition.csv", index=False, float_format='%.6f')

# Compute autocorrelation for lags 1 to 12 (not saved, but could be used internally if needed)
values = df['value'].values
# autocorrs = [np.corrcoef(values[:-lag], values[lag:])[0,1] for lag in range(1,13)]

# Forecast next 12 periods using weighted moving average
# Use last 12 observations
window_size = 12
weights = np.arange(1, window_size + 1)  # 1 to 12
weights = weights / weights.sum()  # normalize

last_values = values[-window_size:]
forecast_value = np.dot(weights, last_values)

# Since weighted moving average is constant for next periods, forecast 12 times same value
forecast_values = [float(forecast_value)] * 12

# Generate next 12 dates
last_date = df['date'].max()
next_dates = [(last_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 13)]

# Write forecast.json
forecast_dict = {
    "dates": next_dates,
    "forecast": forecast_values
}

with open(f"{WORKSPACE}/forecast.json", "w") as f:
    json.dump(forecast_dict, f, indent=2)
EOF
