#!/bin/bash
set -euo pipefail

WORKSPACE=${1:-.}

# Read input files
balance_sheet="$WORKSPACE/environment/data/balance_sheet.csv"
income_statement="$WORKSPACE/environment/data/income_statement.csv"

# Parse data
equity=$(awk -F, '/Total Equity/ {print $2}' "$balance_sheet" | tr -d ' ')
total_debt=$(awk -F, '/Long-term Debt/ {d=$2} /Short-term Debt/ {d+=$2} END {print d}' "$balance_sheet" | tr -d ' ')
interest_expense=$(awk -F, '/Interest Expense/ {print $2}' "$income_statement" | tr -d ' ')
tax_expense=$(awk -F, '/Income Tax Expense/ {print $2}' "$income_statement" | tr -d ' ')
ebt=$(awk -F, '/Income Before Tax/ {print $2}' "$income_statement" | tr -d ' ')

# Calculate components
market_value_equity=$equity
market_value_debt=$total_debt
firm_value=$((market_value_equity + market_value_debt))

# CAPM parameters
risk_free_rate=0.03
market_return=0.08
beta=1.2

# Calculations
cost_of_equity=$(echo "$risk_free_rate + $beta * ($market_return - $risk_free_rate)" | bc -l)
cost_of_debt=$(echo "$interest_expense / $market_value_debt" | bc -l)
tax_rate=$(echo "$tax_expense / $ebt" | bc -l)

equity_weight=$(echo "$market_value_equity / $firm_value" | bc -l)
debt_weight=$(echo "$market_value_debt / $firm_value" | bc -l)

wacc=$(echo "$equity_weight * $cost_of_equity + $debt_weight * $cost_of_debt * (1 - $tax_rate)" | bc -l)

# Create output JSON
cat > "$WORKSPACE/wacc_report.json" <<EOF
{
    "equity_weight": $(printf "%.4f" $equity_weight),
    "debt_weight": $(printf "%.4f" $debt_weight),
    "cost_of_equity": $(printf "%.4f" $cost_of_equity),
    "cost_of_debt": $(printf "%.4f" $cost_of_debt),
    "tax_rate": $(printf "%.4f" $tax_rate),
    "final_wacc": $(printf "%.4f" $wacc)
}
EOF

echo "WACC calculation complete"
