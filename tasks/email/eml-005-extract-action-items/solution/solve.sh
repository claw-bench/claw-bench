#!/usr/bin/env bash
# Oracle solution for eml-005-extract-action-items
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/action_items.json" <<'JSON'
[
  {
    "task": "Prepare the marketing materials for review",
    "assignee": "Marcus",
    "deadline": "March 12"
  },
  {
    "task": "Provide final product screenshots to Marcus",
    "assignee": "Sarah",
    "deadline": "March 10"
  },
  {
    "task": "Coordinate with the press team and reach out to media contacts",
    "assignee": "Elena",
    "deadline": null
  },
  {
    "task": "Review and approve the press release draft",
    "assignee": "Diana",
    "deadline": "March 11"
  },
  {
    "task": "Update the product landing page",
    "assignee": "Kevin",
    "deadline": "March 14"
  },
  {
    "task": "Prepare a brief demo video script",
    "assignee": "Marcus",
    "deadline": "March 13"
  },
  {
    "task": "Ensure staging environment is ready for testing",
    "assignee": "Kevin",
    "deadline": "March 13"
  }
]
JSON

echo "Solution written to $WORKSPACE/action_items.json"
