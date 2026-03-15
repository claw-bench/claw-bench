#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys, json, csv, os
from collections import defaultdict
ws = sys.argv[1]

# Load all CSV sources
rows = []
headers = None
sources_dir = f"{ws}/sources"
for fname in sorted(os.listdir(sources_dir)):
    if fname.endswith(".csv"):
        with open(f"{sources_dir}/{fname}") as f:
            reader = csv.DictReader(f)
            if headers is None:
                headers = reader.fieldnames[:]
            for row in reader:
                rows.append(dict(row))

# Load transforms
with open(f"{ws}/transforms.json") as f:
    transforms = json.load(f)

# Apply transforms
for t in transforms:
    if t["type"] == "filter":
        col = t["column"]
        op = t["operator"]
        val = t["value"]
        filtered = []
        for row in rows:
            rv = row[col]
            # Try numeric comparison
            try:
                rv_num = float(rv)
                val_num = float(val)
                if op == "eq" and rv_num == val_num: filtered.append(row)
                elif op == "neq" and rv_num != val_num: filtered.append(row)
                elif op == "gt" and rv_num > val_num: filtered.append(row)
                elif op == "lt" and rv_num < val_num: filtered.append(row)
                elif op == "gte" and rv_num >= val_num: filtered.append(row)
                elif op == "lte" and rv_num <= val_num: filtered.append(row)
            except (ValueError, TypeError):
                if op == "eq" and rv == val: filtered.append(row)
                elif op == "neq" and rv != val: filtered.append(row)
                elif op == "gt" and rv > val: filtered.append(row)
                elif op == "lt" and rv < val: filtered.append(row)
                elif op == "gte" and rv >= val: filtered.append(row)
                elif op == "lte" and rv <= val: filtered.append(row)
        rows = filtered

    elif t["type"] == "rename_column":
        old_name = t["old_name"]
        new_name = t["new_name"]
        for row in rows:
            if old_name in row:
                row[new_name] = row.pop(old_name)
        if old_name in headers:
            headers = [new_name if h == old_name else h for h in headers]

    elif t["type"] == "aggregate":
        group_col = t["group_by"]
        agg_col = t["column"]
        func = t["function"]
        groups = defaultdict(list)
        for row in rows:
            groups[row[group_col]].append(float(row[agg_col]))
        new_rows = []
        result_col = f"{func}_{agg_col}"
        for key in sorted(groups.keys()):
            vals = groups[key]
            if func == "sum":
                result = sum(vals)
            elif func == "count":
                result = len(vals)
            elif func == "mean":
                result = sum(vals) / len(vals)
            else:
                result = 0
            # Format as int if whole number
            if result == int(result):
                result = int(result)
            new_rows.append({group_col: key, result_col: str(result)})
        rows = new_rows
        headers = [group_col, result_col]

# Write output
with open(f"{ws}/output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
PYEOF
