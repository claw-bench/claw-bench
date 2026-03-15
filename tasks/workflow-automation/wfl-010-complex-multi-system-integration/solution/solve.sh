#!/usr/bin/env bash
# Oracle solution for wfl-010-complex-multi-system-integration
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import csv
import json
import os
from collections import defaultdict

ws = '$WORKSPACE'
os.makedirs(f'{ws}/invoices', exist_ok=True)

# Load data
with open(f'{ws}/customers.json') as f:
    customers = json.load(f)
cust_map = {c['id']: c for c in customers}

with open(f'{ws}/pricing_rules.json') as f:
    pricing = json.load(f)

with open(f'{ws}/orders.csv', newline='') as f:
    reader = csv.DictReader(f)
    orders = list(reader)

# Step 1: Validate
valid_orders = []
invalid_orders = []
for order in orders:
    errors = []
    order['quantity'] = int(order['quantity'])
    order['unit_price'] = float(order['unit_price'])

    if order['customer_id'] not in cust_map:
        errors.append(f\"customer_id {order['customer_id']} not found\")
    if order['quantity'] <= 0:
        errors.append('quantity must be > 0')
    if order['unit_price'] <= 0:
        errors.append('unit_price must be > 0')

    if errors:
        invalid_orders.append({
            'order_id': order['order_id'],
            'errors': errors
        })
    else:
        valid_orders.append(order)

with open(f'{ws}/validation_errors.json', 'w') as f:
    json.dump(invalid_orders, f, indent=2)

# Steps 2-4: Enrich, Price, and Generate Invoices
tier_counts = defaultdict(int)
customer_spend = defaultdict(float)
total_revenue = 0.0
total_discount = 0.0

for order in valid_orders:
    cust = cust_map[order['customer_id']]
    tier = cust['tier']
    tier_counts[tier] += 1

    # Pricing
    subtotal = order['quantity'] * order['unit_price']
    tier_disc = pricing['tier_discounts'].get(tier, 0)

    volume_disc = 0
    for rule in pricing['volume_discounts']:
        if order['quantity'] >= rule['min_quantity']:
            volume_disc = rule['discount']
            break

    discount_pct = tier_disc + volume_disc
    discount_amount = round(subtotal * discount_pct, 2)
    total = round(subtotal - discount_amount, 2)

    total_revenue += total
    total_discount += discount_amount
    customer_spend[order['customer_id']] += total

    invoice = {
        'order_id': order['order_id'],
        'customer_name': cust['name'],
        'customer_email': cust['email'],
        'address': cust['address'],
        'product': order['product'],
        'quantity': order['quantity'],
        'unit_price': order['unit_price'],
        'subtotal': subtotal,
        'discount_pct': discount_pct,
        'discount_amount': discount_amount,
        'total': total,
        'date': order['date']
    }

    with open(f\"{ws}/invoices/invoice_{order['order_id']}.json\", 'w') as f:
        json.dump(invoice, f, indent=2)

# Step 5: Batch summary
top_customer = max(customer_spend, key=customer_spend.get)
avg_order = round(total_revenue / len(valid_orders), 2)

summary = {
    'total_orders': len(orders),
    'valid_orders': len(valid_orders),
    'invalid_orders': len(invalid_orders),
    'total_revenue': round(total_revenue, 2),
    'total_discount': round(total_discount, 2),
    'orders_by_tier': dict(tier_counts),
    'top_customer': top_customer,
    'average_order_value': avg_order
}

with open(f'{ws}/batch_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
"

echo "Solution complete. Check $WORKSPACE/ for outputs."
