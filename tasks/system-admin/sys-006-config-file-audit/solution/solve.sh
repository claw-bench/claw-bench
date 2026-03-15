#!/usr/bin/env bash
# Oracle solution for sys-006-config-file-audit
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json

report = {
    'total_issues': 0,
    'files': {
        'nginx.conf': {'issues': []},
        'ssh_config': {'issues': []},
        'my.cnf': {'issues': []}
    },
    'summary': {'high': 0, 'medium': 0, 'low': 0}
}

# Audit nginx.conf
nginx_issues = [
    {'line_hint': 'server_tokens on', 'severity': 'medium',
     'description': 'Server version information is exposed via server_tokens directive',
     'recommendation': 'Set server_tokens off to hide version information'},
    {'line_hint': 'autoindex on', 'severity': 'high',
     'description': 'Directory listing is enabled, exposing file structure to visitors',
     'recommendation': 'Set autoindex off to disable directory listing'},
    {'line_hint': 'client_max_body_size 0', 'severity': 'medium',
     'description': 'No upload size limit configured, allowing unlimited file uploads',
     'recommendation': 'Set client_max_body_size to a reasonable limit (e.g., 10M)'},
    {'line_hint': 'ssl_protocols TLSv1 TLSv1.1 TLSv1.2', 'severity': 'high',
     'description': 'Weak SSL/TLS protocols (TLSv1, TLSv1.1) are enabled',
     'recommendation': 'Use only TLSv1.2 and TLSv1.3: ssl_protocols TLSv1.2 TLSv1.3'},
    {'line_hint': 'ssl_ciphers ALL:!aNULL:!eNULL', 'severity': 'high',
     'description': 'Weak cipher suites are allowed in SSL configuration',
     'recommendation': 'Use strong cipher suites only, e.g., ssl_ciphers HIGH:!aNULL:!MD5'},
    {'line_hint': 'missing security headers', 'severity': 'medium',
     'description': 'No security headers configured (X-Frame-Options, X-Content-Type-Options, etc.)',
     'recommendation': 'Add security headers: X-Frame-Options DENY, X-Content-Type-Options nosniff, etc.'}
]
report['files']['nginx.conf']['issues'] = nginx_issues

# Audit ssh_config
ssh_issues = [
    {'line_hint': 'PermitRootLogin yes', 'severity': 'high',
     'description': 'Root login via SSH is permitted',
     'recommendation': 'Set PermitRootLogin no or PermitRootLogin prohibit-password'},
    {'line_hint': 'PasswordAuthentication yes', 'severity': 'medium',
     'description': 'Password authentication is enabled, vulnerable to brute-force attacks',
     'recommendation': 'Set PasswordAuthentication no and use key-based authentication'},
    {'line_hint': 'PermitEmptyPasswords yes', 'severity': 'high',
     'description': 'Empty passwords are allowed for authentication',
     'recommendation': 'Set PermitEmptyPasswords no'},
    {'line_hint': 'MaxAuthTries 10', 'severity': 'medium',
     'description': 'Maximum authentication attempts is too high (10)',
     'recommendation': 'Set MaxAuthTries to 3 or 4'},
    {'line_hint': 'X11Forwarding yes', 'severity': 'low',
     'description': 'X11 forwarding is enabled, increasing attack surface',
     'recommendation': 'Set X11Forwarding no unless required'},
    {'line_hint': 'AllowTcpForwarding yes', 'severity': 'medium',
     'description': 'TCP forwarding is enabled, allowing SSH tunneling',
     'recommendation': 'Set AllowTcpForwarding no unless required'},
    {'line_hint': 'ClientAliveInterval 0', 'severity': 'low',
     'description': 'No idle session timeout configured',
     'recommendation': 'Set ClientAliveInterval 300 and ClientAliveCountMax 2'}
]
report['files']['ssh_config']['issues'] = ssh_issues

# Audit my.cnf
mysql_issues = [
    {'line_hint': 'bind-address = 0.0.0.0', 'severity': 'high',
     'description': 'MySQL is bound to all interfaces, accessible from any network',
     'recommendation': 'Set bind-address = 127.0.0.1 to restrict to localhost'},
    {'line_hint': 'local-infile = 1', 'severity': 'high',
     'description': 'LOAD DATA LOCAL INFILE is enabled, potential data exfiltration risk',
     'recommendation': 'Set local-infile = 0 to disable'},
    {'line_hint': 'symbolic-links = 1', 'severity': 'medium',
     'description': 'Symbolic links are enabled, potential privilege escalation risk',
     'recommendation': 'Set symbolic-links = 0 to disable'},
    {'line_hint': 'general_log = 1', 'severity': 'medium',
     'description': 'General query logging is enabled in production, may log sensitive data',
     'recommendation': 'Disable general_log in production or ensure log file permissions are restricted'},
    {'line_hint': 'old_passwords = 1', 'severity': 'high',
     'description': 'Old password hashing format is enabled, using weak hashing algorithm',
     'recommendation': 'Set old_passwords = 0 or 2 to use stronger password hashing'},
    {'line_hint': 'require_secure_transport not set', 'severity': 'medium',
     'description': 'SSL/TLS is not required for database connections',
     'recommendation': 'Enable require_secure_transport = ON to enforce encrypted connections'}
]
report['files']['my.cnf']['issues'] = mysql_issues

# Calculate totals
all_issues = nginx_issues + ssh_issues + mysql_issues
report['total_issues'] = len(all_issues)
report['summary']['high'] = sum(1 for i in all_issues if i['severity'] == 'high')
report['summary']['medium'] = sum(1 for i in all_issues if i['severity'] == 'medium')
report['summary']['low'] = sum(1 for i in all_issues if i['severity'] == 'low')

with open('$WORKSPACE/audit_report.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/audit_report.json"
