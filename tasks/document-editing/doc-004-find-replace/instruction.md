# Task: Find and Replace with Patterns

Apply regex-based replacement rules to a text document.

## Requirements

1. Read `workspace/document.txt` and `workspace/replacements.json`.
2. `replacements.json` contains an array of replacement rules, each with:
   - `pattern`: a regex pattern to find.
   - `replacement`: the replacement string (may include backreferences like `\1`).
   - `description`: human-readable description of the rule.
3. Apply all rules in order to the document text.
4. Write the result to `workspace/result.txt`.

## Output

Save the transformed document to `workspace/result.txt`.
