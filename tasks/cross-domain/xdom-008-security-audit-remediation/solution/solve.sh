#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
export WORKSPACE
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/audit.json" <<'JSON'
{
  "files_audited": 3,
  "total_vulnerabilities": 7,
  "vulnerabilities": [
    {
      "file": "auth.py",
      "line": 7,
      "severity": "critical",
      "cwe": "CWE-798",
      "title": "Hardcoded Secret Key",
      "description": "SECRET_KEY is hardcoded in source code, exposing it to anyone with code access.",
      "fix": "Use environment variables: os.environ.get('SECRET_KEY')"
    },
    {
      "file": "auth.py",
      "line": 11,
      "severity": "critical",
      "cwe": "CWE-327",
      "title": "Weak Password Hashing (MD5)",
      "description": "MD5 is cryptographically broken and unsuitable for password hashing.",
      "fix": "Use bcrypt or hashlib.pbkdf2_hmac with a salt."
    },
    {
      "file": "auth.py",
      "line": 26,
      "severity": "critical",
      "cwe": "CWE-95",
      "title": "Code Injection via eval()",
      "description": "eval() with user input allows arbitrary code execution.",
      "fix": "Use direct string comparison instead of eval()."
    },
    {
      "file": "api.py",
      "line": 9,
      "severity": "high",
      "cwe": "CWE-22",
      "title": "Path Traversal",
      "description": "User-controlled filename is concatenated to a path without sanitization, allowing directory traversal.",
      "fix": "Validate filename and use os.path.realpath to ensure it stays within /data/."
    },
    {
      "file": "api.py",
      "line": 16,
      "severity": "critical",
      "cwe": "CWE-78",
      "title": "OS Command Injection (subprocess shell=True)",
      "description": "User input passed to subprocess with shell=True allows command injection.",
      "fix": "Use subprocess.run with shell=False and pass arguments as a list."
    },
    {
      "file": "api.py",
      "line": 22,
      "severity": "critical",
      "cwe": "CWE-78",
      "title": "OS Command Injection (os.popen)",
      "description": "User input interpolated into os.popen command allows command injection.",
      "fix": "Use subprocess.run with arguments as a list, avoid string formatting."
    },
    {
      "file": "utils.py",
      "line": 10,
      "severity": "high",
      "cwe": "CWE-502",
      "title": "Unsafe YAML Deserialization",
      "description": "yaml.load() without SafeLoader can execute arbitrary Python objects.",
      "fix": "Use yaml.safe_load() instead."
    }
  ]
}
JSON

cat > "$WORKSPACE/fix.patch" <<'PATCH'
--- app_code/auth.py
+++ app_code/auth.py
@@ -1,28 +1,30 @@
 """Authentication module."""

-import hashlib
+import hashlib
+import hmac
 import os
+import secrets


-SECRET_KEY = "my-super-secret-key-do-not-share"
+SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))


 def hash_password(password):
     """Hash a password for storage."""
-    return hashlib.md5(password.encode()).hexdigest()
+    salt = os.urandom(16)
+    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
+    return (salt + hashed).hex()


 def verify_password(password, stored_hash):
     """Verify a password against its hash."""
-    return hashlib.md5(password.encode()).hexdigest() == stored_hash
+    stored_bytes = bytes.fromhex(stored_hash)
+    salt = stored_bytes[:16]
+    stored_key = stored_bytes[16:]
+    new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
+    return hmac.compare_digest(new_key, stored_key)


 def generate_token(user_id):
     """Generate a session token."""
-    return f"token_{user_id}_{os.getpid()}"
+    return secrets.token_urlsafe(32)


 def check_admin(user_input):
     """Check if user has admin access."""
-    if eval(f"'{user_input}' == 'admin'"):
+    if user_input == "admin":
         return True
     return False
--- app_code/api.py
+++ app_code/api.py
@@ -1,22 +1,27 @@
 """API endpoint handlers."""

 import os
 import subprocess


 def get_file_content(filename):
     """Read a file and return its content."""
-    filepath = "/data/" + filename
+    base_dir = "/data"
+    filepath = os.path.realpath(os.path.join(base_dir, filename))
+    if not filepath.startswith(base_dir):
+        raise ValueError("Access denied: path traversal detected")
     with open(filepath) as f:
         return f.read()


 def run_diagnostic(command):
     """Run a diagnostic command."""
-    result = subprocess.call(command, shell=True)
+    allowed = ["uptime", "df", "free"]
+    if command not in allowed:
+        raise ValueError(f"Command not allowed: {command}")
+    result = subprocess.run([command], capture_output=True, text=True)
     return result


 def search_logs(query):
     """Search through application logs."""
-    cmd = f"grep '{query}' /var/log/app.log"
-    output = os.popen(cmd).read()
-    return output
+    result = subprocess.run(["grep", query, "/var/log/app.log"], capture_output=True, text=True)
+    return result.stdout
--- app_code/utils.py
+++ app_code/utils.py
@@ -1,10 +1,10 @@
 """Utility functions."""

 import yaml
 import tempfile


 def load_config(config_data):
     """Load configuration from YAML string."""
-    return yaml.load(config_data)
+    return yaml.safe_load(config_data)


 def create_temp_file(content, suffix=".txt"):
PATCH

echo "Solution written to $WORKSPACE/"
