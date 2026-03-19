#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
export WORKSPACE

python - "$WORKSPACE" << 'PYTHON_EOF'
import json
import os
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("WORKSPACE", ".")

issues = [
    {
        "id": "ISS-001",
        "file": "app/auth/handlers.py",
        "line": 7,
        "severity": "error",
        "category": "security",
        "rule": "SEC-02",
        "description": "Hardcoded secret key 'hardcoded_jwt_secret_key_12345' found in source code",
        "suggestion": "Move the secret to an environment variable or a secrets manager and reference it via os.environ['JWT_SECRET']",
        "code_snippet": 'SECRET = "hardcoded_jwt_secret_key_12345"'
    },
    {
        "id": "ISS-002",
        "file": "app/auth/handlers.py",
        "line": 21,
        "severity": "error",
        "category": "security",
        "rule": "SEC-01",
        "description": "SQL injection vulnerability: user input directly interpolated into SQL query string",
        "suggestion": "Use parameterized query: db.engine.execute('SELECT * FROM users WHERE username = %s', (username,))",
        "code_snippet": "query = f\"SELECT * FROM users WHERE username = '{username}'\""
    },
    {
        "id": "ISS-003",
        "file": "app/auth/handlers.py",
        "line": 22,
        "severity": "error",
        "category": "security",
        "rule": "SEC-06",
        "description": "MD5 is cryptographically broken and must not be used for password hashing",
        "suggestion": "Use bcrypt or argon2 for password hashing: from werkzeug.security import check_password_hash",
        "code_snippet": "password_hash = hashlib.md5(password.encode()).hexdigest()"
    },
    {
        "id": "ISS-004",
        "file": "app/auth/handlers.py",
        "line": 18,
        "severity": "warning",
        "category": "error-handling",
        "rule": "ERR-03",
        "description": "Missing HTTP status code on error response for missing credentials",
        "suggestion": "Add 400 status code: return jsonify({'error': 'Missing credentials'}), 400",
        "code_snippet": "return jsonify({'error': 'Missing credentials'})"
    },
    {
        "id": "ISS-005",
        "file": "app/auth/handlers.py",
        "line": 33,
        "severity": "error",
        "category": "security",
        "rule": "SEC-04",
        "description": "subprocess called with shell=True allows shell injection attacks",
        "suggestion": "Use subprocess.run() with a list of arguments and shell=False",
        "code_snippet": "result = subprocess.shell(cmd, shell=True, capture_output=True)"
    },
    {
        "id": "ISS-006",
        "file": "app/auth/handlers.py",
        "line": 37,
        "severity": "error",
        "category": "security",
        "rule": "SEC-03",
        "description": "pickle.loads() on untrusted data can execute arbitrary code (deserialization attack)",
        "suggestion": "Use a safe serialization format like JSON instead of pickle",
        "code_snippet": "return pickle.loads(data)"
    },
    {
        "id": "ISS-007",
        "file": "app/auth/handlers.py",
        "line": 27,
        "severity": "warning",
        "category": "security",
        "rule": "SEC-09",
        "description": "User ID and admin status stored in unsigned cookies, allowing client-side tampering",
        "suggestion": "Use server-side sessions or signed/encrypted cookies for authentication data",
        "code_snippet": "resp.set_cookie('is_admin', str(user['is_admin']))"
    },
    {
        "id": "ISS-008",
        "file": "app/auth/handlers.py",
        "line": 39,
        "severity": "warning",
        "category": "security",
        "rule": "SEC-10",
        "description": "Admin check relies on client-provided cookie value, allowing privilege escalation",
        "suggestion": "Check admin status from the database/session, never from a client cookie",
        "code_snippet": 'if cookie_val == "True":'
    },
    {
        "id": "ISS-009",
        "file": "app/auth/handlers.py",
        "line": 32,
        "severity": "warning",
        "category": "naming",
        "rule": "NAM-01",
        "description": "Function name 'RunCommand' uses PascalCase instead of snake_case",
        "suggestion": "Rename to 'run_command'",
        "code_snippet": "def RunCommand(cmd):"
    },
    {
        "id": "ISS-010",
        "file": "app/models/user.py",
        "line": 12,
        "severity": "error",
        "category": "security",
        "rule": "SEC-07",
        "description": "SSN and credit card number stored as plain text without encryption",
        "suggestion": "Use encrypted columns or a vault service for PII data",
        "code_snippet": "SSN = db.Column(db.String(11))"
    },
    {
        "id": "ISS-011",
        "file": "app/models/user.py",
        "line": 16,
        "severity": "warning",
        "category": "naming",
        "rule": "NAM-01",
        "description": "Method name 'getData' uses camelCase instead of snake_case",
        "suggestion": "Rename to 'get_data' or 'to_dict'",
        "code_snippet": "def getData(self):"
    },
    {
        "id": "ISS-012",
        "file": "app/models/user.py",
        "line": 22,
        "severity": "warning",
        "category": "security",
        "rule": "SEC-07",
        "description": "password_hash, SSN, and credit card number exposed in getData() serialization method without filtering",
        "suggestion": "Exclude sensitive fields from serialization; create separate methods for internal vs external representations",
        "code_snippet": "d['password_hash'] = self.password_hash"
    },
    {
        "id": "ISS-013",
        "file": "app/models/user.py",
        "line": 10,
        "severity": "warning",
        "category": "error-handling",
        "rule": "ERR-01",
        "description": "Column nullable constraint removed from username, allowing null values",
        "suggestion": "Keep nullable=False to maintain data integrity: db.Column(db.String(80), unique=True, nullable=False)",
        "code_snippet": "username = db.Column(db.String(80), unique=True)"
    },
    {
        "id": "ISS-014",
        "file": "app/models/user.py",
        "line": 34,
        "severity": "warning",
        "category": "security",
        "rule": "SEC-06",
        "description": "Password check uses MD5 hash which is cryptographically insecure",
        "suggestion": "Use bcrypt or argon2 for password verification",
        "code_snippet": "return self.password_hash == hashlib.md5(pwd.encode()).hexdigest()"
    },
    {
        "id": "ISS-015",
        "file": "app/api/routes.py",
        "line": 24,
        "severity": "error",
        "category": "security",
        "rule": "SEC-01",
        "description": "SQL injection in search endpoint: user input directly interpolated into SQL query",
        "suggestion": "Use parameterized query or ORM filter: User.query.filter(User.username.like(f'%{name}%'))",
        "code_snippet": "q = f\"SELECT * FROM users WHERE username LIKE '%{name}%'\""
    },
    {
        "id": "ISS-016",
        "file": "app/api/routes.py",
        "line": 37,
        "severity": "error",
        "category": "security",
        "rule": "SEC-05",
        "description": "Path traversal vulnerability: filename from URL used directly in file path without validation",
        "suggestion": "Use werkzeug.utils.secure_filename() and validate the resolved path is within the upload directory",
        "code_snippet": "filepath = os.path.join('/var/uploads', filename)"
    },
    {
        "id": "ISS-017",
        "file": "app/api/routes.py",
        "line": 41,
        "severity": "warning",
        "category": "security",
        "rule": "SEC-07",
        "description": "Admin export endpoint exposes all user data including PII without access control or field filtering",
        "suggestion": "Add authentication/authorization check and filter sensitive fields from export",
        "code_snippet": "data = [u.getData() for u in users]"
    },
    {
        "id": "ISS-018",
        "file": "app/utils/helpers.py",
        "line": 5,
        "severity": "error",
        "category": "security",
        "rule": "SEC-02",
        "description": "Hardcoded password and database connection string with credentials in source code",
        "suggestion": "Use environment variables: os.environ['DB_PASSWORD']",
        "code_snippet": 'DB_PASSWORD = "postgres://admin:secretpass@db:5432/myapp"'
    },
    {
        "id": "ISS-019",
        "file": "app/utils/helpers.py",
        "line": 9,
        "severity": "error",
        "category": "security",
        "rule": "SEC-03",
        "description": "eval() used on input which allows arbitrary code execution",
        "suggestion": "Use ast.literal_eval() for safe expression parsing, or a proper parser for the expected input format",
        "code_snippet": "result = eval(x)"
    },
    {
        "id": "ISS-020",
        "file": "app/utils/helpers.py",
        "line": 12,
        "severity": "warning",
        "category": "error-handling",
        "rule": "ERR-04",
        "description": "File opened without context manager; resource leak if exception occurs",
        "suggestion": "Use 'with open(path, 'r') as f:' to ensure the file is properly closed",
        "code_snippet": "f = open(path, 'r')"
    },
    {
        "id": "ISS-021",
        "file": "app/utils/helpers.py",
        "line": 16,
        "severity": "warning",
        "category": "naming",
        "rule": "NAM-01",
        "description": "Function name 'Calculate_Total' uses mixed case instead of snake_case",
        "suggestion": "Rename to 'calculate_total'",
        "code_snippet": "def Calculate_Total(items):"
    },
    {
        "id": "ISS-022",
        "file": "app/utils/helpers.py",
        "line": 35,
        "severity": "warning",
        "category": "security",
        "rule": "SEC-08",
        "description": "SSL/TLS verification disabled with verify=False, allowing man-in-the-middle attacks",
        "suggestion": "Remove verify=False to use default certificate verification",
        "code_snippet": "resp = requests.get(url, verify=False)"
    },
    {
        "id": "ISS-023",
        "file": "app/utils/helpers.py",
        "line": 8,
        "severity": "info",
        "category": "documentation",
        "rule": "DOC-01",
        "description": "Function 'process_input' missing docstring",
        "suggestion": "Add a docstring explaining the function purpose, parameters, and return type",
        "code_snippet": "def process_input(x):"
    },
    {
        "id": "ISS-024",
        "file": "app/utils/helpers.py",
        "line": 1,
        "severity": "info",
        "category": "documentation",
        "rule": "DOC-02",
        "description": "Module app/utils/helpers.py missing module-level docstring",
        "suggestion": "Add a module docstring at the top of the file describing its purpose",
        "code_snippet": "import eval"
    },
    {
        "id": "ISS-025",
        "file": "app/utils/helpers.py",
        "line": 1,
        "severity": "info",
        "category": "style",
        "rule": "STY-04",
        "description": "'import eval' is not a valid Python module; likely an error or unused import",
        "suggestion": "Remove the invalid import statement",
        "code_snippet": "import eval"
    },
    {
        "id": "ISS-026",
        "file": "app/utils/helpers.py",
        "line": 30,
        "severity": "info",
        "category": "style",
        "rule": "ERR-05",
        "description": "Email validation is too simplistic; only checks for '@' character",
        "suggestion": "Use a proper email validation library or regex pattern",
        "code_snippet": 'if "@" in email:'
    },
]

# Calculate summary
by_severity = {}
by_category = {}
for iss in issues:
    by_severity[iss["severity"]] = by_severity.get(iss["severity"], 0) + 1
    by_category[iss["category"]] = by_category.get(iss["category"], 0) + 1

# Calculate score
score = 100
for iss in issues:
    if iss["severity"] == "error":
        score -= 10
    elif iss["severity"] == "warning":
        score -= 5
    else:
        score -= 2
score = max(0, score)

has_errors = by_severity.get("error", 0) > 0
has_warnings = by_severity.get("warning", 0) > 0

if has_errors:
    recommendation = "request_changes"
elif has_warnings:
    recommendation = "approve_with_comments"
elif score >= 90:
    recommendation = "approve"
else:
    recommendation = "approve_with_comments"

files_reviewed = [
    {"file": "app/auth/handlers.py", "lines_added": 28, "lines_removed": 7, "status": "modified"},
    {"file": "app/models/user.py", "lines_added": 24, "lines_removed": 9, "status": "modified"},
    {"file": "app/api/routes.py", "lines_added": 30, "lines_removed": 10, "status": "modified"},
    {"file": "app/utils/helpers.py", "lines_added": 38, "lines_removed": 0, "status": "added"},
]

review = {
    "review_id": "REV-2026-0312",
    "diff_file": "changes.diff",
    "files_reviewed": files_reviewed,
    "issues": issues,
    "summary": {
        "total_files": len(files_reviewed),
        "total_issues": len(issues),
        "by_severity": by_severity,
        "by_category": by_category,
    },
    "overall_score": score,
    "recommendation": recommendation,
}

out_path = os.path.join(workspace, "review.json")
with open(out_path, "w") as f:
    json.dump(review, f, indent=2)

print(f"Review complete: {len(issues)} issues found, score={score}, recommendation={recommendation}")
PYTHON_EOF
