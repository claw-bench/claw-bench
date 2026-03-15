#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/company_data.csv" "$WORKSPACE/company_data.csv"
echo "Workspace ready with company_data.csv"
