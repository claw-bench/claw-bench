# Task: Multi-Format Aggregator

You are given three files in `workspace/`:
- `sales.csv` — sales transactions with columns: product, quantity, unit_price
- `inventory.json` — current stock levels per product
- `notes.txt` — operational notes with structured annotations like `ALERT: <message>`

Combine these into a unified dashboard.

## Requirements

1. Read all three input files from `workspace/`.
2. Produce `workspace/dashboard.json` containing a JSON object with a `"products"` array.
3. Each product object must have:
   - `"name"`: the product name (string)
   - `"total_sales"`: sum of (quantity * unit_price) from all CSV rows for that product (number)
   - `"total_units_sold"`: sum of quantity from CSV for that product (integer)
   - `"stock_level"`: current stock from inventory.json (integer)
   - `"alerts"`: array of alert message strings from notes.txt that mention this product
4. Extract alerts from notes.txt by finding lines matching `ALERT: <message>`. Include the full message text (everything after "ALERT: ") in the alerts array for each product whose name appears in that message.
5. Sort the products array alphabetically by name.
6. Write with 2-space indentation.

## Output

Save the result to `workspace/dashboard.json`.
