#!/bin/bash
set -euo pipefail

# Create workspace and data directory
mkdir -p environment/data

# Generate synthetic balance sheet data
cat > environment/data/balance_sheet.csv <<EOF
Item,2023 (in millions)
Total Assets,15000.00
Total Liabilities,9000.00
Total Equity,6000.00
Long-term Debt,3000.00
Short-term Debt,1000.00
EOF

# Generate synthetic income statement data
cat > environment/data/income_statement.csv <<EOF
Item,2023 (in millions)
Revenue,12000.00
Operating Income,2500.00
Interest Expense,200.00
Income Before Tax,2300.00
Income Tax Expense,500.00
Net Income,1800.00
EOF

# Create edge case files for testing
mkdir -p environment/edge_cases

# Zero debt case
cat > environment/edge_cases/zero_debt_balance.csv <<EOF
Item,2023 (in millions)
Total Assets,10000.00
Total Liabilities,0.00
Total Equity,10000.00
Long-term Debt,0.00
Short-term Debt,0.00
EOF

cat > environment/edge_cases/zero_debt_income.csv <<EOF
Item,2023 (in millions)
Revenue,8000.00
Operating Income,1500.00
Interest Expense,0.00
Income Before Tax,1500.00
Income Tax Expense,300.00
Net Income,1200.00
EOF

# Negative equity case
cat > environment/edge_cases/negative_equity_balance.csv <<EOF
Item,2023 (in millions)
Total Assets,8000.00
Total Liabilities,10000.00
Total Equity,-2000.00
Long-term Debt,6000.00
Short-term Debt,1000.00
EOF

cat > environment/edge_cases/negative_equity_income.csv <<EOF
Item,2023 (in millions)
Revenue,5000.00
Operating Income,500.00
Interest Expense,300.00
Income Before Tax,200.00
Income Tax Expense,40.00
Net Income,160.00
EOF

echo "Environment setup complete"
