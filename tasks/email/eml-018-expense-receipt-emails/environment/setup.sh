#!/usr/bin/env bash
# Setup script for eml-018-expense-receipt-emails
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/receipts"

for f in "$(dirname "$0")/data"/receipt_*.json; do
    cp "$f" "$WORKSPACE/receipts/"
done

echo "Workspace created at $WORKSPACE"
