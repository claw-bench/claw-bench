#!/usr/bin/env bash
# Oracle solution for sec-007-log-forensics
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

incidents = [
    {
        'type': 'brute_force',
        'source_ip': '10.0.0.55',
        'time_window': {'start': '15/Mar/2024:08:30:01', 'end': '15/Mar/2024:08:30:23'},
        'description': '12 failed login attempts (HTTP 401) in 22 seconds from 10.0.0.55, indicating automated brute force attack',
        'evidence': [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        'severity': 'high'
    },
    {
        'type': 'scanning',
        'source_ip': '172.16.0.99',
        'time_window': {'start': '15/Mar/2024:09:30:00', 'end': '15/Mar/2024:09:30:11'},
        'description': 'Rapid scanning of 12 sensitive paths (admin, .env, .git, phpmyadmin, backup.sql) in 11 seconds from 172.16.0.99 using Scrapy bot',
        'evidence': [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
        'severity': 'high'
    },
    {
        'type': 'off_hours_access',
        'source_ip': '10.0.0.200',
        'time_window': {'start': '16/Mar/2024:02:15:00', 'end': '16/Mar/2024:02:30:00'},
        'description': 'Admin user accessed 5 admin endpoints between 02:15 and 02:30 including dashboard, users, settings, logs, and data export — unusual off-hours admin activity',
        'evidence': [66, 67, 68, 69, 70],
        'severity': 'medium'
    }
]

with open('$WORKSPACE/security_incidents.json', 'w') as f:
    json.dump(incidents, f, indent=2)
"

echo "Solution written to $WORKSPACE/security_incidents.json"
