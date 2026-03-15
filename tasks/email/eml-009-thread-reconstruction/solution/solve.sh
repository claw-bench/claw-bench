#!/usr/bin/env bash
# Oracle solution for eml-009-thread-reconstruction
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/threads.json" <<'JSON'
[
  {
    "thread_id": 1,
    "subject": "Project Alpha Kickoff",
    "message_count": 6,
    "messages": [
      {"id": 1, "message_id": "msg-001", "from": "alice@company.com", "date": "2026-03-01T10:00:00Z", "body": "Hi team, excited to kick off Project Alpha. Let's discuss the timeline and deliverables."},
      {"id": 2, "message_id": "msg-002", "from": "bob@company.com", "date": "2026-03-01T14:00:00Z", "body": "Looks good Alice! I think we should prioritize the API design first."},
      {"id": 3, "message_id": "msg-003", "from": "alice@company.com", "date": "2026-03-02T09:00:00Z", "body": "Great points Bob. I'll set up the initial project structure today."},
      {"id": 5, "message_id": "msg-005", "from": "carol@company.com", "date": "2026-03-02T14:00:00Z", "body": "I can take the lead on the frontend components. Will start next week."},
      {"id": 9, "message_id": "msg-009", "from": "dave@company.com", "date": "2026-03-04T08:00:00Z", "body": "Just checking in on the project. Alice, how's the initial structure coming along?"},
      {"id": 10, "message_id": "msg-010", "from": "alice@company.com", "date": "2026-03-04T11:00:00Z", "body": "Structure is ready! I've pushed the initial codebase to the repository. Please review."}
    ]
  },
  {
    "thread_id": 2,
    "subject": "Budget Approval Needed",
    "message_count": 4,
    "messages": [
      {"id": 4, "message_id": "msg-004", "from": "bob@company.com", "date": "2026-03-02T11:00:00Z", "body": "Carol, we need budget approval for the new marketing campaign. Total requested: $50,000."},
      {"id": 6, "message_id": "msg-006", "from": "dave@company.com", "date": "2026-03-03T10:00:00Z", "body": "I'd recommend splitting this into two phases to make approval easier."},
      {"id": 7, "message_id": "msg-007", "from": "carol@company.com", "date": "2026-03-03T14:00:00Z", "body": "Budget approved. Please proceed with the vendor selection."},
      {"id": 8, "message_id": "msg-008", "from": "bob@company.com", "date": "2026-03-04T09:00:00Z", "body": "Thanks Carol! I'll reach out to the top three vendors today."}
    ]
  },
  {
    "thread_id": 3,
    "subject": "Website Redesign Feedback",
    "message_count": 5,
    "messages": [
      {"id": 11, "message_id": "msg-011", "from": "frank@company.com", "date": "2026-03-04T09:00:00Z", "body": "Team, I've reviewed the website redesign mockups. Here are my thoughts on the color scheme and layout."},
      {"id": 12, "message_id": "msg-012", "from": "ivan@company.com", "date": "2026-03-04T15:00:00Z", "body": "I like the new design direction. The mobile responsiveness is much improved."},
      {"id": 13, "message_id": "msg-013", "from": "helen@company.com", "date": "2026-03-05T10:00:00Z", "body": "The layout looks good but I think we should reconsider the navigation structure."},
      {"id": 14, "message_id": "msg-014", "from": "grace@company.com", "date": "2026-03-05T11:00:00Z", "body": "I agree with Frank. Let's go with the blue color scheme."},
      {"id": 15, "message_id": "msg-015", "from": "frank@company.com", "date": "2026-03-06T09:00:00Z", "body": "Thanks for all the feedback. I'll compile the suggestions and update the mockups by next week."}
    ]
  },
  {
    "thread_id": 4,
    "subject": "Server Migration Plan",
    "message_count": 5,
    "messages": [
      {"id": 16, "message_id": "msg-016", "from": "ivan@company.com", "date": "2026-03-07T08:00:00Z", "body": "Team, we need to plan the server migration for next month. Here's the proposed timeline."},
      {"id": 17, "message_id": "msg-017", "from": "helen@company.com", "date": "2026-03-07T14:00:00Z", "body": "I've reviewed the plan. We should add a rollback strategy in case something goes wrong."},
      {"id": 18, "message_id": "msg-018", "from": "jack@company.com", "date": "2026-03-08T10:00:00Z", "body": "I can handle the database migration part. Will start on Monday."},
      {"id": 19, "message_id": "msg-019", "from": "grace@company.com", "date": "2026-03-08T16:00:00Z", "body": "I'll coordinate with the networking team to ensure minimal downtime during the switch."},
      {"id": 20, "message_id": "msg-020", "from": "ivan@company.com", "date": "2026-03-09T15:00:00Z", "body": "Great progress everyone. Let's finalize the migration checklist by Friday."}
    ]
  }
]
JSON

echo "Solution written to $WORKSPACE/threads.json"
