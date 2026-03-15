# Security Auditing Skill

## Overview
This skill provides guidance on security analysis including credential detection,
OWASP vulnerability patterns, dependency scanning, and threat modeling.

## Credential Pattern Detection

### Common Secret Patterns
Use regex to scan for accidentally committed secrets:

```python
import re

SECRET_PATTERNS = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"(?i)aws_secret_access_key\s*[=:]\s*\S{40}",
    "Generic API Key": r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?\S{20,}",
    "Generic Secret": r"(?i)(secret|password|passwd|token)\s*[=:]\s*['\"]?\S{8,}",
    "Private Key": r"-----BEGIN\s+(RSA|DSA|EC|OPENSSH)?\s*PRIVATE KEY-----",
    "GitHub Token": r"gh[pousr]_[A-Za-z0-9_]{36,}",
    "Slack Token": r"xox[baprs]-[A-Za-z0-9-]+",
    "JWT": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    "Basic Auth URL": r"https?://[^:\s]+:[^@\s]+@\S+",
}

def scan_for_secrets(text):
    """Scan text for potential secrets and credentials."""
    findings = []
    for name, pattern in SECRET_PATTERNS.items():
        for match in re.finditer(pattern, text):
            findings.append({
                "type": name,
                "match": match.group()[:20] + "...",  # truncate for safety
                "position": match.start(),
            })
    return findings
```

### File-Level Scanning Strategy
1. Identify candidate files: `.env`, config files, source code, scripts.
2. Skip binary files and large generated files (node_modules, vendor).
3. Scan line by line, recording file path and line number.
4. Classify findings by severity (private keys > API tokens > passwords).
5. Check `.gitignore` to verify sensitive files are excluded from version control.

### Reducing False Positives
- Ignore lines that are clearly comments or documentation examples.
- Check for placeholder values ("YOUR_KEY_HERE", "xxx", "changeme").
- Verify entropy of the matched string; low-entropy matches are likely false positives.

## OWASP Top 10 Patterns

### Injection (SQL, Command, Template)
- Look for string concatenation or f-strings in query construction.
- Verify use of parameterized queries or ORM methods.
- Check for `os.system()`, `subprocess.call(shell=True)`, and `eval()`.

```python
# VULNERABLE: string formatting in SQL
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# SAFE: parameterized query
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
```

### Broken Authentication
- Check for hardcoded credentials in source code.
- Verify password hashing uses bcrypt, scrypt, or argon2 (not MD5/SHA1).
- Look for missing rate limiting on login endpoints.

### Sensitive Data Exposure
- Verify TLS is enforced (no plain HTTP for sensitive data).
- Check that logs do not contain passwords, tokens, or PII.
- Ensure error messages do not leak stack traces or internal paths.

### Security Misconfiguration
- Debug mode enabled in production settings.
- Default credentials left unchanged.
- Unnecessary services or ports exposed.
- Directory listing enabled on web servers.

### Cross-Site Scripting (XSS)
- User input rendered without escaping in HTML templates.
- Look for `| safe` filters or `dangerouslySetInnerHTML`.
- Verify Content-Security-Policy headers are set.

## Dependency Vulnerability Scanning

### Approach
1. Identify dependency manifests (requirements.txt, package.json, Gemfile, go.mod).
2. Parse each dependency with its pinned version.
3. Cross-reference against known vulnerability databases.
4. Classify by severity (Critical, High, Medium, Low).
5. Recommend upgrade paths for vulnerable packages.

```python
import re

def parse_requirements(filepath):
    """Parse Python requirements.txt into package-version pairs."""
    deps = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r"^([A-Za-z0-9_.-]+)\s*([=<>!~]+)\s*(.+)", line)
            if match:
                deps.append({
                    "package": match.group(1),
                    "constraint": match.group(2),
                    "version": match.group(3),
                })
    return deps
```

### Version Analysis
- Check for pinned versions that are significantly outdated.
- Flag packages with known CVEs matching the installed version range.
- Identify transitive dependencies that may introduce hidden risks.

## STRIDE Threat Modeling

### The STRIDE Categories
- **Spoofing**: Can an attacker impersonate a user or system?
- **Tampering**: Can data be modified without detection?
- **Repudiation**: Can actions be denied due to lack of logging?
- **Information Disclosure**: Can sensitive data be accessed by unauthorized parties?
- **Denial of Service**: Can the system be made unavailable?
- **Elevation of Privilege**: Can a user gain unauthorized higher-level access?

### Modeling Process
1. **Decompose the system**: Identify entry points, trust boundaries, data flows.
2. **Identify threats**: Apply each STRIDE category to every component and flow.
3. **Assess risk**: Rate each threat by likelihood and impact.
4. **Plan mitigations**: Map each threat to a countermeasure.
5. **Validate**: Verify mitigations are implemented and effective.

### Data Flow Analysis
```
[External User] --HTTPS--> [Web Server] --SQL--> [Database]
                                |
                                +--gRPC--> [Internal Service]
```
At each boundary crossing, ask:
- Is the channel authenticated and encrypted?
- Is input validated on the receiving side?
- Are operations logged for audit?

## Audit Reporting

### Structure
- **Executive summary**: High-level risk posture in 2-3 sentences.
- **Findings table**: Each finding with severity, location, description, remediation.
- **Risk matrix**: Map findings to likelihood vs. impact grid.
- **Recommendations**: Prioritized list of actions ordered by risk reduction.

### Severity Classification
- **Critical**: Exploitable remotely, leads to full system compromise.
- **High**: Significant data exposure or privilege escalation.
- **Medium**: Requires specific conditions or limited impact.
- **Low**: Informational, best-practice deviation.

## Best Practices
- Run secret scanning as a pre-commit hook to prevent accidental commits.
- Audit dependencies on every build, not just periodically.
- Apply the principle of least privilege to all service accounts and roles.
- Log security-relevant events with sufficient detail for forensic analysis.
- Rotate secrets regularly and use short-lived tokens where possible.
- Never trust client-side validation alone; always validate server-side.
