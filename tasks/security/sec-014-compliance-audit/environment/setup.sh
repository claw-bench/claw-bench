#!/usr/bin/env bash
# Setup script for sec-014-compliance-audit
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/system_config"
cp "$TASK_DIR/environment/data/compliance_rules.json" "$WORKSPACE/compliance_rules.json"
cp "$TASK_DIR/environment/data/web_server.json" "$WORKSPACE/system_config/web_server.json"
cp "$TASK_DIR/environment/data/auth_config.json" "$WORKSPACE/system_config/auth_config.json"
cp "$TASK_DIR/environment/data/database.json" "$WORKSPACE/system_config/database.json"
cp "$TASK_DIR/environment/data/logging.json" "$WORKSPACE/system_config/logging.json"
cp "$TASK_DIR/environment/data/network.json" "$WORKSPACE/system_config/network.json"
echo "Workspace ready with system config files and compliance rules"
