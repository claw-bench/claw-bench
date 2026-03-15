#!/usr/bin/env bash
# Oracle solution for doc-010-document-template-engine
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
import re

ws = sys.argv[1]

with open(f'{ws}/data.json', 'r') as f:
    data = json.load(f)

with open(f'{ws}/template.txt', 'r') as f:
    template = f.read()

def resolve(key, context, global_data):
    """Resolve a dotted key against context (loop item) or global data."""
    if key == '.':
        return context
    if key.startswith('.'):
        key = key[1:]
        obj = context
    else:
        obj = global_data
    for part in key.split('.'):
        if isinstance(obj, dict) and part in obj:
            obj = obj[part]
        else:
            return None
    return obj

def is_truthy(val):
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return len(val) > 0
    if isinstance(val, list):
        return len(val) > 0
    return True

def process(text, context, global_data):
    # Process loops: {{#key}}...{{/key}}
    loop_pattern = r'\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}'
    def replace_loop(m):
        key = m.group(1)
        body = m.group(2)
        arr = resolve(key, context, global_data)
        if not isinstance(arr, list):
            return ''
        result = []
        for item in arr:
            result.append(process(body, item, global_data))
        return ''.join(result)

    text = re.sub(loop_pattern, replace_loop, text, flags=re.DOTALL)

    # Process truthy conditionals: {{?key}}...{{/key}}
    cond_pattern = r'\{\{\?([a-zA-Z_][\w.]*)\}\}(.*?)\{\{/\1\}\}'
    def replace_cond(m):
        key = m.group(1)
        body = m.group(2)
        val = resolve(key, context, global_data)
        if is_truthy(val):
            return process(body, context, global_data)
        return ''

    text = re.sub(cond_pattern, replace_cond, text, flags=re.DOTALL)

    # Process falsy conditionals: {{^key}}...{{/key}}
    neg_pattern = r'\{\{\^([a-zA-Z_][\w.]*)\}\}(.*?)\{\{/\1\}\}'
    def replace_neg(m):
        key = m.group(1)
        body = m.group(2)
        val = resolve(key, context, global_data)
        if not is_truthy(val):
            return process(body, context, global_data)
        return ''

    text = re.sub(neg_pattern, replace_neg, text, flags=re.DOTALL)

    # Process variable substitutions: {{key}} or {{.key}} or {{.}}
    var_pattern = r'\{\{(\.?[\w.]*)\}\}'
    def replace_var(m):
        key = m.group(1)
        val = resolve(key, context, global_data)
        if val is None:
            return ''
        if isinstance(val, bool):
            return str(val).lower()
        return str(val)

    text = re.sub(var_pattern, replace_var, text)

    return text

result = process(template, {}, data)

with open(f'{ws}/output.txt', 'w') as f:
    f.write(result)
PYEOF

echo "Solution written to $WORKSPACE/output.txt"
