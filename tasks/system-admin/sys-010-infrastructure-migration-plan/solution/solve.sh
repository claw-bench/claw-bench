#!/usr/bin/env bash
# Oracle solution for sys-010-infrastructure-migration-plan
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json

# Generate migration plan markdown
plan_md = '''# Infrastructure Migration Plan

## Executive Summary

Migration of production infrastructure from us-east-1 to us-west-2, including 12 services
with version upgrades and resource scaling. The migration targets disaster recovery
improvement and latency optimization for West Coast users.

**Target Completion:** 2024-04-30
**Maintenance Window:** Saturday 02:00-06:00 UTC
**Maximum Allowed Downtime:** 30 minutes

## Pre-Migration Checklist

- [ ] Full backup of primary_db (340 GB PostgreSQL database)
- [ ] Snapshot all service configurations
- [ ] Verify target region capacity and quotas
- [ ] Set up cross-region VPN/peering
- [ ] Test database replication between regions
- [ ] Notify stakeholders of maintenance window
- [ ] Prepare rollback scripts for each phase
- [ ] Verify monitoring and alerting in target region

## Migration Phases

### Phase 1: Storage and Data Layer (Saturday 02:00-03:30 UTC)

**Services:** file_storage, primary_db, replica_db

#### Step 1.1: File Storage Migration
- **Service:** file_storage
- **Action:** Enable S3 cross-region replication from us-east-1 to us-west-2
- **Dependencies:** None
- **Estimated Downtime:** 0 minutes (online replication)
- **Verification:**
  - Verify replication status
  - Compare object counts between regions
  - Test read/write operations in target region

#### Step 1.2: Primary Database Migration
- **Service:** primary_db
- **Action:** Set up PostgreSQL 15.2 in us-west-2, configure logical replication from v13.4, perform cutover
- **Dependencies:** None
- **Estimated Downtime:** 15 minutes (during cutover)
- **Verification:**
  - Verify data integrity with checksums
  - Test connection from application layer
  - Confirm replication lag is zero
  - Validate multi-AZ configuration

#### Step 1.3: Replica Database Migration
- **Service:** replica_db
- **Action:** Create read replica from new primary in us-west-2
- **Dependencies:** primary_db
- **Estimated Downtime:** 0 minutes
- **Verification:**
  - Verify replication stream is active
  - Test read queries

**Rollback:** Switch DNS back to us-east-1 primary, disable replication

### Phase 2: Cache and Queue Layer (Saturday 03:30-04:15 UTC)

**Services:** cache_cluster, message_queue

#### Step 2.1: Cache Cluster Migration
- **Service:** cache_cluster
- **Action:** Deploy Redis 7.0 cluster (5 nodes) in us-west-2, warm cache
- **Dependencies:** None
- **Estimated Downtime:** 0 minutes (cold start acceptable)
- **Verification:**
  - Verify cluster health
  - Test read/write operations
  - Confirm node count (5)

#### Step 2.2: Message Queue Migration
- **Service:** message_queue
- **Action:** Deploy RabbitMQ 3.12 in us-west-2, configure federation from old cluster, drain old queues
- **Dependencies:** None
- **Estimated Downtime:** 5 minutes (during queue drain)
- **Verification:**
  - Verify queue federation
  - Test message publish/consume
  - Confirm no message loss

**Rollback:** Redirect services to us-east-1 cache and queue instances

### Phase 3: Core Application Services (Saturday 04:15-05:00 UTC)

**Services:** auth_service, worker_service, notification_service

#### Step 3.1: Auth Service Migration
- **Service:** auth_service
- **Action:** Deploy Java 17 instances (4x) in us-west-2, configure against new DB and cache
- **Dependencies:** primary_db, cache_cluster
- **Estimated Downtime:** 0 minutes (blue-green deployment)
- **Verification:**
  - Health check /health returns 200
  - Test authentication flow
  - Verify session management

#### Step 3.2: Worker Service Migration
- **Service:** worker_service
- **Action:** Deploy Python 3.12 instances (8x) in us-west-2
- **Dependencies:** primary_db, message_queue, cache_cluster
- **Estimated Downtime:** 0 minutes (graceful shutdown of old workers)
- **Verification:**
  - Health check /ready returns 200
  - Verify job processing
  - Monitor queue depths

#### Step 3.3: Notification Service Migration
- **Service:** notification_service
- **Action:** Deploy Go 1.21 instances (3x) in us-west-2
- **Dependencies:** message_queue, cache_cluster
- **Estimated Downtime:** 0 minutes (blue-green deployment)
- **Verification:**
  - Health check /health returns 200
  - Test notification delivery

**Rollback:** Redirect traffic to us-east-1 instances, reconnect to old data layer

### Phase 4: API and Frontend Layer (Saturday 05:00-05:30 UTC)

**Services:** api_gateway, monitoring, web_frontend

#### Step 4.1: API Gateway Migration
- **Service:** api_gateway
- **Action:** Deploy Node.js 20 instances (6x) in us-west-2
- **Dependencies:** auth_service, cache_cluster
- **Estimated Downtime:** 0 minutes (blue-green deployment)
- **Verification:**
  - Health check /status returns 200
  - Test API endpoints
  - Verify routing rules

#### Step 4.2: Monitoring Migration
- **Service:** monitoring
- **Action:** Deploy Go 1.21 instances (3x) in us-west-2
- **Dependencies:** primary_db, cache_cluster
- **Estimated Downtime:** 0 minutes
- **Verification:**
  - Health check /metrics returns 200
  - Verify data collection from all services

#### Step 4.3: Web Frontend Migration
- **Service:** web_frontend
- **Action:** Deploy Node.js 20 instances (4x) in us-west-2
- **Dependencies:** api_gateway
- **Estimated Downtime:** 0 minutes (blue-green deployment)
- **Verification:**
  - Health check /ping returns 200
  - Test user-facing functionality

**Rollback:** Switch DNS to us-east-1 API gateway and frontend

### Phase 5: Load Balancer Cutover (Saturday 05:30-06:00 UTC)

**Services:** load_balancer

#### Step 5.1: Load Balancer Migration
- **Service:** load_balancer
- **Action:** Deploy AWS ALB with WAF in us-west-2, configure SSL, update DNS
- **Dependencies:** api_gateway, web_frontend
- **Estimated Downtime:** 2 minutes (DNS propagation)
- **Verification:**
  - SSL certificate valid
  - WAF rules active
  - Traffic flowing to new backend
  - Response times within SLA

**Rollback:** Revert DNS to us-east-1 load balancer (keep old LB running for 24h)

## Post-Migration Validation

- [ ] All health checks passing
- [ ] Database replication healthy with zero lag
- [ ] Cache hit rates returning to normal
- [ ] Message queue depths stable
- [ ] Error rates at or below pre-migration levels
- [ ] Response latency within acceptable range
- [ ] Monitoring dashboards updated for new region
- [ ] Cross-region replication active for file storage
- [ ] WAF rules verified on new load balancer
- [ ] Run full integration test suite

## Rollback Procedures

Each phase has specific rollback steps documented above. The general rollback strategy:

1. **Within maintenance window:** Revert DNS, redirect to us-east-1 services
2. **After maintenance window:** If issues found within 24h, execute phase-specific rollback
3. **Data rollback:** Primary DB has continuous replication; can fail back with minimal data loss
4. **Full rollback deadline:** 24 hours post-migration
'''

with open('$WORKSPACE/migration_plan.md', 'w') as f:
    f.write(plan_md.strip() + '\n')

# Generate risk assessment
risk_assessment = {
    'overall_risk_level': 'high',
    'total_services': 12,
    'migration_phases': [
        {
            'phase': 1,
            'name': 'Storage and Data Layer',
            'services': ['file_storage', 'primary_db', 'replica_db'],
            'dependencies_met': True,
            'estimated_downtime_minutes': 15,
            'risks': [
                {
                    'description': 'PostgreSQL major version upgrade (13 to 15) may have incompatibilities',
                    'probability': 'medium',
                    'impact': 'high',
                    'mitigation': 'Test upgrade on staging environment first; use logical replication for zero-downtime cutover'
                },
                {
                    'description': 'Large database (340GB) transfer may exceed maintenance window',
                    'probability': 'low',
                    'impact': 'high',
                    'mitigation': 'Use continuous replication started days before cutover; only final sync during window'
                },
                {
                    'description': 'Data consistency issues during cutover',
                    'probability': 'low',
                    'impact': 'critical',
                    'mitigation': 'Use strong consistency mode; verify checksums post-migration'
                }
            ],
            'rollback_steps': [
                'Switch DNS back to us-east-1 primary database',
                'Disable cross-region replication',
                'Verify us-east-1 database is receiving writes'
            ]
        },
        {
            'phase': 2,
            'name': 'Cache and Queue Layer',
            'services': ['cache_cluster', 'message_queue'],
            'dependencies_met': True,
            'estimated_downtime_minutes': 5,
            'risks': [
                {
                    'description': 'Redis version upgrade may cause client compatibility issues',
                    'probability': 'low',
                    'impact': 'medium',
                    'mitigation': 'Test client libraries with Redis 7.0 before migration'
                },
                {
                    'description': 'Message loss during RabbitMQ queue drain',
                    'probability': 'medium',
                    'impact': 'high',
                    'mitigation': 'Use federation plugin for graceful migration; enable publisher confirms'
                }
            ],
            'rollback_steps': [
                'Redirect application services to us-east-1 Redis cluster',
                'Reconnect to us-east-1 RabbitMQ instance',
                'Verify no messages were lost in transition'
            ]
        },
        {
            'phase': 3,
            'name': 'Core Application Services',
            'services': ['auth_service', 'worker_service', 'notification_service'],
            'dependencies_met': True,
            'estimated_downtime_minutes': 0,
            'risks': [
                {
                    'description': 'Java 11 to 17 upgrade may break auth_service due to removed APIs',
                    'probability': 'medium',
                    'impact': 'high',
                    'mitigation': 'Run full test suite against Java 17 build before migration'
                },
                {
                    'description': 'Python 3.10 to 3.12 upgrade may have dependency conflicts',
                    'probability': 'low',
                    'impact': 'medium',
                    'mitigation': 'Test all dependencies in staging; use pinned requirements'
                },
                {
                    'description': 'Worker service scaling from 5 to 8 instances may overwhelm database connections',
                    'probability': 'medium',
                    'impact': 'medium',
                    'mitigation': 'Implement connection pooling; monitor DB connection count during rollout'
                }
            ],
            'rollback_steps': [
                'Redirect traffic to us-east-1 application instances',
                'Reconnect services to us-east-1 data layer',
                'Verify service health in us-east-1'
            ]
        },
        {
            'phase': 4,
            'name': 'API and Frontend Layer',
            'services': ['api_gateway', 'monitoring', 'web_frontend'],
            'dependencies_met': True,
            'estimated_downtime_minutes': 0,
            'risks': [
                {
                    'description': 'Node.js 18 to 20 upgrade may affect API gateway routing behavior',
                    'probability': 'low',
                    'impact': 'high',
                    'mitigation': 'Run integration tests against Node 20 build; deploy canary first'
                },
                {
                    'description': 'Monitoring gaps during migration transition',
                    'probability': 'medium',
                    'impact': 'medium',
                    'mitigation': 'Run monitoring in both regions during transition; set up cross-region alerting'
                }
            ],
            'rollback_steps': [
                'Switch DNS to us-east-1 API gateway',
                'Redirect frontend traffic to us-east-1',
                'Restore monitoring to us-east-1 configuration'
            ]
        },
        {
            'phase': 5,
            'name': 'Load Balancer Cutover',
            'services': ['load_balancer'],
            'dependencies_met': True,
            'estimated_downtime_minutes': 2,
            'risks': [
                {
                    'description': 'DNS propagation delay causing split-brain traffic',
                    'probability': 'medium',
                    'impact': 'medium',
                    'mitigation': 'Use low TTL DNS records before migration; keep old LB active for 24h'
                },
                {
                    'description': 'WAF rules may block legitimate traffic',
                    'probability': 'low',
                    'impact': 'high',
                    'mitigation': 'Start WAF in detection-only mode; tune rules before enforcement'
                },
                {
                    'description': 'SSL certificate issues on new ALB',
                    'probability': 'low',
                    'impact': 'high',
                    'mitigation': 'Pre-provision and validate SSL certificates in target region'
                }
            ],
            'rollback_steps': [
                'Revert DNS records to us-east-1 load balancer',
                'Keep us-east-1 load balancer running for 24 hours',
                'Monitor traffic distribution during DNS propagation'
            ]
        }
    ],
    'total_estimated_downtime_minutes': 22,
    'critical_path': [
        'file_storage', 'primary_db', 'replica_db', 'cache_cluster',
        'message_queue', 'auth_service', 'api_gateway', 'web_frontend', 'load_balancer'
    ],
    'pre_migration_checks': [
        'Full database backup completed and verified',
        'Target region capacity confirmed',
        'Cross-region network connectivity tested',
        'All service artifacts built and tested for target versions',
        'Rollback scripts tested in staging environment',
        'Monitoring and alerting configured in target region',
        'Stakeholders notified of maintenance window',
        'DNS TTL lowered 48 hours before migration'
    ],
    'post_migration_checks': [
        'All service health checks returning 200',
        'Database replication lag is zero',
        'Cache hit rates stabilized',
        'Message queue depths stable and processing normally',
        'Error rates at or below pre-migration baseline',
        'API response latency within SLA',
        'SSL certificates valid and WAF active',
        'Cross-region file replication verified',
        'Full integration test suite passed',
        'Monitoring dashboards showing data from new region'
    ]
}

with open('$WORKSPACE/risk_assessment.json', 'w') as f:
    json.dump(risk_assessment, f, indent=2)
"

echo "Solution written to $WORKSPACE/migration_plan.md and $WORKSPACE/risk_assessment.json"
