# Task: Retry with Backoff

Process a set of jobs, implementing retry logic for jobs that fail.

## Input Files

- `workspace/jobs.json` — an array of 5 jobs, each with:
  - `"id"`: job identifier (e.g., `"job_1"`)
  - `"name"`: descriptive name
  - `"fail_count"`: number of times this job will fail before succeeding (0 means it succeeds on first try)

## Requirements

1. Read `workspace/jobs.json`.
2. Process each job in order. A job "fails" if it has remaining failures (`fail_count > 0`). Each attempt consumes one failure.
3. Implement retry logic with a maximum of 3 retries (so up to 4 total attempts including the first).
4. For each job, track:
   - `"id"`: the job ID
   - `"attempts"`: total number of attempts made
   - `"status"`: `"success"` if the job eventually succeeded, `"failed"` if it exhausted all retries
   - `"history"`: an array of attempt results, each being `"fail"` or `"success"`
5. Write `workspace/execution_log.json` — a JSON object with:
   - `"jobs"`: array of job results (as described above)
   - `"summary"`: object with `"total"`, `"succeeded"`, `"failed"` counts

## Rules

- A job with `fail_count` of 0 succeeds on first try (1 attempt).
- A job with `fail_count` of 2 fails twice, then succeeds on the 3rd attempt.
- A job with `fail_count` of 5 fails all 4 attempts (first try + 3 retries) and is marked `"failed"`.
- Maximum retries = 3 (so max 4 total attempts per job).

## Output

Save results to `workspace/execution_log.json`.
