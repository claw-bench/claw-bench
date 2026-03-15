# Task: Batch File Renamer

You are given a list of filenames and a set of rename rules. Apply the rules to generate new filenames.

## Requirements

1. Read `workspace/file_list.json` which contains an array of filename strings.
2. Read `workspace/rename_rules.json` which contains an array of rules, each with:
   - `pattern`: a regex pattern to match
   - `replacement`: the replacement string (may use regex backreferences like `\1`)
3. For each filename, apply all rules sequentially (in order). Each rule's output becomes the next rule's input.
4. Produce `workspace/new_names.json` with this structure:
   ```json
   [
     {"original": "old_name.txt", "renamed": "new_name.txt"},
     ...
   ]
   ```
5. If no rules match a filename, the renamed value should be the same as the original.

## Output

Save the rename mapping to `workspace/new_names.json`.
