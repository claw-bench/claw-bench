# Access Control Review Skill

## Overview
This skill covers reviewing, auditing, and configuring access control policies
across files, applications, and infrastructure to enforce least-privilege security.

## File System Permissions

### Reviewing POSIX Permissions
```bash
# List permissions with ownership details
ls -la /etc/config/
# Find world-writable files (potential risk)
find /srv -perm -o+w -type f
```

### Fixing Overly Broad Permissions
```bash
# Remove world-read/write; keep owner and group access
chmod 640 /etc/app/secrets.conf
chown root:app-group /etc/app/secrets.conf
```

## Role-Based Access Control (RBAC)

### Key Principles
- **Least privilege**: Grant only the permissions required for each role.
- **Separation of duties**: No single role should control an entire critical workflow.
- **Role hierarchy**: Inherit permissions upward; override only when necessary.

### Auditing an RBAC Policy
```python
def audit_roles(policy: dict) -> list[str]:
    """Flag roles with overly broad permissions."""
    findings = []
    for role, perms in policy.items():
        if "*" in perms or "admin:*" in perms:
            findings.append(f"Role '{role}' has wildcard permissions")
        if len(perms) > 20:
            findings.append(f"Role '{role}' has {len(perms)} permissions; review for over-provisioning")
    return findings
```

## API and Cloud IAM Checks

- Review API keys and tokens for expiration and scope limits.
- Audit cloud IAM policies for `Action: *` or `Resource: *` statements.
- Verify service accounts use short-lived credentials where possible.
- Check that MFA is enforced for privileged accounts.

## Tips
- Automate periodic access reviews with scripts that diff current vs. baseline policies.
- Log and alert on privilege escalation events.
- Rotate secrets on a fixed schedule and immediately after personnel changes.
- Test access controls by attempting actions as each role (positive and negative tests).
- Document every exception to the least-privilege policy with a justification and expiry date.
