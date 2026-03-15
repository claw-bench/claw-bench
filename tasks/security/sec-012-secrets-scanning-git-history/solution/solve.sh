#!/usr/bin/env bash
# Oracle solution for sec-012-secrets-scanning-git-history
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

report = [
    {
        'commit': 'commit_01',
        'file': 'src/config.py',
        'secret_type': 'aws_key',
        'line_content': 'AWS_ACCESS_KEY_ID = \"AKIAIOSFODNN7EXAMPLE\"',
        'remediation': 'Remove AWS credentials from source code. Use IAM roles or environment variables. Rotate the exposed access key immediately.'
    },
    {
        'commit': 'commit_01',
        'file': 'src/config.py',
        'secret_type': 'aws_key',
        'line_content': 'AWS_SECRET_ACCESS_KEY = \"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"',
        'remediation': 'Remove AWS secret key from source code. Rotate the key in AWS IAM console immediately.'
    },
    {
        'commit': 'commit_03',
        'file': 'deploy/docker-compose.yml',
        'secret_type': 'database_credential',
        'line_content': 'DATABASE_URL=postgresql://admin:P@ssw0rd_Pr0d!@db-prod.internal:5432/maindb',
        'remediation': 'Use environment variables or Docker secrets for database credentials. Change the database password immediately.'
    },
    {
        'commit': 'commit_05',
        'file': 'src/services/payment.py',
        'secret_type': 'api_key',
        'line_content': 'STRIPE_KEY = \"REDACTED_STRIPE_sk_live_EXAMPLE_KEY\"',
        'remediation': 'Remove Stripe live key from code. Use environment variables. Rotate the key in the Stripe dashboard.'
    },
    {
        'commit': 'commit_05',
        'file': 'src/services/payment.py',
        'secret_type': 'api_key',
        'line_content': 'GITHUB_TOKEN = \"REDACTED_GHP_TOKEN_EXAMPLE_00000000\"',
        'remediation': 'Remove GitHub token from code. Revoke the token in GitHub settings and create a new one stored securely.'
    },
    {
        'commit': 'commit_07',
        'file': 'config/ssl/server.key',
        'secret_type': 'private_key',
        'line_content': '-----BEGIN FAKE RSA PRIVATE KEY-----',
        'remediation': 'Remove private key from repository. Store in a secrets manager or certificate management system. Generate a new key pair.'
    },
    {
        'commit': 'commit_09',
        'file': 'src/auth/jwt_handler.py',
        'secret_type': 'jwt_secret',
        'line_content': 'SECRET = \"super-secret-jwt-key-that-should-not-be-here-2024!\"',
        'remediation': 'Remove JWT secret from code. Use environment variables. Rotate the JWT signing key and invalidate existing tokens.'
    }
]

with open('$WORKSPACE/secrets_report.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/secrets_report.json"
