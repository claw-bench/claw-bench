# Task: Data Pipeline Orchestrator

You are given CSV source files and a set of transform operations. Apply the transforms and produce a final output.

## Requirements

1. Read all CSV files from `workspace/sources/` directory. Combine them into a single dataset (they all have the same columns).
2. Read `workspace/transforms.json` which contains an ordered array of transform operations. Apply them sequentially:
   - **filter**: `{"type": "filter", "column": "col_name", "operator": "op", "value": "val"}` - Keep only rows matching the condition. Operators: `eq`, `neq`, `gt`, `lt`, `gte`, `lte`. For numeric comparisons, compare as numbers.
   - **rename_column**: `{"type": "rename_column", "old_name": "old", "new_name": "new"}` - Rename a column.
   - **aggregate**: `{"type": "aggregate", "group_by": "col", "column": "col", "function": "sum|count|mean"}` - Group by one column and aggregate another. Output has two columns: the group_by column and the aggregated column (named `{function}_{column}`).
3. Write the final result to `workspace/output.csv` with a header row.

## Output

Save the transformed data to `workspace/output.csv`.
