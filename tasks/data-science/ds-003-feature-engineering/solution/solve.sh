#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import pandas as pd
import numpy as np
import json
from itertools import combinations

# Load data
raw_path = f"{WORKSPACE}/raw_data.csv"
df = pd.read_csv(raw_path)

# Separate target
target = df['target']

# Identify numeric and categorical features
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols.remove('target')
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

# 1. Binning: bin 'num_feat2' into 4 equal-width bins
bin_feature = 'num_feat2'
bins = 4
binned = pd.cut(df[bin_feature], bins=bins, labels=[f'{bin_feature}_bin{i+1}' for i in range(bins)])

# Add binned feature as categorical
df[f'{bin_feature}_binned'] = binned

# Update categorical columns to include binned
categorical_cols.append(f'{bin_feature}_binned')

# 2. One-hot encode categorical features
one_hot = pd.get_dummies(df[categorical_cols], prefix=categorical_cols, drop_first=False)

# 3. Log transform numeric features using log1p
log_transformed = df[numeric_cols].apply(lambda x: np.log1p(x.clip(lower=0)))
log_transformed.columns = [f'{col}_log' for col in numeric_cols]

# 4. Interaction terms: between all pairs of numeric features including log-transformed
# Combine original numeric and log-transformed
num_and_log = pd.concat([df[numeric_cols], log_transformed], axis=1)

interaction_features = {}
for f1, f2 in combinations(num_and_log.columns, 2):
    interaction_name = f'{f1}_x_{f2}'
    interaction_features[interaction_name] = num_and_log[f1] * num_and_log[f2]

interaction_df = pd.DataFrame(interaction_features)

# Combine all engineered features
engineered_df = pd.concat([one_hot, log_transformed, interaction_df], axis=1)

# Compute Pearson correlation with target
correlations = engineered_df.apply(lambda x: x.corr(target))

# Drop features with NaN correlation (constant features)
correlations = correlations.dropna()

# Select top 10 features by absolute correlation
top_10_features = correlations.abs().sort_values(ascending=False).head(10).index.tolist()

# Prepare output dataframe with selected features and target
output_df = pd.concat([engineered_df[top_10_features], target], axis=1)

# Write engineered_features.csv
output_df.to_csv(f'{WORKSPACE}/engineered_features.csv', index=False)

# Write feature_report.json
report = {
    'correlations': correlations.to_dict(),
    'selected_features': top_10_features
}
with open(f'{WORKSPACE}/feature_report.json', 'w') as f:
    json.dump(report, f, indent=2)
EOF
