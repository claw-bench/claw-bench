#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

with open('$WORKSPACE/notifications.json') as f:
    notifications = json.load(f)
with open('$WORKSPACE/preferences.json') as f:
    preferences = json.load(f)

routed = []
for n in notifications:
    user_prefs = preferences.get(n['user'], preferences['default'])
    channels = user_prefs.get(n['type'], [])
    routed.append({
        'notification_id': n['id'],
        'user': n['user'],
        'type': n['type'],
        'channels': channels,
        'title': n['title'],
        'message': n['message']
    })

routed.sort(key=lambda x: x['notification_id'])
with open('$WORKSPACE/routed.json', 'w') as f:
    json.dump(routed, f, indent=2)
"

echo "Solution written to $WORKSPACE/routed.json"
