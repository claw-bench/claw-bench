#!/usr/bin/env bash
# Oracle solution for wfl-004-retry-with-backoff
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

with open('$WORKSPACE/jobs.json') as f:
    jobs = json.load(f)

MAX_RETRIES = 3
results = []
succeeded = 0
failed = 0

for job in jobs:
    job_id = job['id']
    fail_count = job['fail_count']
    history = []
    remaining_failures = fail_count
    status = 'failed'

    for attempt in range(MAX_RETRIES + 1):
        if remaining_failures > 0:
            history.append('fail')
            remaining_failures -= 1
        else:
            history.append('success')
            status = 'success'
            break

    if status == 'success':
        succeeded += 1
    else:
        failed += 1

    results.append({
        'id': job_id,
        'attempts': len(history),
        'status': status,
        'history': history
    })

output = {
    'jobs': results,
    'summary': {
        'total': len(jobs),
        'succeeded': succeeded,
        'failed': failed
    }
}

with open('$WORKSPACE/execution_log.json', 'w') as f:
    json.dump(output, f, indent=2)
"

echo "Solution written to $WORKSPACE/execution_log.json"
