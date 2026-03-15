#!/usr/bin/env bash
# Oracle solution for eml-008-attachment-inventory
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/attachments.json" <<'JSON'
[
  {"email_id": 1, "filename": "q1_report.pdf", "size_bytes": 245000, "content_type": "application/pdf"},
  {"email_id": 1, "filename": "q1_spreadsheet.xlsx", "size_bytes": 189000, "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
  {"email_id": 2, "filename": "logo_v1.png", "size_bytes": 520000, "content_type": "image/png"},
  {"email_id": 2, "filename": "logo_v2.png", "size_bytes": 480000, "content_type": "image/png"},
  {"email_id": 2, "filename": "brand_guidelines.pdf", "size_bytes": 1200000, "content_type": "application/pdf"},
  {"email_id": 4, "filename": "employee_handbook_2026.pdf", "size_bytes": 3400000, "content_type": "application/pdf"},
  {"email_id": 5, "filename": "review_notes.md", "size_bytes": 8500, "content_type": "text/markdown"},
  {"email_id": 5, "filename": "diff_output.txt", "size_bytes": 12300, "content_type": "text/plain"},
  {"email_id": 7, "filename": "client_deck.pptx", "size_bytes": 4500000, "content_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation"},
  {"email_id": 7, "filename": "pricing_sheet.xlsx", "size_bytes": 67000, "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
  {"email_id": 8, "filename": "vendor_contract.pdf", "size_bytes": 890000, "content_type": "application/pdf"},
  {"email_id": 8, "filename": "terms_addendum.docx", "size_bytes": 45000, "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
  {"email_id": 9, "filename": "campaign_results.csv", "size_bytes": 34000, "content_type": "text/csv"},
  {"email_id": 10, "filename": "team_photo.jpg", "size_bytes": 2300000, "content_type": "image/jpeg"},
  {"email_id": 10, "filename": "event_video.mp4", "size_bytes": 15000000, "content_type": "video/mp4"}
]
JSON

echo "Solution written to $WORKSPACE/attachments.json"
