# Task: Disk Usage Analyzer

You are given a file at `workspace/disk_usage.txt` containing output similar to the `du` command, with each line showing a size in KB followed by a tab and a directory path.

## Requirements

1. Read `workspace/disk_usage.txt`.
2. Parse each line to extract the directory path and its size in KB.
3. Generate a JSON report saved to `workspace/disk_report.json` with the following structure:

```json
{
  "total_usage_kb": <sum of all sizes in KB>,
  "top_5_largest": [
    {"path": "<dir>", "size_kb": <n>},
    ...
  ],
  "dirs_over_1gb": [
    {"path": "<dir>", "size_kb": <n>},
    ...
  ],
  "entry_count": <total number of entries>
}
```

4. The `top_5_largest` array must contain exactly 5 entries sorted by size in descending order.
5. The `dirs_over_1gb` array must include all directories with size >= 1 GB (1048576 KB).
6. The `dirs_over_1gb` array must be sorted by size in descending order.

## Input Format

Each line of `disk_usage.txt` has the format:
```
<size_in_kb>\t<path>
```

For example:
```
524288	/var/log
```

This means `/var/log` uses 524288 KB (512 MB).

## Output

Save the report to `workspace/disk_report.json`.
