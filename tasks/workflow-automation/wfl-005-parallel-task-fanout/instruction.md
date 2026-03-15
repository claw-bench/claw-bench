# Task: Parallel Task Fan-Out and Aggregation

Process multiple independent items through a pipeline, then aggregate the results.

## Input Files

- `workspace/items/` — a directory containing 5 JSON files (`item_1.json` through `item_5.json`)
- Each item file contains:
  - `"id"`: item identifier
  - `"name"`: item name
  - `"value"`: numeric value
  - `"category"`: category string
  - `"tags"`: array of tags

## Requirements

For each item, perform these steps:

1. **Validate**: Check that the item has all required fields (`id`, `name`, `value`, `category`, `tags`). Mark as `"valid": true` or `"valid": false`.
2. **Transform**: Normalize the value to a 0-100 scale using: `normalized = (value / 1000) * 100` (cap at 100). Add a `"label"` field that is the uppercase version of the name.
3. **Score**: Calculate a score based on: `score = normalized * (1 + 0.1 * len(tags))`. Round to 2 decimal places.

Write individual results to `workspace/results/` as `result_1.json` through `result_5.json`, each containing the original fields plus `valid`, `normalized`, `label`, and `score`.

Then write `workspace/aggregated_results.json` with:
- `"items"`: array of all processed item results
- `"summary"`: object with `"total_items"`, `"valid_count"`, `"total_score"`, `"average_score"`, `"highest_scorer"` (id of the item with the highest score)

## Output

- Individual results in `workspace/results/`
- Aggregated results in `workspace/aggregated_results.json`
