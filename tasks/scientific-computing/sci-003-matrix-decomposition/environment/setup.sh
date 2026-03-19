#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import numpy as np
np.random.seed(42)

# Generate a random 50x20 matrix with some structure
U, _ = np.linalg.qr(np.random.randn(50, 50))
V, _ = np.linalg.qr(np.random.randn(20, 20))
singular_values = np.linspace(100, 1, 20)
S = np.diag(singular_values)

# Construct matrix with controlled singular values
matrix = U[:, :20] @ S @ V.T

# Add small noise
matrix += 0.01 * np.random.randn(50, 20)

# Save to CSV
np.savetxt(f"{WORKSPACE}/data_matrix.csv", matrix, delimiter=",")
EOF
