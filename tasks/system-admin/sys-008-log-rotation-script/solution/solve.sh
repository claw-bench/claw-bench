#!/usr/bin/env bash
# Oracle solution for sys-008-log-rotation-script
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
from datetime import datetime

with open('$WORKSPACE/logs/log_manifest.json') as f:
    manifest = json.load(f)

current_date = datetime.strptime(manifest['current_date'], '%Y-%m-%d')
SIZE_THRESHOLD = 100  # MB
AGE_THRESHOLD = 7     # days
MAX_ROTATIONS = 5

to_rotate = []
to_skip = []
space_to_free = 0

for finfo in manifest['files']:
    mod_date = datetime.strptime(finfo['last_modified'], '%Y-%m-%d')
    age_days = (current_date - mod_date).days
    size_mb = finfo['size_mb']
    name = finfo['name']
    cur_rot = finfo['current_rotations']

    over_size = size_mb >= SIZE_THRESHOLD
    over_age = age_days >= AGE_THRESHOLD

    if over_size or over_age:
        if over_size and over_age:
            reason = 'both'
        elif over_size:
            reason = 'size'
        else:
            reason = 'age'

        if cur_rot >= MAX_ROTATIONS:
            action = 'rotate_and_compress'
        else:
            action = 'rotate'

        to_rotate.append({
            'name': name,
            'reason': reason,
            'size_mb': size_mb,
            'age_days': age_days,
            'current_rotations': cur_rot,
            'action': action
        })
        space_to_free += size_mb
    else:
        to_skip.append({
            'name': name,
            'reason': 'within_thresholds'
        })

plan = {
    'current_date': '2024-03-15',
    'rules': {
        'size_threshold_mb': SIZE_THRESHOLD,
        'age_threshold_days': AGE_THRESHOLD,
        'max_rotations': MAX_ROTATIONS
    },
    'files_to_rotate': to_rotate,
    'files_to_skip': to_skip,
    'summary': {
        'total_files': len(manifest['files']),
        'to_rotate': len(to_rotate),
        'to_skip': len(to_skip),
        'space_to_free_mb': round(space_to_free, 1)
    }
}

with open('$WORKSPACE/rotation_plan.json', 'w') as f:
    json.dump(plan, f, indent=2)

# Generate rotation script
log_dir = manifest['log_directory']
script_lines = [
    '#!/usr/bin/env bash',
    'set -euo pipefail',
    '',
    '# Log Rotation Script',
    '# Generated on 2024-03-15',
    '# Rotates log files based on size (>=100MB) and age (>=7 days) thresholds',
    '# Max rotations: 5',
    '',
    'LOG_DIR=\"' + log_dir + '\"',
    'MAX_ROTATIONS=5',
    '',
    'rotate_file() {',
    '    local file=\"\$1\"',
    '    local filepath=\"\$LOG_DIR/\$file\"',
    '',
    '    if [ ! -f \"\$filepath\" ]; then',
    '        echo \"Warning: \$filepath not found, skipping\"',
    '        return',
    '    fi',
    '',
    '    echo \"Rotating \$file...\"',
    '',
    '    # Remove oldest rotation if at max',
    '    if [ -f \"\$filepath.\$MAX_ROTATIONS\" ]; then',
    '        rm -f \"\$filepath.\$MAX_ROTATIONS\"',
    '    fi',
    '',
    '    # Shift existing rotations up',
    '    for i in $(seq \$((MAX_ROTATIONS - 1)) -1 1); do',
    '        if [ -f \"\$filepath.\$i\" ]; then',
    '            mv \"\$filepath.\$i\" \"\$filepath.\$((i + 1))\"',
    '        fi',
    '    done',
    '',
    '    # Rotate current file',
    '    mv \"\$filepath\" \"\$filepath.1\"',
    '',
    '    # Create new empty log file',
    '    touch \"\$filepath\"',
    '    chmod 644 \"\$filepath\"',
    '',
    '    echo \"Done rotating \$file\"',
    '}',
    '',
    '# Rotate files that exceed thresholds',
]

for entry in to_rotate:
    script_lines.append(f'rotate_file \"{entry[\"name\"]}\"  # reason: {entry[\"reason\"]}, size: {entry[\"size_mb\"]}MB, age: {entry[\"age_days\"]}d')

script_lines.extend([
    '',
    'echo \"Log rotation complete.\"',
])

with open('$WORKSPACE/rotate.sh', 'w') as f:
    f.write('\n'.join(script_lines) + '\n')
"

chmod +x "$WORKSPACE/rotate.sh"
echo "Solution written to $WORKSPACE/rotation_plan.json and $WORKSPACE/rotate.sh"
