#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv, json, statistics
with open('$WORKSPACE/stock_returns.csv') as f:
    reader = csv.DictReader(f)
    data = list(reader)
stocks = ['AAPL','GOOGL','MSFT','AMZN','TSLA']
mkt = [float(r['MARKET']) for r in data]
mkt_var = statistics.variance(mkt)
betas = {}
for s in stocks:
    sr = [float(r[s]) for r in data]
    cov = sum((a-statistics.mean(sr))*(b-statistics.mean(mkt)) for a,b in zip(sr,mkt))/(len(mkt)-1)
    betas[s] = round(cov/mkt_var, 4)
pb = round(sum(betas.values())/len(betas), 4)
risk = 'conservative' if pb<0.8 else 'aggressive' if pb>1.2 else 'moderate'
json.dump({'individual_betas':betas,'portfolio_beta':pb,'portfolio_risk_level':risk},
          open('$WORKSPACE/portfolio_analysis.json','w'), indent=2)
"
