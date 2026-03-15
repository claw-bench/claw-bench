#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json

ws = sys.argv[1]

with open(f"{ws}/chart_data.json") as f:
    data = json.load(f)

max_val = max(item["value"] for item in data)
chart_width = 600
chart_height = 400
bar_width = 60
gap = 20
margin_left = 50
margin_top = 60
margin_bottom = 40
plot_height = chart_height - margin_top - margin_bottom

lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="{chart_height}">')
lines.append(f'  <text x="{chart_width // 2}" y="30" text-anchor="middle" font-size="20" font-weight="bold">Sales by Region</text>')

for i, item in enumerate(data):
    x = margin_left + i * (bar_width + gap)
    bar_height = (item["value"] / max_val) * plot_height
    y = margin_top + plot_height - bar_height
    lines.append(f'  <rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="steelblue" />')
    label_x = x + bar_width // 2
    label_y = margin_top + plot_height + 20
    lines.append(f'  <text x="{label_x}" y="{label_y}" text-anchor="middle" font-size="12">{item["label"]}</text>')

lines.append('</svg>')

with open(f"{ws}/chart.svg", "w") as f:
    f.write("\n".join(lines) + "\n")
PYEOF
