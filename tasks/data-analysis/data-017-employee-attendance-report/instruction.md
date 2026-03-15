# Task: Employee Attendance Analysis

You are given a file `workspace/attendance.csv` containing employee clock-in and clock-out records with columns: `employee`, `date`, `clock_in`, `clock_out`.

## Requirements

1. Read `workspace/attendance.csv`.
2. The standard work start time is **09:00**. Any clock-in strictly after 09:00 counts as a late arrival.
3. For each employee, compute:
   - `total_hours`: sum of hours worked across all days (clock_out minus clock_in, in decimal hours). Round to 2 decimal places.
   - `avg_hours_per_day`: total_hours divided by the number of days worked. Round to 2 decimal places.
   - `late_days`: number of days the employee clocked in after 09:00.
   - `late_dates`: list of date strings (YYYY-MM-DD) when the employee was late, sorted chronologically.
   - `punctuality_rate`: fraction of days the employee was on time (not late), as a decimal. Round to 2 decimal places.
4. Compute team-level statistics:
   - `team_avg_hours`: average of all employees' total_hours. Round to 2 decimal places.
   - `most_punctual`: name of the employee with the highest punctuality_rate. If tied, pick the one with the most total_hours.
   - `total_late_arrivals`: sum of all employees' late_days.
5. Produce `workspace/attendance_report.json` with the following structure:

```json
{
  "period": "2026-03-09 to 2026-03-13",
  "employees": [
    {
      "name": "<string>",
      "total_hours": <number>,
      "avg_hours_per_day": <number>,
      "late_days": <int>,
      "late_dates": ["<date>", ...],
      "punctuality_rate": <number>
    }
  ],
  "team_avg_hours": <number>,
  "most_punctual": "<string>",
  "total_late_arrivals": <int>
}
```

6. The `employees` list should be sorted alphabetically by name.

## Output

Save the JSON report to `workspace/attendance_report.json`.
