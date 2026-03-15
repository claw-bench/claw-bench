#!/usr/bin/env bash
# Setup script for sec-011-incident-response-plan
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/incident.json" "$WORKSPACE/incident.json"
cp "$TASK_DIR/environment/data/playbooks.json" "$WORKSPACE/playbooks.json"
echo "Workspace ready with incident.json and playbooks.json"
