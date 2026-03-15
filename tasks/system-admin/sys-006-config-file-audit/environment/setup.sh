#!/usr/bin/env bash
# Setup script for sys-006-config-file-audit
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/server_configs"
cp "$TASK_DIR/environment/data/nginx.conf" "$WORKSPACE/server_configs/nginx.conf"
cp "$TASK_DIR/environment/data/ssh_config" "$WORKSPACE/server_configs/ssh_config"
cp "$TASK_DIR/environment/data/my.cnf" "$WORKSPACE/server_configs/my.cnf"
echo "Workspace ready with server_configs/"
