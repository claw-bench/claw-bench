#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
import datetime
random.seed(42)

num_sensors = 5
readings_per_sensor = 25
start_time = datetime.datetime(2023, 1, 1, 0, 0, 0)

fieldnames = ['timestamp', 'sensor_id', 'value']

with open(f'{WORKSPACE}/sensor_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for sensor_idx in range(1, num_sensors + 1):
        sensor_id = f'sensor_{sensor_idx}'
        base_value = 50 + sensor_idx * 10
        for i in range(readings_per_sensor):
            # Increment time by 10 minutes
            timestamp = (start_time + datetime.timedelta(minutes=10*i)).isoformat()
            # Generate normal value
            value = random.gauss(base_value, 5)
            # Inject anomalies randomly
            if random.random() < 0.08:
                # Large spike or drop
                value += random.choice([-30, 30])
            writer.writerow({'timestamp': timestamp, 'sensor_id': sensor_id, 'value': round(value, 2)})
EOF
