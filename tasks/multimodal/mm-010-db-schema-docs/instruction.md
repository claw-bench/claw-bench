# Task: Database Schema Documentation

You are given a SQL file at `workspace/schema.sql` containing SQLite `CREATE TABLE` statements. Parse these statements and produce structured JSON documentation.

## Requirements

1. Read `workspace/schema.sql`.
2. Produce `workspace/schema_docs.json` containing a JSON object with a `"tables"` key, which is an array of table objects.
3. Each table object must have:
   - `"name"`: the table name (string)
   - `"columns"`: an array of column objects, each with:
     - `"name"`: column name (string)
     - `"type"`: the SQL data type as written (string, e.g. `"INTEGER"`, `"VARCHAR(255)"`, `"TEXT"`)
     - `"nullable"`: boolean (`false` if `NOT NULL` is specified, `true` otherwise)
     - `"primary_key"`: boolean (`true` if this column is a primary key)
   - `"foreign_keys"`: an array of foreign key objects, each with:
     - `"column"`: the column name in this table (string)
     - `"references_table"`: the referenced table name (string)
     - `"references_column"`: the referenced column name (string)
4. Tables should appear in the same order as in the SQL file.
5. Columns should appear in the same order as defined in the CREATE TABLE statement.
6. Write the output with 2-space indentation.

## Notes

- Primary keys may be defined inline (`id INTEGER PRIMARY KEY`) or as a separate `PRIMARY KEY(...)` constraint.
- Foreign keys are defined as `FOREIGN KEY (col) REFERENCES table(col)`.
- A column is nullable unless explicitly marked `NOT NULL` or it is a `PRIMARY KEY`.

## Output

Save the result to `workspace/schema_docs.json`.
