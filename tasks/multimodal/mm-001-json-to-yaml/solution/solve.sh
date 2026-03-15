#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import json, sys

ws = sys.argv[1]

def to_yaml(obj, indent=0):
    lines = []
    prefix = '  ' * indent
    if isinstance(obj, dict):
        for key, val in obj.items():
            if val is None:
                lines.append(f'{prefix}{key}: null')
            elif isinstance(val, bool):
                lines.append(f'{prefix}{key}: {str(val).lower()}')
            elif isinstance(val, (dict,)):
                lines.append(f'{prefix}{key}:')
                lines.extend(to_yaml(val, indent + 1).splitlines())
            elif isinstance(val, list):
                lines.append(f'{prefix}{key}:')
                for item in val:
                    if isinstance(item, dict):
                        first = True
                        for k2, v2 in item.items():
                            if first:
                                if v2 is None:
                                    lines.append(f'{prefix}- {k2}: null')
                                elif isinstance(v2, bool):
                                    lines.append(f'{prefix}- {k2}: {str(v2).lower()}')
                                elif isinstance(v2, (int, float)):
                                    lines.append(f'{prefix}- {k2}: {v2}')
                                elif isinstance(v2, str):
                                    lines.append(f'{prefix}- {k2}: {repr_str(v2)}')
                                elif isinstance(v2, (dict, list)):
                                    lines.append(f'{prefix}- {k2}:')
                                    lines.extend(to_yaml(v2, indent + 2).splitlines())
                                first = False
                            else:
                                sub = to_yaml({k2: v2}, indent + 1)
                                lines.extend(sub.splitlines())
                    elif isinstance(item, str):
                        lines.append(f'{prefix}- {repr_str(item)}')
                    elif isinstance(item, (int, float)):
                        lines.append(f'{prefix}- {item}')
            elif isinstance(val, (int, float)):
                lines.append(f'{prefix}{key}: {val}')
            elif isinstance(val, str):
                lines.append(f'{prefix}{key}: {repr_str(val)}')
    return '\n'.join(lines)

def repr_str(s):
    # Quote strings that contain special chars
    if any(c in s for c in [':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@']):
        return repr(s)
    return s

with open(f'{ws}/config.json') as f:
    data = json.load(f)

result = to_yaml(data)
with open(f'{ws}/config.yaml', 'w') as f:
    f.write(result + '\n')
PYEOF
