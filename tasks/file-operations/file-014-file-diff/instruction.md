# Task: File Comparison and Diff

You are given two text files: `workspace/original.txt` and `workspace/modified.txt`. Generate a diff report.

## Requirements

1. Read both `workspace/original.txt` and `workspace/modified.txt`.
2. Compare them line by line and identify:
   - Lines that were **removed** (present in original, absent in modified)
   - Lines that were **added** (absent in original, present in modified)
3. Generate `workspace/diff.txt` with the following format:
   - Lines removed from the original are prefixed with `- ` (minus and space)
   - Lines added in the modified version are prefixed with `+ ` (plus and space)
   - Unchanged lines are prefixed with `  ` (two spaces)
4. Include all lines from both files (unchanged lines provide context).
5. The output should reflect a unified-style diff showing the complete file with change markers.

## Example

Original:
```
line one
line two
line three
```

Modified:
```
line one
line TWO
line three
line four
```

Output:
```
  line one
- line two
+ line TWO
  line three
+ line four
```

## Output

Save the diff report to `workspace/diff.txt`.
