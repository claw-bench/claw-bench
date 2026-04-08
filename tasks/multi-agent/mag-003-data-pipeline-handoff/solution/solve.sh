#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WS="$WORKSPACE"

mkdir -p "$WORKSPACE/pipeline"

# ── Stage 1: Data Cleaning ────────────────────────────────────

python3 << 'PYSTAGE1'
import csv, re, os
from datetime import datetime

ws = os.environ["WS"]

rows_in = 0
rows_out = 0
with open(f"{ws}/raw_data.csv") as fin, open(f"{ws}/pipeline/stage1_clean.csv", "w", newline="") as fout:
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, fieldnames=["date", "region", "product", "amount", "sales_rep"])
    writer.writeheader()
    for row in reader:
        rows_in += 1
        if not any(v.strip() for v in row.values() if v):
            continue
        date_str = (row.get("date") or "").strip()
        if not date_str:
            continue
        try:
            if "/" in date_str:
                d = datetime.strptime(date_str, "%m/%d/%Y")
            else:
                d = datetime.strptime(date_str, "%Y-%m-%d")
            date_str = d.strftime("%Y-%m-%d")
        except ValueError:
            continue
        amt = (row.get("amount") or "0").strip()
        amt = re.sub(r"[^\d.]", "", amt)
        amt = float(amt) if amt else 0.0
        region = (row.get("region") or "").strip() or "unknown"
        product = (row.get("product") or "").strip() or "unknown"
        sales_rep = (row.get("sales_rep") or "").strip() or "unknown"
        writer.writerow({"date": date_str, "region": region, "product": product, "amount": f"{amt:.2f}", "sales_rep": sales_rep})
        rows_out += 1

with open(f"{ws}/pipeline/stage1_log.md", "w") as f:
    f.write(f"""# Stage 1: Data Cleaning Agent Log

## Input
- Source file: raw_data.csv
- Rows read: {rows_in}

## Operations
- Removed rows with all empty fields
- Standardized dates from MM/DD/YYYY and YYYY-MM-DD to YYYY-MM-DD
- Removed currency symbols ($) from amounts, converted to float
- Filled missing region/product/sales_rep with "unknown"
- Skipped rows without valid dates

## Output
- Output file: pipeline/stage1_clean.csv
- Rows written: {rows_out}
- Rows dropped: {rows_in - rows_out}
""")
PYSTAGE1

# ── Stage 2: Feature Engineering ──────────────────────────────

python3 << 'PYSTAGE2'
import csv, os
from datetime import datetime

ws = os.environ["WS"]

rows = 0
with open(f"{ws}/pipeline/stage1_clean.csv") as fin, open(f"{ws}/pipeline/stage2_features.csv", "w", newline="") as fout:
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, fieldnames=list(reader.fieldnames) + ["month", "quarter", "amount_category", "is_weekend"])
    writer.writeheader()
    for row in reader:
        d = datetime.strptime(row["date"], "%Y-%m-%d")
        row["month"] = str(d.month)
        q = (d.month - 1) // 3 + 1
        row["quarter"] = f"Q{q}"
        amt = float(row["amount"])
        if amt < 100:
            row["amount_category"] = "low"
        elif amt <= 500:
            row["amount_category"] = "medium"
        else:
            row["amount_category"] = "high"
        row["is_weekend"] = str(d.weekday() >= 5).lower()
        writer.writerow(row)
        rows += 1

with open(f"{ws}/pipeline/stage2_log.md", "w") as f:
    f.write(f"""# Stage 2: Feature Engineering Agent Log

## Input
- Source file: pipeline/stage1_clean.csv
- Rows read: {rows}

## Operations
- Extracted month from date field
- Computed quarter (Q1-Q4) from month
- Categorized amounts: low (<100), medium (100-500), high (>500)
- Added is_weekend flag from date day-of-week

## Output
- Output file: pipeline/stage2_features.csv
- Rows written: {rows}
- New columns added: month, quarter, amount_category, is_weekend
""")
PYSTAGE2

# ── Stage 3: Statistical Analysis ─────────────────────────────

python3 << 'PYSTAGE3'
import csv, json, os, statistics

ws = os.environ["WS"]

with open(f"{ws}/pipeline/stage2_features.csv") as f:
    rows = list(csv.DictReader(f))

amounts = [float(r["amount"]) for r in rows]
total = sum(amounts)
mean = statistics.mean(amounts) if amounts else 0
median = statistics.median(amounts) if amounts else 0
min_a = min(amounts) if amounts else 0
max_a = max(amounts) if amounts else 0

by_quarter = {}
for r in rows:
    q = r["quarter"]
    amt = float(r["amount"])
    by_quarter.setdefault(q, {"count": 0, "total": 0})
    by_quarter[q]["count"] += 1
    by_quarter[q]["total"] += amt

by_category = {}
for r in rows:
    cat = r["amount_category"]
    amt = float(r["amount"])
    by_category.setdefault(cat, {"count": 0, "total": 0})
    by_category[cat]["count"] += 1
    by_category[cat]["total"] += amt

by_region = {}
for r in rows:
    reg = r["region"]
    amt = float(r["amount"])
    by_region.setdefault(reg, 0)
    by_region[reg] += amt
top_regions = sorted(by_region.items(), key=lambda x: -x[1])[:3]

stats = {
    "total": round(total, 2),
    "mean": round(mean, 2),
    "median": round(median, 2),
    "min": round(min_a, 2),
    "max": round(max_a, 2),
    "count": len(amounts),
    "by_quarter": {k: {"count": v["count"], "total": round(v["total"], 2)} for k, v in sorted(by_quarter.items())},
    "by_category": {k: {"count": v["count"], "total": round(v["total"], 2)} for k, v in sorted(by_category.items())},
    "top_regions": [{"region": r, "total": round(t, 2)} for r, t in top_regions],
}

with open(f"{ws}/pipeline/stage3_stats.json", "w") as f:
    json.dump(stats, f, indent=2)

with open(f"{ws}/pipeline/stage3_log.md", "w") as f:
    f.write(f"""# Stage 3: Statistical Analysis Agent Log

## Input
- Source file: pipeline/stage2_features.csv
- Rows analyzed: {len(rows)}

## Operations
- Computed summary statistics (total, mean, median, min, max)
- Aggregated sales by quarter
- Aggregated sales by amount category
- Identified top 3 regions by total sales

## Output
- Output file: pipeline/stage3_stats.json
- Summary: total={total:.2f}, mean={mean:.2f}, median={median:.2f}
- Top region: {top_regions[0][0]} (${top_regions[0][1]:.2f})
""")
PYSTAGE3

# ── Stage 4: Report Generation ────────────────────────────────

python3 << 'PYSTAGE4'
import json, os

ws = os.environ["WS"]

with open(f"{ws}/pipeline/stage3_stats.json") as f:
    stats = json.load(f)

report = f"""# Sales Data Analysis Report

## Executive Summary

Analysis of {stats['count']} sales transactions yielded total revenue of ${stats['total']:,.2f}.
The average transaction value was ${stats['mean']:,.2f} with a median of ${stats['median']:,.2f}.
Transaction values ranged from ${stats['min']:,.2f} to ${stats['max']:,.2f}.

## Quarterly Breakdown

| Quarter | Transactions | Total Sales |
|---------|-------------|-------------|
"""
for q, data in sorted(stats["by_quarter"].items()):
    report += f"| {q} | {data['count']} | ${data['total']:,.2f} |\n"

report += f"""
## Category Distribution

| Category | Count | Total |
|----------|-------|-------|
"""
for cat, data in stats["by_category"].items():
    report += f"| {cat} | {data['count']} | ${data['total']:,.2f} |\n"

report += f"""
## Top Regions

"""
for i, region in enumerate(stats["top_regions"], 1):
    report += f"{i}. **{region['region']}**: ${region['total']:,.2f}\n"

report += f"""
## Business Insights

- Total revenue of ${stats['total']:,.2f} across {stats['count']} transactions indicates healthy sales volume.
- The median (${stats['median']:,.2f}) is {'close to' if abs(stats['mean'] - stats['median']) < 50 else 'different from'} the mean (${stats['mean']:,.2f}), suggesting {'relatively symmetric' if abs(stats['mean'] - stats['median']) < 50 else 'skewed'} distribution of deal sizes.
- The high-value segment (>$500) represents premium transactions warranting focused account management.

## Recommendations

1. Focus sales efforts on the top-performing region ({stats['top_regions'][0]['region']}) while investigating growth opportunities in underperforming regions.
2. Develop strategies to move medium-category deals into the high-value segment.
3. Monitor quarterly trends for seasonal patterns to optimize resource allocation.
"""

with open(f"{ws}/pipeline/stage4_report.md", "w") as f:
    f.write(report)
with open(f"{ws}/report.md", "w") as f:
    f.write(report)

with open(f"{ws}/pipeline/stage4_log.md", "w") as f:
    f.write(f"""# Stage 4: Report Generation Agent Log

## Input
- Source files: pipeline/stage3_stats.json, pipeline/stage2_features.csv
- Stats loaded: {stats['count']} transactions, ${stats['total']:,.2f} total

## Operations
- Generated executive summary from summary statistics
- Created quarterly breakdown table
- Created category distribution table
- Listed top 3 regions
- Wrote business insights based on statistical patterns
- Produced actionable recommendations

## Output
- Output files: pipeline/stage4_report.md, report.md (workspace root copy)
- Report sections: Executive Summary, Quarterly, Category, Top Regions, Insights, Recommendations
""")
PYSTAGE4
