#!/usr/bin/env bash
# Setup script for comm-014-chat-sentiment-analysis
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE"
cp "$TASK_DIR/environment/data/chat_log.jsonl" "$WORKSPACE/chat_log.jsonl"
cp "$TASK_DIR/environment/data/keywords.json" "$WORKSPACE/keywords.json"
echo "Workspace ready with chat_log.jsonl and keywords.json"
