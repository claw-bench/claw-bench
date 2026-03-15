#!/usr/bin/env bash
# Setup script for comm-012-contact-deduplicator
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/contacts.csv" "$WORKSPACE/contacts.csv"
echo "Workspace ready with contacts.csv"
