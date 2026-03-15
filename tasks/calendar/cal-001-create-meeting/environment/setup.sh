#!/usr/bin/env bash
# Setup script for cal-001-create-meeting
# Creates the workspace directory for the agent to write output into.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"
echo "Workspace created at $WORKSPACE"
