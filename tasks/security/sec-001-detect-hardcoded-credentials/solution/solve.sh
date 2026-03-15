#!/usr/bin/env bash
# Oracle solution for sec-001-detect-hardcoded-credentials
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

findings = [
    {
        'file': 'config.py',
        'line': 10,
        'type': 'password',
        'severity': 'high',
        'evidence': 'DB_PASSWORD = \"SuperSecret123!\"'
    },
    {
        'file': 'api_client.py',
        'line': 14,
        'type': 'api_key',
        'severity': 'high',
        'evidence': 'API_KEY = \"ak_live_7f3a9b2c1d4e5f6789012345abcdef\"'
    },
    {
        'file': 'api_client.py',
        'line': 39,
        'type': 'token',
        'severity': 'high',
        'evidence': 'weather_token = \"wt_8k3m5n7p9q1r3s5t7u9v1w3x5y7z9a\"'
    },
    {
        'file': 'auth_service.py',
        'line': 16,
        'type': 'password',
        'severity': 'high',
        'evidence': 'JWT_SECRET = \"my-jwt-secret-key-do-not-share-2024xYz!\"'
    },
    {
        'file': 'auth_service.py',
        'line': 55,
        'type': 'api_key',
        'severity': 'high',
        'evidence': 'messaging_api_key = \"sk_prod_A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6\"'
    }
]

with open('$WORKSPACE/findings.json', 'w') as f:
    json.dump(findings, f, indent=2)
"

echo "Solution written to $WORKSPACE/findings.json"
