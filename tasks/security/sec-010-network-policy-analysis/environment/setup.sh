#!/usr/bin/env bash
# Setup script for sec-010-network-policy-analysis
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/firewall_rules.json" "$WORKSPACE/firewall_rules.json"
echo "Workspace ready with firewall_rules.json"
