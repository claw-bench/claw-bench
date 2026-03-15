#!/usr/bin/env bash
# Oracle solution for doc-016-meeting-minutes
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/minutes.md" << 'EOF'
# Product Review Meeting

**Date:** March 10, 2026

## Attendees

**Present:**
- Sarah Chen
- Mike Johnson
- Lisa Wang
- Tom Brown

**Absent:**
- James Lee (sick)

## Discussion Summary

- **Sarah Chen:** Q1 numbers look good, revenue up 15%.
- **Mike Johnson:** Need to finalize the pricing for new tier by Friday.
- **Lisa Wang:** Design mockups ready for review, will send link after meeting.
- **Tom Brown:** Backend migration 80% complete, estimated done by March 20.

## Decisions

1. Approved new pricing tier at $49/month.
2. Postponed mobile app launch to Q2.
3. Hire 2 more frontend devs.

## Action Items

| Person | Action | Due Date |
| --- | --- | --- |
| Mike Johnson | Send pricing proposal to finance | March 13, 2026 |
| Lisa Wang | Share Figma link with team | Today (March 10, 2026) |
| Tom Brown | Update migration timeline doc | TBD |
| Sarah Chen | Schedule follow-up meeting | March 17, 2026 |
EOF

echo "Solution written to $WORKSPACE/minutes.md"
