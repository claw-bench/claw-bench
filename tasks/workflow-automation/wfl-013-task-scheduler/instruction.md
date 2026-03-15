# Task: Task Scheduler

You are given a set of tasks with priorities, deadlines, durations, and dependencies. Produce an optimal schedule.

## Requirements

1. Read `workspace/tasks.json` which contains an array of tasks, each with:
   - `id`: unique task identifier (string)
   - `duration_minutes`: how long the task takes
   - `priority`: integer (1=highest, 5=lowest)
   - `deadline`: minutes from time 0 by which the task should complete
   - `dependencies`: array of task IDs that must complete before this task starts
2. Schedule tasks on a single worker, one at a time. A task cannot start until all its dependencies are complete.
3. Among tasks whose dependencies are satisfied, prefer tasks with:
   - Higher priority (lower number) first
   - Earlier deadline as tiebreaker
4. Time starts at 0. Each task runs for its `duration_minutes` without interruption.
5. Produce `workspace/schedule.json` with this structure:
   ```json
   [
     {
       "id": "task_id",
       "start_time": 0,
       "end_time": 30
     },
     ...
   ]
   ```
6. Tasks should appear in the order they are scheduled.

## Output

Save the schedule to `workspace/schedule.json`.
