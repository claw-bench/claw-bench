# Incident Response Runbook

## 1. Identification
- Review all available log sources
- Identify indicators of compromise (IOCs)
- Determine the attack vector and entry point

## 2. Timeline Construction
- Correlate events across log sources by timestamp and IP
- Identify phases: reconnaissance, initial access, persistence, lateral movement, exfiltration
- Document each significant event with timestamp, source, and description

## 3. Scope Assessment
- Map affected IPs to network topology
- Identify all compromised hosts and services
- Determine data exposure scope

## 4. Severity Classification
- **Critical**: Active data exfiltration, credential theft, persistence mechanism
- **High**: Unauthorized admin access, configuration changes
- **Medium**: Brute force attempts, reconnaissance
- **Low**: Anomalous but non-malicious activity

## 5. Root Cause Analysis
- Determine why the attack succeeded
- Identify security control failures
- Document the full attack chain

## 6. Remediation
- Immediate containment actions
- Credential rotation requirements
- Configuration rollback steps
- Long-term security improvements

## 7. Lessons Learned
- What detection gaps existed
- What preventive controls should be added
- Process improvements for future incidents
