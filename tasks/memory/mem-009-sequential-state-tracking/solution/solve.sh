#!/usr/bin/env bash
# Oracle solution for mem-009-sequential-state-tracking
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json

ws = sys.argv[1]

state = {}

def get_val(name_or_num, state):
    """Return numeric value: parse as int if possible, otherwise look up variable."""
    try:
        return int(name_or_num)
    except ValueError:
        return state.get(name_or_num, 0)

with open(f'{ws}/transitions.txt', 'r') as f:
    lines = f.readlines()

for line in lines:
    line = line.strip()
    if not line or line.startswith('#'):
        continue

    parts = line.split()
    cmd = parts[0]

    if cmd == 'SET':
        # SET x=5 or SET x=y
        assignment = parts[1]
        var_name, val_str = assignment.split('=', 1)
        try:
            state[var_name] = int(val_str)
        except ValueError:
            state[var_name] = state.get(val_str, 0)

    elif cmd == 'ADD':
        var_name = parts[1]
        operand = get_val(parts[2], state)
        state[var_name] = state.get(var_name, 0) + operand

    elif cmd == 'SUBTRACT':
        var_name = parts[1]
        operand = get_val(parts[2], state)
        state[var_name] = state.get(var_name, 0) - operand

    elif cmd == 'MULTIPLY':
        var_name = parts[1]
        operand = get_val(parts[2], state)
        state[var_name] = state.get(var_name, 0) * operand

    elif cmd == 'DIVIDE':
        var_name = parts[1]
        operand = get_val(parts[2], state)
        if operand != 0:
            current = state.get(var_name, 0)
            state[var_name] = int(current / operand) if current >= 0 else -(abs(current) // abs(operand))

    elif cmd == 'MOD':
        var_name = parts[1]
        operand = get_val(parts[2], state)
        if operand != 0:
            state[var_name] = state.get(var_name, 0) % operand

    elif cmd == 'SWAP':
        var_a = parts[1]
        var_b = parts[2]
        val_a = state.get(var_a, 0)
        val_b = state.get(var_b, 0)
        state[var_a] = val_b
        state[var_b] = val_a

    elif cmd == 'DELETE':
        var_name = parts[1]
        state.pop(var_name, None)

with open(f'{ws}/final_state.json', 'w') as f:
    json.dump(dict(sorted(state.items())), f, indent=2)
    f.write('\n')
PYEOF

echo "Solution written to $WORKSPACE/final_state.json"
