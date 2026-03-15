# Task: Data Format Converter

You are given two files in `workspace/`:
- `input.csv` — tabular data with 10 rows
- `schema.json` — a schema describing how to map CSV columns to JSON fields, including renames and type conversions

Convert the CSV data to JSON according to the schema.

## Requirements

1. Read `workspace/input.csv` and `workspace/schema.json`.
2. Produce `workspace/output.json` containing a JSON array of objects.
3. The schema defines a `"mappings"` array where each entry has:
   - `"csv_column"`: the source column name in the CSV
   - `"json_field"`: the target field name in the JSON output
   - `"type"`: the target type — one of `"string"`, `"integer"`, `"float"`, `"boolean"`
4. Apply the mappings to each CSV row:
   - Rename fields according to csv_column -> json_field.
   - Convert types: `"integer"` means parse as int, `"float"` as float, `"boolean"` converts "true"/"false" strings (case-insensitive) to JSON booleans.
   - `"string"` values should be stripped of leading/trailing whitespace.
5. The output must be a JSON array with one object per CSV data row.
6. Write with 2-space indentation.

## Output

Save the result to `workspace/output.json`.
