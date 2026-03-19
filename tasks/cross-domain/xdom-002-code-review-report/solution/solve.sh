#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
export WORKSPACE
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/review.json" <<'JSON'
{
  "file": "pull_request.py",
  "total_issues": 5,
  "issues": [
    {
      "line": 8,
      "severity": "critical",
      "category": "security",
      "description": "Hardcoded database credentials (DB_PASSWORD and DB_HOST) are stored directly in source code.",
      "suggestion": "Use environment variables or a secrets manager to store sensitive credentials."
    },
    {
      "line": 14,
      "severity": "critical",
      "category": "security",
      "description": "SQL injection vulnerability. User input is concatenated directly into SQL query string.",
      "suggestion": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE email = ?', (email,))"
    },
    {
      "line": 19,
      "severity": "high",
      "category": "bug",
      "description": "Discount calculation is incorrect. It returns the discount amount instead of the discounted price (price - discount).",
      "suggestion": "Change to: discounted = price - (price * discount_percent / 100); or discounted = price * (1 - discount_percent / 100)"
    },
    {
      "line": 25,
      "severity": "high",
      "category": "security",
      "description": "Unsafe deserialization using pickle.loads() on untrusted data can lead to arbitrary code execution.",
      "suggestion": "Use a safe serialization format like JSON, or validate/sanitize the input before deserializing."
    },
    {
      "line": 30,
      "severity": "medium",
      "category": "bug",
      "description": "Off-by-one error in loop. range(1, len(users)) skips the first user at index 0.",
      "suggestion": "Change to range(0, len(users)) or range(len(users)), or use 'for user in users:' directly."
    },
    {
      "line": 13,
      "severity": "low",
      "category": "style",
      "description": "Function name GetUserByEmail uses CamelCase instead of snake_case as per PEP 8.",
      "suggestion": "Rename to get_user_by_email."
    },
    {
      "line": 37,
      "severity": "low",
      "category": "style",
      "description": "Variable DisplayName uses CamelCase instead of snake_case as per PEP 8.",
      "suggestion": "Rename to display_name."
    }
  ]
}
JSON

cat > "$WORKSPACE/review_summary.md" <<'MARKDOWN'
# Code Review Summary: pull_request.py

## Overview

| Severity | Count |
|----------|-------|
| Critical | 2     |
| High     | 2     |
| Medium   | 1     |
| Low      | 2     |
| **Total**| **7** |

## Issues

### 1. [CRITICAL] Hardcoded Credentials (Line 8)
Database password and host are hardcoded in source code. This is a serious security risk if the code is committed to version control.

**Fix:** Use environment variables (`os.environ["DB_PASSWORD"]`) or a secrets manager.

### 2. [CRITICAL] SQL Injection (Line 14)
User-supplied email is concatenated directly into a SQL query, allowing SQL injection attacks.

**Fix:** Use parameterized queries with placeholders.

### 3. [HIGH] Incorrect Discount Calculation (Line 19)
The function returns the discount amount rather than the discounted price.

**Fix:** Return `price - (price * discount_percent / 100)`.

### 4. [HIGH] Unsafe Pickle Deserialization (Line 25)
`pickle.loads()` on untrusted input can lead to arbitrary code execution.

**Fix:** Use JSON or another safe serialization format.

### 5. [MEDIUM] Off-by-One Error (Line 30)
Loop starts at index 1, skipping the first user in the list.

**Fix:** Start the range at 0 or iterate directly over the list.

### 6. [LOW] CamelCase Function Name (Line 13)
`GetUserByEmail` violates PEP 8 naming conventions.

**Fix:** Rename to `get_user_by_email`.

### 7. [LOW] CamelCase Variable Name (Line 37)
`DisplayName` violates PEP 8 naming conventions.

**Fix:** Rename to `display_name`.

## Recommendation

**Request Changes** - The code contains critical security vulnerabilities (SQL injection, hardcoded credentials, unsafe deserialization) and logic bugs that must be addressed before merging.
MARKDOWN

echo "Solution written to $WORKSPACE/"
