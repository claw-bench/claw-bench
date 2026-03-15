#!/usr/bin/env bash
# Oracle solution for xdom-016-meeting-to-tasks
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json

tasks = {
    'sprint': '2026-03-12 to 2026-03-31',
    'tasks': [
        {
            'id': 'TASK-001',
            'title': 'Implement payment API',
            'assignee': 'Mike',
            'priority': 'high',
            'deadline': '2026-03-28',
            'estimate_days': 5,
            'dependencies': []
        },
        {
            'id': 'TASK-002',
            'title': 'Fix timeout bug in order service',
            'assignee': 'Mike',
            'priority': 'medium',
            'deadline': '2026-03-15',
            'estimate_days': 1,
            'dependencies': []
        },
        {
            'id': 'TASK-003',
            'title': 'Build payment checkout UI',
            'assignee': 'Lisa',
            'priority': 'high',
            'deadline': '2026-03-31',
            'estimate_days': 3,
            'dependencies': ['TASK-001']
        },
        {
            'id': 'TASK-004',
            'title': 'Dashboard performance fix',
            'assignee': 'Lisa',
            'priority': 'low',
            'deadline': '2026-03-31',
            'estimate_days': 2,
            'dependencies': []
        },
        {
            'id': 'TASK-005',
            'title': 'Set up payment service infrastructure',
            'assignee': 'Tom',
            'priority': 'high',
            'deadline': '2026-03-18',
            'estimate_days': 3,
            'dependencies': []
        },
        {
            'id': 'TASK-006',
            'title': 'Update monitoring dashboards',
            'assignee': 'Tom',
            'priority': 'medium',
            'deadline': '2026-03-25',
            'estimate_days': 2,
            'dependencies': []
        }
    ],
    'high_priority_count': 3,
    'total_estimate_days': 16
}

with open('$WORKSPACE/tasks.json', 'w') as f:
    json.dump(tasks, f, indent=2)
"

echo "Solution written to $WORKSPACE/tasks.json"
