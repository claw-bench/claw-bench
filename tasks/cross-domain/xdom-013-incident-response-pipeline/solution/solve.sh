#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

cat > "$WORKSPACE/incident_report.json" << 'REPORT_EOF'
{
  "incident_id": "INC-2026-0312",
  "title": "Brute Force Compromise Leading to Data Exfiltration and Persistent Backdoor Creation",
  "severity": "critical",
  "timeline": [
    {
      "timestamp": "2026-03-11T10:32:07Z",
      "event": "Attacker begins reconnaissance by accessing login page using automated python-requests tool",
      "source": "access.log",
      "source_ip": "198.51.100.77",
      "target": "web-frontend-01"
    },
    {
      "timestamp": "2026-03-11T10:32:08Z",
      "event": "Brute force attack begins against admin account with 15 rapid failed login attempts over 8 seconds",
      "source": "access.log, auth.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "auth-service-01"
    },
    {
      "timestamp": "2026-03-11T10:32:16Z",
      "event": "Attacker successfully authenticates as admin after brute force attack",
      "source": "access.log, auth.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "auth-service-01"
    },
    {
      "timestamp": "2026-03-11T10:33:01Z",
      "event": "Attacker accesses admin dashboard and begins enumerating users, exports user list as CSV (284KB)",
      "source": "access.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "web-frontend-01"
    },
    {
      "timestamp": "2026-03-11T10:35:30Z",
      "event": "Attacker modifies admin settings: disables MFA, extends session timeout to 24h, raises API rate limit to 10000",
      "source": "access.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "web-frontend-01"
    },
    {
      "timestamp": "2026-03-11T10:36:15Z",
      "event": "Full database export initiated via API, 1.5MB of data exfiltrated from db-primary-01",
      "source": "access.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "db-primary-01"
    },
    {
      "timestamp": "2026-03-11T10:37:44Z",
      "event": "Attacker creates backdoor service account 'backdoor-svc' with admin role for persistence",
      "source": "access.log, auth.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "auth-service-01"
    },
    {
      "timestamp": "2026-03-11T10:38:20Z",
      "event": "Backdoor account elevated to super-admin role",
      "source": "access.log, auth.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "auth-service-01"
    },
    {
      "timestamp": "2026-03-11T10:40:05Z",
      "event": "Secrets endpoint accessed - API keys, database credentials, and encryption keys exfiltrated",
      "source": "access.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "web-frontend-01"
    },
    {
      "timestamp": "2026-03-11T10:42:33Z",
      "event": "Attacker attempts to delete audit logs to cover tracks",
      "source": "access.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "web-frontend-01"
    },
    {
      "timestamp": "2026-03-11T11:20:10Z",
      "event": "Outbound webhook registered pointing to attacker C2 server (exfil.attacker-c2.example.net) for ongoing data exfiltration",
      "source": "access.log, auth.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "web-frontend-01"
    },
    {
      "timestamp": "2026-03-11T11:25:45Z",
      "event": "Customer database table exfiltrated via backdoor account (3.4MB)",
      "source": "access.log, auth.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "db-primary-01"
    },
    {
      "timestamp": "2026-03-11T11:45:12Z",
      "event": "Orders database table exfiltrated via backdoor account (5.7MB)",
      "source": "access.log, auth.log, error.log",
      "source_ip": "198.51.100.77",
      "target": "db-primary-01"
    }
  ],
  "affected_systems": [
    {
      "hostname": "web-frontend-01",
      "ip": "10.0.0.10",
      "subnet": "dmz",
      "services": ["nginx", "webapp"],
      "impact": "Admin settings modified (MFA disabled, session timeout extended), secrets exposed, audit logs deleted, used as primary attack surface"
    },
    {
      "hostname": "auth-service-01",
      "ip": "10.0.1.10",
      "subnet": "internal-services",
      "services": ["auth-api", "ldap"],
      "impact": "Admin account compromised via brute force, backdoor service account created with super-admin privileges"
    },
    {
      "hostname": "db-primary-01",
      "ip": "10.0.2.10",
      "subnet": "database",
      "services": ["postgresql"],
      "impact": "Full database export performed, customer and orders tables exfiltrated totaling over 10MB of sensitive data"
    },
    {
      "hostname": "db-replica-01",
      "ip": "10.0.2.11",
      "subnet": "database",
      "services": ["postgresql"],
      "impact": "Replica synced from compromised primary; may contain replicated malicious changes"
    }
  ],
  "root_cause": "The admin account was protected by a weak password that was susceptible to brute force attack. The application lacked adequate brute force protections - although rate limit warnings were generated, the attacker was not blocked after exceeding thresholds. No multi-factor authentication was enforced on the admin account. Once the admin account was compromised, there were insufficient controls to prevent privilege escalation, bulk data export, and security setting modifications from a single session.",
  "attack_vector": "External brute force attack against the web application login endpoint from IP 198.51.100.77 using automated python-requests tooling, targeting the admin account",
  "remediation_steps": [
    "Immediately disable the 'backdoor-svc' account and revoke all associated API keys and sessions",
    "Force password reset for the 'admin' account and all other privileged accounts, enforcing strong password policy",
    "Re-enable MFA requirement and revert admin settings (session_timeout, api_rate_limit) to secure defaults",
    "Block IP 198.51.100.77 at the network firewall and WAF level",
    "Remove the malicious outbound webhook pointing to exfil.attacker-c2.example.net",
    "Rotate all secrets, API keys, database credentials, and encryption keys that were exposed via the /api/v1/config/secrets endpoint",
    "Restore audit logs from backup and implement immutable audit logging",
    "Implement account lockout after 5 failed login attempts with progressive delays",
    "Deploy WAF rules to detect and block automated brute force attacks based on user-agent and request patterns",
    "Conduct full forensic review of db-primary-01 and db-replica-01 to assess data integrity"
  ],
  "lessons_learned": [
    "Brute force detection alerts were generated but no automated blocking was triggered - implement automated IP blocking on threshold breach",
    "MFA was not enforced for admin accounts - mandate MFA for all privileged accounts with no ability to disable via admin settings",
    "Bulk data export APIs lacked additional authorization controls - implement approval workflows for large data exports",
    "Audit log deletion should not be permitted even by admin accounts - implement immutable append-only audit logging",
    "No alerting was configured for critical events like new account creation or role elevation - implement real-time SIEM alerting for privileged operations"
  ]
}
REPORT_EOF
