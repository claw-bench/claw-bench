#!/usr/bin/env bash
# Oracle solution for eml-010-auto-reply-generator
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/replies.json" <<'JSON'
[
  {
    "email_id": 1,
    "rule_id": "R1",
    "to": "sarah.t@clientcorp.com",
    "subject": "Re: Invoice #8834 Payment Status",
    "body": "Dear Sarah,\n\nThank you for reaching out about your invoice. Our accounts team has been notified and will review the status within 2 business days. You will receive a detailed update shortly.\n\nBest regards"
  },
  {
    "email_id": 2,
    "rule_id": "R3",
    "to": "mike.r@partnerfirm.com",
    "subject": "Re: Meeting Request for Next Week",
    "body": "Hi Mike,\n\nThank you for your meeting request. I am currently out of the office but will review available time slots upon my return. In the meantime, feel free to book a slot via our scheduling link.\n\nBest regards"
  },
  {
    "email_id": 3,
    "rule_id": "R2",
    "to": "jenny.l@techstart.io",
    "subject": "Re: Technical Support - Login Issues",
    "body": "Dear Jenny,\n\nWe're sorry to hear you're experiencing difficulties. A support ticket has been created and assigned to our technical team. We aim to respond within 4 hours during business hours.\n\nBest regards"
  },
  {
    "email_id": 4,
    "rule_id": "R4",
    "to": "alex.m@bigretail.com",
    "subject": "Re: Product Inquiry - Enterprise Plan",
    "body": "Dear Alex,\n\nThank you for your interest in our products. A member of our sales team will reach out within 24 hours with detailed pricing information and a customized proposal.\n\nBest regards"
  },
  {
    "email_id": 6,
    "rule_id": "R1",
    "to": "david.p@supplierx.com",
    "subject": "Re: Overdue Invoice Reminder",
    "body": "Dear David,\n\nThank you for reaching out about your invoice. Our accounts team has been notified and will review the status within 2 business days. You will receive a detailed update shortly.\n\nBest regards"
  },
  {
    "email_id": 7,
    "rule_id": "R5",
    "to": "rachel.g@designco.com",
    "subject": "Re: Support Request - Export Feature Bug",
    "body": "Dear Rachel,\n\nThank you for reporting this issue. Our engineering team has been notified and will investigate the bug immediately. We will provide a fix or workaround as soon as possible.\n\nBest regards"
  },
  {
    "email_id": 8,
    "rule_id": "R3",
    "to": "tom.b@ventures.co",
    "subject": "Re: Partnership Opportunity Discussion",
    "body": "Hi Tom,\n\nThank you for your meeting request. I am currently out of the office but will review available time slots upon my return. In the meantime, feel free to book a slot via our scheduling link.\n\nBest regards"
  }
]
JSON

echo "Solution written to $WORKSPACE/replies.json"
