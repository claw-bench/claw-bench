# Task: Config File Audit

You are given three server configuration files in `workspace/server_configs/`:
- `nginx.conf` - Nginx web server configuration
- `ssh_config` - SSH daemon configuration (sshd_config format)
- `my.cnf` - MySQL server configuration

Each file contains intentional security weaknesses that need to be identified.

## Requirements

1. Read all three configuration files.
2. Audit each file for security issues.
3. Generate a JSON report with the following structure:

```json
{
  "total_issues": <count>,
  "files": {
    "nginx.conf": {
      "issues": [
        {
          "line_hint": "<relevant config directive>",
          "severity": "high|medium|low",
          "description": "<what the issue is>",
          "recommendation": "<how to fix it>"
        },
        ...
      ]
    },
    "ssh_config": {
      "issues": [...]
    },
    "my.cnf": {
      "issues": [...]
    }
  },
  "summary": {
    "high": <count>,
    "medium": <count>,
    "low": <count>
  }
}
```

## Known Security Issues to Look For

### nginx.conf
- Server tokens revealing version information
- Missing security headers
- Autoindex enabled (directory listing)
- SSL using weak protocols

### ssh_config
- Root login permitted
- Password authentication enabled
- Empty passwords allowed
- Weak or missing protocol version
- No login grace time limit

### my.cnf
- Binding to all interfaces (0.0.0.0) instead of localhost
- Local infile enabled
- Symbolic links enabled
- No password validation

## Output

Save the report to `workspace/audit_report.json`.
