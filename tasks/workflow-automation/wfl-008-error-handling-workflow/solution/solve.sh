#!/usr/bin/env bash
# Oracle solution for wfl-008-error-handling-workflow
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

with open('$WORKSPACE/workflow_steps.json') as f:
    steps = json.load(f)

results = []
compensations = []
completed_compensatable = []  # stack of completed compensatable steps
workflow_status = 'completed'
aborted = False

for step in steps:
    if aborted:
        results.append({
            'id': step['id'],
            'name': step['name'],
            'status': 'skipped',
            'action_taken': None
        })
        continue

    if step['will_fail']:
        # Primary action fails
        if step['fallback']:
            # Fallback succeeds
            results.append({
                'id': step['id'],
                'name': step['name'],
                'status': 'completed_with_fallback',
                'action_taken': step['fallback']
            })
            if step['compensatable']:
                completed_compensatable.append(step)
        else:
            # No fallback
            if step['critical']:
                # Critical failure -> compensate and abort
                results.append({
                    'id': step['id'],
                    'name': step['name'],
                    'status': 'failed',
                    'action_taken': step['action']
                })
                # Compensate in reverse order
                for comp_step in reversed(completed_compensatable):
                    compensations.append({
                        'step_id': comp_step['id'],
                        'step_name': comp_step['name'],
                        'compensation_action': comp_step['compensation_action']
                    })
                    # Update the result for this step
                    for r in results:
                        if r['id'] == comp_step['id']:
                            r['status'] = 'compensated'
                            break
                workflow_status = 'aborted'
                aborted = True
            else:
                results.append({
                    'id': step['id'],
                    'name': step['name'],
                    'status': 'failed',
                    'action_taken': step['action']
                })
    else:
        results.append({
            'id': step['id'],
            'name': step['name'],
            'status': 'completed',
            'action_taken': step['action']
        })
        if step['compensatable']:
            completed_compensatable.append(step)

# Count summary
completed_count = sum(1 for r in results if r['status'] in ('completed', 'completed_with_fallback'))
failed_count = sum(1 for r in results if r['status'] == 'failed')
compensated_count = sum(1 for r in results if r['status'] == 'compensated')
skipped_count = sum(1 for r in results if r['status'] == 'skipped')

report = {
    'steps': results,
    'compensations': compensations,
    'workflow_status': workflow_status,
    'summary': {
        'completed_count': completed_count,
        'failed_count': failed_count,
        'compensated_count': compensated_count,
        'skipped_count': skipped_count
    }
}

with open('$WORKSPACE/execution_report.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/execution_report.json"
