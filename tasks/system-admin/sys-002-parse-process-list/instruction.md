# Task: Parse Process List

You are given a file at `workspace/processes.txt` containing simulated `ps aux` output showing running processes on a system.

## Requirements

1. Read `workspace/processes.txt`.
2. Parse the process list (skip the header line).
3. Identify the top 5 processes by CPU usage.
4. Generate a JSON report with the following structure:

```json
{
  "total_processes": <count>,
  "top_5_cpu": [
    {
      "pid": <pid as integer>,
      "user": "<username>",
      "cpu_percent": <cpu% as float>,
      "mem_percent": <mem% as float>,
      "command": "<command name>"
    },
    ...
  ],
  "total_cpu_usage": <sum of all CPU percentages>,
  "total_mem_usage": <sum of all memory percentages>
}
```

5. The `top_5_cpu` array must be sorted by `cpu_percent` descending.
6. The `command` field should contain the full command string (last column, which may contain spaces).

## Output

Save the report to `workspace/top_processes.json`.
