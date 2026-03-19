#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import pandas as pd
import numpy as np
np.random.seed(42)

# Create synthetic data
num_rows = 50

# Numeric features
num_feat1 = np.random.normal(loc=50, scale=15, size=num_rows)
num_feat2 = np.random.uniform(low=0, high=100, size=num_rows)
num_feat3 = np.random.exponential(scale=10, size=num_rows)

# Categorical features
cat_feat1 = np.random.choice(['A', 'B', 'C'], size=num_rows)
cat_feat2 = np.random.choice(['X', 'Y'], size=num_rows)

# Target variable, somewhat correlated with num_feat1 and num_feat3
noise = np.random.normal(0, 5, size=num_rows)
target = 0.5 * num_feat1 + 0.3 * num_feat3 + noise

# Assemble DataFrame
raw_df = pd.DataFrame({
    'num_feat1': num_feat1,
    'num_feat2': num_feat2,
    'num_feat3': num_feat3,
    'cat_feat1': cat_feat1,
    'cat_feat2': cat_feat2,
    'target': target
})

raw_df.to_csv(f'{WORKSPACE}/raw_data.csv', index=False)
EOF
