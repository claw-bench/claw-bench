#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

# Extract the five due-diligence sections from the merger agreement.
# Implemented in Python to stay independent of the host bash version
# (associative arrays require bash 4+, unavailable on macOS bash 3.2) and
# to avoid a jq dependency.
python3 - <<'EOF'
import json
import os

ws = os.environ.get("WORKSPACE", "workspace")
input_file = os.path.join(ws, "merger_agreement.txt")
output_file = os.path.join(ws, "due_diligence.json")

section_map = {
    "CONDITIONS PRECEDENT": "conditions_precedent",
    "REPRESENTATIONS AND WARRANTIES": "representations_warranties",
    "INDEMNIFICATION TERMS": "indemnification_terms",
    "CLOSING TIMELINE": "closing_timeline",
    "MATERIAL ADVERSE CHANGE CLAUSE": "material_adverse_change_clause",
}

result = {key: "" for key in section_map.values()}
current = None

with open(input_file) as f:
    for line in f:
        stripped = line.strip()
        # Switch section on an exact recognized header match.
        if stripped in section_map:
            current = section_map[stripped]
            continue
        # Skip header underlines made solely of dashes.
        if stripped and set(stripped) == {"-"}:
            continue
        # Accumulate body text under the most recent recognized section.
        if current is not None:
            result[current] += line.rstrip("\n") + "\n"

with open(output_file, "w") as f:
    json.dump(result, f, indent=2)
EOF
