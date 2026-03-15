#!/usr/bin/env bash
# Oracle solution for sec-011-incident-response-plan
set -euo pipefail

WORKSPACE="${1:-workspace}"

cat > "$WORKSPACE/response_plan.md" << 'PLANEOF'
# Incident Response Plan: INC-2024-0042

## Incident Summary

- **Incident ID**: INC-2024-0042
- **Type**: Data Breach
- **Severity**: Critical
- **Reported**: 2024-03-15T14:30:00Z
- **Status**: Not Contained

Unauthorized access to the customer database was detected via anomalous queries from a compromised service account (svc-analytics). Approximately 45,000 customer records with PII (email, phone, address, SSN, name) were potentially exposed.

## Affected Systems

| System | Type | IP Address |
|--------|------|------------|
| app-srv-03 | Application Server | 10.0.2.30 |
| db-primary-01 | Database | 10.0.4.10 |
| db-replica-02 | Database | 10.0.4.11 |

## Immediate Actions (Containment)

Based on Playbook PB-002 (Data Breach Response):

1. **Immediately revoke compromised credentials** — Disable the svc-analytics account and rotate all associated API keys
2. **Isolate affected systems** — Remove app-srv-03 from the network; restrict database access to essential services only
3. **Preserve all logs and forensic evidence** — Capture database query logs, application logs from app-srv-03, network flow data, and authentication logs
4. **Block malicious IP** — Add 203.0.113.42 to firewall deny list

## Investigation Steps

1. Analyze authentication logs to determine how 203.0.113.42 obtained svc-analytics credentials
2. Review all queries executed by svc-analytics since 2024-03-15T08:15:00Z
3. Examine the suspicious binary (hash: a1b2c3d4e5f6789012345678abcdef01) found on app-srv-03
4. Check for lateral movement to other systems from app-srv-03
5. Analyze outbound network traffic to determine if data was exfiltrated and to where
6. Determine exact number of records accessed vs. the estimated 45,000

## Remediation Steps

1. Patch the vulnerability or close the attack vector that allowed credential compromise
2. Implement multi-factor authentication for all service accounts
3. Apply principle of least privilege to database access (svc-analytics should not have SELECT * access to PII)
4. Enable database activity monitoring with real-time alerting
5. Implement data masking for SSN and other sensitive fields at the application layer
6. Rotate all credentials for affected systems

## Communication Plan

- **Internal (immediate)**: Notify CISO and executive leadership
- **Legal counsel**: Engage for breach notification requirements (state/federal regulations)
- **Regulatory**: File notifications as required (within 72 hours for GDPR, per state laws for US)
- **Affected individuals**: Prepare breach notification letters for ~45,000 customers
- **Public relations**: Prepare public statement if breach becomes public knowledge

## Post-Incident Review

- [ ] Root cause fully identified and documented
- [ ] All affected systems remediated
- [ ] Credentials rotated across all affected services
- [ ] Detection gap analyzed (6+ hours from initial compromise to SIEM alert)
- [ ] Monitoring improvements implemented
- [ ] Playbook PB-002 updated with lessons learned
- [ ] Review scheduled within 72 hours of containment
PLANEOF

python3 -c "
import json

timeline = [
    {
        'timestamp': '2024-03-15T08:15:00Z',
        'event': 'svc-analytics account authenticated from unusual external IP 203.0.113.42',
        'source': 'authentication_logs',
        'severity': 'high'
    },
    {
        'timestamp': '2024-03-15T08:22:00Z',
        'event': 'First anomalous SELECT query against customers table detected',
        'source': 'database_audit_logs',
        'severity': 'high'
    },
    {
        'timestamp': '2024-03-15T10:45:00Z',
        'event': 'Spike in outbound data transfer from app-srv-03 (2.3 GB)',
        'source': 'network_monitoring',
        'severity': 'critical'
    },
    {
        'timestamp': '2024-03-15T14:30:00Z',
        'event': 'SIEM alert triggered, incident reported to security team',
        'source': 'siem',
        'severity': 'critical'
    },
    {
        'timestamp': '2024-03-15T14:45:00Z',
        'event': 'Security team acknowledged and began initial assessment',
        'source': 'incident_management',
        'severity': 'info'
    },
    {
        'timestamp': '2024-03-15T15:00:00Z',
        'event': 'PLANNED: Revoke svc-analytics credentials and isolate app-srv-03',
        'source': 'response_plan',
        'severity': 'critical'
    },
    {
        'timestamp': '2024-03-15T15:30:00Z',
        'event': 'PLANNED: Preserve forensic evidence from all affected systems',
        'source': 'response_plan',
        'severity': 'high'
    },
    {
        'timestamp': '2024-03-15T16:00:00Z',
        'event': 'PLANNED: Notify CISO and executive leadership',
        'source': 'response_plan',
        'severity': 'high'
    },
    {
        'timestamp': '2024-03-15T18:00:00Z',
        'event': 'PLANNED: Complete initial scope assessment',
        'source': 'response_plan',
        'severity': 'high'
    },
    {
        'timestamp': '2024-03-16T14:30:00Z',
        'event': 'PLANNED: Engage legal counsel for breach notification',
        'source': 'response_plan',
        'severity': 'medium'
    },
    {
        'timestamp': '2024-03-18T14:30:00Z',
        'event': 'PLANNED: Post-incident review meeting (within 72 hours)',
        'source': 'response_plan',
        'severity': 'medium'
    }
]

with open('$WORKSPACE/timeline.json', 'w') as f:
    json.dump(timeline, f, indent=2)
"

echo "Solution written to $WORKSPACE/response_plan.md and $WORKSPACE/timeline.json"
