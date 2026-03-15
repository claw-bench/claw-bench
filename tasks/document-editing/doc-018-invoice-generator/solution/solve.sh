#!/usr/bin/env bash
# Oracle solution for doc-018-invoice-generator
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json

with open('$WORKSPACE/order.json') as f:
    order = json.load(f)

lines = []
lines.append('# Invoice')
lines.append('')
lines.append(f'**Invoice Number:** {order[\"invoice_number\"]}')
lines.append(f'**Date:** {order[\"date\"]}')
lines.append(f'**Due Date:** {order[\"due_date\"]}')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## From')
lines.append('')
lines.append(f'**{order[\"from\"][\"company\"]}**')
lines.append(f'{order[\"from\"][\"address\"]}')
lines.append('')
lines.append('## To')
lines.append('')
lines.append(f'**{order[\"to\"][\"company\"]}**')
lines.append(f'{order[\"to\"][\"address\"]}')
lines.append(f'Contact: {order[\"to\"][\"contact\"]}')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## Line Items')
lines.append('')
lines.append('| Description | Qty | Unit Price | Total |')
lines.append('| --- | --- | --- | --- |')

subtotal = 0.0
for item in order['items']:
    total = item['quantity'] * item['unit_price']
    subtotal += total
    lines.append(f'| {item[\"description\"]} | {item[\"quantity\"]} | \${item[\"unit_price\"]:.2f} | \${total:.2f} |')

tax = round(subtotal * order['tax_rate'], 2)
grand_total = subtotal + tax

lines.append('')
lines.append(f'**Subtotal:** \${subtotal:.2f}')
lines.append(f'**Tax (8%):** \${tax:.2f}')
lines.append(f'**Grand Total:** \${grand_total:.2f}')
lines.append('')
lines.append('---')
lines.append('')
lines.append('## Notes')
lines.append('')
lines.append(order['notes'])
lines.append('')

with open('$WORKSPACE/invoice.md', 'w') as f:
    f.write('\n'.join(lines))
"

echo "Solution written to $WORKSPACE/invoice.md"
