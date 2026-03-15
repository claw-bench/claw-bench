# CSV and JSON Merge

You have two data files in your workspace:

1. `employees.csv` - Contains employee records with columns: employee_id, first_name, last_name, department, hire_date
2. `performance.json` - Contains performance review data as a JSON array with fields: employee_id, review_year, rating, goals_met, reviewer

**Task:** Merge these two data sources on the `employee_id` field and produce `combined.json` in the workspace.

## Requirements

- The output `combined.json` must be a JSON array of objects
- Each object contains all fields from the CSV row plus a `performance_reviews` array containing all matching review records for that employee
- Employees with no performance reviews should still appear with an empty `performance_reviews` array
- Performance review entries in the `performance_reviews` array should NOT include the `employee_id` field (it is already on the parent object)
- The output array must be sorted by `employee_id` (ascending, as strings)
- Numeric fields in the CSV (employee_id) should remain strings in the output to match the CSV source format
- The `rating` field from performance data should remain a number
- The `goals_met` field should remain a boolean
- The JSON output must be properly formatted (indented with 2 spaces)
