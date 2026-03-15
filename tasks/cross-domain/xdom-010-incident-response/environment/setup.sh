#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/incident_data"

cp "$TASK_DIR/environment/data/service.log" "$WORKSPACE/incident_data/service.log"
cp "$TASK_DIR/environment/data/alerts.json" "$WORKSPACE/incident_data/alerts.json"
cp "$TASK_DIR/environment/data/config_change.json" "$WORKSPACE/incident_data/config_change.json"
cp "$TASK_DIR/environment/data/team_contacts.json" "$WORKSPACE/incident_data/team_contacts.json"

echo "Workspace ready at $WORKSPACE"
