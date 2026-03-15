#!/usr/bin/env bash
# Oracle solution for sec-010-network-policy-analysis
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

analysis = {
    'issues': [
        {
            'rule_ids': [7],
            'type': 'overly_permissive',
            'description': 'Rule 7 allows all traffic from any source to any destination on any port — this overrides all other rules and defeats the firewall',
            'severity': 'critical'
        },
        {
            'rule_ids': [1, 14],
            'type': 'redundant',
            'description': 'Rule 14 is an exact duplicate of Rule 1 — both allow HTTPS from 10.0.1.0/24 to 10.0.2.0/24',
            'severity': 'low'
        },
        {
            'rule_ids': [6, 1],
            'type': 'redundant',
            'description': 'Rule 6 allows HTTPS to 10.0.2.10/32 from office, but Rule 1 already allows HTTPS to the entire 10.0.2.0/24 subnet from office',
            'severity': 'low'
        },
        {
            'rule_ids': [17, 18],
            'type': 'conflict',
            'description': 'Rule 17 allows RDP from anywhere to servers, but Rule 18 denies the same traffic — depending on evaluation order, one shadows the other',
            'severity': 'high'
        },
        {
            'rule_ids': [3, 4],
            'type': 'shadowed',
            'description': 'Rule 3 blocks SSH from everywhere (0.0.0.0/0) to servers, but Rule 4 tries to allow SSH from a specific admin IP — if rules are evaluated top-down, Rule 4 is shadowed',
            'severity': 'high'
        },
        {
            'rule_ids': [17],
            'type': 'overly_permissive',
            'description': 'Rule 17 allows RDP (port 3389) from any source to internal servers — RDP should be restricted to specific management IPs',
            'severity': 'critical'
        }
    ],
    'optimized_rules': [
        {'action': 'allow', 'source': '10.0.1.50/32', 'destination': '10.0.2.0/24', 'port': 22, 'protocol': 'tcp', 'description': 'Allow SSH from admin workstation'},
        {'action': 'allow', 'source': '10.0.1.0/24', 'destination': '10.0.2.0/24', 'port': 443, 'protocol': 'tcp', 'description': 'Allow HTTPS from office to servers'},
        {'action': 'allow', 'source': '10.0.1.0/24', 'destination': '10.0.2.0/24', 'port': 80, 'protocol': 'tcp', 'description': 'Allow HTTP from office to servers'},
        {'action': 'allow', 'source': '10.0.1.0/24', 'destination': '10.0.2.0/24', 'port': 8080, 'protocol': 'tcp', 'description': 'Allow 8080 from office to servers'},
        {'action': 'allow', 'source': '0.0.0.0/0', 'destination': '10.0.3.0/24', 'port': 443, 'protocol': 'tcp', 'description': 'Allow HTTPS to DMZ'},
        {'action': 'allow', 'source': '0.0.0.0/0', 'destination': '10.0.3.0/24', 'port': 80, 'protocol': 'tcp', 'description': 'Allow HTTP to DMZ'},
        {'action': 'allow', 'source': '10.0.1.0/24', 'destination': '10.0.4.0/24', 'port': 3306, 'protocol': 'tcp', 'description': 'Allow MySQL from office to DB'},
        {'action': 'allow', 'source': '10.0.1.0/24', 'destination': '10.0.4.0/24', 'port': 5432, 'protocol': 'tcp', 'description': 'Allow PostgreSQL from office to DB'},
        {'action': 'allow', 'source': '10.0.2.0/24', 'destination': '10.0.4.0/24', 'port': 3306, 'protocol': 'tcp', 'description': 'Allow MySQL from app to DB'},
        {'action': 'allow', 'source': '10.0.2.0/24', 'destination': '10.0.4.0/24', 'port': 5432, 'protocol': 'tcp', 'description': 'Allow PostgreSQL from app to DB'},
        {'action': 'deny', 'source': '192.168.0.0/16', 'destination': '10.0.2.0/24', 'port': 'any', 'protocol': 'any', 'description': 'Block guest network from servers'},
        {'action': 'deny', 'source': '10.0.5.0/24', 'destination': '10.0.2.0/24', 'port': 443, 'protocol': 'tcp', 'description': 'Block contractor from servers HTTPS'},
        {'action': 'deny', 'source': '0.0.0.0/0', 'destination': '0.0.0.0/0', 'port': 'any', 'protocol': 'any', 'description': 'Default deny all'}
    ],
    'summary': {
        'total_rules': 20,
        'issues_found': 6,
        'optimized_count': 13
    }
}

with open('$WORKSPACE/policy_analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2)
"

echo "Solution written to $WORKSPACE/policy_analysis.json"
