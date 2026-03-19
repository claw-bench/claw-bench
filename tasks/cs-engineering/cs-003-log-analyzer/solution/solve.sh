#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import json
from collections import defaultdict, deque
from datetime import datetime, timedelta

log_path = f"{WORKSPACE}/server.log"
report_path = f"{WORKSPACE}/incident_report.json"

# Read logs
logs = []
with open(log_path, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        timestamp_str, level, service, message = line.split(',', 3)
        timestamp = datetime.fromisoformat(timestamp_str)
        logs.append({'timestamp': timestamp, 'level': level, 'service': service, 'message': message})

# Sort logs by timestamp (just in case)
logs.sort(key=lambda x: x['timestamp'])

# Detect error spikes (>5 errors in 1 minute)
error_spikes = []
error_times = [log['timestamp'] for log in logs if log['level'] == 'ERROR']

start_idx = 0
for end_idx in range(len(error_times)):
    while error_times[end_idx] - error_times[start_idx] > timedelta(minutes=1):
        start_idx += 1
    count = end_idx - start_idx + 1
    if count > 5:
        # Record spike time window
        window_start = error_times[start_idx]
        window_end = error_times[end_idx]
        # Avoid duplicates: only add if new
        if not error_spikes or error_spikes[-1]['window_end'] < window_start:
            error_spikes.append({'window_start': window_start, 'window_end': window_end, 'count': count})

# Detect repeated patterns (3+ consecutive identical messages)
repeated_patterns = []
if logs:
    prev_msg = logs[0]['message']
    prev_level = logs[0]['level']
    prev_service = logs[0]['service']
    count = 1
    start_time = logs[0]['timestamp']

    for i in range(1, len(logs)):
        log = logs[i]
        if log['message'] == prev_msg:
            count += 1
        else:
            if count >= 3:
                repeated_patterns.append({'message': prev_msg, 'start_time': start_time, 'count': count})
            prev_msg = log['message']
            count = 1
            start_time = log['timestamp']
    # Check last sequence
    if count >= 3:
        repeated_patterns.append({'message': prev_msg, 'start_time': start_time, 'count': count})

# Detect service failures (3+ consecutive ERRORs from same service)
service_failures = []

current_service = None
current_count = 0
start_time = None

for log in logs:
    if log['level'] == 'ERROR':
        if log['service'] == current_service:
            current_count += 1
        else:
            # Check previous
            if current_count >= 3:
                service_failures.append({'service': current_service, 'start_time': start_time, 'count': current_count})
            current_service = log['service']
            current_count = 1
            start_time = log['timestamp']
    else:
        if current_count >= 3:
            service_failures.append({'service': current_service, 'start_time': start_time, 'count': current_count})
        current_service = None
        current_count = 0
        start_time = None

# Check at end
if current_count >= 3:
    service_failures.append({'service': current_service, 'start_time': start_time, 'count': current_count})

# Compose timeline
timeline = []
for spike in error_spikes:
    timeline.append({
        'timestamp': spike['window_start'].isoformat(),
        'description': f"Error spike detected from {spike['window_start'].isoformat()} to {spike['window_end'].isoformat()} with {spike['count']} errors"
    })

for rp in repeated_patterns:
    timeline.append({
        'timestamp': rp['start_time'].isoformat(),
        'description': f"Repeated pattern detected: '{rp['message']}' repeated {rp['count']} times consecutively"
    })

for sf in service_failures:
    timeline.append({
        'timestamp': sf['start_time'].isoformat(),
        'description': f"Service failure detected: service '{sf['service']}' had {sf['count']} consecutive errors"
    })

# Sort timeline by timestamp
timeline.sort(key=lambda x: x['timestamp'])

# Anomalies summary
anomalies = []
if error_spikes:
    anomalies.append('error_spikes')
if repeated_patterns:
    anomalies.append('repeated_patterns')
if service_failures:
    anomalies.append('service_failures')

# Affected services
affected_services = set()
for sf in service_failures:
    affected_services.add(sf['service'])
for log in logs:
    if log['level'] == 'ERROR':
        affected_services.add(log['service'])
for rp in repeated_patterns:
    # We do not have service info for repeated patterns directly, but can scan logs
    # Find services that logged that message consecutively
    msg = rp['message']
    # Find first occurrence index
    idx = next((i for i,l in enumerate(logs) if l['message'] == msg and l['timestamp'] == rp['start_time']), None)
    if idx is not None:
        # Collect services for the repeated messages
        services_set = set()
        for j in range(idx, min(idx + rp['count'], len(logs))):
            if logs[j]['message'] == msg:
                services_set.add(logs[j]['service'])
        affected_services.update(services_set)

affected_services = sorted(affected_services)

# Determine severity
severity = 'low'
if ('error_spikes' in anomalies or 'service_failures' in anomalies) and 'repeated_patterns' in anomalies:
    severity = 'high'
elif 'error_spikes' in anomalies or 'service_failures' in anomalies:
    severity = 'medium'

# Write report
report = {
    'timeline': timeline,
    'anomalies': anomalies,
    'affected_services': affected_services,
    'severity': severity
}

with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)
EOF
