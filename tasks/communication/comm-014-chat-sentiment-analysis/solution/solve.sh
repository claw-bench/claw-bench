#!/usr/bin/env bash
# Oracle solution for comm-014-chat-sentiment-analysis
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import json
import re
import sys

ws = sys.argv[1]

with open(f"{ws}/keywords.json", 'r') as f:
    keywords = json.load(f)

positive_words = [w.lower() for w in keywords['positive']]
negative_words = [w.lower() for w in keywords['negative']]

messages = []
with open(f"{ws}/chat_log.jsonl", 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            messages.append(json.loads(line))

def classify(text):
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'

users = {}
overall = {'total_messages': 0, 'positive': 0, 'negative': 0, 'neutral': 0}

for msg in messages:
    user = msg['user']
    sentiment = classify(msg['text'])

    if user not in users:
        users[user] = {'total_messages': 0, 'positive': 0, 'negative': 0, 'neutral': 0}

    users[user]['total_messages'] += 1
    users[user][sentiment] += 1
    overall['total_messages'] += 1
    overall[sentiment] += 1

report = {'users': users, 'overall': overall}

with open(f"{ws}/sentiment_report.json", 'w') as f:
    json.dump(report, f, indent=2)
PYEOF

echo "Solution written to $WORKSPACE/sentiment_report.json"
