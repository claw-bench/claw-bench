#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
import re

ws = sys.argv[1]

with open(f"{ws}/form.html", "r") as f:
    html = f.read()

# Split into form blocks
form_pattern = r'<form\s+([^>]*)>(.*?)</form>'
form_matches = re.findall(form_pattern, html, re.DOTALL)

forms = []
for attrs_str, body in form_matches:
    # Extract action
    action_match = re.search(r'action="([^"]*)"', attrs_str)
    action = action_match.group(1) if action_match else ""

    # Extract method
    method_match = re.search(r'method="([^"]*)"', attrs_str)
    method = method_match.group(1).upper() if method_match else "GET"

    fields = []

    # Find input elements (exclude submit buttons)
    for m in re.finditer(r'<input\s+([^>]*)/?>', body):
        input_attrs = m.group(1)
        type_match = re.search(r'type="([^"]*)"', input_attrs)
        input_type = type_match.group(1) if type_match else "text"
        if input_type == "submit":
            continue
        name_match = re.search(r'name="([^"]*)"', input_attrs)
        if not name_match:
            continue
        required = "required" in input_attrs
        fields.append({
            "name": name_match.group(1),
            "type": input_type,
            "required": required
        })

    # Find select elements
    for m in re.finditer(r'<select\s+([^>]*)>', body):
        select_attrs = m.group(1)
        name_match = re.search(r'name="([^"]*)"', select_attrs)
        if not name_match:
            continue
        required = "required" in select_attrs
        fields.append({
            "name": name_match.group(1),
            "type": "select",
            "required": required
        })

    # Find textarea elements
    for m in re.finditer(r'<textarea\s+([^>]*)>', body):
        ta_attrs = m.group(1)
        name_match = re.search(r'name="([^"]*)"', ta_attrs)
        if not name_match:
            continue
        required = "required" in ta_attrs
        fields.append({
            "name": name_match.group(1),
            "type": "textarea",
            "required": required
        })

    forms.append({
        "action": action,
        "method": method,
        "fields": fields
    })

with open(f"{ws}/forms.json", "w") as f:
    json.dump(forms, f, indent=2)
PYEOF
