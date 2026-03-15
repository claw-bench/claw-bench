# Task: Convert CSV to JSON

You are given a CSV file at `workspace/data.csv`. Convert it into a JSON file.

## Requirements

1. Read `workspace/data.csv`.
2. Produce a JSON file containing an array of objects, where:
   - Each object represents one row of the CSV.
   - The keys of each object match the CSV column headers exactly.
   - Numeric values (such as Salary) should remain as strings in the JSON output.
3. Write the result to `workspace/output.json`.

## Example

Given this CSV:

```
Name,Email
Alice,alice@example.com
```

The output should be:

```json
[
  {
    "Name": "Alice",
    "Email": "alice@example.com"
  }
]
```

## Output

Save the JSON array to `workspace/output.json`.
