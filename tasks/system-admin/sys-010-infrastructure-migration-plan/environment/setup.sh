#!/usr/bin/env bash
# Setup script for sys-010-infrastructure-migration-plan
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/infrastructure.yaml" "$WORKSPACE/infrastructure.yaml"
cp "$TASK_DIR/environment/data/requirements.yaml" "$WORKSPACE/requirements.yaml"
echo "Workspace ready with infrastructure.yaml and requirements.yaml"
