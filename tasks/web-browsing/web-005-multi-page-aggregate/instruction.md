# Task: Multi-Page Data Aggregation

Aggregate product data from multiple HTML catalog pages.

## Requirements

1. Read all HTML files in `workspace/pages/` (page1.html through page5.html).
2. Each page contains a list of products in `<div class="product">` elements.
3. Extract from each product: `name`, `price` (as number), `category`, and `rating` (as number).
4. Produce `workspace/aggregated.json` with:
   - `products`: array of all products from all pages, each with `name`, `price`, `category`, `rating`, and `source_page` (filename).
   - `total_products`: total count.
   - `price_range`: object with `min` and `max` prices.
   - `categories`: sorted array of unique category names.
   - `avg_rating`: average rating across all products, rounded to 2 decimal places.

## Output

Save the aggregated data to `workspace/aggregated.json`.
