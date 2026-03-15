#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv

with open('$WORKSPACE/customers.csv') as f:
    customers = {row['customer_id']: row for row in csv.DictReader(f)}

with open('$WORKSPACE/orders.csv') as f:
    orders = list(csv.DictReader(f))

with open('$WORKSPACE/enriched_orders.csv', 'w', newline='') as f:
    fields = ['order_id', 'customer_id', 'product', 'amount', 'name', 'email', 'city']
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for order in orders:
        cust = customers.get(order['customer_id'], {})
        row = {**order, 'name': cust.get('name', ''), 'email': cust.get('email', ''), 'city': cust.get('city', '')}
        writer.writerow(row)
"
echo "Solution written to $WORKSPACE/enriched_orders.csv"
