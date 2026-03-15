# Task: Scheduled Workflow Plan with Critical Path

Generate an execution schedule and identify the critical path for a set of dependent tasks.

## Input Files

- `workspace/tasks.json` — array of 12 tasks, each with:
  - `"id"`: task identifier (e.g., `"T1"`)
  - `"name"`: task name
  - `"duration"`: time units to complete
  - `"dependencies"`: array of task IDs that must complete before this task can start

## Requirements

1. Read `workspace/tasks.json`.
2. Compute a valid topological ordering of tasks.
3. For each task, compute:
   - `"earliest_start"`: the earliest time the task can start (max of dependency completion times)
   - `"earliest_finish"`: earliest_start + duration
   - `"latest_start"`: the latest time the task can start without delaying the project
   - `"latest_finish"`: latest_start + duration
   - `"slack"`: latest_start - earliest_start
4. Identify the **critical path**: the longest path through the dependency graph (tasks with 0 slack).
5. Write `workspace/schedule.json` — a JSON object with:
   - `"tasks"`: array of task schedules (each with id, name, duration, earliest_start, earliest_finish, latest_start, latest_finish, slack)
   - `"total_duration"`: the minimum total time to complete all tasks
6. Write `workspace/critical_path.json` — a JSON object with:
   - `"path"`: array of task IDs on the critical path (in order)
   - `"total_duration"`: the total project duration
   - `"path_length"`: number of tasks on the critical path

## Output

- `workspace/schedule.json`
- `workspace/critical_path.json`
