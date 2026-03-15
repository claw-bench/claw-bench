# Task: Complex Multi-System Order Processing Integration

Orchestrate a complete order processing workflow that reads orders, validates them, enriches with customer data, applies pricing rules, generates invoices, and creates a batch summary.

## Input Files

- `workspace/orders.csv` — 15 orders with columns: `order_id`, `customer_id`, `product`, `quantity`, `unit_price`, `date`
- `workspace/customers.json` — 8 customer records with: `id`, `name`, `email`, `tier` (bronze/silver/gold/platinum), `address`
- `workspace/pricing_rules.json` — tiered pricing rules defining discounts by tier and volume thresholds

## Workflow Steps

### 1. Validate Orders
- Each order must have a valid `customer_id` that exists in `customers.json`
- `quantity` must be > 0
- `unit_price` must be > 0
- Write invalid orders to `workspace/validation_errors.json`

### 2. Enrich Orders
- For each valid order, add customer `name`, `email`, `tier`, and `address` from the customer data

### 3. Apply Pricing
Using `workspace/pricing_rules.json`:
- Apply tier-based discount: bronze=0%, silver=5%, gold=10%, platinum=15%
- Apply volume discount: quantity >= 10 gets additional 5%, quantity >= 50 gets additional 10%
- Calculate: `subtotal = quantity * unit_price`, `discount_pct = tier_discount + volume_discount`, `discount_amount = subtotal * discount_pct`, `total = subtotal - discount_amount`

### 4. Generate Invoices
- For each valid, priced order, generate a JSON invoice in `workspace/invoices/`
- Filename: `invoice_{order_id}.json`
- Each invoice contains: `order_id`, `customer_name`, `customer_email`, `address`, `product`, `quantity`, `unit_price`, `subtotal`, `discount_pct`, `discount_amount`, `total`, `date`

### 5. Create Batch Summary
Write `workspace/batch_summary.json` with:
- `"total_orders"`: total orders in input
- `"valid_orders"`: count of valid orders
- `"invalid_orders"`: count of invalid orders
- `"total_revenue"`: sum of all totals
- `"total_discount"`: sum of all discount amounts
- `"orders_by_tier"`: object with count per tier
- `"top_customer"`: customer_id with highest total spend
- `"average_order_value"`: average total across valid orders

## Output

- `workspace/validation_errors.json`
- `workspace/invoices/` (one file per valid order)
- `workspace/batch_summary.json`
