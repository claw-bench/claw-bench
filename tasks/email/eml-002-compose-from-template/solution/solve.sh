#!/usr/bin/env bash
# Oracle solution for eml-002-compose-from-template
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/composed_email.txt" <<'EMAIL'
To: maria.garcia@innovatech.com
From: James Wilson <notifications@innovatech.com>
Subject: Atlas Platform Migration - Upcoming Review Meeting

Dear Maria Garcia,

I hope this email finds you well. I am writing to remind you about the upcoming review meeting for the Atlas Platform Migration project.

The meeting is scheduled for March 20, 2026. Please ensure that all deliverables and progress reports are ready for presentation.

If you have any questions or need to reschedule, please do not hesitate to reach out.

Best regards,
James Wilson
Project Manager
innovatech
EMAIL

echo "Solution written to $WORKSPACE/composed_email.txt"
