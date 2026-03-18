#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"
python3 -c "
import csv, random
random.seed(77)
header = ['customer_id','annual_spending','visit_frequency','avg_transaction','loyalty_years']
rows = [header]
# Cluster 1: High spenders, frequent, loyal
for i in range(30):
    rows.append([f'C{i+1:04d}', round(random.gauss(8000,1500),2), random.randint(40,80), round(random.gauss(150,30),2), random.randint(5,15)])
# Cluster 2: Medium spenders, moderate
for i in range(30,70):
    rows.append([f'C{i+1:04d}', round(random.gauss(3500,800),2), random.randint(15,35), round(random.gauss(80,20),2), random.randint(2,8)])
# Cluster 3: Low spenders, infrequent, new
for i in range(70,100):
    rows.append([f'C{i+1:04d}', round(random.gauss(1000,400),2), random.randint(2,12), round(random.gauss(40,15),2), random.randint(0,3)])
with open('$WORKSPACE/customers.csv','w',newline='') as f:
    csv.writer(f).writerows(rows)
"
