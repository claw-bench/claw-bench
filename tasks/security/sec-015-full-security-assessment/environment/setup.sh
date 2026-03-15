#!/usr/bin/env bash
# Setup script for sec-015-full-security-assessment
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/application"
cp "$TASK_DIR/environment/data/app.py" "$WORKSPACE/application/app.py"
cp "$TASK_DIR/environment/data/config.py" "$WORKSPACE/application/config.py"
cp "$TASK_DIR/environment/data/requirements.txt" "$WORKSPACE/application/requirements.txt"
cp "$TASK_DIR/environment/data/Dockerfile" "$WORKSPACE/application/Dockerfile"
cp "$TASK_DIR/environment/data/docker-compose.yml" "$WORKSPACE/application/docker-compose.yml"
echo "Workspace ready with application files"
