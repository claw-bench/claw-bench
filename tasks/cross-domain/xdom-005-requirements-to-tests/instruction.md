# Task: Requirements to Tests

You have software requirements in `workspace/requirements.md` describing a user authentication system. Generate a test plan and test stubs.

## Objective

1. Read `workspace/requirements.md` (8 requirements for a user auth system).
2. Generate `workspace/test_plan.json` mapping requirements to test cases.
3. Generate `workspace/test_stubs.py` with Python test functions (using pytest style).

## Output: test_plan.json

```json
{
  "project": "User Authentication System",
  "total_requirements": 8,
  "test_cases": [
    {
      "requirement_id": "REQ-001",
      "requirement_summary": "Brief summary",
      "test_functions": ["test_function_name_1", "test_function_name_2"],
      "priority": "high"
    }
  ]
}
```

- Every requirement (REQ-001 through REQ-008) must have at least one test case.
- `priority` must be one of: "critical", "high", "medium", "low"

## Output: test_stubs.py

- Must be valid Python (parseable by `ast.parse`).
- Each test function must start with `test_`.
- Each test function must contain at least one `assert` statement.
- Functions referenced in test_plan.json must exist in test_stubs.py.
- Include docstrings describing what each test verifies.
