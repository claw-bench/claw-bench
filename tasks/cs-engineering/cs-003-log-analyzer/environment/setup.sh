#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import random
import datetime
random.seed(42)

levels = ['INFO', 'WARN', 'ERROR']
services = ['auth', 'payment', 'database', 'cache', 'api']

start_time = datetime.datetime(2024, 6, 1, 12, 0, 0)

entries = []

# Generate 120 log entries (2 hours approx, one per minute)
for i in range(120):
    current_time = start_time + datetime.timedelta(seconds=i * 60)
    # Randomly decide number of logs in this minute (1 to 3)
    count = random.choice([1, 2, 3])
    for _ in range(count):
        timestamp = current_time + datetime.timedelta(seconds=random.randint(0,59))
        # Introduce error spikes: at minute 30 and 90, generate 7 errors
        if i == 30:
            level = 'ERROR'
            service = random.choice(services)
            message = 'Simulated error spike event'
        elif i == 90:
            level = 'ERROR'
            service = random.choice(services)
            message = 'Simulated error spike event'
        else:
            # Normal distribution of levels
            level = random.choices(levels, weights=[70, 20, 10])[0]
            service = random.choice(services)
            if level == 'ERROR':
                message = random.choice(['Timeout occurred', 'Connection lost', 'Null pointer exception', 'Failed to connect'])
            elif level == 'WARN':
                message = random.choice(['Slow response', 'High memory usage', 'Retrying request'])
            else:
                message = random.choice(['Request processed', 'User login', 'Cache hit'])

        entries.append((timestamp.isoformat(timespec='seconds'), level, service, message))

# Add repeated patterns: 3 times consecutively at minute 45
repeat_time = start_time + datetime.timedelta(minutes=45)
for i in range(3):
    ts = repeat_time + datetime.timedelta(seconds=i)
    entries.append((ts.isoformat(timespec='seconds'), 'WARN', 'api', 'Repeated warning message'))

# Add service failure: 4 consecutive errors for 'database' at minute 60
failure_time = start_time + datetime.timedelta(minutes=60)
for i in range(4):
    ts = failure_time + datetime.timedelta(seconds=i * 10)
    entries.append((ts.isoformat(timespec='seconds'), 'ERROR', 'database', 'Database connection failure'))

# Sort entries by timestamp
entries.sort(key=lambda x: x[0])

with open(f'{WORKSPACE}/server.log', 'w') as f:
    for e in entries:
        f.write(','.join(e) + '\n')
EOF
