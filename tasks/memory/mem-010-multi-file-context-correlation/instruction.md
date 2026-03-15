# Task: Multi-File Context Correlation

You are given 5 text files in your workspace: `file_a.txt`, `file_b.txt`, `file_c.txt`, `file_d.txt`, and `file_e.txt`. Each file contains a short passage with a clue embedded in it.

## Requirements

1. Read all 5 files (`file_a.txt` through `file_e.txt`).
2. From each file, extract the **first word** of the passage (the very first word of the file content, ignoring any leading whitespace).
3. Order the extracted words **alphabetically by filename** (file_a, file_b, file_c, file_d, file_e).
4. Combine the words into a single message, separated by spaces.
5. Write the result to `workspace/answer.txt` as a single line of text.

## Example

If:
- `file_a.txt` starts with "Hello there..."
- `file_b.txt` starts with "World of wonder..."
- `file_c.txt` starts with "Today we..."

Then extracting first words in file order: "Hello World Today"

## Output

Write the combined message to `workspace/answer.txt` (single line, no trailing newline needed).
