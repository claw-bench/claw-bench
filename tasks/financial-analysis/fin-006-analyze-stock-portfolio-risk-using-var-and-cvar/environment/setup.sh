#!/bin/bash
set -euo pipefail

# Create workspace directory
WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

# Generate synthetic portfolio returns data
cat > portfolio_returns.csv <<EOF
date,daily_return
$(python3 -c "
import numpy as np
import pandas as pd

np.random.seed(42)
base_returns = np.random.normal(0.0005, 0.01, 490)
tail_events = np.random.normal(-0.05, 0.02, 10)
returns = np.concatenate([base_returns, tail_events])
dates = pd.date_range(end=pd.Timestamp.today(), periods=500).strftime('%Y-%m-%d')

for date, ret in zip(dates, returns):
    print(f'{date},{ret:.6f}')
")
EOF

echo "Setup complete: portfolio_returns.csv generated"
