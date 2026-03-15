#!/usr/bin/env bash
# Oracle solution for eml-006-generate-summary
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/summary.json" <<'JSON'
{
  "key_points": [
    "Core banking mainframe systems are approaching end-of-life with vendor support ending September 30, 2026, six months ahead of the originally planned 18-month migration timeline",
    "February saw 14 unplanned downtime incidents costing over $18 million, with projected losses of $50-75 million over the next six months without intervention",
    "Three vendor proposals received: CloudFirst ($45M), Nexus hybrid approach ($38M recommended), and Meridian hardware refresh ($28M)",
    "Federal Banking Commission requires a detailed migration plan by March 20, 2026, with potential regulatory consequences for non-compliance",
    "CTO requests emergency board meeting by March 13 to approve $38M Nexus migration, 40 additional staff, and external audit oversight"
  ],
  "action_required": true,
  "urgency": "high"
}
JSON

echo "Solution written to $WORKSPACE/summary.json"
