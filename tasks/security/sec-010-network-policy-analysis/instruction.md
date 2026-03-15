# Task: Analyze Firewall Rules for Security Issues

Analyze `workspace/firewall_rules.json` for redundant, conflicting, and overly permissive rules.

## Requirements

1. Read `workspace/firewall_rules.json` containing 20 firewall rules.
2. Identify:
   - **Conflicts**: Rules where one allows and another denies the same traffic
   - **Redundancies**: Rules fully covered by a broader rule
   - **Overly permissive**: Rules allowing too-wide access (e.g., 0.0.0.0/0 to sensitive ports)
   - **Shadowed rules**: Rules that can never match because a prior rule catches all the traffic
3. Write `workspace/policy_analysis.json` with:
   - `issues`: array of objects, each with `rule_ids` (array), `type` (conflict/redundant/overly_permissive/shadowed), `description`, `severity`
   - `optimized_rules`: a reduced ruleset that achieves the same intended security posture with fewer rules
   - `summary`: object with `total_rules`, `issues_found`, `optimized_count`

## Notes

- The ruleset has at least 5 distinct issues.
- The optimized ruleset should have fewer rules than the original 20.

## Output

Save results to `workspace/policy_analysis.json`.
