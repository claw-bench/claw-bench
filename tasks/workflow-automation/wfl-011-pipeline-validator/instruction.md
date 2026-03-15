# Task: CI/CD Pipeline Validator

You are given a CI/CD pipeline definition at `workspace/pipeline.json`. Validate it and produce a report.

## Requirements

1. Read `workspace/pipeline.json` which contains a pipeline with stages and jobs.
2. Validate the pipeline for the following errors:
   - **circular_dependency**: A job depends (directly or transitively) on itself.
   - **missing_dependency**: A job references a dependency that does not exist.
   - **duplicate_job_name**: Two or more jobs share the same name.
3. Produce `workspace/validation_report.json` with this structure:
   ```json
   {
     "valid": false,
     "errors": [
       {
         "type": "error_type",
         "message": "Human-readable description",
         "jobs": ["affected_job_1", "affected_job_2"]
       }
     ],
     "summary": {
       "total_stages": 4,
       "total_jobs": 8,
       "total_errors": 2
     }
   }
   ```
4. If the pipeline has no errors, `valid` should be `true` and `errors` should be empty.

## Output

Save the validation report to `workspace/validation_report.json`.
