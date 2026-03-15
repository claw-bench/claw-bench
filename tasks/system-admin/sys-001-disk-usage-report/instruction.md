# Task: Disk Usage Report

You are given a file at `workspace/filesystem.txt` containing simulated `du -sh` output showing directory sizes across a filesystem.

## Requirements

1. Read `workspace/filesystem.txt`.
2. Parse each line to extract the directory path and its size.
3. Convert all sizes to a common unit (bytes) for comparison.
4. Generate a JSON report with the following structure:

```json
{
  "total_size_bytes": <total size in bytes>,
  "total_size_human": "<human-readable total>",
  "top_5_largest": [
    {"path": "<dir>", "size_bytes": <n>, "size_human": "<readable>"},
    ...
  ],
  "dirs_over_1gb": [
    {"path": "<dir>", "size_bytes": <n>, "size_human": "<readable>"},
    ...
  ],
  "dir_count": <total number of directories analyzed>
}
```

5. The `top_5_largest` array must be sorted by size descending.
6. The `dirs_over_1gb` array must include all directories with size >= 1 GB (1073741824 bytes).

## Size Parsing

- Sizes use standard suffixes: K (kilobytes, 1024), M (megabytes, 1024^2), G (gigabytes, 1024^3), T (terabytes, 1024^4).
- Example: `4.2G` = 4.2 * 1073741824 bytes.

## Output

Save the report to `workspace/report.json`.
