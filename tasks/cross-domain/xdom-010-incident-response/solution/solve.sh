#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/timeline.json" <<'JSON'
{
  "incident_id": "INC-2026-0310",
  "events": [
    {
      "timestamp": "2026-03-10T08:00:00",
      "source": "log",
      "description": "Payment service started normally, version 3.2.1"
    },
    {
      "timestamp": "2026-03-10T08:15:00",
      "source": "config",
      "description": "Config change CHG-2026-0310-001: rate limit reduced from 200 TPS to 50 TPS (auto-approved by deploy-bot)"
    },
    {
      "timestamp": "2026-03-10T08:15:02",
      "source": "log",
      "description": "Warning: rate limit threshold significantly reduced"
    },
    {
      "timestamp": "2026-03-10T08:20:00",
      "source": "alert",
      "description": "Transaction queue at 90% capacity (45/50)"
    },
    {
      "timestamp": "2026-03-10T08:21:00",
      "source": "alert",
      "description": "Critical: Rate limit exceeded - 52 TPS against 50 TPS limit"
    },
    {
      "timestamp": "2026-03-10T08:21:01",
      "source": "log",
      "description": "Multiple payments rejected due to rate limiting (ORD-88410, 88411, 88412)"
    },
    {
      "timestamp": "2026-03-10T08:22:00",
      "source": "log",
      "description": "15 payments rejected in 60 seconds, customer complaints growing"
    },
    {
      "timestamp": "2026-03-10T08:23:30",
      "source": "alert",
      "description": "Circuit breaker OPENED for payment-gateway - all payments halted"
    },
    {
      "timestamp": "2026-03-10T08:25:00",
      "source": "alert",
      "description": "Revenue impact: estimated $12,500/hour loss"
    },
    {
      "timestamp": "2026-03-10T08:30:00",
      "source": "log",
      "description": "On-call engineer Sarah Kim acknowledged alert"
    },
    {
      "timestamp": "2026-03-10T08:40:00",
      "source": "log",
      "description": "Root cause identified: rate limit config change"
    },
    {
      "timestamp": "2026-03-10T08:41:30",
      "source": "log",
      "description": "Config rolled back: rate limit restored to 200 TPS"
    },
    {
      "timestamp": "2026-03-10T08:42:00",
      "source": "log",
      "description": "Circuit breaker reset to CLOSED, payment processing resumed"
    },
    {
      "timestamp": "2026-03-10T08:45:00",
      "source": "log",
      "description": "Backlog cleared, normal operations fully restored"
    }
  ]
}
JSON

cat > "$WORKSPACE/root_cause.md" <<'MARKDOWN'
# Root Cause Analysis

## Incident Summary

**Incident ID:** INC-2026-0310
**Duration:** ~25 minutes (08:20 - 08:45 UTC)
**Severity:** Critical (P1)
**Service Affected:** Payment Service

## Root Cause

An automated configuration change (CHG-2026-0310-001) reduced the payment service rate limit from 200 TPS to 50 TPS at 08:15 UTC. This was deployed by `deploy-bot` with auto-approval, bypassing human review.

The dramatically reduced rate limit (75% reduction) caused the transaction queue to fill rapidly. Within 6 minutes, the service exceeded the new limit, triggering rate-limiting rejections. This cascade led to the circuit breaker opening at 08:23, halting all payment processing.

## Contributing Factors

1. **No human review for critical config changes**: The rate limit change was auto-approved despite being a 75% reduction in capacity.
2. **Queue size also reduced**: Queue size was changed from 500 to 50 alongside the TPS reduction, compounding the problem.
3. **No gradual rollout**: The config change was applied immediately to all instances rather than using a canary deployment.
4. **Insufficient alerting thresholds**: The first warning came at 90% queue capacity, leaving little time to react.

## Evidence

- Config change log shows `max_tps` changed from 200 to 50 at 08:15:00
- Service log shows rate limit warnings starting at 08:15:02
- First payment rejections at 08:21:01 (6 minutes after change)
- Circuit breaker opened at 08:23:30
- Config rollback at 08:41:30 resolved the issue

## Impact

- **Duration of outage**: ~22 minutes of degraded/halted payments
- **Payments rejected**: 15+ confirmed, estimated 30+ total
- **Revenue impact**: Estimated $5,000-$6,000 in delayed/lost transactions
- **Customer impact**: 8+ support tickets filed
MARKDOWN

cat > "$WORKSPACE/remediation_plan.json" <<'JSON'
{
  "immediate_actions": [
    {
      "description": "Verify all payment processing has returned to normal and backlog is cleared",
      "owner": "Sarah Kim",
      "priority": "critical",
      "deadline": "2026-03-10T10:00:00"
    },
    {
      "description": "Contact affected customers and process any stuck payments",
      "owner": "Lisa Park",
      "priority": "high",
      "deadline": "2026-03-10T12:00:00"
    }
  ],
  "short_term_fixes": [
    {
      "description": "Require human approval for rate limit changes exceeding 20% reduction",
      "owner": "Mike Chen",
      "priority": "critical",
      "deadline": "2026-03-13T17:00:00"
    },
    {
      "description": "Add pre-deployment validation to reject rate limit configs below minimum safe threshold",
      "owner": "Sarah Kim",
      "priority": "high",
      "deadline": "2026-03-17T17:00:00"
    },
    {
      "description": "Lower alerting threshold from 90% to 70% queue capacity",
      "owner": "Sarah Kim",
      "priority": "medium",
      "deadline": "2026-03-13T17:00:00"
    }
  ],
  "long_term_improvements": [
    {
      "description": "Implement canary deployment for all configuration changes to payment service",
      "owner": "Mike Chen",
      "priority": "high",
      "deadline": "2026-04-15T17:00:00"
    },
    {
      "description": "Build automated rollback capability triggered by error rate thresholds",
      "owner": "Sarah Kim",
      "priority": "high",
      "deadline": "2026-04-30T17:00:00"
    },
    {
      "description": "Create comprehensive runbook for payment service incidents",
      "owner": "Mike Chen",
      "priority": "medium",
      "deadline": "2026-04-15T17:00:00"
    }
  ]
}
JSON

cat > "$WORKSPACE/communication_draft.md" <<'MARKDOWN'
# Incident Notification: Payment Service Disruption

**Date:** March 10, 2026
**Incident ID:** INC-2026-0310
**Status:** RESOLVED

## Summary

On March 10, 2026, between approximately 08:20 and 08:45 UTC, the payment processing service experienced a disruption that resulted in some customer payments being temporarily rejected or delayed.

## Impact

- Payment processing was intermittently unavailable for approximately 25 minutes.
- Some customer transactions were temporarily rejected and have since been reprocessed.
- No data loss occurred. All customer data and payment records remain intact.

## Root Cause

A configuration change inadvertently reduced the payment processing capacity, causing the system to reject transactions that exceeded the lowered threshold. The issue was identified and the configuration was reverted, restoring normal operations.

## Current Status

- All payment processing has been fully restored as of 08:45 UTC.
- Affected transactions have been identified and reprocessed.
- Customer support is reaching out to impacted customers.

## Next Steps

- We are implementing additional safeguards to prevent similar configuration issues.
- A full post-incident review is scheduled to identify further improvements.
- Enhanced monitoring will be deployed to detect capacity changes earlier.

## Contact

For questions regarding this incident, please contact:
- **Technical:** Sarah Kim, Senior SRE (sarah.kim@company.com)
- **Business:** Lisa Park, Product Owner (lisa.park@company.com)
MARKDOWN

echo "Solution written to $WORKSPACE/"
