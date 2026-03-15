#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE/outputs"

python3 -c "
import json

with open('$WORKSPACE/message.json') as f:
    msg = json.load(f)

# Telegram
lines = []
lines.append('*' + msg['subject'] + '*')
lines.append('')
lines.append(msg['body'])
lines.append('')
for link in msg['links']:
    lines.append(link['label'] + ': ' + link['url'])
with open('$WORKSPACE/outputs/telegram.txt', 'w') as f:
    f.write('\n'.join(lines) + '\n')

# Slack
blocks = []
blocks.append({'type': 'header', 'text': {'type': 'plain_text', 'text': msg['subject']}})
blocks.append({'type': 'section', 'text': {'type': 'mrkdwn', 'text': msg['body']}})
for link in msg['links']:
    blocks.append({'type': 'section', 'text': {'type': 'mrkdwn', 'text': '<' + link['url'] + '|' + link['label'] + '>'}})
with open('$WORKSPACE/outputs/slack.json', 'w') as f:
    json.dump({'blocks': blocks}, f, indent=2)

# Email
lines = []
lines.append('Subject: ' + msg['subject'])
lines.append('From: ' + msg['sender'])
lines.append('To: ' + ', '.join(msg['recipients']))
lines.append('')
lines.append(msg['body'])
lines.append('')
for link in msg['links']:
    lines.append(link['label'] + ' — ' + link['url'])
with open('$WORKSPACE/outputs/email.txt', 'w') as f:
    f.write('\n'.join(lines) + '\n')
"

echo "Solution written to $WORKSPACE/outputs/"
