#!/usr/bin/env bash
# Setup script for wfl-010-complex-multi-system-integration
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/orders.csv" "$WORKSPACE/orders.csv"
cp "$TASK_DIR/environment/data/customers.json" "$WORKSPACE/customers.json"
cp "$TASK_DIR/environment/data/pricing_rules.json" "$WORKSPACE/pricing_rules.json"
echo "Workspace ready with orders.csv, customers.json, and pricing_rules.json"
