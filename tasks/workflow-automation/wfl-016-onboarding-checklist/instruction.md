# Task: Process Employee Onboarding Checklist

You are given a new hire information file at `workspace/new_hire.json` and a department equipment template at `workspace/templates/equipment_by_dept.json`. Process the onboarding request and generate three output files.

## Requirements

1. Read `workspace/new_hire.json` for employee details.
2. Read `workspace/templates/equipment_by_dept.json` for equipment lists by department.
3. Produce the following three files:

### File 1: `workspace/account_setup.json`

Generate account setup details:
- `username`: derive from email (the part before `@`)
- `email`: the employee's email
- `groups`: a list containing the department name in lowercase and `"all-staff"`
- `access_level`: `"developer"` for Engineering, `"standard"` for all other departments

### File 2: `workspace/welcome_email.json`

Generate a welcome email draft:
- `to`: the employee's email
- `cc`: the manager's email
- `subject`: `"Welcome to the team, <first_name>!"` where `<first_name>` is the employee's first name
- `body`: a welcome message that mentions the employee's full name, department, start date, and manager's name

### File 3: `workspace/equipment_request.json`

Generate an equipment request:
- `employee`: the employee's full name
- `department`: the employee's department
- `items`: the list of equipment for their department from the template
- `delivery_date`: 3 calendar days before the start date (in `YYYY-MM-DD` format)

## Output

Save the three JSON files to the workspace directory as specified above.
