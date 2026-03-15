# Task: Security Audit with Remediation Patch

Audit Python application files for security issues and produce a fix patch.

## Input Files

- `workspace/app_code/auth.py` - Authentication module
- `workspace/app_code/api.py` - API endpoint handlers
- `workspace/app_code/utils.py` - Utility functions

## Objective

1. Audit all three files for security vulnerabilities.
2. Generate `workspace/audit.json` listing all found vulnerabilities.
3. Generate `workspace/fix.patch` as a unified diff that fixes the issues.

## Output: audit.json

```json
{
  "files_audited": 3,
  "total_vulnerabilities": 4,
  "vulnerabilities": [
    {
      "file": "auth.py",
      "line": 10,
      "severity": "critical",
      "cwe": "CWE-XXX",
      "title": "Short title",
      "description": "What the issue is",
      "fix": "How to fix it"
    }
  ]
}
```

- `severity` must be one of: "low", "medium", "high", "critical"
- `cwe` should reference a CWE ID if applicable

## Output: fix.patch

A unified diff format patch file. Must be a valid patch that could be applied with `patch -p0` or `git apply`.
