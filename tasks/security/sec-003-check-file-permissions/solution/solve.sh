#!/usr/bin/env bash
# Oracle solution for sec-003-check-file-permissions
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

audit = [
    {
        'file': 'config.yaml',
        'permissions': '-rwxrwxrwx',
        'issue': 'Configuration file has 777 permissions — world-readable, writable, and executable',
        'recommendation': '640'
    },
    {
        'file': 'private_key.pem',
        'permissions': '-rw-rw-rw-',
        'issue': 'Private key file is world-readable and world-writable',
        'recommendation': '600'
    },
    {
        'file': 'backup_script.sh',
        'permissions': '-rwsr-xr-x',
        'issue': 'SUID bit set on shell script — potential privilege escalation',
        'recommendation': '755'
    },
    {
        'file': 'passwords.db',
        'permissions': '-rw-r--rw-',
        'issue': 'Password database is world-writable',
        'recommendation': '600'
    },
    {
        'file': 'upload_handler.cgi',
        'permissions': '-rwxrwxrwx',
        'issue': 'CGI handler has 777 permissions — world-writable executable',
        'recommendation': '755'
    },
    {
        'file': '.htpasswd',
        'permissions': '-rw-rw-r--',
        'issue': 'Password file is group-writable and world-readable',
        'recommendation': '600'
    }
]

with open('$WORKSPACE/permission_audit.json', 'w') as f:
    json.dump(audit, f, indent=2)
"

echo "Solution written to $WORKSPACE/permission_audit.json"
