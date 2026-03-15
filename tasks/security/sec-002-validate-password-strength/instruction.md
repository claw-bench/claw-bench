# Task: Validate Password Strength

Check passwords in `workspace/passwords.txt` against the organization's security policy.

## Security Policy

A password is **strong** if it meets ALL of the following:
1. Minimum 12 characters long
2. Contains at least one uppercase letter (A-Z)
3. Contains at least one lowercase letter (a-z)
4. Contains at least one digit (0-9)
5. Contains at least one special character (`!@#$%^&*()-_=+[]{}|;:',.<>?/~`)

A password that fails any rule is **weak**.

## Requirements

1. Read `workspace/passwords.txt` (one password per line).
2. Evaluate each password against all 5 rules.
3. Write `workspace/results.json` as a JSON array of objects, each with:
   - `password`: the password string
   - `status`: `"pass"` or `"fail"`
   - `reasons`: array of strings describing which rules failed (empty if pass)

## Notes

- There are 10 passwords. 6 are weak, 4 are strong.
- Reason strings should clearly reference the failing rule (e.g., `"too short"`, `"missing uppercase"`, `"missing digit"`, `"missing special character"`, `"missing lowercase"`).

## Output

Save results to `workspace/results.json`.
