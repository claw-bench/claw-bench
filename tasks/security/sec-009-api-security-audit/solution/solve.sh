#!/usr/bin/env bash
# Oracle solution for sec-009-api-security-audit
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

audit = [
    {
        'endpoint': 'GET /users',
        'category': 'authentication',
        'description': 'User listing endpoint has no authentication — anyone can access all user data',
        'severity': 'critical',
        'recommendation': 'Add bearerAuth security requirement'
    },
    {
        'endpoint': 'GET /users',
        'category': 'pii_exposure',
        'description': 'Response includes SSN, date_of_birth, and address — sensitive PII exposed without filtering',
        'severity': 'critical',
        'recommendation': 'Remove SSN and other PII from default response; require elevated permissions for sensitive fields'
    },
    {
        'endpoint': 'DELETE /users/{id}',
        'category': 'authentication',
        'description': 'User deletion endpoint has no authentication — anyone can delete users',
        'severity': 'critical',
        'recommendation': 'Add bearerAuth security requirement and admin role check'
    },
    {
        'endpoint': 'GET /export/users',
        'category': 'authentication',
        'description': 'User data export endpoint has no authentication — allows unauthenticated bulk PII export',
        'severity': 'critical',
        'recommendation': 'Add bearerAuth security requirement with admin role'
    },
    {
        'endpoint': 'POST /auth/login',
        'category': 'rate_limiting',
        'description': 'Login endpoint has no rate limiting, enabling brute force attacks',
        'severity': 'high',
        'recommendation': 'Add rate limiting (e.g., 5 attempts per minute per IP)'
    },
    {
        'endpoint': 'global',
        'category': 'cors',
        'description': 'CORS allow-origin is set to * with all methods and headers allowed — permits cross-origin attacks',
        'severity': 'high',
        'recommendation': 'Restrict allow-origin to specific trusted domains and limit methods/headers'
    },
    {
        'endpoint': 'GET /users/search',
        'category': 'input_validation',
        'description': 'Search query parameter q has no maxLength or pattern constraint; limit parameter has no maximum — allows abuse',
        'severity': 'medium',
        'recommendation': 'Add maxLength to q parameter and maximum to limit parameter'
    }
]

with open('$WORKSPACE/api_audit.json', 'w') as f:
    json.dump(audit, f, indent=2)
"

echo "Solution written to $WORKSPACE/api_audit.json"
