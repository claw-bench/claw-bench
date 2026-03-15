#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

with open('$WORKSPACE/thread.json') as f:
    thread = json.load(f)

participants = sorted(set(m['user'] for m in thread))

summary = {
    'participants': participants,
    'key_decisions': [
        'Use Python with FastAPI for the microservice',
        'Use PostgreSQL as the database',
        'Use Redis Streams as the message queue',
        'Use pytest with 80% minimum coverage enforcement in CI',
        'Include integration tests'
    ],
    'action_items': [
        {'assignee': 'eve', 'task': 'Set up the database schema'},
        {'assignee': 'bob', 'task': 'Handle CI/CD pipeline setup with coverage check'},
        {'assignee': 'charlie', 'task': 'Create API scaffolding with FastAPI by Friday'},
        {'assignee': 'diana', 'task': 'Take care of Docker configuration and deployment scripts'},
        {'assignee': 'eve', 'task': 'Write integration tests after schema is ready'}
    ],
    'topic': 'Tech stack decision for new microservice',
    'message_count': len(thread)
}

with open('$WORKSPACE/summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
"

echo "Solution written to $WORKSPACE/summary.json"
