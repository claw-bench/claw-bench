# Task: Error Handling Workflow with Compensation

Execute a series of workflow steps with error handling, fallbacks, and compensation logic.

## Input Files

- `workspace/workflow_steps.json` — array of 8 steps, each with:
  - `"id"`: step identifier
  - `"name"`: step name
  - `"action"`: what this step does
  - `"will_fail"`: boolean indicating if this step will fail
  - `"fail_reason"`: reason for failure (null if won't fail)
  - `"fallback"`: fallback action to execute if this step fails (null if none)
  - `"compensatable"`: boolean indicating if this step can be undone
  - `"compensation_action"`: action to undo this step (null if not compensatable)
  - `"critical"`: boolean - if true and step fails (even after fallback), trigger compensation of all previously completed steps and abort

## Requirements

1. Execute steps in order.
2. For each step:
   - If it succeeds, record it as `"completed"`.
   - If it fails:
     - Try the fallback action if available. If the fallback succeeds, record as `"completed_with_fallback"`.
     - If no fallback or fallback also fails: record as `"failed"`.
     - If the step is `critical` and it fails (no fallback available or fallback doesn't help): compensate all previously completed compensatable steps (in reverse order) and mark the workflow as `"aborted"`.
3. Steps that are configured with `"will_fail": true` always fail on their primary action. Fallbacks always succeed.
4. Write `workspace/execution_report.json` with:
   - `"steps"`: array of step results with `"id"`, `"name"`, `"status"` (completed/completed_with_fallback/failed/compensated/skipped), `"action_taken"` (primary action, fallback, or compensation action)
   - `"compensations"`: array of compensation actions executed (in order)
   - `"workflow_status"`: `"completed"` if all steps finished, `"aborted"` if a critical failure occurred
   - `"summary"`: `"completed_count"`, `"failed_count"`, `"compensated_count"`, `"skipped_count"`

## Output

Save results to `workspace/execution_report.json`.
