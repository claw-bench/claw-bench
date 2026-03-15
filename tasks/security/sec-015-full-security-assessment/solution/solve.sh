#!/usr/bin/env bash
# Oracle solution for sec-015-full-security-assessment
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

assessment = {
    'executive_summary': {
        'overall_risk': 'critical',
        'total_findings': 15,
        'critical': 5,
        'high': 5,
        'medium': 3,
        'low': 2,
        'summary': 'The application has critical security vulnerabilities across all categories including SQL injection, insecure deserialization, hardcoded secrets, weak cryptography, and insecure container configuration. Immediate remediation is required before production deployment.'
    },
    'findings': [
        {
            'id': 'FIND-001', 'category': 'code', 'severity': 'critical',
            'title': 'SQL Injection in user search',
            'description': 'search_users() uses f-string to build SQL query with user input, allowing SQL injection',
            'file': 'app.py', 'remediation': 'Use parameterized queries: cursor.execute(\"SELECT * FROM users WHERE username LIKE ?\", (\"%\" + name + \"%\",))'
        },
        {
            'id': 'FIND-002', 'category': 'code', 'severity': 'critical',
            'title': 'SQL Injection in user deletion',
            'description': 'delete_user() uses f-string to build DELETE query, allowing SQL injection',
            'file': 'app.py', 'remediation': 'Use parameterized query: cursor.execute(\"DELETE FROM users WHERE id = ?\", (user_id,))'
        },
        {
            'id': 'FIND-003', 'category': 'code', 'severity': 'critical',
            'title': 'Insecure deserialization via pickle',
            'description': 'upload() uses pickle.loads() on user-supplied data, enabling remote code execution',
            'file': 'app.py', 'remediation': 'Replace pickle with json.loads() or a safe serialization format. Never deserialize untrusted data with pickle.'
        },
        {
            'id': 'FIND-004', 'category': 'code', 'severity': 'high',
            'title': 'Debug endpoint exposes environment variables',
            'description': 'debug_info() returns all environment variables including secrets and credentials',
            'file': 'app.py', 'remediation': 'Remove debug endpoint entirely or restrict to development only with authentication'
        },
        {
            'id': 'FIND-005', 'category': 'code', 'severity': 'high',
            'title': 'Password hashes exposed in user listing',
            'description': 'list_users() returns password_hash field in API response',
            'file': 'app.py', 'remediation': 'Exclude password_hash from SELECT query and API response'
        },
        {
            'id': 'FIND-006', 'category': 'authentication', 'severity': 'critical',
            'title': 'MD5 used for password hashing',
            'description': 'login() uses MD5 to hash passwords which is cryptographically broken and fast to brute force',
            'file': 'app.py', 'remediation': 'Use bcrypt, scrypt, or argon2id for password hashing'
        },
        {
            'id': 'FIND-007', 'category': 'config', 'severity': 'critical',
            'title': 'Hardcoded secret key',
            'description': 'SECRET_KEY is hardcoded as development-secret-key-12345 in both app.py and config.py',
            'file': 'config.py', 'remediation': 'Generate a cryptographically random secret key and store in environment variables'
        },
        {
            'id': 'FIND-008', 'category': 'config', 'severity': 'high',
            'title': 'Insecure session cookies',
            'description': 'SESSION_COOKIE_SECURE and SESSION_COOKIE_HTTPONLY are both False',
            'file': 'config.py', 'remediation': 'Set both to True to protect session cookies'
        },
        {
            'id': 'FIND-009', 'category': 'config', 'severity': 'high',
            'title': 'Wildcard CORS with credentials',
            'description': 'CORS_ORIGINS is * with CORS_ALLOW_CREDENTIALS True, allowing credential theft from any origin',
            'file': 'config.py', 'remediation': 'Restrict CORS_ORIGINS to specific trusted domains'
        },
        {
            'id': 'FIND-010', 'category': 'config', 'severity': 'medium',
            'title': 'Dangerous file extensions allowed',
            'description': 'ALLOWED_EXTENSIONS includes exe, sh, py which could allow malicious file uploads',
            'file': 'config.py', 'remediation': 'Remove executable extensions from allowed list'
        },
        {
            'id': 'FIND-011', 'category': 'config', 'severity': 'high',
            'title': 'Password logging enabled',
            'description': 'LOG_PASSWORDS is True, causing credentials to be written to log files',
            'file': 'config.py', 'remediation': 'Set LOG_PASSWORDS to False and audit existing logs'
        },
        {
            'id': 'FIND-012', 'category': 'infrastructure', 'severity': 'high',
            'title': 'Container runs as root',
            'description': 'Dockerfile explicitly uses USER root instead of a non-privileged user',
            'file': 'Dockerfile', 'remediation': 'Create and use a non-root user: RUN adduser --disabled-password appuser && USER appuser'
        },
        {
            'id': 'FIND-013', 'category': 'infrastructure', 'severity': 'medium',
            'title': 'Debug mode enabled in production container',
            'description': 'FLASK_DEBUG=1 and FLASK_ENV=development in Dockerfile and docker-compose.yml',
            'file': 'Dockerfile', 'remediation': 'Set FLASK_ENV=production and remove FLASK_DEBUG'
        },
        {
            'id': 'FIND-014', 'category': 'infrastructure', 'severity': 'medium',
            'title': 'Privileged container with host networking',
            'description': 'docker-compose.yml uses privileged: true and network_mode: host, breaking container isolation',
            'file': 'docker-compose.yml', 'remediation': 'Remove privileged flag and use bridge networking with explicit port mapping'
        },
        {
            'id': 'FIND-015', 'category': 'data_protection', 'severity': 'low',
            'title': 'Database credentials in docker-compose',
            'description': 'Database password admin123 is exposed in docker-compose.yml environment',
            'file': 'docker-compose.yml', 'remediation': 'Use Docker secrets or environment file with restricted permissions'
        }
    ],
    'risk_summary': {
        'by_severity': {'critical': 5, 'high': 5, 'medium': 3, 'low': 2},
        'by_category': {'code': 3, 'config': 4, 'authentication': 1, 'infrastructure': 3, 'data_protection': 1, 'dependency': 0}
    }
}

with open('$WORKSPACE/assessment.json', 'w') as f:
    json.dump(assessment, f, indent=2)
"

cat > "$WORKSPACE/remediation_plan.md" << 'PLANEOF'
# Remediation Plan

## Priority 1: Critical (Immediate Action Required)

### 1. Fix SQL Injection Vulnerabilities
- **Findings**: FIND-001, FIND-002
- **Files**: app.py (search_users, delete_user)
- **Action**: Replace all f-string/concatenation queries with parameterized queries
- **Effort**: Low (1-2 hours)
- **Dependencies**: None

### 2. Remove Insecure Deserialization
- **Finding**: FIND-003
- **File**: app.py (upload endpoint)
- **Action**: Replace pickle.loads() with json.loads() or safe alternative
- **Effort**: Low (1 hour)
- **Dependencies**: None

### 3. Replace MD5 Password Hashing
- **Finding**: FIND-006
- **File**: app.py (login function)
- **Action**: Migrate to bcrypt/argon2id, rehash existing passwords on next login
- **Effort**: Medium (4-8 hours including migration)
- **Dependencies**: Requires user re-authentication

### 4. Rotate Hardcoded Secret Key
- **Finding**: FIND-007
- **Files**: app.py, config.py
- **Action**: Generate random secret key, store in environment variable
- **Effort**: Low (30 minutes)
- **Dependencies**: Will invalidate existing sessions

## Priority 2: High

### 5. Remove Debug Endpoint
- **Finding**: FIND-004
- **File**: app.py
- **Effort**: Low (15 minutes)

### 6. Remove Password Hash from API Response
- **Finding**: FIND-005
- **File**: app.py
- **Effort**: Low (15 minutes)

### 7. Fix Session Cookie Security
- **Finding**: FIND-008
- **File**: config.py
- **Effort**: Low (15 minutes)

### 8. Fix CORS Configuration
- **Finding**: FIND-009
- **File**: config.py
- **Effort**: Low (30 minutes)

### 9. Disable Password Logging
- **Finding**: FIND-011
- **File**: config.py
- **Effort**: Low (15 minutes)
- **Dependencies**: Audit and purge existing logs

### 10. Run Container as Non-Root
- **Finding**: FIND-012
- **File**: Dockerfile
- **Effort**: Low (30 minutes)

## Priority 3: Medium

### 11. Remove Dangerous File Extensions
- **Finding**: FIND-010
- **Effort**: Low (15 minutes)

### 12. Disable Debug Mode
- **Finding**: FIND-013
- **Effort**: Low (15 minutes)

### 13. Fix Container Privileges
- **Finding**: FIND-014
- **Effort**: Low (30 minutes)

## Priority 4: Low

### 14. Secure Database Credentials
- **Finding**: FIND-015
- **Effort**: Medium (1-2 hours, Docker secrets setup)

## Quick Wins (Low Effort, High Impact)

1. Fix SQL injection (FIND-001, FIND-002) — 1 hour
2. Remove pickle usage (FIND-003) — 1 hour
3. Rotate secret key (FIND-007) — 30 minutes
4. Disable password logging (FIND-011) — 15 minutes
5. Remove debug endpoint (FIND-004) — 15 minutes
6. Fix session cookies (FIND-008) — 15 minutes
PLANEOF

echo "Solution written to $WORKSPACE/assessment.json and $WORKSPACE/remediation_plan.md"
