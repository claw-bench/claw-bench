# Task: Detect SQL Injection Vulnerabilities

Analyze `workspace/queries.py` for SQL injection vulnerabilities.

## Requirements

1. Read `workspace/queries.py`, which contains 8 database query functions.
2. Identify functions that are vulnerable to SQL injection (those using string concatenation or f-strings to build queries with user input).
3. Identify functions that are safe (those using parameterized queries).
4. Write `workspace/vulnerabilities.json` as a JSON array of objects for **vulnerable functions only**, each with:
   - `function`: function name
   - `line`: line number where the vulnerable query is constructed
   - `pattern`: type of vulnerability (e.g., `"string_concatenation"`, `"f_string"`, `"format_string"`)
   - `description`: explanation of why it is vulnerable
   - `fix`: suggested fix using parameterized queries

## Notes

- 4 of the 8 functions are vulnerable; 4 are safe.
- Do NOT flag the safe functions.
- Fix suggestions should show parameterized query syntax.

## Output

Save results to `workspace/vulnerabilities.json`.
