#!/usr/bin/env bash
# Setup script for sec-012-secrets-scanning-git-history
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/git_diffs"
for f in "$TASK_DIR/environment/data/"commit_*.diff; do
    cp "$f" "$WORKSPACE/git_diffs/"
done
echo "Workspace ready with git diff files"
