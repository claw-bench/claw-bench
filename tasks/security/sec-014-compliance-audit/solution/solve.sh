#!/usr/bin/env bash
# Oracle solution for sec-014-compliance-audit
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

results = [
    {'rule_id': 'SEC-001', 'rule_name': 'TLS Version Minimum', 'status': 'pass', 'evidence': 'tls_version is 1.2, meets minimum requirement of 1.2', 'config_file': 'web_server.json'},
    {'rule_id': 'SEC-002', 'rule_name': 'HSTS Enabled', 'status': 'pass', 'evidence': 'hsts.enabled is true', 'config_file': 'web_server.json'},
    {'rule_id': 'SEC-003', 'rule_name': 'HSTS Max Age', 'status': 'fail', 'evidence': 'hsts.max_age is 15768000 (6 months), requires at least 31536000 (1 year)', 'config_file': 'web_server.json'},
    {'rule_id': 'SEC-004', 'rule_name': 'X-Frame-Options', 'status': 'pass', 'evidence': 'x_frame_options is SAMEORIGIN, which is an accepted value', 'config_file': 'web_server.json'},
    {'rule_id': 'AUTH-001', 'rule_name': 'Password Minimum Length', 'status': 'fail', 'evidence': 'password_policy.min_length is 8, requires at least 12', 'config_file': 'auth_config.json'},
    {'rule_id': 'AUTH-002', 'rule_name': 'MFA Enforcement', 'status': 'pass', 'evidence': 'mfa.admin_required is true', 'config_file': 'auth_config.json'},
    {'rule_id': 'AUTH-003', 'rule_name': 'Session Timeout', 'status': 'fail', 'evidence': 'session.timeout_minutes is 60, must be 30 or less', 'config_file': 'auth_config.json'},
    {'rule_id': 'AUTH-004', 'rule_name': 'Account Lockout', 'status': 'fail', 'evidence': 'lockout.max_attempts is 10, must be 5 or fewer', 'config_file': 'auth_config.json'},
    {'rule_id': 'AUTH-005', 'rule_name': 'Password Complexity', 'status': 'fail', 'evidence': 'require_special is false, password policy must require special characters', 'config_file': 'auth_config.json'},
    {'rule_id': 'DATA-001', 'rule_name': 'Encryption at Rest', 'status': 'pass', 'evidence': 'encryption.at_rest.enabled is true', 'config_file': 'database.json'},
    {'rule_id': 'DATA-002', 'rule_name': 'Encryption Algorithm', 'status': 'pass', 'evidence': 'encryption.at_rest.algorithm is AES-256', 'config_file': 'database.json'},
    {'rule_id': 'DATA-003', 'rule_name': 'Backup Encryption', 'status': 'fail', 'evidence': 'backup.encrypted is false, backups must be encrypted', 'config_file': 'database.json'},
    {'rule_id': 'DATA-004', 'rule_name': 'Connection Encryption', 'status': 'pass', 'evidence': 'connection.require_ssl is true', 'config_file': 'database.json'},
    {'rule_id': 'LOG-001', 'rule_name': 'Audit Logging Enabled', 'status': 'pass', 'evidence': 'audit.enabled is true', 'config_file': 'logging.json'},
    {'rule_id': 'LOG-002', 'rule_name': 'Log Retention', 'status': 'pass', 'evidence': 'retention.days is 365, exceeds minimum of 90', 'config_file': 'logging.json'},
    {'rule_id': 'LOG-003', 'rule_name': 'Log Integrity', 'status': 'fail', 'evidence': 'integrity.enabled is false, log integrity checking must be enabled', 'config_file': 'logging.json'},
    {'rule_id': 'LOG-004', 'rule_name': 'Sensitive Data Masking', 'status': 'pass', 'evidence': 'masking.pii is true', 'config_file': 'logging.json'},
    {'rule_id': 'NET-001', 'rule_name': 'Firewall Enabled', 'status': 'pass', 'evidence': 'firewall.enabled is true', 'config_file': 'network.json'},
    {'rule_id': 'NET-002', 'rule_name': 'Default Deny Policy', 'status': 'fail', 'evidence': 'firewall.default_policy is allow, must be deny', 'config_file': 'network.json'},
    {'rule_id': 'NET-003', 'rule_name': 'SSH Key-Only Auth', 'status': 'fail', 'evidence': 'ssh.password_auth is true, must be false (key-only authentication required)', 'config_file': 'network.json'}
]

passed = sum(1 for r in results if r['status'] == 'pass')
failed = sum(1 for r in results if r['status'] == 'fail')

report = {
    'audit_date': '2024-03-15T00:00:00Z',
    'total_rules': 20,
    'passed': passed,
    'failed': failed,
    'results': results
}

with open('$WORKSPACE/compliance_report.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/compliance_report.json"
