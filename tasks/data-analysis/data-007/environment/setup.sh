#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/orders.csv" "$WORKSPACE/orders.csv"
cp "$TASK_DIR/environment/data/customers.csv" "$WORKSPACE/customers.csv"
echo "Workspace ready with orders.csv and customers.csv"
