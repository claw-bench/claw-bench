#!/usr/bin/env bash
# Oracle solution for eml-012-complex-workflow
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json, re

with open('$WORKSPACE/incoming_batch.json') as f:
    emails = json.load(f)
with open('$WORKSPACE/routing_rules.json') as f:
    rules = json.load(f)

urgent_words = ['urgent', 'critical', 'asap', 'immediately', 'deadline']
low_words = ['fyi', 'newsletter', 'no action needed']

def classify(email):
    text = (email['subject'] + ' ' + email['body']).lower()
    if any(w in text for w in urgent_words):
        return 'urgent'
    if any(w in text for w in low_words):
        return 'low'
    return 'normal'

def route(email, departments):
    text = (email['subject'] + ' ' + email['body']).lower()
    best_dept = 'general'
    best_count = 0
    for dept, info in departments.items():
        count = sum(1 for kw in info['keywords'] if kw.lower() in text)
        if count > best_count:
            best_count = count
            best_dept = dept
    return best_dept

def summarize(email):
    subj = email['subject']
    if len(subj) <= 100:
        return subj
    return subj[:97] + '...'

results = []
for email in emails:
    c = classify(email)
    d = route(email, rules['departments'])
    s = summarize(email)
    results.append({
        'id': email['id'],
        'classification': c,
        'department': d,
        'summary': s,
        'priority_rank': 0
    })

# Sort: urgent first, then normal, then low, then by date
class_order = {'urgent': 0, 'normal': 1, 'low': 2}
id_to_date = {e['id']: e['date'] for e in emails}
results.sort(key=lambda r: (class_order[r['classification']], id_to_date[r['id']]))
for i, r in enumerate(results):
    r['priority_rank'] = i + 1

with open('$WORKSPACE/processed_batch.json', 'w') as f:
    json.dump(results, f, indent=2)

# Generate routing report
from collections import Counter
dept_counts = Counter(r['department'] for r in results)
class_counts = Counter(r['classification'] for r in results)
urgent_items = [r for r in results if r['classification'] == 'urgent']
id_to_email = {e['id']: e for e in emails}

report = '# Email Routing Report\n\n'
report += f'## Summary\n\nTotal emails processed: {len(results)}\n\n'
report += '## By Department\n\n'
for dept, count in sorted(dept_counts.items()):
    report += f'- **{dept}**: {count}\n'
report += '\n## By Classification\n\n'
for cls in ['urgent', 'normal', 'low']:
    report += f'- **{cls}**: {class_counts[cls]}\n'
report += '\n## Urgent Emails\n\n'
report += '| ID | Subject | Department |\n'
report += '|----|---------|------------|\n'
for r in urgent_items:
    subj = id_to_email[r['id']]['subject']
    report += f'| {r[\"id\"]} | {subj} | {r[\"department\"]} |\n'

with open('$WORKSPACE/routing_report.md', 'w') as f:
    f.write(report)
"

echo "Solution written to $WORKSPACE/processed_batch.json and $WORKSPACE/routing_report.md"
