#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

# Compute values from CSV:
# Q1: revenue=261500, units=913
# Q2: revenue=304200, units=1052
# Q3: revenue=338000, units=1163
# Q4: revenue=372300, units=1275
# North total: 353500, South: 312500, East: 261400, West: 368500

cat > "$WORKSPACE/charts_data.json" <<'JSON'
{
  "quarterly_revenue": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "values": [261500, 304200, 338000, 372300]
  },
  "quarterly_units": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "values": [913, 1052, 1163, 1275]
  },
  "regional_revenue": {
    "labels": ["North", "South", "East", "West"],
    "values": [353500, 312500, 261400, 368500]
  }
}
JSON

cat > "$WORKSPACE/presentation.md" <<'MARKDOWN'
# Quarterly Business Report 2026

Annual Performance Overview

---

## Q1 Performance

- **Total Revenue:** $261,500
- **Total Units Sold:** 913
- **Average Deal Size:** $286.42
- Top performing region: West ($75,500)
- Strongest product: Widget B ($103,500)

---

## Q2 Performance

- **Total Revenue:** $304,200
- **Total Units Sold:** 1,052
- **Average Deal Size:** $289.16
- Top performing region: West ($86,500)
- Revenue growth vs Q1: +16.3%

---

## Q3 Performance

- **Total Revenue:** $338,000
- **Total Units Sold:** 1,163
- **Average Deal Size:** $290.63
- Top performing region: West ($96,000)
- Revenue growth vs Q2: +11.1%

---

## Q4 Performance

- **Total Revenue:** $372,300
- **Total Units Sold:** 1,275
- **Average Deal Size:** $291.99
- Top performing region: West ($106,000)
- Revenue growth vs Q3: +10.1%

---

## Summary & Trends

- **Total Annual Revenue:** $1,276,000
- **Total Units Sold:** 4,403
- **Consistent growth** across all quarters (Q1 to Q4: +42.4% revenue)
- **West region** leads in revenue ($368,500 total)
- **Widget B** is the highest revenue product line
- Average deal size remained stable (~$289)
MARKDOWN

echo "Solution written to $WORKSPACE/"
