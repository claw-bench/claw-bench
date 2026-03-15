#!/usr/bin/env bash
# Oracle solution for eml-014-thread-reconstructor
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import json, sys

ws = sys.argv[1]

with open(f'{ws}/emails.json') as f:
    emails = json.load(f)

# Index by id
by_id = {e['id']: e for e in emails}

# Find root of each message
def find_root(msg_id):
    msg = by_id[msg_id]
    while msg['in_reply_to'] is not None:
        msg = by_id[msg['in_reply_to']]
    return msg['id']

# Group by thread root
threads_map = {}
for e in emails:
    root_id = find_root(e['id'])
    if root_id not in threads_map:
        threads_map[root_id] = []
    threads_map[root_id].append(e)

# Build thread objects
threads = []
for root_id, messages in threads_map.items():
    root_msg = by_id[root_id]
    # Sort messages by date
    messages.sort(key=lambda m: m['date'])

    # Collect participants
    participants = set()
    for m in messages:
        participants.add(m['from'])
        for addr in m['to'].split(','):
            participants.add(addr.strip())

    threads.append({
        'thread_id': root_id,
        'subject': root_msg['subject'],
        'message_count': len(messages),
        'participants': sorted(participants),
        'messages': [
            {
                'id': m['id'],
                'from': m['from'],
                'to': m['to'],
                'subject': m['subject'],
                'date': m['date']
            }
            for m in messages
        ]
    })

# Sort threads by root message date
threads.sort(key=lambda t: by_id[t['thread_id']]['date'])

with open(f'{ws}/threads.json', 'w') as f:
    json.dump(threads, f, indent=2)
PYEOF

echo "Threads reconstructed to $WORKSPACE/threads.json"
