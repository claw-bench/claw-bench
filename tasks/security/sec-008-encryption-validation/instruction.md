# Task: Validate Encryption Configuration

Analyze `workspace/crypto_config.json` for weak or insecure encryption settings.

## Requirements

1. Read `workspace/crypto_config.json` which contains encryption settings for various system components.
2. Identify security issues including:
   - Weak or deprecated algorithms (MD5, SHA1 for hashing; DES, 3DES, RC4 for encryption)
   - Insufficient key lengths (RSA < 2048 bits, AES < 128 bits)
   - Insecure TLS versions (< TLS 1.2)
   - Weak cipher suites
   - Missing or disabled certificate validation
3. Write `workspace/crypto_audit.json` as a JSON array of objects, each with:
   - `component`: the system component name
   - `setting`: the specific setting that is problematic
   - `current_value`: the current insecure value
   - `issue`: description of why it is insecure
   - `recommendation`: the secure alternative
   - `severity`: `"critical"`, `"high"`, `"medium"`, or `"low"`

## Notes

- The config has 8 components; 6 have at least one security issue (8 total issues).
- Some components have multiple issues.

## Output

Save results to `workspace/crypto_audit.json`.
