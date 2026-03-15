# Task: Incident Response Workflow

Process incident data through a full incident response workflow.

## Input Files

- `workspace/incident_data/service.log` - Application service logs
- `workspace/incident_data/alerts.json` - Monitoring alerts
- `workspace/incident_data/config_change.json` - Recent config changes
- `workspace/incident_data/team_contacts.json` - Team contact information

## Objective

Generate a complete incident response package:

1. `workspace/timeline.json` - Chronological event timeline
2. `workspace/root_cause.md` - Root cause analysis document
3. `workspace/remediation_plan.json` - Structured remediation steps
4. `workspace/communication_draft.md` - Stakeholder notification

## Output: timeline.json

```json
{
  "incident_id": "INC-2026-0310",
  "events": [
    {
      "timestamp": "2026-03-10T08:00:00",
      "source": "log|alert|config",
      "description": "What happened"
    }
  ]
}
```

Events must be in chronological order and cover all major incident phases.

## Output: root_cause.md

Must include: summary, contributing factors, root cause statement, evidence from the data.

## Output: remediation_plan.json

```json
{
  "immediate_actions": [...],
  "short_term_fixes": [...],
  "long_term_improvements": [...]
}
```

Each action must have `description`, `owner`, `priority`, and `deadline`.

## Output: communication_draft.md

Stakeholder notification with: incident summary, impact, current status, next steps, contact person.
