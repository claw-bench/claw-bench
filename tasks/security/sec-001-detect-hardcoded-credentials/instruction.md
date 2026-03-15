# Task: Detect Hardcoded Credentials in Source Code

Scan the Python source files in `workspace/source_code/` for hardcoded credentials such as passwords, API keys, and tokens.

## Requirements

1. Examine all `.py` files in `workspace/source_code/`.
2. Identify hardcoded credentials including:
   - Passwords assigned to variables
   - API keys (strings that look like API keys)
   - Authentication tokens
3. Write findings to `workspace/findings.json` as a JSON array of objects, each with:
   - `file`: filename (e.g., `config.py`)
   - `line`: line number (integer)
   - `type`: one of `"password"`, `"api_key"`, or `"token"`
   - `severity`: one of `"high"`, `"medium"`, `"low"`
   - `evidence`: the offending line content (trimmed)

## Notes

- There are exactly 5 credential leaks across the 3 files.
- Passwords and tokens should be rated `"high"` severity. API keys should be rated `"high"` severity.
- Do not flag comments, documentation strings, or placeholder values like `"changeme"` or `"TODO"`.

## Output

Save results to `workspace/findings.json`.
