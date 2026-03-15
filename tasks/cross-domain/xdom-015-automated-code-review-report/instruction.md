# Automated Code Review Report

You are a senior software engineer performing an automated code review. Given a git diff file, a coding standards document, and a project configuration, produce a comprehensive code review report.

## Input Files

- `changes.diff` — A unified diff file containing changes across multiple files in a Python web application
- `standards.md` — The team's coding standards document covering naming conventions, error handling, security, testing, documentation, and performance
- `project.toml` — Project configuration specifying language, framework, required test coverage, max complexity, and lint rules

## Requirements

### Step 1: Diff Analysis
- Parse the unified diff to identify all changed files and the specific lines modified
- Understand the context and purpose of each change

### Step 2: Standards Compliance Check
- Compare each change against the coding standards in `standards.md`
- Check for violations in: naming conventions, error handling, security practices, documentation, performance, and style

### Step 3: Project Rules Check
- Apply project-specific rules from `project.toml` (e.g., max function length, required docstrings, banned imports)

### Step 4: Generate Review Report
Produce `review.json` in the workspace with this structure:

```json
{
  "review_id": "REV-2026-0312",
  "diff_file": "changes.diff",
  "files_reviewed": [
    {
      "file": "path/to/file.py",
      "lines_added": 25,
      "lines_removed": 10,
      "status": "modified"
    }
  ],
  "issues": [
    {
      "id": "ISS-001",
      "file": "path/to/file.py",
      "line": 42,
      "severity": "error|warning|info",
      "category": "security|naming|error-handling|documentation|performance|style|testing",
      "rule": "rule identifier from standards",
      "description": "what the issue is",
      "suggestion": "how to fix it",
      "code_snippet": "the problematic line or block"
    }
  ],
  "summary": {
    "total_files": 4,
    "total_issues": 12,
    "by_severity": {
      "error": 3,
      "warning": 5,
      "info": 4
    },
    "by_category": {
      "security": 2,
      "naming": 3
    }
  },
  "overall_score": 65,
  "recommendation": "request_changes|approve_with_comments|approve"
}
```

### Constraints
- Every issue must reference a specific file and line number from the diff
- Issue IDs must be sequential (ISS-001, ISS-002, ...)
- `overall_score` is 0-100 where 100 is perfect; deduct points per issue (error=-10, warning=-5, info=-2)
- Start from 100 and deduct; minimum score is 0
- `recommendation` must be: "request_changes" if any error-severity issues exist, "approve_with_comments" if only warnings/info, "approve" if score >= 90 and no errors/warnings
- The `summary.total_issues` must equal the length of the `issues` array
- `by_severity` and `by_category` counts must be consistent with the issues list
- Identify at least 8 issues across the diff (the diff is intentionally written with multiple problems)
