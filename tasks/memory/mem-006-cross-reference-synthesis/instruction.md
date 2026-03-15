# Task: Cross-Reference Synthesis

You are given three data files in the `workspace/` directory:

- `workspace/employees.csv` - Employee records with columns: id, name, department, role, hire_date
- `workspace/projects.csv` - Project assignments with columns: project_id, project_name, lead_id, budget, status
- `workspace/performance.csv` - Performance reviews with columns: employee_id, quarter, rating, notes

Your job is to **cross-reference** these three files and produce `workspace/merged_analysis.json`.

The JSON output must contain:

1. `"department_summary"` - An object keyed by department name, each containing:
   - `"headcount"` (integer): number of employees
   - `"avg_rating"` (number): average performance rating across all employees in that department (rounded to 1 decimal)
   - `"active_projects"` (integer): number of projects with status "active" led by employees in that department

2. `"top_performers"` - A list of employee names whose average performance rating is 4.5 or above, sorted alphabetically.

3. `"budget_by_status"` - An object with keys "active", "completed", "on_hold", each mapping to the total budget of projects with that status.

4. `"unreviewed_employees"` - A list of employee names who appear in employees.csv but have NO entries in performance.csv, sorted alphabetically.

## Output

- `workspace/merged_analysis.json` - valid JSON with the structure described above
