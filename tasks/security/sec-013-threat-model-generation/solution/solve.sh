#!/usr/bin/env bash
# Oracle solution for sec-013-threat-model-generation
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

model = {
    'metadata': {
        'system_name': 'E-Commerce Platform',
        'version': '3.2',
        'analysis_date': '2024-03-15',
        'methodology': 'STRIDE'
    },
    'threats': [
        {'id': 'T001', 'category': 'Spoofing', 'component': 'api-gateway', 'description': 'JWT token theft or forging allows attacker to impersonate legitimate users', 'likelihood': 'medium', 'impact': 'high', 'mitigation': 'Implement short-lived tokens, token binding, and refresh token rotation'},
        {'id': 'T002', 'category': 'Tampering', 'component': 'order-service', 'description': 'Order data could be tampered during transit between services if mTLS is misconfigured', 'likelihood': 'low', 'impact': 'high', 'mitigation': 'Enforce strict mTLS validation and implement message signing'},
        {'id': 'T003', 'category': 'Repudiation', 'component': 'payment-service', 'description': 'Payment transactions without adequate audit logging could be disputed', 'likelihood': 'medium', 'impact': 'high', 'mitigation': 'Implement immutable audit logs with transaction signing and timestamps'},
        {'id': 'T004', 'category': 'Information Disclosure', 'component': 'user-db', 'description': 'PII and credentials in user-db could be exposed through SQL injection or backup compromise', 'likelihood': 'medium', 'impact': 'high', 'mitigation': 'Use parameterized queries, encrypt backups, implement column-level encryption for SSN/PII'},
        {'id': 'T005', 'category': 'Denial of Service', 'component': 'api-gateway', 'description': 'API gateway could be overwhelmed by volumetric DDoS attack', 'likelihood': 'high', 'impact': 'high', 'mitigation': 'Deploy CDN/WAF with DDoS protection, implement adaptive rate limiting'},
        {'id': 'T006', 'category': 'Elevation of Privilege', 'component': 'admin-dashboard', 'description': 'Privilege escalation through session hijacking or RBAC bypass on admin dashboard', 'likelihood': 'medium', 'impact': 'high', 'mitigation': 'Implement MFA for admin access, enforce principle of least privilege, audit role assignments'},
        {'id': 'T007', 'category': 'Information Disclosure', 'component': 'cache', 'description': 'Redis cache stores session tokens without encryption at rest, risk of exposure if server is compromised', 'likelihood': 'medium', 'impact': 'medium', 'mitigation': 'Enable Redis encryption at rest and in transit, set appropriate TTLs on sensitive data'},
        {'id': 'T008', 'category': 'Spoofing', 'component': 'notification-service', 'description': 'API key authentication is weaker than mTLS — attacker could spoof requests if key is leaked', 'likelihood': 'medium', 'impact': 'medium', 'mitigation': 'Upgrade notification-service to mTLS authentication'},
        {'id': 'T009', 'category': 'Tampering', 'component': 'cache', 'description': 'Redis cache without authentication could allow data tampering including session manipulation', 'likelihood': 'low', 'impact': 'high', 'mitigation': 'Enable Redis AUTH, restrict network access, use ACLs'},
        {'id': 'T010', 'category': 'Denial of Service', 'component': 'payment-service', 'description': 'Payment service could be targeted to prevent checkout, causing revenue loss', 'likelihood': 'medium', 'impact': 'high', 'mitigation': 'Implement circuit breakers, queuing, and failover payment providers'},
        {'id': 'T011', 'category': 'Repudiation', 'component': 'user-service', 'description': 'User account changes (password reset, email change) without sufficient audit trail', 'likelihood': 'medium', 'impact': 'medium', 'mitigation': 'Log all account modification events with immutable audit trail'},
        {'id': 'T012', 'category': 'Elevation of Privilege', 'component': 'user-service', 'description': 'IDOR vulnerability could allow users to access or modify other users profiles', 'likelihood': 'medium', 'impact': 'high', 'mitigation': 'Implement authorization checks on all endpoints, use UUID instead of sequential IDs'}
    ],
    'summary': {
        'total_threats': 12,
        'by_category': {'Spoofing': 2, 'Tampering': 2, 'Repudiation': 2, 'Information Disclosure': 2, 'Denial of Service': 2, 'Elevation of Privilege': 2},
        'risk_rating': 'high',
        'critical_components': ['api-gateway', 'user-db', 'admin-dashboard']
    }
}

with open('$WORKSPACE/threat_model.json', 'w') as f:
    json.dump(model, f, indent=2)
"

cat > "$WORKSPACE/threat_report.md" << 'REPORTEOF'
# Threat Model Report: E-Commerce Platform v3.2

## Executive Summary

This threat model analyzes the E-Commerce Platform using the STRIDE methodology. The system comprises 6 components, 3 data stores, and 3 external API integrations. Analysis identified 12 threats across all STRIDE categories. The overall risk rating is **HIGH** due to internet-facing components handling sensitive PII and financial transactions.

## Architecture Overview

The platform follows a microservice architecture with an API gateway as the internet-facing entry point. Internal services communicate via mTLS (with one exception). Data stores include two PostgreSQL databases (encrypted at rest) and a Redis cache (not encrypted at rest).

### Internet-Facing Components
- **api-gateway** (nginx + Lua) — JWT-authenticated API routing
- **admin-dashboard** (React + Express) — Internal admin with session-based auth + RBAC

### Internal Services
- **user-service** — User management (Python/FastAPI)
- **order-service** — Order processing (Java/Spring Boot)
- **payment-service** — Payment integration (Go)
- **notification-service** — Notifications (Node.js) — Uses API key auth (weaker than mTLS)

## Threat Analysis by Component

### api-gateway
| Threat | Category | Likelihood | Impact |
|--------|----------|------------|--------|
| JWT token theft/forging | Spoofing | Medium | High |
| DDoS attack | Denial of Service | High | High |

### user-service / user-db
| Threat | Category | Likelihood | Impact |
|--------|----------|------------|--------|
| PII exposure via SQL injection | Information Disclosure | Medium | High |
| Account modification without audit | Repudiation | Medium | Medium |
| IDOR privilege escalation | Elevation of Privilege | Medium | High |

### order-service
| Threat | Category | Likelihood | Impact |
|--------|----------|------------|--------|
| Order data tampering in transit | Tampering | Low | High |

### payment-service
| Threat | Category | Likelihood | Impact |
|--------|----------|------------|--------|
| Transaction repudiation | Repudiation | Medium | High |
| Service disruption | Denial of Service | Medium | High |

### notification-service
| Threat | Category | Likelihood | Impact |
|--------|----------|------------|--------|
| Request spoofing via leaked API key | Spoofing | Medium | Medium |

### admin-dashboard
| Threat | Category | Likelihood | Impact |
|--------|----------|------------|--------|
| Privilege escalation via RBAC bypass | Elevation of Privilege | Medium | High |

### Redis Cache
| Threat | Category | Likelihood | Impact |
|--------|----------|------------|--------|
| Session token exposure (no encryption at rest) | Information Disclosure | Medium | Medium |
| Data tampering if unauthenticated | Tampering | Low | High |

## Risk Matrix

| Impact \ Likelihood | High | Medium | Low |
|---------------------|------|--------|-----|
| **High** | DDoS on gateway | JWT spoofing, PII exposure, IDOR, Payment repudiation, Payment DoS, Admin privilege escalation | Order tampering, Cache tampering |
| **Medium** | — | Cache exposure, Notification spoofing, User audit | — |
| **Low** | — | — | — |

## Prioritized Mitigation Recommendations

1. **Deploy DDoS protection** (CDN/WAF) for api-gateway — addresses highest likelihood/impact threat
2. **Enable Redis encryption** at rest and in transit, add AUTH — addresses 2 threats
3. **Implement MFA** for admin-dashboard — addresses privilege escalation
4. **Upgrade notification-service** to mTLS — addresses weaker authentication
5. **Add immutable audit logging** to payment-service and user-service — addresses repudiation
6. **Implement short-lived JWT tokens** with refresh rotation — addresses spoofing
7. **Add authorization checks** and use UUIDs in user-service — addresses IDOR
8. **Implement circuit breakers** for payment-service — addresses DoS
REPORTEOF

echo "Solution written to $WORKSPACE/threat_model.json and $WORKSPACE/threat_report.md"
