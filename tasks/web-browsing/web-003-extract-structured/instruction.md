# Task: Extract Structured Data from Product Page

Extract product information from an HTML product page.

## Requirements

1. Read `workspace/product_page.html`.
2. Extract:
   - `name`: the product name (from the `<h1>` with class `product-name`).
   - `price`: the price as a number (from the element with class `price`), without the currency symbol.
   - `currency`: the currency symbol (e.g., `$`).
   - `description`: the product description text (from the element with class `product-description`).
   - `rating`: the rating as a number (from the element with class `rating-value`).
   - `review_count`: number of reviews (from element with class `review-count`).
   - `features`: array of feature strings (from the `<ul>` with class `features`).
   - `in_stock`: boolean (true if element with class `stock-status` contains "In Stock").
   - `sku`: the SKU string (from element with class `sku`).
3. Write to `workspace/product.json`.

## Output

Save the extracted product data to `workspace/product.json`.
