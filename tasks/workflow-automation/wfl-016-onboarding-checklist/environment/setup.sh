#!/usr/bin/env bash
# Setup script for wfl-016-onboarding-checklist
# Creates workspace with new hire info and equipment templates.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/templates"
cp "$TASK_DIR/environment/data/new_hire.json" "$WORKSPACE/new_hire.json"
cp "$TASK_DIR/environment/data/equipment_by_dept.json" "$WORKSPACE/templates/equipment_by_dept.json"
echo "Workspace ready with new_hire.json and templates"
