#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import re, sys
import yaml

ws = sys.argv[1]

with open(f'{ws}/config.yaml') as f:
    config = yaml.safe_load(f)

with open(f'{ws}/server.log') as f:
    log_lines = f.read().strip().split('\n')

services_config = config['services']
total = len(log_lines)
errors = [l for l in log_lines if ' ERROR ' in l]
warnings = [l for l in log_lines if ' WARNING ' in l]

# Threshold violations
error_counts = {}
for svc in services_config:
    count = sum(1 for l in errors if svc.lower() in l.lower())
    error_counts[svc] = count

violations = []
for svc in sorted(error_counts):
    if error_counts[svc] > services_config[svc]['max_errors']:
        violations.append(f'- {svc}: {error_counts[svc]} errors (threshold: {services_config[svc]["max_errors"]})')

# Unknown services
svc_pattern = re.compile(r'[Ss]ervice (\w+)')
found_services = set()
for l in log_lines:
    m = svc_pattern.search(l)
    if m:
        found_services.add(m.group(1).lower())
known = set(s.lower() for s in services_config)
unknown = sorted(found_services - known)

# Port mismatches
port_pattern = re.compile(r'[Ss]ervice (\w+).*port (\d+)')
mismatches = {}
for l in log_lines:
    m = port_pattern.search(l)
    if m:
        svc_name = m.group(1).lower()
        log_port = int(m.group(2))
        if svc_name in known and svc_name not in mismatches:
            cfg_port = services_config[svc_name]['port']
            if log_port != cfg_port:
                mismatches[svc_name] = (log_port, cfg_port)

lines = []
lines.append(f'Total log entries: {total}')
lines.append(f'Error count: {len(errors)}')
lines.append(f'Warning count: {len(warnings)}')
lines.append('')
lines.append('Threshold Violations:')
for v in violations:
    lines.append(v)
lines.append('')
lines.append('Unknown Services:')
for u in unknown:
    lines.append(f'- {u}')
lines.append('')
lines.append('Port Mismatches:')
for svc in sorted(mismatches):
    lp, cp = mismatches[svc]
    lines.append(f'- {svc}: log port {lp}, config port {cp}')

with open(f'{ws}/report.txt', 'w') as f:
    f.write('\n'.join(lines) + '\n')
PYEOF
