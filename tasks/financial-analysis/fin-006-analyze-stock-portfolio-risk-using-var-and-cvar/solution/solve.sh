#!/bin/bash
set -euo pipefail

workspace=$1
cd "$workspace"

# Read input data
import pandas as pd
import numpy as np
from scipy.stats import norm

df = pd.read_csv("portfolio_returns.csv")
returns = df["daily_return"].values

# Historical simulation method
historical_var_95 = np.percentile(returns, 5)
historical_var_99 = np.percentile(returns, 1)
historical_cvar_95 = returns[returns <= historical_var_95].mean()
historical_cvar_99 = returns[returns <= historical_var_99].mean()

# Parametric (normal) method
mean, std = np.mean(returns), np.std(returns)
parametric_var_95 = mean + std * norm.ppf(0.05)
parametric_var_99 = mean + std * norm.ppf(0.01)
parametric_cvar_95 = mean + std * norm.pdf(norm.ppf(0.05)) / 0.05
parametric_cvar_99 = mean + std * norm.pdf(norm.ppf(0.01)) / 0.01

# Determine which method is more conservative
more_conservative = "historical" if historical_var_95 < parametric_var_95 else "parametric"

# Create output JSON
output = {
    "historical": {
        "var_95": float(historical_var_95),
        "var_99": float(historical_var_99),
        "cvar_95": float(historical_cvar_95),
        "cvar_99": float(historical_cvar_99)
    },
    "parametric": {
        "var_95": float(parametric_var_95),
        "var_99": float(parametric_var_99),
        "cvar_95": float(parametric_cvar_95),
        "cvar_99": float(parametric_cvar_99)
    },
    "summary": f"{more_conservative} method is more conservative"
}

import json
with open("risk_report.json", "w") as f:
    json.dump(output, f, indent=2)
