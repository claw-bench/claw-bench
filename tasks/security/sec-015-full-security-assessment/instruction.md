# Task: Comprehensive Application Security Assessment

Perform a full security review of the application in `workspace/application/`.

## Requirements

1. Analyze all files in `workspace/application/`:
   - `app.py` — Main application code
   - `config.py` — Application configuration
   - `requirements.txt` — Python dependencies
   - `Dockerfile` — Container configuration
   - `docker-compose.yml` — Service orchestration

2. Generate `workspace/assessment.json` with:
   - `executive_summary`: overall risk rating and key findings count
   - `findings`: array of objects, each with:
     - `id`: finding identifier (e.g., `"FIND-001"`)
     - `category`: one of `"code"`, `"config"`, `"dependency"`, `"infrastructure"`, `"authentication"`, `"data_protection"`
     - `severity`: `"critical"`, `"high"`, `"medium"`, `"low"`
     - `title`: brief title
     - `description`: detailed description
     - `file`: affected file
     - `remediation`: specific fix recommendation
   - `risk_summary`: counts by severity and category

3. Generate `workspace/remediation_plan.md` with:
   - Prioritized list of fixes (critical first)
   - Estimated effort for each fix
   - Dependencies between fixes
   - Quick wins section (low effort, high impact)

## Notes

- The application has intentional security issues across multiple categories.
- Expect at least 10 findings spanning code, config, dependencies, and infrastructure.
- Findings should be actionable with specific remediation steps.

## Output

Save `workspace/assessment.json` and `workspace/remediation_plan.md`.
