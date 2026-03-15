# Task: Code Review Report

You have a Python file `workspace/pull_request.py` that represents code submitted in a pull request. Your job is to review it for issues and produce a structured report.

## Objective

1. Analyze `workspace/pull_request.py` for code quality issues.
2. Generate `workspace/review.json` with all identified issues.
3. Generate `workspace/review_summary.md` with a human-readable summary.

## Expected Issues

The file contains at least 5 intentional issues across these categories:
- **Style**: PEP 8 violations, naming conventions
- **Bug**: Logic errors, off-by-one errors, incorrect return values
- **Security**: SQL injection, hardcoded credentials, unsafe deserialization

## Output: review.json

```json
{
  "file": "pull_request.py",
  "total_issues": 5,
  "issues": [
    {
      "line": 10,
      "severity": "high",
      "category": "security",
      "description": "Description of the issue",
      "suggestion": "How to fix it"
    }
  ]
}
```

- `severity` must be one of: "low", "medium", "high", "critical"
- `category` must be one of: "style", "bug", "security", "performance"
- Each issue must have `line`, `severity`, `category`, `description`, and `suggestion`.

## Output: review_summary.md

A markdown document with:
- A summary section with total issues by severity
- A section for each issue with description and fix suggestion
- An overall recommendation (approve, request changes, or reject)
