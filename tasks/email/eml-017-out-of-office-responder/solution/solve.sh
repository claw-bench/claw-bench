#!/usr/bin/env bash
# Oracle solution for eml-017-out-of-office-responder
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE/replies"

cat > "$WORKSPACE/replies/reply_to_sarah.jones.json" <<'JSON'
{
  "to": "sarah.jones@partnerco.com",
  "subject": "Re: Partnership Agreement Review",
  "body": "Dear Sarah,\n\nThank you for your email. I am currently on annual leave.\n\nI will be back on March 22, 2026. For urgent matters, please contact 李伟 at li.wei@company.com.\n\nBest regards,\n张明"
}
JSON

cat > "$WORKSPACE/replies/reply_to_mike.chen.json" <<'JSON'
{
  "to": "mike.chen@vendor.io",
  "subject": "Re: Invoice #2026-0342",
  "body": "Dear Mike,\n\nThank you for your email. I am currently on annual leave.\n\nI will be back on March 22, 2026. For urgent matters, please contact 李伟 at li.wei@company.com.\n\nBest regards,\n张明"
}
JSON

cat > "$WORKSPACE/replies/reply_to_emma.wilson.json" <<'JSON'
{
  "to": "emma.wilson@client.org",
  "subject": "Re: Project Timeline Update",
  "body": "Dear Emma,\n\nThank you for your email. I am currently on annual leave.\n\nI will be back on March 22, 2026. For urgent matters, please contact 李伟 at li.wei@company.com.\n\nBest regards,\n张明"
}
JSON

cat > "$WORKSPACE/replies/reply_to_raj.kumar.json" <<'JSON'
{
  "to": "raj.kumar@techfirm.com",
  "subject": "Re: Conference Speaker Invitation",
  "body": "Dear Raj,\n\nThank you for your email. I am currently on annual leave.\n\nI will be back on March 22, 2026. For urgent matters, please contact 李伟 at li.wei@company.com.\n\nBest regards,\n张明"
}
JSON

echo "Solution written to $WORKSPACE/replies/"
