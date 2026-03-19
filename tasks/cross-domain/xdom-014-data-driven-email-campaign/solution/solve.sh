#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
export WORKSPACE

python - "$WORKSPACE" << 'PYTHON_EOF'
import csv
import json
import os
import re
import sys

workspace = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("WORKSPACE", ".")

# -- helpers to parse a minimal TOML (rules.toml) without third-party libs --
def parse_toml_minimal(path):
    """Bare-bones TOML parser sufficient for rules.toml."""
    import re as _re
    data = {}
    current = data
    stack = [data]
    keys_stack = []
    with open(path) as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            header = _re.match(r'^\[([^\]]+)\]$', line)
            if header:
                parts = header.group(1).split(".")
                current = data
                for p in parts:
                    current = current.setdefault(p, {})
                continue
            m = _re.match(r'^(\w+)\s*=\s*(.+)$', line)
            if m:
                key, val = m.group(1), m.group(2).strip()
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                elif val == "true":
                    val = True
                elif val == "false":
                    val = False
                else:
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                current[key] = val
    return data

# Read rules
rules = parse_toml_minimal(os.path.join(workspace, "rules.toml"))
campaign = rules.get("campaign", {})
segments_cfg = rules.get("segments", {})

# Read customers
customers = []
with open(os.path.join(workspace, "customers.csv")) as f:
    reader = csv.DictReader(f)
    for row in reader:
        customers.append(row)

# Read templates
templates = {}
tmpl_dir = os.path.join(workspace, "templates")
for fname in os.listdir(tmpl_dir):
    if fname.endswith(".html"):
        with open(os.path.join(tmpl_dir, fname)) as f:
            templates[fname] = f.read()

# Filter and process
output_dir = os.path.join(workspace, "output")
os.makedirs(output_dir, exist_ok=True)

segment_counts = {}
ab_dist = {}
eligible = []
excluded = 0

for cust in customers:
    # Check opted_in
    if cust["opted_in"].strip().lower() != "true":
        excluded += 1
        continue

    seg_name = cust["segment"].strip()
    seg_cfg = segments_cfg.get(seg_name)
    if not seg_cfg:
        excluded += 1
        continue

    # Segment-specific eligibility
    ok = True
    if "min_lifetime_value" in seg_cfg:
        if float(cust["lifetime_value"]) < seg_cfg["min_lifetime_value"]:
            ok = False
    if "min_purchase_count" in seg_cfg:
        if int(cust["purchase_count"]) < seg_cfg["min_purchase_count"]:
            ok = False
    if "max_purchase_count" in seg_cfg:
        if int(cust["purchase_count"]) > seg_cfg["max_purchase_count"]:
            ok = False
    if "last_purchase_before" in seg_cfg:
        if cust["last_purchase_date"] >= seg_cfg["last_purchase_before"]:
            ok = False

    if not ok:
        excluded += 1
        continue

    eligible.append((cust, seg_name, seg_cfg))

for cust, seg_name, seg_cfg in eligible:
    seg_counts = segment_counts.setdefault(seg_name, {"count": 0, "template": seg_cfg["template"], "ab_test": seg_cfg.get("ab_test", False)})
    seg_counts["count"] += 1

    # Determine variant
    cid = int(cust["customer_id"])
    is_ab = seg_cfg.get("ab_test", False)
    if is_ab:
        variant = "a" if cid % 2 == 0 else "b"
        ab_seg = ab_dist.setdefault(seg_name, {"variant_a": 0, "variant_b": 0})
        ab_seg[f"variant_{variant}"] += 1
        subject_line = seg_cfg.get(f"subject_{variant}", seg_cfg.get("subject_a", ""))
    else:
        subject_line = seg_cfg.get("subject_a", "")

    # Build variables dict
    variables = {}
    seg_vars = seg_cfg.get("variables", {})
    variables.update(seg_vars)
    variables["first_name"] = cust["first_name"]
    variables["last_name"] = cust["last_name"]
    variables["email"] = cust["email"]
    variables["purchase_count"] = cust["purchase_count"]
    variables["preferred_category"] = cust["preferred_category"]
    variables["last_purchase_date"] = cust["last_purchase_date"]
    variables["lifetime_value"] = cust["lifetime_value"]
    variables["customer_id"] = cust["customer_id"]
    variables["from_name"] = campaign.get("from_name", "Acme Store")
    # Substitute subject line variables first
    for k, v in variables.items():
        subject_line = subject_line.replace("{{" + k + "}}", str(v))
    variables["subject_line"] = subject_line

    # Render template
    tmpl = templates[seg_cfg["template"]]
    rendered = tmpl
    for k, v in variables.items():
        rendered = rendered.replace("{{" + k + "}}", str(v))

    out_path = os.path.join(output_dir, f"{cust['customer_id']}.html")
    with open(out_path, "w") as f:
        f.write(rendered)

# Campaign summary
summary = {
    "total_customers": len(customers),
    "eligible_customers": len(eligible),
    "excluded_customers": excluded,
    "segments": segment_counts,
    "ab_test_distribution": ab_dist,
    "emails_generated": len(eligible),
}

with open(os.path.join(workspace, "output", "campaign_summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print(f"Generated {len(eligible)} emails, excluded {excluded} customers")
PYTHON_EOF
