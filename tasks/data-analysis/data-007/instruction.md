# Task: Join Two Datasets

You are given two CSV files:
- `workspace/orders.csv` with columns: `order_id`, `customer_id`, `product`, `amount`
- `workspace/customers.csv` with columns: `customer_id`, `name`, `email`, `city`

## Requirements

1. Read both CSV files.
2. Perform a **left join** of orders with customers on `customer_id`.
3. The resulting CSV should have columns: `order_id`, `customer_id`, `product`, `amount`, `name`, `email`, `city`.
4. Preserve the original order of rows from orders.csv.
5. Write the result to `workspace/enriched_orders.csv`.

## Output

Save the joined data to `workspace/enriched_orders.csv`.
