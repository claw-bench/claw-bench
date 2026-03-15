# Multi-Table Join and Aggregation

You have three CSV files in the `data/` directory:

- `customers.csv` — columns: customer_id, name, region
- `orders.csv` — columns: order_id, customer_id, product_id, quantity, order_date
- `products.csv` — columns: product_id, product_name, category, unit_price

Join these three tables and produce a file called `summary.csv` in the workspace directory with the following columns:

- `customer_name` — from customers table
- `region` — from customers table
- `category` — product category
- `total_revenue` — sum of (quantity × unit_price) for that customer+category combination

Sort the output by `total_revenue` descending. Round `total_revenue` to 2 decimal places.
