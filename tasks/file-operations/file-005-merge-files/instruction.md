# Task: Merge Multiple Files

You are given three text files in the workspace: `workspace/part1.txt`, `workspace/part2.txt`, and `workspace/part3.txt`. Each file has the same header line as its first line, followed by data lines. Merge them into a single file.

## Requirements

1. Read `workspace/part1.txt`, `workspace/part2.txt`, and `workspace/part3.txt`.
2. Each file begins with the header line `Name,Score,Grade`. This header should appear only once in the output.
3. Concatenate all data lines (non-header lines) from the three files in order: part1 data first, then part2, then part3.
4. Write the result to `workspace/merged.txt`.

## Output

Save the merged content to `workspace/merged.txt`.
