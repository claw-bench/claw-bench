# Task: Scan Git Diffs for Leaked Secrets

Analyze simulated git diff files in `workspace/git_diffs/` for leaked secrets.

## Requirements

1. Read all `.diff` files in `workspace/git_diffs/` (10 diff files simulating git commits).
2. Scan for leaked secrets including:
   - API keys (prefixed patterns like `AKIA`, `sk_` + `live_`, `ghp_`, etc.)
   - Passwords in configuration or code
   - Private keys (PEM format)
   - Database connection strings with embedded credentials
   - JWT secrets or signing keys
   - Cloud service credentials
3. Write `workspace/secrets_report.json` as a JSON array of objects, each with:
   - `commit`: the commit identifier (from the diff filename, e.g., `commit_03`)
   - `file`: the file path modified in the diff
   - `secret_type`: type of secret (e.g., `"aws_key"`, `"password"`, `"private_key"`, `"api_key"`, `"database_credential"`, `"jwt_secret"`)
   - `line_content`: the line containing the secret (trimmed)
   - `remediation`: recommended action

## Notes

- There are 10 diff files; 6 contain secrets (some may have multiple).
- 4 diffs are clean (code changes without secrets).
- Do not flag false positives (e.g., placeholder values, documentation examples).

## Output

Save results to `workspace/secrets_report.json`.
