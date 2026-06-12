#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 - "$WORKSPACE" <<'PYEOF'
import csv
import json
import sys
from pathlib import Path

workspace = Path(sys.argv[1])
balance_sheet = workspace / "environment" / "data" / "balance_sheet.csv"
income_statement = workspace / "environment" / "data" / "income_statement.csv"


def read_items(path):
    items = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) < 2:
                continue
            items[row[0].strip()] = float(row[1].strip())
    return items


bs = read_items(balance_sheet)
is_ = read_items(income_statement)

# Balance sheet figures
equity = bs["Total Equity"]
total_debt = bs["Long-term Debt"] + bs["Short-term Debt"]

# Income statement figures
interest_expense = is_["Interest Expense"]
tax_expense = is_["Income Tax Expense"]
ebt = is_["Income Before Tax"]

# Market values and firm value
market_value_equity = equity
market_value_debt = total_debt
firm_value = market_value_equity + market_value_debt

# CAPM parameters
risk_free_rate = 0.03
market_return = 0.08
beta = 1.2

# Components (handle zero-denominator edge cases gracefully)
cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
cost_of_debt = interest_expense / market_value_debt if market_value_debt else 0.0
tax_rate = tax_expense / ebt if ebt else 0.0

equity_weight = market_value_equity / firm_value if firm_value else 0.0
debt_weight = market_value_debt / firm_value if firm_value else 0.0

wacc = equity_weight * cost_of_equity + debt_weight * cost_of_debt * (1 - tax_rate)

report = {
    "equity_weight": round(equity_weight, 4),
    "debt_weight": round(debt_weight, 4),
    "cost_of_equity": round(cost_of_equity, 4),
    "cost_of_debt": round(cost_of_debt, 4),
    "tax_rate": round(tax_rate, 4),
    "final_wacc": round(wacc, 4),
}

with open(workspace / "wacc_report.json", "w") as f:
    json.dump(report, f, indent=4)
PYEOF

echo "WACC calculation complete"
