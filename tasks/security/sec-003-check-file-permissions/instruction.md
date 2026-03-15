# Task: Check File Permissions for Security Issues

Analyze `workspace/permissions.txt` which contains simulated `ls -la` output and identify files with overly permissive or dangerous permissions.

## Requirements

1. Read `workspace/permissions.txt`.
2. Identify files with dangerous permissions:
   - World-writable files (o+w)
   - World-executable files that shouldn't be (o+x on config/data files)
   - Permission mode 777 (full access to everyone)
   - Sensitive files (keys, configs, passwords) readable by others
   - SUID/SGID bits on unusual files
3. Write `workspace/permission_audit.json` as a JSON array of objects, each with:
   - `file`: the filename
   - `permissions`: the permission string (e.g., `-rwxrwxrwx`)
   - `issue`: description of the security issue
   - `recommendation`: recommended permission (e.g., `644`, `600`)

## Notes

- There are 15 file entries; 6 have dangerous permissions.
- Focus on files that expose security risks. Standard permissions on normal files are fine.

## Output

Save results to `workspace/permission_audit.json`.
