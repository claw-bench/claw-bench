# Task: Audit System Configuration for Compliance

Audit configuration files in `workspace/system_config/` against compliance rules in `workspace/compliance_rules.json`.

## Requirements

1. Read `workspace/compliance_rules.json` (20 compliance rules based on OWASP/SOC2 subset).
2. Read the 5 configuration files in `workspace/system_config/`.
3. Check each rule against the relevant configuration.
4. Write `workspace/compliance_report.json` with:
   - `audit_date`: ISO 8601 date
   - `total_rules`: number of rules checked
   - `passed`: count of passed rules
   - `failed`: count of failed rules
   - `results`: array of objects, each with:
     - `rule_id`: from the compliance rules
     - `rule_name`: human-readable rule name
     - `status`: `"pass"` or `"fail"`
     - `evidence`: string explaining what was checked and the result
     - `config_file`: which config file was checked

## Notes

- There are 20 rules across 5 config files.
- Some rules pass, some fail. Expect roughly 12 pass and 8 fail.
- Evidence must reference specific values from the config files.

## Output

Save results to `workspace/compliance_report.json`.
