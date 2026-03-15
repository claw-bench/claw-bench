# Task: Convert Meeting Notes to Project Tasks

You are given meeting notes at `workspace/meeting_notes.md` from a sprint planning meeting. Parse the notes and extract all action items into a structured task tracker format.

## Requirements

1. Read `workspace/meeting_notes.md`.
2. Extract all action items mentioned in the discussion.
3. Produce `workspace/tasks.json` with the following structure:

### Fields

- `sprint`: the sprint date range in format `"YYYY-MM-DD to YYYY-MM-DD"` (from the meeting date to end of month)
- `tasks`: a list of task objects, each with:
  - `id`: sequential ID in format `"TASK-001"`, `"TASK-002"`, etc.
  - `title`: concise description of the task
  - `assignee`: the person responsible
  - `priority`: `"high"`, `"medium"`, or `"low"` as mentioned in the notes
  - `deadline`: the deadline in `YYYY-MM-DD` format
  - `estimate_days`: estimated effort in days (integer)
  - `dependencies`: list of task IDs this task depends on (empty list if none)
- `high_priority_count`: number of tasks with high priority
- `total_estimate_days`: sum of all task estimate_days

### Guidelines

- Order tasks by their ID.
- If a task depends on another task (e.g., Lisa's checkout UI depends on Mike's API), list the dependency using the dependent task's ID.
- Use the priorities and deadlines as stated in the meeting notes.
- If an estimate is not explicitly stated, infer a reasonable estimate based on context.

## Output

Save the result to `workspace/tasks.json`.
