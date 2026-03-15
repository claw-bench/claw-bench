# Task: Generate Incident Response Plan

Given details of a security incident and available response playbooks, generate a comprehensive response plan.

## Requirements

1. Read `workspace/incident.json` (security incident details).
2. Read `workspace/playbooks.json` (available response playbooks).
3. Generate `workspace/response_plan.md` with:
   - **Incident Summary**: What happened, when, severity
   - **Affected Systems**: List of affected components
   - **Immediate Actions**: Steps to contain the incident (from matching playbook)
   - **Investigation Steps**: How to determine scope and root cause
   - **Remediation Steps**: How to fix the vulnerability
   - **Communication Plan**: Who to notify (stakeholders, affected users, legal)
   - **Post-Incident Review**: Lessons learned checklist
4. Generate `workspace/timeline.json` as a JSON array of events, each with:
   - `timestamp`: ISO 8601 format
   - `event`: description of what happened
   - `source`: where this information came from
   - `severity`: impact level

## Notes

- The incident is a data breach involving customer PII.
- Match the correct playbook from the available playbooks.
- Timeline must include all events from the incident plus planned response milestones.

## Output

Save `workspace/response_plan.md` and `workspace/timeline.json`.
