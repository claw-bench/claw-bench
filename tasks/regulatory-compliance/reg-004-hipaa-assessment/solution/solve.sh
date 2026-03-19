#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import json

config_path = f"{WORKSPACE}/system_config.json"
output_path = f"{WORKSPACE}/hipaa_assessment.json"

with open(config_path) as f:
    config = json.load(f)

analysis = {}

# Helper function

def compliant_status(condition, explanation):
    if condition:
        return {"status": "compliant"}
    else:
        return {"status": "non-compliant", "explanation": explanation}

# encryption_at_rest
analysis["encryption_at_rest"] = compliant_status(
    config.get("encryption_at_rest") is True,
    "Encryption at rest must be enabled."
)

# encryption_in_transit
analysis["encryption_in_transit"] = compliant_status(
    config.get("encryption_in_transit") is True,
    "Encryption in transit must be enabled."
)

# access_control_type
analysis["access_control_type"] = compliant_status(
    config.get("access_control_type") in ["role-based", "mandatory"],
    f"Access control type '{config.get('access_control_type')}' is not compliant. Must be 'role-based' or 'mandatory'."
)

# audit_logging
analysis["audit_logging"] = compliant_status(
    config.get("audit_logging") is True,
    "Audit logging must be enabled."
)

# backup_frequency
backup_freq = config.get("backup_frequency")
analysis["backup_frequency"] = compliant_status(
    backup_freq in ["daily", "hourly"],
    f"Backup frequency '{backup_freq}' is not compliant. Must be 'daily' or more frequent."
)

# password_policy.min_length
min_len = config.get("password_policy", {}).get("min_length")
analysis["password_policy.min_length"] = compliant_status(
    isinstance(min_len, int) and min_len >= 8,
    f"Password minimum length {min_len} is less than 8."
)

# password_policy.complexity_required
complexity = config.get("password_policy", {}).get("complexity_required")
analysis["password_policy.complexity_required"] = compliant_status(
    complexity is True,
    "Password complexity is not required."
)

# session_timeout
timeout = config.get("session_timeout")
analysis["session_timeout"] = compliant_status(
    isinstance(timeout, int) and timeout <= 15,
    f"Session timeout {timeout} minutes exceeds 15 minutes."
)

# data_classification
classification = config.get("data_classification")
analysis["data_classification"] = compliant_status(
    classification in ["PHI", "Sensitive"],
    f"Data classification '{classification}' is not compliant. Must be 'PHI' or 'Sensitive'."
)

output = {"gap_analysis": analysis}

with open(output_path, "w") as f:
    json.dump(output, f, indent=2)
EOF
