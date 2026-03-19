#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import json
import random
random.seed(42)

# Generate realistic system configuration data

# encryption_at_rest and encryption_in_transit booleans
encryption_at_rest = random.choice([True, True, False])  # bias towards True
encryption_in_transit = random.choice([True, False])

# access_control_type options
access_control_type = random.choice(['role-based', 'mandatory', 'discretionary', 'none'])

# audit_logging boolean
audit_logging = random.choice([True, True, False])

# backup_frequency options
backup_frequency = random.choice(['hourly', 'daily', 'weekly', 'monthly'])

# password_policy
password_min_length = random.choice([6, 8, 10])
password_complexity_required = random.choice([True, False])

# session_timeout in minutes
session_timeout = random.choice([10, 15, 20, 30])

# data_classification
data_classification = random.choice(['PHI', 'Sensitive', 'Public', 'Internal'])

system_config = {
    "encryption_at_rest": encryption_at_rest,
    "encryption_in_transit": encryption_in_transit,
    "access_control_type": access_control_type,
    "audit_logging": audit_logging,
    "backup_frequency": backup_frequency,
    "password_policy": {
        "min_length": password_min_length,
        "complexity_required": password_complexity_required
    },
    "session_timeout": session_timeout,
    "data_classification": data_classification
}

with open(f"{WORKSPACE}/system_config.json", "w") as f:
    json.dump(system_config, f, indent=2)
EOF
