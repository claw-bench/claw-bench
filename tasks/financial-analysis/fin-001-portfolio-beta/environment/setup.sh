#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"
python3 -c "
import csv, random, math
random.seed(42)
header = ['date','AAPL','GOOGL','MSFT','AMZN','TSLA','MARKET']
rows = [header]
for i in range(252):
    date = f'2024-{(i//21)+1:02d}-{(i%21)+1:02d}'
    mkt = random.gauss(0.0004, 0.012)
    stocks = []
    betas = [1.15, 0.92, 1.05, 1.30, 1.85]
    for b in betas:
        s = b * mkt + random.gauss(0, 0.008)
        stocks.append(f'{s:.6f}')
    rows.append([date] + stocks + [f'{mkt:.6f}'])
with open('$WORKSPACE/stock_returns.csv','w',newline='') as f:
    csv.writer(f).writerows(rows)
"
