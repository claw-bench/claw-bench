#!/usr/bin/env bash
# Oracle solution for sys-009-performance-diagnostic
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json, csv, math

def read_csv(path, value_col):
    data = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({'hour': int(row['hour']), 'value': float(row[value_col])})
    return data

def stats(data):
    values = [d['value'] for d in data]
    mean = sum(values) / len(values)
    variance = sum((v - mean)**2 for v in values) / len(values)
    stddev = math.sqrt(variance)
    return mean, min(values), max(values), stddev

def find_anomalies(data, mean, stddev, threshold=2.0):
    anomalies = []
    for d in data:
        deviation = abs(d['value'] - mean)
        if deviation > threshold * stddev:
            atype = 'spike' if d['value'] > mean else 'drop'
            anomalies.append({'hour': d['hour'], 'value': d['value'], 'type': atype})
    return anomalies

cpu_data = read_csv('$WORKSPACE/metrics/cpu.csv', 'usage_percent')
mem_data = read_csv('$WORKSPACE/metrics/memory.csv', 'usage_percent')
dio_data = read_csv('$WORKSPACE/metrics/disk_io.csv', 'throughput_mbps')

cpu_mean, cpu_min, cpu_max, cpu_std = stats(cpu_data)
mem_mean, mem_min, mem_max, mem_std = stats(mem_data)
dio_mean, dio_min, dio_max, dio_std = stats(dio_data)

cpu_anomalies = find_anomalies(cpu_data, cpu_mean, cpu_std)
mem_anomalies = find_anomalies(mem_data, mem_mean, mem_std)
dio_anomalies = find_anomalies(dio_data, dio_mean, dio_std)

bottlenecks = []

# CPU bottleneck: hours 14-17 are > 80%
cpu_high = [d for d in cpu_data if d['value'] > 80]
if cpu_high:
    start_h = min(d['hour'] for d in cpu_high)
    end_h = max(d['hour'] for d in cpu_high)
    severity = 'critical' if any(d['value'] > 90 for d in cpu_high) else 'warning'
    bottlenecks.append({
        'resource': 'cpu',
        'severity': severity,
        'time_window': {'start_hour': start_h, 'end_hour': end_h},
        'description': f'CPU usage exceeded 80% for {len(cpu_high)} hours (peak: {cpu_max}%)'
    })

# Memory bottleneck: hours 14-17 are > 80%
mem_high = [d for d in mem_data if d['value'] > 80]
if mem_high:
    start_h = min(d['hour'] for d in mem_high)
    end_h = max(d['hour'] for d in mem_high)
    severity = 'critical' if any(d['value'] > 90 for d in mem_high) else 'warning'
    bottlenecks.append({
        'resource': 'memory',
        'severity': severity,
        'time_window': {'start_hour': start_h, 'end_hour': end_h},
        'description': f'Memory usage exceeded 80% for {len(mem_high)} hours (peak: {mem_max}%)'
    })

# Disk I/O bottleneck: > 100 MB/s
dio_high = [d for d in dio_data if d['value'] > 100]
if dio_high:
    start_h = min(d['hour'] for d in dio_high)
    end_h = max(d['hour'] for d in dio_high)
    bottlenecks.append({
        'resource': 'disk_io',
        'severity': 'warning',
        'time_window': {'start_hour': start_h, 'end_hour': end_h},
        'description': f'Disk I/O exceeded 100 MB/s for {len(dio_high)} hours (peak: {dio_max} MB/s)'
    })

recommendations = [
    'Consider scaling CPU resources or optimizing workloads during peak hours (14:00-17:00)',
    'Investigate memory-intensive processes during afternoon hours; consider adding RAM or optimizing memory usage',
    'Review disk I/O patterns at hours 12, 16-17; consider SSD upgrade or I/O scheduling optimization',
    'Implement resource-based autoscaling to handle peak demand periods',
    'Schedule batch jobs and heavy workloads outside of peak hours (14:00-17:00)'
]

report = {
    'analysis_period': {
        'start': '2024-03-15T00:00:00',
        'end': '2024-03-15T23:00:00',
        'data_points': 24
    },
    'cpu': {
        'mean': round(cpu_mean, 1),
        'max': cpu_max,
        'min': cpu_min,
        'anomalies': cpu_anomalies
    },
    'memory': {
        'mean': round(mem_mean, 1),
        'max': mem_max,
        'min': mem_min,
        'anomalies': mem_anomalies
    },
    'disk_io': {
        'mean': round(dio_mean, 1),
        'max': dio_max,
        'min': dio_min,
        'anomalies': dio_anomalies
    },
    'bottlenecks': bottlenecks,
    'recommendations': recommendations
}

with open('$WORKSPACE/diagnosis.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/diagnosis.json"
