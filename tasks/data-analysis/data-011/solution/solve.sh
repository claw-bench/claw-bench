#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv, json
from collections import defaultdict

with open('${WORKSPACE}/company_data.csv') as f:
    rows = list(csv.DictReader(f))

total_rev = round(sum(float(r['revenue']) for r in rows), 2)
avg_rev = round(total_rev / len(rows), 2)
total_emp = sum(int(r['employees']) for r in rows)
avg_sat = round(sum(float(r['satisfaction_score']) for r in rows) / len(rows), 2)

company_rev = defaultdict(float)
for r in rows:
    company_rev[r['company']] += float(r['revenue'])
top5 = sorted(company_rev.items(), key=lambda x: -x[1])[:5]

region_rev = defaultdict(list)
region_emp = defaultdict(int)
for r in rows:
    region_rev[r['region']].append(float(r['revenue']))
    region_emp[r['region']] += int(r['employees'])

q_rev = defaultdict(float)
for r in rows:
    q_rev[r['quarter']] += float(r['revenue'])

lines = []
lines.append('# Company Data Analysis Report')
lines.append('')
lines.append('## Summary Statistics')
lines.append('')
lines.append('- **Total Revenue**: ' + f'{total_rev:,.2f}')
lines.append('- **Average Revenue**: ' + f'{avg_rev:,.2f}')
lines.append('- **Total Employees**: ' + f'{total_emp:,}')
lines.append('- **Average Satisfaction Score**: ' + f'{avg_sat:.2f}')
lines.append('')
lines.append('## Top Performers')
lines.append('')
lines.append('Top 5 companies by total revenue:')
lines.append('')
for i, (comp, rev) in enumerate(top5, 1):
    lines.append(f'{i}. **{comp}**: {rev:,.2f}')
lines.append('')
lines.append('## Regional Trends')
lines.append('')
lines.append('Average revenue by region:')
lines.append('')
for reg in sorted(region_rev):
    avg = sum(region_rev[reg]) / len(region_rev[reg])
    lines.append(f'- **{reg}**: {avg:,.2f}')
lines.append('')
lines.append('## Quarterly Trends')
lines.append('')
lines.append('Total revenue per quarter:')
lines.append('')
for q in ['Q1','Q2','Q3','Q4']:
    lines.append(f'- **{q}**: {q_rev[q]:,.2f}')
lines.append('')
lines.append('## Recommendations')
lines.append('')
lines.append('1. **Invest in high-performing regions**: Focus resources on regions showing highest revenue averages.')
lines.append('2. **Address satisfaction gaps**: Implement employee engagement programs for companies with lower scores.')
lines.append('3. **Scale Q4 strategies**: Apply successful late-quarter approaches to earlier quarters.')

with open('${WORKSPACE}/report.md', 'w') as f:
    f.write(chr(10).join(lines) + chr(10))

charts = {
    'bar_chart': {
        'labels': sorted(region_rev.keys()),
        'values': [round(sum(region_rev[r])/len(region_rev[r]), 2) for r in sorted(region_rev.keys())]
    },
    'line_chart': {
        'labels': ['Q1','Q2','Q3','Q4'],
        'values': [round(q_rev[q], 2) for q in ['Q1','Q2','Q3','Q4']]
    },
    'pie_chart': {
        'labels': sorted(region_emp.keys()),
        'values': [region_emp[r] for r in sorted(region_emp.keys())]
    }
}
with open('${WORKSPACE}/charts_data.json', 'w') as f:
    json.dump(charts, f, indent=2)
"
echo "Solution written"
