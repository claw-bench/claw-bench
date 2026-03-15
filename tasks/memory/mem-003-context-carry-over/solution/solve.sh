#!/usr/bin/env bash
# Oracle solution for mem-003-context-carry-over
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

# 1. Database connection string
cat > "$WORKSPACE/db_connection.txt" <<'EOF'
postgresql://app_service:xK9#mP2$vL5n@db.internal.example.com:5432/inventory_prod
EOF

# 2. Feature report
cat > "$WORKSPACE/feature_report.txt" <<'EOF'
dark_mode: ENABLED
beta_dashboard: DISABLED
export_csv: ENABLED
multi_language: DISABLED
audit_logging: ENABLED
EOF

# 3. Notification summary
cat > "$WORKSPACE/notification_summary.txt" <<'EOF'
Email notifications: on
Email recipient: ops-team@example.com
SMS notifications: off
SMS phone: +1-555-0142
Slack webhook: not configured
EOF

echo "Solution written to $WORKSPACE/"
