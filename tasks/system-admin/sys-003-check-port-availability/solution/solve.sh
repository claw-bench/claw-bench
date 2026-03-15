#!/usr/bin/env bash
# Oracle solution for sys-003-check-port-availability
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json, re

service_map = {
    22: 'ssh', 25: 'smtp', 53: 'dns', 80: 'http', 443: 'https',
    3306: 'mysql', 5432: 'postgresql', 6379: 'redis',
    8080: 'http-alt', 8443: 'https-alt', 9090: 'prometheus'
}

ports = []
with open('$WORKSPACE/ports.txt') as f:
    for line in f:
        line = line.strip()
        if not line.startswith('tcp'):
            continue
        parts = line.split()
        local_addr = parts[3]
        addr_parts = local_addr.rsplit(':', 1)
        bind_address = addr_parts[0]
        port = int(addr_parts[1])
        pid_prog = parts[6] if len(parts) > 6 else '-'
        pid = None
        process_name = 'unknown'
        if '/' in pid_prog:
            pid_str, process_name = pid_prog.split('/', 1)
            pid = int(pid_str)
        service = service_map.get(port, 'unknown')
        ports.append({
            'port': port,
            'bind_address': bind_address,
            'protocol': 'tcp',
            'pid': pid,
            'process_name': process_name,
            'service': service
        })

ports.sort(key=lambda x: x['port'])
well_known = sorted([p['port'] for p in ports if p['port'] <= 1023])
high = sorted([p['port'] for p in ports if p['port'] > 1023])

report = {
    'total_listening_ports': len(ports),
    'ports': ports,
    'well_known_ports': well_known,
    'high_ports': high
}

with open('$WORKSPACE/port_report.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/port_report.json"
