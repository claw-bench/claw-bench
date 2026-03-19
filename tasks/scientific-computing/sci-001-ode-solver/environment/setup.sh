#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

# Generate dummy files to simulate initial conditions and parameters (not strictly needed but for realism)
# We will generate a parameters.json file for reference
python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import json
params = {
    "a": 1.1,
    "b": 0.4,
    "c": 0.4,
    "d": 0.1,
    "x0": 10.0,
    "y0": 10.0,
    "t0": 0.0,
    "t_end": 50.0,
    "dt": 0.01
}
json.dump(params, open(f"{WORKSPACE}/parameters.json", "w"), indent=2)
EOF

# No other input files needed; the solver will use these parameters
