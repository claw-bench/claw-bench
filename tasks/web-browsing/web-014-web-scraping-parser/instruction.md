# Task: Parse Product Table and Compute Statistics

You are given `workspace/products.html` containing an HTML table of product listings. Parse the data and compute statistics.

## Requirements

1. Read `workspace/products.html`.
2. Parse the product table. Each row has columns: Name, Price, Category, In Stock.
3. Produce `workspace/products.json` with two top-level keys:
   - **products**: A list of product objects, each with:
     - **name**: String
     - **price**: Float (parsed from price string like "$29.99")
     - **category**: String
     - **in_stock**: Boolean (`true` if "Yes", `false` if "No")
   - **statistics**: An object with:
     - **total_products**: Integer count of all products
     - **avg_price**: Float, average price rounded to 2 decimal places
     - **categories**: An object mapping each category name to its product count
     - **in_stock_count**: Integer count of products that are in stock

## Output

Save the result to `workspace/products.json`.
