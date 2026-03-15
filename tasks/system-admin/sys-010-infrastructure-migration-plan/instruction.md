# Task: Infrastructure Migration Plan

You are given two YAML files describing a complex infrastructure migration:
- `workspace/infrastructure.yaml` - Current infrastructure setup (12 services, databases, load balancers)
- `workspace/requirements.yaml` - Target state requirements and constraints

## Requirements

1. Read both YAML files.
2. Analyze the current infrastructure and target requirements.
3. Generate two output files:

### workspace/migration_plan.md

A detailed, ordered migration plan in Markdown format with:
- Executive summary
- Pre-migration checklist
- Ordered migration steps (must respect service dependencies)
- Each step should include: what to migrate, dependencies, estimated downtime, verification steps
- Post-migration validation steps
- Rollback procedures for each major step

### workspace/risk_assessment.json

```json
{
  "overall_risk_level": "low|medium|high|critical",
  "total_services": <count>,
  "migration_phases": [
    {
      "phase": <number>,
      "name": "<phase name>",
      "services": ["<service names>"],
      "dependencies_met": true,
      "estimated_downtime_minutes": <int>,
      "risks": [
        {
          "description": "<risk>",
          "probability": "low|medium|high",
          "impact": "low|medium|high",
          "mitigation": "<mitigation strategy>"
        }
      ],
      "rollback_steps": ["<step1>", "<step2>"]
    }
  ],
  "total_estimated_downtime_minutes": <sum>,
  "critical_path": ["<service1>", "<service2>", ...],
  "pre_migration_checks": ["<check1>", "<check2>", ...],
  "post_migration_checks": ["<check1>", "<check2>", ...]
}
```

## Key Constraints
- Database migrations must happen before dependent services
- Load balancers must be migrated last (to maintain traffic routing)
- Services with shared state must be migrated together
- Zero-downtime is preferred where possible; document any unavoidable downtime

## Output

Save `workspace/migration_plan.md` and `workspace/risk_assessment.json`.
