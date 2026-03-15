#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys, json, re
from datetime import datetime, timedelta

ws = sys.argv[1]

with open(f"{ws}/fragments.json") as f:
    fragments = json.load(f)

with open(f"{ws}/anchors.json") as f:
    anchors = json.load(f)

# Build lookup
frag_map = {frag["id"]: frag for frag in fragments}
dates = {}

# Set anchor dates
for anchor in anchors:
    dates[anchor["event_id"]] = datetime.strptime(anchor["date"], "%Y-%m-%d")

# Resolve all dates iteratively
max_iterations = len(fragments)
for _ in range(max_iterations):
    all_resolved = True
    for frag in fragments:
        eid = frag["id"]
        if eid in dates:
            continue
        ref = frag["reference"]
        rel_to = frag["relative_to"]

        if rel_to not in dates:
            all_resolved = False
            continue

        base_date = dates[rel_to]

        if ref == "same day as " + rel_to:
            dates[eid] = base_date
            continue

        # Parse "N days/weeks before/after EVENT"
        m = re.match(r"(\d+)\s+(days?|weeks?)\s+(before|after)\s+\S+", ref)
        if m:
            n = int(m.group(1))
            unit = m.group(2)
            direction = m.group(3)

            if unit.startswith("week"):
                n *= 7

            if direction == "before":
                dates[eid] = base_date - timedelta(days=n)
            else:
                dates[eid] = base_date + timedelta(days=n)

    if all_resolved:
        break

# Build output
events_out = []
for frag in fragments:
    eid = frag["id"]
    events_out.append({
        "id": eid,
        "event": frag["event"],
        "date": dates[eid].strftime("%Y-%m-%d")
    })

# Sort chronologically, then by id
events_out.sort(key=lambda x: (x["date"], x["id"]))

all_dates = [dates[frag["id"]] for frag in fragments]
earliest = min(all_dates).strftime("%Y-%m-%d")
latest = max(all_dates).strftime("%Y-%m-%d")

result = {
    "events": events_out,
    "total_events": len(events_out),
    "earliest_date": earliest,
    "latest_date": latest
}

with open(f"{ws}/timeline.json", "w") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
PYEOF
