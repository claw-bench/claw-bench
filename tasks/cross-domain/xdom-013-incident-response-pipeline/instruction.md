# Incident Response Pipeline

You are a senior incident response engineer. A potential security breach has been detected across multiple servers. You have been given raw log files, a network configuration, and a runbook template. Your job is to perform a full incident analysis and produce a structured incident response report.

## Input Files

- `access.log` — HTTP access log from the web server (Apache combined format)
- `error.log` — Application error log with timestamps and severity levels
- `auth.log` — Authentication log showing login attempts, successes, and failures
- `network.yaml` — Network topology and configuration describing subnets, hosts, and services
- `runbook.md` — Incident response runbook template with sections to guide your analysis

## Requirements

### Step 1: Log Correlation and Timeline Construction
- Parse all three log files and identify suspicious events
- Correlate events across logs by timestamp and source IP to build an attack timeline
- Identify the initial compromise vector, lateral movement, and data exfiltration phases

### Step 2: Affected Systems Identification
- Cross-reference IPs and hostnames from the logs with the network configuration
- Determine which subnets and services were affected
- Identify the blast radius of the incident

### Step 3: Incident Response Report Generation
Produce a file called `incident_report.json` in the workspace with the following structure:

```json
{
  "incident_id": "INC-2026-0312",
  "title": "string describing the incident",
  "severity": "critical|high|medium|low",
  "timeline": [
    {
      "timestamp": "ISO 8601 timestamp",
      "event": "description of what happened",
      "source": "which log file(s) this was found in",
      "source_ip": "IP address involved",
      "target": "affected host or service"
    }
  ],
  "affected_systems": [
    {
      "hostname": "name from network config",
      "ip": "IP address",
      "subnet": "subnet name",
      "services": ["list of services on this host"],
      "impact": "description of impact"
    }
  ],
  "root_cause": "detailed explanation of how the attack succeeded",
  "attack_vector": "initial entry point description",
  "remediation_steps": [
    "ordered list of specific remediation actions"
  ],
  "lessons_learned": [
    "list of improvements to prevent recurrence"
  ]
}
```

### Constraints
- The `timeline` array must have at least 6 events in chronological order
- The `affected_systems` array must include all hosts that appear in suspicious log entries and exist in the network config
- `remediation_steps` must include at least 5 specific, actionable steps
- `severity` must be justified by the scope and nature of the attack found in the logs
- All timestamps in the timeline must be valid ISO 8601 format
