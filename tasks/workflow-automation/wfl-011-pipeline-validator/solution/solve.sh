#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys, json
ws = sys.argv[1]

with open(f"{ws}/pipeline.json") as f:
    pipeline = json.load(f)

errors = []
all_jobs = []
job_names = []

for stage in pipeline["stages"]:
    for job in stage["jobs"]:
        all_jobs.append(job)
        job_names.append(job["name"])

# Check duplicate job names
seen = {}
for name in job_names:
    seen[name] = seen.get(name, 0) + 1
for name, count in seen.items():
    if count > 1:
        errors.append({
            "type": "duplicate_job_name",
            "message": f"Job name '{name}' appears {count} times in the pipeline",
            "jobs": [name]
        })

# Check missing dependencies
unique_names = set(job_names)
for job in all_jobs:
    for dep in job["dependencies"]:
        if dep not in unique_names:
            errors.append({
                "type": "missing_dependency",
                "message": f"Job '{job['name']}' depends on '{dep}' which does not exist",
                "jobs": [job["name"]]
            })

report = {
    "valid": len(errors) == 0,
    "errors": errors,
    "summary": {
        "total_stages": len(pipeline["stages"]),
        "total_jobs": len(all_jobs),
        "total_errors": len(errors)
    }
}

with open(f"{ws}/validation_report.json", "w") as f:
    json.dump(report, f, indent=2)
PYEOF
