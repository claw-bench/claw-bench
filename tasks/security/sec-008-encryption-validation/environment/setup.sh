#!/usr/bin/env bash
# Setup script for sec-008-encryption-validation
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/crypto_config.json" "$WORKSPACE/crypto_config.json"
echo "Workspace ready with crypto_config.json"
