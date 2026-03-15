# Task: Analyze Cookie Policy for Privacy Compliance

You are given `workspace/cookies.json` containing an array of cookie objects. Analyze them for privacy and security issues.

## Requirements

1. Read `workspace/cookies.json`. Each cookie has: `name`, `domain`, `path`, `expires`, `secure`, `httpOnly`, `sameSite`, `category`.
2. Produce `workspace/cookie_report.json` with:

### summary
- **total_cookies**: Total count
- **by_category**: Object mapping category to count (e.g., `{"essential": 3, "analytics": 2, ...}`)
- **third_party_count**: Count of cookies whose domain does NOT start with the primary domain "example.com" (i.e., domain is not "example.com" and does not end with ".example.com")
- **secure_count**: Count of cookies with `secure: true`
- **httponly_count**: Count of cookies with `httpOnly: true`

### privacy_score
An integer from 0-100 computed as:
- Start at 100
- Subtract 5 for each cookie missing the `secure` flag
- Subtract 5 for each cookie missing the `httpOnly` flag
- Subtract 3 for each third-party cookie
- Subtract 10 for each cookie in category "tracking"
- Minimum score is 0

### issues
A list of issue objects, each with:
- **cookie_name**: Name of the cookie
- **issue**: Description string. Identify these issues:
  - `"missing_secure_flag"` if `secure` is `false`
  - `"missing_httponly_flag"` if `httpOnly` is `false`
  - `"third_party_tracking"` if it is a third-party cookie AND category is `"tracking"` or `"analytics"`
  - `"no_samesite"` if `sameSite` is `"None"` or empty string

Sort issues by cookie_name, then by issue.

## Output

Save the result to `workspace/cookie_report.json`.
