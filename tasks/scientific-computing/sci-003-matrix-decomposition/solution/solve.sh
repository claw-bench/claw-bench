#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import numpy as np
import json

# Load matrix
matrix = np.loadtxt(f"{WORKSPACE}/data_matrix.csv", delimiter=",")

# Compute SVD
U, s, VT = np.linalg.svd(matrix, full_matrices=False)

ks = [1, 2, 3, 5, 10, 15, 20]
reconstruction_errors = {}

for k in ks:
    Uk = U[:, :k]
    sk = np.diag(s[:k])
    Vk = VT[:k, :]
    reconstructed = Uk @ sk @ Vk
    err = np.linalg.norm(matrix - reconstructed, ord='fro')
    reconstruction_errors[str(k)] = float(err)

optimal_k = min(reconstruction_errors, key=reconstruction_errors.get)

output = {
    "singular_values": s.tolist(),
    "reconstruction_errors": reconstruction_errors,
    "optimal_k": int(optimal_k)
}

with open(f"{WORKSPACE}/svd_analysis.json", "w") as f:
    json.dump(output, f, indent=2)
EOF
