# Task: Text Formatting

Apply formatting rules to a plain text document.

## Requirements

1. Read `workspace/document.txt` and `workspace/rules.json`.
2. Apply the following formatting rules (also described in rules.json):
   - **Line wrapping**: Wrap lines at 80 characters maximum. Break at the last space before the 80-character limit. Do not break words.
   - **Whitespace normalization**: Replace multiple consecutive spaces with a single space. Remove trailing whitespace from each line. Remove leading whitespace from each line (except indentation — lines starting with `  ` two spaces are intentional indentation and should be preserved as exactly two spaces).
   - **Punctuation spacing**: Ensure exactly one space after periods, commas, colons, and semicolons (unless at end of line). Remove spaces before periods, commas, colons, and semicolons.
3. Write the formatted result to `workspace/formatted.txt`.

## Output

Save the formatted document to `workspace/formatted.txt`.
