#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/customers.csv" "$WORKSPACE/"
cp "$TASK_DIR/environment/data/orders.csv" "$WORKSPACE/"
cp "$TASK_DIR/environment/data/products.csv" "$WORKSPACE/"
