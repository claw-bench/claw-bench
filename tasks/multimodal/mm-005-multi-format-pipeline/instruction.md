# Multi-Format Data Pipeline

You have the following files in your workspace:
- `products.csv` — product catalog with columns: id, name, category, base_price
- `discounts.json` — discount rules mapping category names to discount percentages
- `tags.txt` — line-delimited file with format `<product_id>:<tag1>,<tag2>,...`
- `rules.toml` — transformation rules to apply

**Task:** Read all input files, apply the transformation rules, and produce `result.json` in the workspace.

## Transformation Rules (defined in rules.toml)

The `rules.toml` file specifies:
- `price_adjustment`: a multiplier applied to `base_price` after discount (e.g., 1.08 for 8% tax)
- `min_price`: floor price — if final price is below this, set it to this value
- `exclude_categories`: list of categories to exclude from the output entirely
- `tag_required`: if set, only include products that have at least one of these tags

## Output Format

`result.json` must be a JSON array of objects, each with:
- `id` (integer): the product id
- `name` (string): the product name
- `category` (string): the product category
- `original_price` (number): the base_price from CSV (as a float)
- `discount_percent` (number): the discount percentage from discounts.json for this category (0 if none)
- `final_price` (number): computed as `base_price * (1 - discount_percent/100) * price_adjustment`, but no less than `min_price`. Round to 2 decimal places.
- `tags` (list of strings): tags from tags.txt for this product (empty list if none)

Sort the output array by `id` ascending.
