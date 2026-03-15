# Task: Sequential Task Execution

Execute a sequence of text analysis tasks in the order specified by a task definition file.

## Input Files

- `workspace/tasks.json` — an ordered list of tasks to execute. Each task has:
  - `"name"`: the task name (e.g., `"count_lines"`, `"count_words"`, `"count_chars"`)
  - `"description"`: what the task does
- `workspace/input.txt` — the text file to analyze

## Requirements

1. Read `workspace/tasks.json` to get the ordered list of tasks.
2. Execute each task in the specified order against `workspace/input.txt`:
   - `"count_lines"`: count the number of non-empty lines
   - `"count_words"`: count the total number of words (whitespace-separated tokens)
   - `"count_chars"`: count the total number of characters (including whitespace, excluding the final trailing newline if present)
3. Write `workspace/results.json` — a JSON array where each element has:
   - `"task"`: the task name
   - `"result"`: the numeric result
   - `"order"`: the execution order (1-based)

## Output

Save results to `workspace/results.json`.
